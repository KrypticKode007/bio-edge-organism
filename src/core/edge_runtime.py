import numpy as np

class EdgeInferenceEngine:
    """
    Pure-NumPy Leaky Integrate-and-Fire (LIF) Spiking Neural Network
    with reward-modulated Hebbian homeostasis for local edge autonomy.
    """
    def __init__(self, config: dict):
        snn_cfg = config.get("snn", {})
        self.tau = snn_cfg.get("membrane_tau", 0.85)
        self.threshold = snn_cfg.get("firing_threshold", 1.0)
        self.lr = snn_cfg.get("learning_rate", 0.02)

        # 4 sensory inputs -> 3 motor/behavioral populations
        # Inputs: [ATP_deficit, Free_Energy_Stress, Thermal_Load, Node_Integrity]
        self.weights = np.array([
            [0.95,  0.40, -0.20,  0.10],  # Pop 0: FORAGE_ORGANIC_MATTER
            [-0.30, -0.60, -0.20,  0.85], # Pop 1: EXPLORE_PERIMETER
            [0.20,  0.75,  0.90, -0.50]   # Pop 2: ENTER_LOW_POWER_STASIS
        ], dtype=np.float64)
        self.membrane_potential = np.zeros(3, dtype=np.float64)
        self.commands = ["FORAGE_ORGANIC_MATTER", "EXPLORE_PERIMETER", "ENTER_LOW_POWER_STASIS"]

    def infer(self, telemetry: dict, homeostatic_state: dict) -> dict:
        sensory_vector = np.array([
            1.0 - telemetry["atp_nutrient"],
            homeostatic_state["free_energy"],
            telemetry["tissue_temp_c"] / 50.0,
            telemetry["healthy_node_ratio"]
        ], dtype=np.float64)

        spike_counts = np.zeros(3, dtype=int)
        # Run 8 sub-millisecond neuromorphic integration steps per control cycle
        for _ in range(8):
            synaptic_current = np.dot(self.weights, sensory_vector) * 0.35
            self.membrane_potential = (self.tau * self.membrane_potential) + synaptic_current
            fired = self.membrane_potential >= self.threshold
            spike_counts += fired.astype(int)
            self.membrane_potential[fired] = 0.0  # Reset after spike

        winner = int(np.argmax(spike_counts)) if np.max(spike_counts) > 0 else int(np.argmax(self.membrane_potential))
        choice = self.commands[winner]

        # Online Homeostatic Plasticity: reinforce pathways when free energy is low
        stability_reward = 1.0 - homeostatic_state["free_energy"]
        self.weights[winner] += self.lr * stability_reward * (sensory_vector - 0.5)
        self.weights = np.clip(self.weights, -1.5, 1.5)

        power_mw = 2.0 if choice == "ENTER_LOW_POWER_STASIS" else (12.5 + float(np.sum(spike_counts)) * 0.4)
        return {
            "cmd": choice,
            "power_mw": round(power_mw, 2),
            "spikes": int(np.sum(spike_counts)),
            "winning_pop": winner
        }
