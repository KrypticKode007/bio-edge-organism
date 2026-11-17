class EnergyManager:
    def optimize_harvesting(self, telemetry: dict, state: dict) -> str:
        if telemetry["light_lux"] > 400:
            return "SOLAR_TRICKLE_ACTIVE"
        elif telemetry["atp_nutrient"] < 0.75:
            return "MICROBIAL_FUEL_CELL_BOOST"
        return "BALANCED_HARVEST"
