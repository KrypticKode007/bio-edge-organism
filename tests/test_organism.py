import os
import sys
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def load_cfg():
    with open("configs/organism_params.yaml", "r") as f:
        return yaml.safe_load(f)

def test_reflex_arc_overrides_on_shock():
    cfg = load_cfg()
    reflex = ReflexArc(cfg)
    telemetry = {"tissue_temp_c": 37.0, "shock_g": 3.5}
    assert reflex.detect_immediate_hazard(telemetry) is True
    action = reflex.trigger_evasion(telemetry)
    assert "REFLEX_EVASION" in action["cmd"]

def test_topological_self_repair():
    bridge = BioSyntheticBridge(use_real_sensors=False)
    repair = FaultRecoverySystem()
    bridge.active_nodes["motor_right"] = False
    telemetry = {"nodes": bridge.active_nodes.copy()}
    damaged = repair.diagnose(telemetry)
    assert damaged == ["motor_right"]
    repair.reroute_pathways(damaged, bridge, silent=True)
    assert bridge.active_nodes["motor_right"] is True

def test_snn_edge_inference_determinism():
    cfg = load_cfg()
    snn = EdgeInferenceEngine(cfg)
    telemetry = {"atp_nutrient": 0.2, "tissue_temp_c": 37.0, "healthy_node_ratio": 1.0}
    state = {"free_energy": 0.8}
    decision = snn.infer(telemetry, state)
    assert decision["cmd"] in ["FORAGE_ORGANIC_MATTER", "EXPLORE_PERIMETER", "ENTER_LOW_POWER_STASIS"]
    assert decision["power_mw"] > 0

def test_homeostatic_free_energy_escalation():
    cfg = load_cfg()
    hc = HomeostaticController(cfg)
    stressed_telemetry = {"voltage": 3.25, "tissue_temp_c": 43.0, "atp_nutrient": 0.3, "healthy_node_ratio": 0.5}
    res = hc.evaluate(stressed_telemetry)
    assert res["mode"] == "CRITICAL_SURVIVAL_OVERRIDE"
    assert res["free_energy"] > 0.65
