import os
import sys
import json
import random
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def evaluate_variant(variant_name: str, enable_reflex: bool, enable_repair: bool, enable_harvest: bool, cycles: int = 1000, seed: int = 42) -> dict:
    random.seed(seed)
    with open("configs/organism_params.yaml", "r") as f:
        config = yaml.safe_load(f)

    bridge = BioSyntheticBridge(use_real_sensors=False)
    edge_ai = EdgeInferenceEngine(config)
    homeostasis = HomeostaticController(config)
    energy = EnergyManager()
    reflex = ReflexArc(config)
    repair = FaultRecoverySystem()

    survived = 0
    fe_history = []
    trauma_penalties = 0

    for _ in range(1, cycles + 1):
        telemetry = bridge.read_sensors()

        # Severe stochastic stress test: 8% shock, 6% node lesion, 5% thermal spike
        if random.random() < 0.08:
            telemetry["shock_g"] = round(random.uniform(2.5, 4.8), 2)
        if random.random() < 0.06:
            victim = random.choice(list(bridge.active_nodes.keys()))
            bridge.active_nodes[victim] = False
            telemetry["nodes"] = bridge.active_nodes.copy()
            telemetry["healthy_node_ratio"] = sum(bridge.active_nodes.values()) / len(bridge.active_nodes)
        if random.random() < 0.05:
            telemetry["tissue_temp_c"] = round(random.uniform(45.2, 49.0), 2)

        # Reflex Arc check
        if enable_reflex and reflex.detect_immediate_hazard(telemetry):
            action = reflex.trigger_evasion(telemetry)
            bridge.apply_metabolic_update(0.0, -0.005, action["power_mw"])
            fe_history.append(0.85)
            survived += 1
            continue
        elif not enable_reflex and reflex.detect_immediate_hazard(telemetry):
            # Unmitigated physical/thermal trauma degrades voltage & ATP
            bridge.apply_metabolic_update(-0.045, -0.06, 20.0)
            trauma_penalties += 1

        # Self-Repair check
        damaged = repair.diagnose(telemetry)
        if damaged and enable_repair:
            repair.reroute_pathways(damaged, bridge, silent=True)
            telemetry["nodes"] = bridge.active_nodes.copy()
            telemetry["healthy_node_ratio"] = 1.0
        elif damaged and not enable_repair:
            # Damaged actuators increase metabolic drag
            bridge.apply_metabolic_update(-0.015 * len(damaged), -0.02 * len(damaged), 15.0)

        state = homeostasis.evaluate(telemetry)
        fe_history.append(state["free_energy"])

        if enable_harvest:
            _, dv, datp = energy.optimize_harvesting(telemetry, state)
        else:
            dv, datp = 0.0, 0.0

        action = edge_ai.infer(telemetry, state)
        if action["cmd"] == "FORAGE_ORGANIC_MATTER" and enable_harvest:
            datp += 0.025

        bridge.apply_metabolic_update(dv, datp, action["power_mw"])

        if bridge.voltage > 3.15 and bridge.atp_nutrient > 0.05 and telemetry["healthy_node_ratio"] > 0.0:
            survived += 1
        else:
            break

    return {
        "variant": variant_name,
        "survived_cycles": survived,
        "survival_rate_pct": round((survived / cycles) * 100, 2),
        "mean_free_energy": round(sum(fe_history) / max(1, len(fe_history)), 4),
        "intact_nodes_pct": round(telemetry["healthy_node_ratio"] * 100, 1),
        "final_voltage": bridge.voltage,
        "final_atp": bridge.atp_nutrient
    }

def run_all_ablations():
    variants = [
        ("Full_6_Pillar_Organism", True, True, True),
        ("No_Reflex_Arc", False, True, True),
        ("No_Self_Repair", True, False, True),
        ("No_Energy_Harvesting", True, True, False),
    ]
    results = [evaluate_variant(*v) for v in variants]

    os.makedirs("data/logs", exist_ok=True)
    out_path = "data/logs/ablation_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== ABLATION STUDY RESULTS (1,000 CYCLES SEVERE STRESS) ===")
    print(f"{'Variant':<24} | {'Survival':<10} | {'Mean FE':<8} | {'Nodes':<7} | {'Final V':<8} | {'Final ATP'}")
    print("-" * 80)
    for r in results:
        print(f"{r['variant']:<24} | {r['survival_rate_pct']:>7.2f}%  | {r['mean_free_energy']:<8.4f} | {r['intact_nodes_pct']:>5.1f}% | {r['final_voltage']:<8.3f} | {r['final_atp']:.3f}")
    print(f"\nSaved structured ablation results to: {out_path}")

if __name__ == "__main__":
    run_all_ablations()
