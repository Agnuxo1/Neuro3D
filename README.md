# NEBULA EMERGENT — Unreal Engine 5 Neural Simulation

[![UE5](https://img.shields.io/badge/Unreal%20Engine-5.6-purple.svg)](https://www.unrealengine.com/)
[![CUDA](https://img.shields.io/badge/CUDA-13.0-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![GPU](https://img.shields.io/badge/GPU-RTX%203090%2024GB-76b900.svg)](https://www.nvidia.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

NEBULA EMERGENT is an Unreal Engine 5.6 project that implements emergent neural simulation with GPU-accelerated CUDA kernels integrated directly into the UE5 rendering pipeline. The system models complex neuronal behaviors including evolution, diversity maintenance, and photonic language expansion using real-time ray-traced shaders.

---

## Features

- **UE5.6 Integration**: Full Unreal Engine 5.6 project with C++ source and custom Blueprint nodes
- **CUDA 13.0 Neural Kernels**: `OptiXRayTracing.cu` — GPU ray tracing for neural field simulation
- **Custom HLSL Shaders**: `NeuronEvolution.usf` — neuron lifecycle and evolution shader
- **Emergent Behaviors**: `DiversityMaintenance.cpp`, `MetaOptimizer.cpp` — adaptive diversity and meta-optimization
- **Medical Translation**: `NEBULA_MEDICAL_TRANSLATOR.cpp` — neural pattern to medical imaging bridge
- **Physical Language Expansion**: `PhysicalLanguageExpansion.cpp` — physics-driven language model
- **Pattern Decoding**: `PatternDecoder.cpp` — neural pattern recognition system
- **Validity Oracle**: `ValidityOracle.cpp` — self-validation and quality assurance layer
- **ARC-AGI Solver**: `NEBULA_ARC_AGI_SOLVER-UE5/` — AGI reasoning integration within UE5

---

## Architecture

```
NEBULA EMERGENT (UE5 Project)
├── NEBULA.uproject              # UE5 project descriptor
├── Source/                      # C++ game module source
│   ├── NEBULA_EMERGENT_UE5.h    # Main module header
│   ├── DiversityMaintenance.cpp # Diversity control system
│   ├── MetaOptimizer.cpp        # Meta-learning optimizer
│   ├── NEBULA_MEDICAL_TRANSLATOR.cpp
│   ├── PhysicalLanguageExpansion.cpp
│   ├── PatternDecoder.cpp
│   └── ValidityOracle.cpp
├── Content/                     # UE5 assets (tracked separately)
│   └── NEBULA/                  # NEBULA-specific assets
├── Config/                      # UE5 project configuration
│   ├── DefaultEngine.ini
│   └── DefaultGame.ini
├── Plugins/                     # UE5 plugins
├── CUDA/
│   └── OptiXRayTracing.cu       # CUDA neural ray tracer
├── Shaders/
│   ├── NeuronEvolution.usf      # HLSL neuron evolution shader
│   └── NeuronEvolution_Fixed.usf
├── NEBULA_ARC_AGI_SOLVER-UE5/   # AGI solver integration
└── NEBULA.fbx                   # Neural geometry reference mesh
```

---

## Requirements

### Hardware
- **GPU**: NVIDIA RTX 3090 24 GB (CUDA 13.0 support)
- **CPU**: 8+ cores (AMD Ryzen 9 / Intel Core i9 recommended)
- **RAM**: 32 GB minimum (64 GB recommended)
- **Storage**: 100 GB SSD for UE5 project + 50 GB for compiled shaders

### Software
- **Unreal Engine**: 5.6 (via Epic Games Launcher)
- **CUDA Toolkit**: 13.0+
- **Visual Studio**: 2022 with C++ game development workload
- **Windows**: 10/11 (64-bit)

---

## Installation

```powershell
# 1. Clone the repository
git clone https://github.com/Agnuxo1/NEBULA-New-Unreal-Engine-Neural-Simulation.git
cd NEBULA-New-Unreal-Engine-Neural-Simulation

# 2. Install UE5.6 via Epic Games Launcher

# 3. Right-click NEBULA.uproject -> "Generate Visual Studio project files"

# 4. Build C++ source
# Open NEBULA.sln in Visual Studio 2022
# Build -> Development Editor -> Win64

# 5. Launch from UE5 Editor
# Open Epic Games Launcher -> Library -> Launch UE 5.6
# Open Project -> select NEBULA.uproject
```

### Alternative: PowerShell Scripts

```powershell
# Build automation
.\Scripts\Build_NEBULA.ps1

# Launch NEBULA in UE5
.\Scripts\Launch_NEBULA.ps1
```

---

## Key Components

### OptiXRayTracing.cu
CUDA kernel implementing real-time neural field ray tracing. Integrates with UE5's RHI (Rendering Hardware Interface) via the CUDA-Vulkan interop.

### NeuronEvolution.usf
HLSL compute shader running on the GPU's vertex/compute pipeline. Models neuron lifecycle, plasticity, and evolution over time.

### DiversityMaintenance.cpp
Implements genetic-diversity maintenance algorithms to prevent mode collapse in the neural simulation population.

### MetaOptimizer.cpp
Meta-learning system that dynamically adjusts hyperparameters based on simulation performance metrics.

---

## Note on Large Files

UE5 binary assets (`.uasset`, `.umap`, `.pak`), compiled binaries (`Binaries/`), build artifacts (`Build/`, `DerivedDataCache/`, `Intermediate/`) are excluded from this repository via `.gitignore` to keep the repo manageable. Only source code, shaders, configuration, and the project descriptor are tracked.

---

## Author

**Francisco Angulo de Lafuente**
- GitHub: [@Agnuxo1](https://github.com/Agnuxo1)

---

## License

MIT License - see [LICENSE](LICENSE) for details.
