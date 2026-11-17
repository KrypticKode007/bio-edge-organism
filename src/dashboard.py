import time
import argparse
import yaml
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

from core.cybernetic_interface import BioSyntheticBridge
from core.edge_runtime import EdgeInferenceEngine
from core.homeostasis import HomeostaticController
from capabilities.energy_harvester import EnergyManager
from capabilities.threat_reflex import ReflexArc
from capabilities.self_repair import FaultRecoverySystem

def build_view(cycle: int, telemetry: dict, state: dict, action: dict, harvest: str, latency_us: float, repairs: int) -> Panel:
    table = Table(expand=True, border_style="cyan")
    table.add_column("Subsystem / Pillar", style="bold white")
    table.add_column("Live Telemetry / State", style="green")
    table.add_column("Threshold / Target", style="dim")

    fe_color = "green" if state["free_energy"] < 0.4 else ("yellow" if state["free_energy"] < 0.65 else "bold red")
    nodes_status = " ".join([f"[green]{k}:OK[/]" if v else f"[red]{k}:ERR[/]" for k, v in telemetry["nodes"].items()])

    table.add_row("1. Bio-Synthetic Bridge", f"Temp: {telemetry['tissue_temp_c']}°C | Shock: {telemetry['shock_g']}G", "< 45.0°C | < 2.2G")
    table.add_row("2. LIF Spiking Runtime", f"Cmd: [bold cyan]{action['cmd']}[/] (Spikes: {action.get('spikes', 0)})", f"Latency: {latency_us:.1f} µs")
    table.add_row("3. Free-Energy Homeostasis", f"[{fe_color}]{state['mode']} (F = {state['free_energy']:.4f})[/]", "Target F < 0.25")
    table.add_row("4. Energy Harvester", f"{harvest} | Bus: {telemetry['voltage']}V | ATP: {telemetry['atp_nutrient']}", "V > 3.35V | ATP ~ 0.85")
    table.add_row("5. Threat Reflex Arc", "[bold red]ACTIVE OVERRIDE[/]" if "REFLEX" in action["cmd"] else "[green]ARMED (Sub-ms Interrupt)[/]", "Hardware Bypass")
    table.add_row("6. Topological Self-Repair", f"{nodes_status} (Total Repairs: {repairs})", "100% Bus Continuity")

    return Panel(table, title=f"[bold magenta]BioEdge-SNN-Apex Live Telemetry — Cycle {cycle}[/]", subtitle="Press Ctrl+C to exit")

def run_dashboard(use_real_sensors: bool = False, cycles: int = 40):
    with open("configs/organism_params.yaml", "r") as f:
        config = yaml.safe_load(f)

    bridge = BioSyntheticBridge(use_real_sensors=use_real_sensors)
    edge_ai = EdgeInferenceEngine(config)
    homeostasis = HomeostaticController(config)
    energy = EnergyManager()
    reflex = ReflexArc(config)
    repair = FaultRecoverySystem()

    with Live(refresh_per_second=8) as live:
        for cycle in range(1, cycles + 1):
            t0 = time.perf_counter()
            telemetry = bridge.read_sensors()

            if not use_real_sensors and cycle % 12 == 0:
                telemetry["shock_g"] = 2.85
                bridge.active_nodes["motor_left"] = False

            if reflex.detect_immediate_hazard(telemetry):
                action = reflex.trigger_evasion(telemetry)
                bridge.apply_metabolic_update(0.0, -0.005, action["power_mw"])
                state = {"mode": "REFLEX_OVERRIDE", "free_energy": 0.92}
                harvest = "SUSPENDED"
            else:
                damaged = repair.diagnose(telemetry)
                if damaged:
                    repair.reroute_pathways(damaged, bridge, silent=True)
                    telemetry["nodes"] = bridge.active_nodes.copy()
                    telemetry["healthy_node_ratio"] = 1.0

                state = homeostasis.evaluate(telemetry)
                harvest, dv, datp = energy.optimize_harvesting(telemetry, state)
                action = edge_ai.infer(telemetry, state)
                if action["cmd"] == "FORAGE_ORGANIC_MATTER":
                    datp += 0.025
                bridge.apply_metabolic_update(dv, datp, action["power_mw"])

            latency_us = (time.perf_counter() - t0) * 1e6
            live.update(build_view(cycle, telemetry, state, action, harvest, latency_us, repair.total_repairs))
            time.sleep(0.25)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Stream live Android hardware sensors")
    parser.add_argument("--cycles", type=int, default=40, help="Number of cycles to visualize")
    args = parser.parse_args()
    run_dashboard(use_real_sensors=args.live, cycles=args.cycles)
