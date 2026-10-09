# Installed Cycles OptiX component: explicit native4×4 extent

The original prospective trial and its null extent failure remain preserved. Actual driver logs establish partial RTX3090 OptiX rendering, but no complete network candidate result was accepted.

This new prospective version requests the native minimum4×4 render extent and selects a declared fixed pixel(2,2). All64 float32 EXR values must be finite. The whole orthographic camera footprint remains1e-7 BU, samples remain1, denoising/adaptive sampling remain disabled, and every object/primitive/projected-distance candidate still requires exact independent admission of the represented requested ray. Pixel offset, jitter, native camera transforms and mesh rounding remain approximate candidate effects; none is asserted to be the exact optical ray. Wrong candidates still produce null, with no CPU replacement. All geometric, optical-readout, full-coverage and resource thresholds are unchanged.

The existing installed OptiX backend is used without a new SDK. Private OptiX/CUDA cache locations are requested via environment variables; actual driver logs retain whether that request is honored. Cache presence is part of the runtime context and no universal or cold-start speed factor is assumed.

Publication on main and the scientific branch, byte verification and shared FIFO precede execution. The prior continuing GitHub authorization applies; external/IPFS registration remains pending. Full133-state/186-edge/17,060-path exact-verified graph, all150 CPU coherent outputs and identical-proof CPU BVH baseline are required for success. GPU coherent optical fields/training and RT kernel counters are separate.

[Frozen v2 profile](research/native_cycles_optix_profile_v2_2026-10-09.json), [v2 registration](research/native_cycles_optix_registration_v2_2026-10-09.json), [original protocol and retained null](NATIVE_CYCLES_OPTIX_COMPONENT_PROTOCOL_2026-10-09.md).
