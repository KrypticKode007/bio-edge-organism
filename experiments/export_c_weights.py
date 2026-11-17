import os
import sys
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from core.edge_runtime import EdgeInferenceEngine

def export_header():
    with open("configs/organism_params.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    snn = EdgeInferenceEngine(cfg)
    rows = []
    for r in snn.weights:
        rows.append("    { " + ", ".join(f"{val:.4f}f" for val in r) + " }")
    c_array = "static const float EXPORTED_SNN_WEIGHTS[3][4] = {\n" + ",\n".join(rows) + "\n};\n"
    out_file = "firmware/esp32_stm32_port/exported_weights.h"
    with open(out_file, "w") as f:
        f.write("#ifndef EXPORTED_WEIGHTS_H\n#define EXPORTED_WEIGHTS_H\n\n" + c_array + "\n#endif\n")
    print(f"Exported C99 synaptic weight header to: {out_file}")

if __name__ == "__main__":
    export_header()
