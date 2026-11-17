import time
import argparse
import yaml
from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def run(use_real_sensors: bool = False, cycles: int = 12):
    with open("configs/organism_params.yaml", "r") as f:
        config = yaml.safe_load(f)

    bridge = BioSyntheticBridge(use_real_sensors=use_real_sensors)
    edge_ai = EdgeInferenceEngine(config)
    homeostasis = HomeostaticController(config)
    energy = EnergyManager()
    reflex = ReflexArc(config)
    repair = FaultRecoverySystem()

    sensor_mode = "LIVE ANDROID TERMUX-API" if use_real_sensors else "SIMULATED BIO-HYBRID"
    print(f"=== {config['organism']['name']} | Mode: {sensor_mode} ===")

    for cycle in range(1, cycles + 1):
        t0 = time.perf_counter()
        telemetry = bridge.read_sensors()

        # Inject synthetic trauma on cycle 5 during simulation mode
        if not use_real_sensors and cycle == 5:
            telemetry["shock_g"] = 3.15
            bridge.active_nodes["motor_left"] = False
            bridge.active_nodes["chemo_sensor"] = False

        print(f"\n[Cycle {cycle:02d}] Temp:{telemetry['tissue_temp_c']}C | V:{telemetry['voltage']}V | ATP:{telemetry['atp_nutrient']} | G:{telemetry['shock_g']}")

        if reflex.detect_immediate_hazard(telemetry):
            action = reflex.trigger_evasion(telemetry)
            bridge.actuate(action)
            bridge.apply_metabolic_update(0.0, -0.01, action["power_mw"])
            latency_us = (time.perf_counter() - t0) * 1e6
            print(f"[REFLEX LATENCY] {latency_us:.1f} us (Cloud Bypassed)")
            continue

        damaged = repair.diagnose(telemetry)
        if damaged:
            repair.reroute_pathways(damaged, bridge)
            telemetry["nodes"] = bridge.active_nodes.copy()
            telemetry["healthy_node_ratio"] = 1.0

        state = homeostasis.evaluate(telemetry)
        harvest_mode, dv, datp = energy.optimize_harvesting(telemetry, state)
        action = edge_ai.infer(telemetry, state)

        # Foraging yields extra organic ATP
        if action["cmd"] == "FORAGE_ORGANIC_MATTER":
            datp += 0.025

        bridge.apply_metabolic_update(dv, datp, action["power_mw"])
        latency_us = (time.perf_counter() - t0) * 1e6
        print(f"[HOMEOSTASIS] {state['mode']} (FE={state['free_energy']}) | Harvest: {harvest_mode} | Latency: {latency_us:.1f} us")
        bridge.actuate(action)
        time.sleep(0.25)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Use real Android hardware sensors via termux-api")
    parser.add_argument("--cycles", type=int, default=12, help="Number of control cycles to run")
    args = parser.parse_args()
    run(use_real_sensors=args.live, cycles=args.cycles)
