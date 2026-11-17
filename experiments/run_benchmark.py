import os
import sys
import csv
import json
import time
import random
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def run_stress_experiment(total_cycles: int = 1000, seed: int = 42):
    random.seed(seed)
    with open("configs/organism_params.yaml", "r") as f:
        config = yaml.safe_load(f)

    bridge = BioSyntheticBridge(use_real_sensors=False)
    edge_ai = EdgeInferenceEngine(config)
    homeostasis = HomeostaticController(config)
    energy = EnergyManager()
    reflex = ReflexArc(config)
    repair = FaultRecoverySystem()

    os.makedirs("data/logs", exist_ok=True)
    csv_path = "data/logs/telemetry_benchmark.csv"
    summary_path = "data/logs/experiment_summary.json"

    latencies = []
    reflex_triggers = 0
    survived_cycles = 0

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["cycle", "voltage", "atp", "temp_c", "shock_g", "free_energy", "mode", "action", "spikes", "latency_us"])

        for cycle in range(1, total_cycles + 1):
            t0 = time.perf_counter()
            telemetry = bridge.read_sensors()

            # Stochastic hostile events: 5% shock hazard, 4% node trauma, 3% thermal spike
            if random.random() < 0.05:
                telemetry["shock_g"] = round(random.uniform(2.3, 4.5), 2)
            if random.random() < 0.04:
                victim = random.choice(list(bridge.active_nodes.keys()))
                bridge.active_nodes[victim] = False
                telemetry["nodes"] = bridge.active_nodes.copy()
                telemetry["healthy_node_ratio"] = sum(bridge.active_nodes.values()) / len(bridge.active_nodes)
            if random.random() < 0.03:
                telemetry["tissue_temp_c"] = round(random.uniform(45.1, 48.0), 2)

            if reflex.detect_immediate_hazard(telemetry):
                action = reflex.trigger_evasion(telemetry)
                bridge.apply_metabolic_update(0.0, -0.005, action["power_mw"])
                reflex_triggers += 1
                state = {"free_energy": 0.95, "mode": "REFLEX_OVERRIDE"}
            else:
                damaged = repair.diagnose(telemetry)
                if damaged:
                    repair.reroute_pathways(damaged, bridge, silent=True)
                    telemetry["nodes"] = bridge.active_nodes.copy()
                    telemetry["healthy_node_ratio"] = 1.0

                state = homeostasis.evaluate(telemetry)
                _, dv, datp = energy.optimize_harvesting(telemetry, state)
                action = edge_ai.infer(telemetry, state)
                if action["cmd"] == "FORAGE_ORGANIC_MATTER":
                    datp += 0.025
                bridge.apply_metabolic_update(dv, datp, action["power_mw"])

            latency_us = round((time.perf_counter() - t0) * 1e6, 2)
            latencies.append(latency_us)

            writer.writerow([
                cycle, telemetry["voltage"], telemetry["atp_nutrient"],
                telemetry["tissue_temp_c"], telemetry["shock_g"],
                state["free_energy"], state["mode"], action["cmd"],
                action.get("spikes", 0), latency_us
            ])

            if telemetry["voltage"] > 3.15 and telemetry["atp_nutrient"] > 0.05:
                survived_cycles += 1
            else:
                break

    summary = {
        "organism": config["organism"]["name"],
        "requested_cycles": total_cycles,
        "survived_cycles": survived_cycles,
        "survival_rate_pct": round((survived_cycles / total_cycles) * 100, 2),
        "mean_edge_latency_us": round(sum(latencies) / len(latencies), 2),
        "max_edge_latency_us": max(latencies),
        "reflex_evasion_count": reflex_triggers,
        "autonomous_node_repairs": repair.total_repairs,
        "final_voltage": bridge.voltage,
        "final_atp": bridge.atp_nutrient
    }

    with open(summary_path, "w") as jf:
        json.dump(summary, jf, indent=2)

    print("=== BENCHMARK COMPLETE ===")
    print(json.dumps(summary, indent=2))
    print(f"Telemetry saved to: {csv_path}")

if __name__ == "__main__":
    run_stress_experiment(total_cycles=1000)
