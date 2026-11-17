import numpy as np

class EdgeInferenceEngine:
    def __init__(self):
        # Lightweight 3x3 synaptic weight matrix for local edge decisions
        self.weights = np.array([
            [0.8, -0.5, 0.2],  # Forage / Harvest priority
            [-0.4, 0.9, 0.1],  # Explore priority
            [0.1, 0.2, -0.9]   # Dormancy / Conserve priority
        ])

    def infer(self, telemetry: dict, homeostatic_state: dict) -> dict:
        inputs = np.array([
            1.0 - telemetry["atp_nutrient"],
            homeostatic_state["stability_score"],
            telemetry["tissue_temp_c"] / 50.0
        ])
        scores = np.dot(self.weights, inputs)
        commands = ["FORAGE_ORGANIC_MATTER", "EXPLORE_PERIMETER", "ENTER_LOW_POWER_STASIS"]
        choice = commands[int(np.argmax(scores))]
        return {"cmd": choice, "power_mw": 15.0 if choice != "ENTER_LOW_POWER_STASIS" else 2.5}
