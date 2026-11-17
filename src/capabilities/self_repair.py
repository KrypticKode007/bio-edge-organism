class FaultRecoverySystem:
    def __init__(self):
        self.total_repairs = 0

    def diagnose(self, telemetry: dict) -> list:
        return [node for node, healthy in telemetry["nodes"].items() if not healthy]

    def reroute_pathways(self, damaged_nodes: list, bridge, silent: bool = False) -> int:
        repaired_count = 0
        for node in damaged_nodes:
            if not silent:
                print(f"[SELF-REPAIR] Bypassing lesion at '{node}' via redundant bio-polymer bus.")
            bridge.active_nodes[node] = True
            self.total_repairs += 1
            repaired_count += 1
        return repaired_count
