import csv
import json
import os

def generate_homeostasis_svg(csv_path: str, out_svg: str):
    cycles, fe_vals, atp_vals, volt_vals = [], [], [], []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = int(row["cycle"])
            if c % 5 == 0:  # Downsample every 5th cycle for crisp vector rendering
                cycles.append(c)
                fe_vals.append(float(row["free_energy"]))
                atp_vals.append(float(row["atp"]))
                volt_vals.append((float(row["voltage"]) - 3.0) / 1.3)

    w, h, pad = 820, 380, 60
    plot_w, plot_h = w - 2 * pad, h - 2 * pad

    def to_pts(vals):
        pts = []
        for i, v in enumerate(vals):
            x = pad + (i / max(1, len(vals) - 1)) * plot_w
            y = pad + (1.0 - min(1.0, max(0.0, v))) * plot_h
            pts.append(f"{x:.1f},{y:.1f}")
        return " ".join(pts)

    svg = f'''<svg xmlns="http://w3.org" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{w/2}" y="28" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#111">
    BioEdge-SNN-Apex: 1,000-Cycle Homeostatic Trajectory (ARM64 Edge Node)
  </text>
  <line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="#333" stroke-width="1.5"/>
  <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h-pad}" stroke="#333" stroke-width="1.5"/>
  <polyline fill="none" stroke="#2563eb" stroke-width="2" points="{to_pts(atp_vals)}"/>
  <polyline fill="none" stroke="#16a34a" stroke-width="2" points="{to_pts(volt_vals)}"/>
  <polyline fill="none" stroke="#dc2626" stroke-width="1.8" points="{to_pts(fe_vals)}"/>
  <rect x="{w-250}" y="{pad+10}" width="180" height="75" fill="#f8fafc" stroke="#cbd5e1" rx="4"/>
  <line x1="{w-240}" y1="{pad+28}" x2="{w-215}" y2="{pad+28}" stroke="#2563eb" stroke-width="2.5"/>
  <text x="{w-208}" y="{pad+32}" font-family="Arial" font-size="12" fill="#1e293b">Intracellular ATP</text>
  <line x1="{w-240}" y1="{pad+48}" x2="{w-215}" y2="{pad+48}" stroke="#16a34a" stroke-width="2.5"/>
  <text x="{w-208}" y="{pad+52}" font-family="Arial" font-size="12" fill="#1e293b">Normalized Voltage</text>
  <line x1="{w-240}" y1="{pad+68}" x2="{w-215}" y2="{pad+68}" stroke="#dc2626" stroke-width="2.5"/>
  <text x="{w-208}" y="{pad+72}" font-family="Arial" font-size="12" fill="#1e293b">Free Energy (F)</text>
  <text x="{w/2}" y="{h-18}" font-family="Arial" font-size="13" text-anchor="middle" fill="#334155">Control Cycles (N = 1,000)</text>
  <text x="18" y="{h/2}" font-family="Arial" font-size="13" text-anchor="middle" transform="rotate(-90 18,{h/2})" fill="#334155">Normalized Physiological State</text>
</svg>'''
    with open(out_svg, "w") as f:
        f.write(svg)

def generate_ablation_svg(json_path: str, out_svg: str):
    with open(json_path, "r") as f:
        data = json.load(f)

    w, h, pad = 760, 360, 65
    bar_w = 100
    gap = 55
    colors = ["#0f172a", "#dc2626", "#ea580c", "#d97706"]

    bars = ""
    for i, item in enumerate(data):
        pct = item["survival_rate_pct"]
        bar_h = (pct / 100.0) * (h - 2 * pad)
        x = pad + 35 + i * (bar_w + gap)
        y = (h - pad) - bar_h
        label = item["variant"].replace("_", " ")
        bars += f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bar_h:.1f}" fill="{colors[i % len(colors)]}" rx="4"/>\n'
        bars += f'<text x="{x + bar_w/2}" y="{y - 8:.1f}" font-family="Arial" font-size="13" font-weight="bold" text-anchor="middle" fill="#111">{pct:.1f}%</text>\n'
        bars += f'<text x="{x + bar_w/2}" y="{h - pad + 20}" font-family="Arial" font-size="11" text-anchor="middle" fill="#334155">{label}</text>\n'

    svg = f'''<svg xmlns="http://w3.org" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{w/2}" y="28" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#111">
    Ablation Study: 1,000-Cycle Severe Trauma Survival Rate
  </text>
  <line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="#333" stroke-width="1.5"/>
  <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h-pad}" stroke="#333" stroke-width="1.5"/>
  {bars}
  <text x="20" y="{h/2}" font-family="Arial" font-size="13" text-anchor="middle" transform="rotate(-90 20,{h/2})" fill="#334155">Survival Rate (%)</text>
</svg>'''
    with open(out_svg, "w") as f:
        f.write(svg)

if __name__ == "__main__":
    os.makedirs("docs/figures", exist_ok=True)
    generate_homeostasis_svg("data/logs/telemetry_benchmark.csv", "docs/figures/fig1_homeostasis_trajectory.svg")
    generate_ablation_svg("data/logs/ablation_results.json", "docs/figures/fig2_ablation_survival.svg")
    print("Generated publication SVG figures in docs/figures/")
