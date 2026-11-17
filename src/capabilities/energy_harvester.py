class EnergyManager:
    def optimize_harvesting(self, telemetry: dict, state: dict) -> tuple:
        delta_v = 0.0
        atp_gain = 0.0
        mode = "PASSIVE_TRICKLE"

        if telemetry["light_lux"] > 450.0:
            delta_v += 0.006
            mode = "SOLAR_ARRAY_ACTIVE"

        if telemetry["atp_nutrient"] < 0.80 or state["free_energy"] > 0.45:
            atp_gain += 0.015
            delta_v += 0.003
            mode = "HYBRID_MFC_AND_SOLAR" if delta_v > 0.006 else "MICROBIAL_FUEL_CELL_BOOST"

        return mode, delta_v, atp_gain
