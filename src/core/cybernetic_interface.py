import subprocess
import json
import random
import math

class BioSyntheticBridge:
    def __init__(self, use_real_sensors: bool = False):
        self.use_real_sensors = use_real_sensors
        self.atp_nutrient = 0.88
        self.voltage = 3.95
        self.active_nodes = {
            "motor_left": True,
            "motor_right": True,
            "chemo_sensor": True,
            "thermo_receptor": True
        }

    def _poll_termux_battery(self) -> tuple:
        try:
            raw = subprocess.check_output(["termux-battery-status"], timeout=0.8)
            data = json.loads(raw)
            v = data.get("voltage", 3950) / 1000.0
            t = float(data.get("temperature", 37.0))
            return v, t
        except Exception:
            return self.voltage, round(random.uniform(36.5, 38.8), 2)

    def _poll_termux_accel(self) -> float:
        try:
            raw = subprocess.check_output(["termux-sensor", "-s", "accelerometer", "-n", "1"], timeout=0.8)
            data = json.loads(raw)
            for key, val in data.items():
                if "values" in val and len(val["values"]) >= 3:
                    x, y, z = val["values"][:3]
                    g_force = abs(math.sqrt(x*x + y*y + z*z) - 9.81) / 9.81
                    return round(g_force, 3)
        except Exception:
            pass
        return round(random.uniform(0.01, 0.25), 3)

    def read_sensors(self) -> dict:
        # Natural metabolic ATP decay per cycle
        self.atp_nutrient = max(0.05, round(self.atp_nutrient - 0.008, 4))

        if self.use_real_sensors:
            v, temp = self._poll_termux_battery()
            shock = self._poll_termux_accel()
            self.voltage = v
        else:
            temp = round(random.uniform(36.5, 39.2), 2)
            shock = round(random.uniform(0.01, 0.30), 3)
            self.voltage = max(3.10, round(self.voltage - 0.003, 4))

        return {
            "atp_nutrient": self.atp_nutrient,
            "tissue_temp_c": temp,
            "shock_g": shock,
            "voltage": self.voltage,
            "light_lux": round(random.uniform(150.0, 900.0), 1),
            "nodes": self.active_nodes.copy(),
            "healthy_node_ratio": sum(self.active_nodes.values()) / len(self.active_nodes)
        }

    def apply_metabolic_update(self, harvest_delta_v: float, atp_gain: float, power_mw: float):
        self.voltage = min(4.25, max(3.0, round(self.voltage + harvest_delta_v - (power_mw * 0.0001), 4)))
        self.atp_nutrient = min(1.0, max(0.0, round(self.atp_nutrient + atp_gain, 4)))

    def actuate(self, action: dict, silent: bool = False):
        if not silent:
            print(f"[ACTUATOR] {action['cmd']} | Power: {action['power_mw']}mW | Spikes: {action.get('spikes', 0)}")
