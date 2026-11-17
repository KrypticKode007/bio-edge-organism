import math

class HomeostaticController:
    """
    Computes physiological divergence (Variational Free Energy proxy)
    from optimal survival setpoints to drive self-preservation.
    """
    def __init__(self, config: dict):
        h_cfg = config["homeostasis"]
        self.min_v = h_cfg["min_voltage"]
        self.opt_v = h_cfg.get("optimal_voltage", 4.0)
        self.opt_atp = h_cfg["optimal_atp_level"]
        self.crit_temp = h_cfg["critical_temp_c"]
        self.fe_threshold = h_cfg.get("free_energy_threshold", 0.65)
        self.mode = "HOMEOSTATIC_EQUILIBRIUM"

    def evaluate(self, telemetry: dict) -> dict:
        v_err = max(0.0, (self.opt_v - telemetry["voltage"]) / (self.opt_v - self.min_v))
        atp_err = max(0.0, (self.opt_atp - telemetry["atp_nutrient"]) / self.opt_atp)
        temp_err = max(0.0, (telemetry["tissue_temp_c"] - 37.0) / (self.crit_temp - 37.0))
        node_err = 1.0 - telemetry["healthy_node_ratio"]

        # Weighted physiological surprise / Free Energy score [0.0 to 1.0+]
        free_energy = round(min(1.0, math.sqrt((0.35 * v_err**2) + (0.30 * atp_err**2) + (0.20 * temp_err**2) + (0.15 * node_err**2))), 4)

        if telemetry["voltage"] < self.min_v or telemetry["tissue_temp_c"] >= self.crit_temp:
            self.mode = "CRITICAL_SURVIVAL_OVERRIDE"
        elif free_energy >= self.fe_threshold:
            self.mode = "PRESERVATION_ALERT"
        else:
            self.mode = "HOMEOSTATIC_EQUILIBRIUM"

        return {
            "mode": self.mode,
            "free_energy": free_energy,
            "stability_score": round(1.0 - free_energy, 4)
        }
