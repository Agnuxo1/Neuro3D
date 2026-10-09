# Advanced graphics technologies: evidence and actual applicability

The present hardware is one RTX3090 (Ampere), driver581.29, Blender4.5.14. The actual native pipeline already uses instanced captured triangles, depth selection, coherent FP64 fragment transport, exact integer readback, source-driven wavefront traversal and hybrid geometric differentiation. Whole-device utilization samples are not kernel occupancy, energy or comparative efficiency measurements.

| Technology | Verified applicability and current evidence |
|---|---|
| Native OpenGL4.6 raster/depth and FP64 fragments | Actually executed: complete geometry,150 coherent decisions, four phase/interference controls and16 parameter derivative probes. Exact topology/affine jets/coherent merges/power-loss chain are CPU. |
| Cycles OptiX on RTX | Actually executed in Blender4.5.14 on RTX3090:133 native captured-triangle queries, complete exact-verified graph and150 matching CPU coherent decisions. One equivalent candidate+proof pair:OptiX41.008s/CPU BVH10.331s, so no speed gain here. Full63.168s; RT kernel counters remain unmeasured. |
| Shader Execution Reordering (SER) | NVIDIA documents effective hardware thread reordering on Ada. Prior architectures may accept API calls as no-ops. RTX3090 must not be credited with Ada SER gains. |
| Vulkan in Blender4.5 | An officially supported alternative graphics backend, with limitations. Our exact Windows OpenGL integer reader and shader contracts do not automatically transfer to Vulkan; a separate implementation and equivalence audit would be required. |
| AMD HIP / hardware ray tracing | Blender documents supported AMD GPUs and hardware RT options. There is no AMD GPU on this machine, so actual AMD validation remains open. |
| HIPRT source | GPUOpen repository source license inspected as MIT. Downloaded binaries have a separate acceptance route. No source integration/build or execution is claimed. |
| Persistent buffers, wavefront grouping and instancing | Applicable ways to reduce setup/transfer/divergence. They must preserve source/phase/state identity, every nonzero branch and coherent merging, and be tested under equivalent precision and total cost. |

OptiX headers/tools were not installed: the upstream repository's license information includes DesignWorks terms in addition to individual file notices. Reading the license does not establish a new agreement or integration. The completed component experiment uses the already installed Cycles backend. Cycles emission pixels are used only to encode geometric candidates; they do not replace coherent neural fields with rendered intensities.

Primary sources checked on9October2026:

- [Blender4.5 GPU rendering and OptiX/HIP requirements](https://docs.blender.org/manual/en/4.5/render/cycles/gpu_rendering.html).
- [Blender4.5 EEVEE Vulkan release notes](https://developer.blender.org/docs/release_notes/4.5/eevee/).
- [NVIDIA OptiX product documentation](https://developer.nvidia.com/rtx/ray-tracing/optix), [upstream API repository and licensing](https://github.com/NVIDIA/optix-dev).
- [NVIDIA SER white paper](https://developer.nvidia.com/sites/default/files/akamai/gameworks/ser-whitepaper.pdf), [OptiX application examples and requirements](https://github.com/NVIDIA/OptiX_Apps).
- [AMD GPUOpen HIPRT documentation](https://gpuopen.com/hiprt/), [upstream source and license](https://github.com/GPUOpen-LibrariesAndSDKs/HIPRT).
- [Galgoczi2026 optical-photon SER preprint](https://arxiv.org/abs/2608.21396): its abstract reports a separate large detector Monte Carlo benchmark, including transfers/initialization and output equivalence. That study is prior optical GPU acceleration, not evidence for our coherent classifier, our hardware, our energy use or our novelty. We do not import its performance figures as our own.

[Actual coherent graphics evidence](NATIVE_GRAPHICS_COHERENT_FIELD_PROTOCOL_2026-10-09.md), [independent observed-output certificate](NATIVE_GRAPHICS_FIELD_CERTIFICATE_PROTOCOL_2026-10-09.md), [graphics derivative audit](NATIVE_GRAPHICS_GEOMETRY_GRADIENT_PROTOCOL_2026-10-09.md), [actual installed OptiX component and retained null](NATIVE_CYCLES_OPTIX_COMPONENT_V2_PROTOCOL_2026-10-09.md).
