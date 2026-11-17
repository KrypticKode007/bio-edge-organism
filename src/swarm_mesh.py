import random
import json
import yaml
from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

class SwarmAgent:
    def __init__(self, agent_id: str, config: dict):
        self.agent_id = agent_id
        self.bridge = BioSyntheticBridge(use_real_sensors=False)
        self.edge_ai = EdgeInferenceEngine(config)
        self.homeostasis = HomeostaticController(config)
        self.energy = EnergyManager()
        self.reflex = ReflexArc(config)
        self.repair = FaultRecoverySystem()
        self.alive = True

class DecentralizedSwarmMesh:
    """
    Peer-to-peer local swarm coordinator enabling hazard pheromone broadcasting
    and symbiotic ATP/charge sharing across edge-native organisms without cloud relays.
    """
    def __init__(self, num_agents: int = 5, seed: int = 42):
        random.seed(seed)
        with open("configs/organism_params.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        self.agents = [SwarmAgent(f"BioNode-{i+1:02d}", self.config) for i in range(num_agents)]
        self.hazard_broadcasts = 0
        self.symbiotic_transfers = 0

    def step_swarm(self) -> dict:
        local_hazard_alert = False

        # Pass 1: Local sensing & immediate reflex detection
        telemetries = {}
        for agent in self.agents:
            if not agent.alive:
                continue
            t = agent.bridge.read_sensors()
            if random.random() < 0.08:
                t["shock_g"] = round(random.uniform(2.5, 4.5), 2)
            if random.random() < 0.05:
                victim = random.choice(list(agent.bridge.active_nodes.keys()))
                agent.bridge.active_nodes[victim] = False
                t["nodes"] = agent.bridge.active_nodes.copy()
                t["healthy_node_ratio"] = sum(agent.bridge.active_nodes.values()) / len(agent.bridge.active_nodes)

            if agent.reflex.detect_immediate_hazard(t):
                local_hazard_alert = True
                self.hazard_broadcasts += 1
            telemetries[agent.agent_id] = t

        # Pass 2: Swarm P2P Reflex Propagation, Self-Repair & Homeostatic Inference
        for agent in self.agents:
            if not agent.alive:
                continue
            t = telemetries[agent.agent_id]

            if agent.reflex.detect_immediate_hazard(t) or local_hazard_alert:
                action = agent.reflex.trigger_evasion(t)
                agent.bridge.apply_metabolic_update(0.0, -0.004, action["power_mw"])
                continue

            damaged = agent.repair.diagnose(t)
            if damaged:
                agent.repair.reroute_pathways(damaged, agent.bridge, silent=True)
                t["nodes"] = agent.bridge.active_nodes.copy()
                t["healthy_node_ratio"] = 1.0

            state = agent.homeostasis.evaluate(t)
            _, dv, datp = agent.energy.optimize_harvesting(t, state)
            action = agent.edge_ai.infer(t, state)
            if action["cmd"] == "FORAGE_ORGANIC_MATTER":
                datp += 0.025
            agent.bridge.apply_metabolic_update(dv, datp, action["power_mw"])

        # Pass 3: Symbiotic Metabolic Sharing (Donors > 0.85 ATP share with stressed < 0.55 ATP)
        donors = [a for a in self.agents if a.alive and a.bridge.atp_nutrient > 0.85]
        recipients = [a for a in self.agents if a.alive and a.bridge.atp_nutrient < 0.55]
        for donor, rec in zip(donors, recipients):
            donor.bridge.atp_nutrient = round(donor.bridge.atp_nutrient - 0.08, 4)
            rec.bridge.atp_nutrient = round(rec.bridge.atp_nutrient + 0.08, 4)
            self.symbiotic_transfers += 1

        for agent in self.agents:
            if agent.bridge.voltage <= 3.15 or agent.bridge.atp_nutrient <= 0.05:
                agent.alive = False

        alive_count = sum(1 for a in self.agents if a.alive)
        return {
            "alive_agents": alive_count,
            "total_agents": len(self.agents),
            "hazard_broadcasts": self.hazard_broadcasts,
            "symbiotic_transfers": self.symbiotic_transfers
        }

if __name__ == "__main__":
    swarm = DecentralizedSwarmMesh(num_agents=6)
    for cycle in range(1, 501):
        stats = swarm.step_swarm()
    print("=== 500-CYCLE SWARM MESH BENCHMARK ===")
    print(json.dumps(stats, indent=2))
