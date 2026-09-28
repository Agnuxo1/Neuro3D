# Santo Grial Photonic Neural Core

This plugin is the first clean reconstruction layer for the NEBULA / Santo Grial idea.

It deliberately separates simulation from presentation:

- C++ owns deterministic graph construction and the Unreal render-thread dispatch.
- Render Dependency Graph schedules three compute passes.
- HLSL transports optical-like state: intensity, phase, frequency and RGB color.
- Optional `FRHIGPUBufferReadback` snapshots report a reproducible GPU checksum, active neurons and total energy.
- Niagara/Lumen are not part of the numerical core; they belong to the next visualization gate.

The model is a digital GPU simulation. It does not claim physical photonic computation, hardware optical neurons, or a full electromagnetic solver.

Run the CPU oracle from the plugin directory:

```powershell
python Tests/photonic_reference.py
```

The Unreal project must be compiled with Unreal Engine 5.6 before the plugin can be exercised in-editor.
