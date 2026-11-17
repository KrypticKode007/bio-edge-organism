class HomeostaticController:
    def __init__(self, config: dict):
        self.min_v = config["homeostasis"]["min_voltage"]
        self.crit_temp = config["homeostasis"]["critical_temp_c"]
        self.mode = "NORMAL"

    def evaluate(self, telemetry: dict) -> dict:
        v_ok = telemetry["voltage"] >= self.min_v
        t_ok = telemetry["tissue_temp_c"] < self.crit_temp
        stability = 1.0 if (v_ok and t_ok) else 0.3
        if not v_ok or not t_ok:
            self.mode = "PRESERVATION_ALERT"
        return {"mode": self.mode, "stability_score": stability}
