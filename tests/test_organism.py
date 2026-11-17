import os
import sys
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def load_cfg():
    with open("configs/organism_params.yaml", "r") as f:
        return yaml.safe_load(f)

def test_pillar1_bio_synthetic_bridge():
    bridge = BioSyntheticBridge(use_real_sensors=False)
    telemetry = bridge.read_sensors()
    assert "atp_nutrient" in telemetry
    assert "voltage" in telemetry
    assert telemetry["healthy_node_ratio"] == 1.0

def test_pillar2_snn_hebbian_plasticity():
    cfg = load_cfg()
    snn = EdgeInferenceEngine(cfg)
    w_before = snn.weights.copy()
    telemetry = {"atp_nutrient": 0.25, "tissue_temp_c": 37.0, "healthy_node_ratio": 1.0}
    state = {"free_energy": 0.2}
    decision = snn.infer(telemetry, state)
    assert decision["cmd"] in ["FORAGE_ORGANIC_MATTER", "EXPLORE_PERIMETER", "ENTER_LOW_POWER_STASIS"]
    assert not (snn.weights == w_before).all(), "Synaptic weights should adapt via Hebbian plasticity"

def test_pillar3_homeostatic_free_energy_escalation():
    cfg = load_cfg()
    hc = HomeostaticController(cfg)
    stressed_telemetry = {"voltage": 3.25, "tissue_temp_c": 43.0, "atp_nutrient": 0.3, "healthy_node_ratio": 0.5}
    res = hc.evaluate(stressed_telemetry)
    assert res["mode"] == "CRITICAL_SURVIVAL_OVERRIDE"
    assert res["free_energy"] > 0.65

def test_pillar4_multimodal_energy_harvester():
    em = EnergyManager()
    telemetry = {"light_lux": 700.0, "atp_nutrient": 0.50}
    state = {"free_energy": 0.60}
    mode, dv, datp = em.optimize_harvesting(telemetry, state)
    assert mode == "HYBRID_MFC_AND_SOLAR"
    assert dv > 0 and datp > 0

def test_pillar5_reflex_arc_override():
    cfg = load_cfg()
    reflex = ReflexArc(cfg)
    telemetry = {"tissue_temp_c": 46.5, "shock_g": 0.2}
    assert reflex.detect_immediate_hazard(telemetry) is True
    action = reflex.trigger_evasion(telemetry)
    assert action["cmd"] == "REFLEX_EVASION_THERMAL_SPIKE"

def test_pillar6_topological_self_repair():
    bridge = BioSyntheticBridge(use_real_sensors=False)
    repair = FaultRecoverySystem()
    bridge.active_nodes["motor_right"] = False
    bridge.active_nodes["chemo_sensor"] = False
    telemetry = {"nodes": bridge.active_nodes.copy()}
    damaged = repair.diagnose(telemetry)
    assert set(damaged) == {"motor_right", "chemo_sensor"}
    repaired = repair.reroute_pathways(damaged, bridge, silent=True)
    assert repaired == 2
    assert all(bridge.active_nodes.values())
