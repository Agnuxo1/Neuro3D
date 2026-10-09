# Installed Cycles OptiX component: explicit native4×4 extent

The original prospective trial and its null extent failure remain preserved. Actual driver logs establish partial RTX3090 OptiX rendering, but no complete network candidate result was accepted.

This new prospective version requests the native minimum4×4 render extent and selects a declared fixed pixel(2,2). All64 float32 EXR values must be finite. The whole orthographic camera footprint remains1e-7 BU, samples remain1, denoising/adaptive sampling remain disabled, and every object/primitive/projected-distance candidate still requires exact independent admission of the represented requested ray. Pixel offset, jitter, native camera transforms and mesh rounding remain approximate candidate effects; none is asserted to be the exact optical ray. Wrong candidates still produce null, with no CPU replacement. All geometric, optical-readout, full-coverage and resource thresholds are unchanged.

The existing installed OptiX backend is used without a new SDK. Private OptiX/CUDA cache locations are requested via environment variables; actual driver logs retain whether that request is honored. Cache presence is part of the runtime context and no universal or cold-start speed factor is assumed.

Publication on main and the scientific branch, byte verification and shared FIFO precede execution. The prior continuing GitHub authorization applies; external/IPFS registration remains pending. Full133-state/186-edge/17,060-path exact-verified graph, all150 CPU coherent outputs and identical-proof CPU BVH baseline are required for success. GPU coherent optical fields/training and RT kernel counters are separate.

[Frozen v2 profile](research/native_cycles_optix_profile_v2_2026-10-09.json), [v2 registration](research/native_cycles_optix_registration_v2_2026-10-09.json), [original protocol and retained null](NATIVE_CYCLES_OPTIX_COMPONENT_PROTOCOL_2026-10-09.md).

## Actual complete installed OptiX component: accepted

Frozen c0917e20/profile befe0aa4/95 source pins was verified on GitHub before shared-FIFO execution. Blender4.5.14 selected RTX3090 OPTIX exclusively. All133 native renders produced geometric candidates admitted by the independent exact represented-ray verifier:133states,186edges,17,060represented terminal paths. CPU coherent propagation then gave all150 identical decisions, field difference5.118e-16 and power difference5.552e-16. No approximate candidate was silently replaced by a CPU result.

Complete supervised cost63.167784s, peak owned RSS704.27MiB. OptiX candidates plus the identical exact proof took41.008216s; CPU BVH plus that proof10.330787s. This single equivalent pair favors CPU for this small scene; it does not establish an acceleration benefit. Samples of the whole GPU peaked at71% utilization and2631MiB allocated memory; these are not kernel occupancy or energy measurements. Actual rendering is established by selected device and native logs; RT kernel counters were not measured. The coherent fields in this component were computed in CPU, separately from our verified coherent fragment shaders and prepared graphics learning trial. The original extent failure remains preserved.

[Raw evidence and hashes](validation/native-cycles-optix-2026-10-09/attempt02/evidence_index.json), [native result and equivalent costs](validation/native-cycles-optix-2026-10-09/attempt02/worker/result.json), [complete supervisor receipt](validation/native-cycles-optix-2026-10-09/attempt02/supervisor.json).
