import subprocess
import threading
import time
import json
import random
import math

class BioSyntheticBridge:
    def __init__(self, use_real_sensors: bool = False):
        self.use_real_sensors = use_real_sensors
        self.atp_nutrient = 0.88
        self.voltage = 3.95
        self.live_temp = 37.5
        self.live_shock = 0.05
        self.active_nodes = {
            "motor_left": True,
            "motor_right": True,
            "chemo_sensor": True,
            "thermo_receptor": True
        }
        if self.use_real_sensors:
            t = threading.Thread(target=self._hardware_sensor_loop, daemon=True)
            t.start()

    def _hardware_sensor_loop(self):
        while True:
            try:
                raw_bat = subprocess.check_output(["termux-battery-status"], timeout=1.5)
                bat = json.loads(raw_bat)
                self.voltage = bat.get("voltage", 3950) / 1000.0
                self.live_temp = float(bat.get("temperature", 37.5))
            except Exception:
                pass
            try:
                raw_acc = subprocess.check_output(["termux-sensor", "-s", "accelerometer", "-n", "1"], timeout=1.5)
                acc = json.loads(raw_acc)
                for _, val in acc.items():
                    if "values" in val and len(val["values"]) >= 3:
                        x, y, z = val["values"][:3]
                        self.live_shock = round(abs(math.sqrt(x*x + y*y + z*z) - 9.81) / 9.81, 3)
            except Exception:
                pass
            time.sleep(0.1)

    def read_sensors(self) -> dict:
        self.atp_nutrient = max(0.05, round(self.atp_nutrient - 0.008, 4))
        if self.use_real_sensors:
            temp = self.live_temp
            shock = self.live_shock
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
