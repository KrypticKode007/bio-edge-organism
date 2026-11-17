# BioEdge-SNN-Apex: Self-Preserving, Edge-Native Cybernetic Organism

## Abstract
**BioEdge-SNN-Apex** is an open-source, edge-native research framework modeling an autonomous bio-hybrid cybernetic organism. Eliminating cloud latency and external telemetry dependencies, the organism achieves continuous self-preservation through a 6-pillar closed-loop architecture:
1. **Bio-Synthetic Sensorimotor Bridge** (`src/core/cybernetic_interface.py`)
2. **Neuromorphic Leaky Integrate-and-Fire (LIF) Edge Runtime** (`src/core/edge_runtime.py`)
3. **Variational Free-Energy Homeostatic Controller** (`src/core/homeostasis.py`)
4. **Multi-Modal Microbial Fuel Cell & Solar Energy Harvester** (`src/capabilities/energy_harvester.py`)
5. **Sub-Millisecond Hardware-Interrupt Threat Reflex Arc** (`src/capabilities/threat_reflex.py`)
6. **Topological Neural Pathway Self-Repair** (`src/capabilities/self_repair.py`)

## Mathematical Formulation
### 1. Physiological Free-Energy Proxy ($F$)
The homeostatic controller quantifies internal divergence from viable biological and electrical setpoints:
$$F = \min\left(1.0,\; \sqrt{w_v \epsilon_v^2 + w_{atp} \epsilon_{atp}^2 + w_T \epsilon_T^2 + w_n \epsilon_n^2}\right)$$
where $\epsilon_v$, $\epsilon_{atp}$, $\epsilon_T$, and $\epsilon_n$ represent normalized deficits in bus voltage, intracellular ATP concentration, thermal margin, and intact actuator nodes.

### 2. Edge Neuromorphic Dynamics & Hebbian Homeostasis
Motor populations evolve according to discrete Leaky Integrate-and-Fire membrane dynamics:
$$V_m[t+1] = \tau V_m[t] + \mathbf{W}\mathbf{x}[t]$$
Synaptic weights $\mathbf{W}$ undergo online reward-modulated Hebbian updates scaled by homeostatic stability $(1 - F)$:
$$\Delta \mathbf{W}_{i} = \eta (1 - F)(\mathbf{x}[t] - 0.5)$$

## Quickstart (Termux / Linux ARM64)
```bash
# Run unit verification suite
pytest -v

# Run 12-cycle interactive simulation
python src/main.py --cycles 12

# Run live on Android hardware sensors (requires Termux:API app)
python src/main.py --live --cycles 20

# Execute 1,000-cycle hostile environment benchmark & export CSV/JSON
python experiments/run_benchmark.py
```

---

## Automated Verification & Figures
![Verification CI](https://github.com)

* **Figure 1 (`docs/figures/fig1_homeostasis_trajectory.svg`):** 1,000-cycle ATP, voltage, and Free-Energy trajectories on ARM64 hardware.
* **Figure 2 (`docs/figures/fig2_ablation_survival.svg`):** Comparative survival rates across ablated architectural variants.
