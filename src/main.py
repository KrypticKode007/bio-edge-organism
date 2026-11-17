import time
import yaml
from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def run():
    with open("configs/organism_params.yaml", "r") as f:
        config = yaml.safe_load(f)

    bridge = BioSyntheticBridge(use_real_sensors=False)
    edge_ai = EdgeInferenceEngine()
    homeostasis = HomeostaticController(config)
    energy = EnergyManager()
    reflex = ReflexArc(config)
    repair = FaultRecoverySystem()

    print(f"--- Booting {config['organism']['name']} on Termux Edge Node ---")
    for cycle in range(1, 11):
        # Inject a simulated physical shock & node failure on cycle 5
        telemetry = bridge.read_sensors()
        if cycle == 5:
            telemetry["shock_g"] = 3.1
            bridge.active_nodes["motor_left"] = False

        print(f"\n[Cycle {cycle}] Temp: {telemetry['tissue_temp_c']}C | Volt: {telemetry['voltage']}V | ATP: {telemetry['atp_nutrient']}")

        if reflex.detect_immediate_hazard(telemetry):
            action = reflex.trigger_evasion(telemetry)
            bridge.actuate(action)
            continue

        damaged = repair.diagnose(telemetry)
        if damaged:
            repair.reroute_pathways(damaged, bridge)

        state = homeostasis.evaluate(telemetry)
        harvest_mode = energy.optimize_harvesting(telemetry, state)
        print(f"[HOMEOSTASIS] Mode: {state['mode']} | Energy: {harvest_mode}")

        action = edge_ai.infer(telemetry, state)
        bridge.actuate(action)
        time.sleep(0.5)

if __name__ == "__main__":
    run()
