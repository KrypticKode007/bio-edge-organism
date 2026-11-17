import subprocess
import json
import random

class BioSyntheticBridge:
    def __init__(self, use_real_sensors: bool = False):
        self.use_real_sensors = use_real_sensors
        self.bio_tissue_integrity = 1.0  # 1.0 = 100% healthy organic tissue
        self.active_nodes = {"motor_left": True, "motor_right": True, "chemo_sensor": True}

    def read_sensors(self) -> dict:
        # Simulated biological telemetry
        telemetry = {
            "atp_nutrient": round(random.uniform(0.6, 0.95), 3),
            "tissue_temp_c": round(random.uniform(36.5, 39.0), 2),
            "shock_g": round(random.uniform(0.0, 0.4), 2),
            "light_lux": random.uniform(100, 800),
            "nodes": self.active_nodes.copy()
        }
        # Optional: Pull real battery/sensor data from Android via termux-api
        if self.use_real_sensors:
            try:
                bat = json.loads(subprocess.check_output(["termux-battery-status"], timeout=1))
                telemetry["voltage"] = bat.get("voltage", 4000) / 1000.0
                telemetry["tissue_temp_c"] = bat.get("temperature", 37.0)
            except Exception:
                telemetry["voltage"] = 3.85
        else:
            telemetry["voltage"] = round(random.uniform(3.5, 4.2), 2)
        return telemetry

    def actuate(self, action: dict):
        print(f"[ACTUATOR] Executing: {action['cmd']} | Power Draw: {action['power_mw']}mW")
