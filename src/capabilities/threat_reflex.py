class ReflexArc:
    def __init__(self, config: dict):
        self.max_temp = config["reflex"]["hazard_temp_threshold_c"]
        self.max_g = config["reflex"]["shock_g_threshold"]

    def detect_immediate_hazard(self, telemetry: dict) -> bool:
        return telemetry["tissue_temp_c"] >= self.max_temp or telemetry["shock_g"] >= self.max_g

    def trigger_evasion(self, telemetry: dict) -> dict:
        reason = "THERMAL_SPIKE" if telemetry["tissue_temp_c"] >= self.max_temp else "KINETIC_IMPACT"
        return {"cmd": f"REFLEX_EVASION_{reason}", "power_mw": 42.0, "spikes": 24}
