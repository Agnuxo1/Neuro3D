# Native graphics frontier and coherent inference: prospective protocol

The validated graphical component is now used to construct the network from the five actual source rays. Each newly generated frontier is rendered against the evaluated 6,656 triangles through native Blender instancing, rasterization and depth. The GPU receives mesh vertices, origins, directions and the exactly proved previous zero-contact plane; it receives no precomputed reference graph, expected hit or optical matrix.

For every returned surface candidate, CPU rational predicates refine its closed triangle support and exclude all closer planar competitors independently. A wrong surface, primitive, miss or unsupported contact makes that branch incomplete and forbids fields; the CPU does not substitute a different hit. This is required by the already recorded near-plane FP32 ordering failure. Refined exact represented lengths, not approximate depth, feed coherent phase propagation.

Run three fresh exact CPU graph constructions followed by three fresh GPU-assisted constructions on the same owned Blender process and CPU affinity. Each GPU construction includes vertex packing, shader compilation, upload, frontier draw/synchronization/readback and exact verification. Retain all timings and first-run costs, with no timing acceptance threshold. Shared-host three repetitions are exploratory rather than statistical performance certification.

Positive acceptance requires 133 verified states, exact node/edge/root/topology agreement with fresh CPU and the previously captured native reference, 186 edges and 17,060 represented terminal paths. An independent full graph audit must pass. All 150 original encoded inputs must reproduce native complex fields and powers within 1e-11 and all 150 class predictions. Coherent arithmetic remains CPU and is measured separately; the GPU performs geometric selection.

Three software adversarial controls verify branch completeness from source queries, rejection of a wrong candidate without CPU replacement, and rejection of missing readback. They use an explicit mock and are not GPU evidence. Native execution uses the shared FIFO, hidden owned Blender GUI context and fixed RTX3090. The existing 300-second/4,000-MiB initial RAM/2,500-MiB floor/2,000-MiB RSS/128-MiB evidence/2,048-MiB GPU/80-C envelope is retained. Temporary files are directed to the owned D: directory.

[Profile](research/native_graphics_frontier_profile_2026-10-09.json) and [authorization](research/native_graphics_frontier_registration_2026-10-09.json) must be published and byte-verified before execution. External/IPFS identifiers remain absent. A complete rejected GPU frontier is a valid negative result with null fields; environment stops or invalid output have a null primary metric.

This tests a graphics-engine contribution to the own network. Hardware RT cores, OptiX, AMD, physical fidelity, GPU coherent arithmetic, training speed and energy are separate unproved claims.

## Native result: complete autonomous frontier, no full construction speedup

Frozen commit `f3339141370ba5d3894704f78de67611ced8071c`, profile SHA `19bd4e0c78952d1bd17526ceaa4256638318e5e612dd27d9af4d39c4a7472f3b`, 43 pinned sources byte-verified before FIFO execution. The actual RTX3090 native graphics frontier starts from the five source rays and completes 17 newly generated batches. All three constructions reproduce 133 states, 186 edges and 17,060 terminal paths. All 133 graphics surface and primitive candidates were exactly verified per construction, with zero rejected candidates or CPU replacement. Exact graph nodes match both fresh CPU and historical native scene references.

An independent graph/branch/field audit passes. All 150 encoded inputs retain their native predictions; maximum complex field difference is 5.117875266520903e-16 and maximum power difference 5.551115123125783e-16. Coherent arithmetic is CPU, using exact refined lengths rather than approximate graphical depth.

Full graph construction times: CPU 30.7660, 30.4246, 29.8658 seconds; graphical GPU plus exact verification 31.5350, 32.1434, 33.0084 seconds. There is no observed full construction speedup. Exact candidate support and nearest verification dominate at 30.5500, 31.1753 and 32.0184 seconds. GPU packing/compile/upload is included (0.0523, 0.0478, 0.0502 seconds). Full process cost is 201.1724 seconds and peak RSS 357.48 MiB; capture/admission 1.7349 seconds, independent full audit 6.0033 seconds, and 150 coherent inferences 0.4954 seconds. Three shared-host repetitions are exploratory, not a timing confidence interval.

[Evidence index](validation/native-graphics-frontier-2026-10-09/attempt01/evidence_index.json), [supervisor](validation/native-graphics-frontier-2026-10-09/attempt01/supervisor.json), [full result](validation/native-graphics-frontier-2026-10-09/attempt01/worker/result.json), [autonomous graph and GPU readbacks](validation/native-graphics-frontier-2026-10-09/attempt01/worker/graphics_graph_2.json).

![Full frontier costs](assets/native-graphics-frontier-2026-10-09.png)

The graph uses the existing rational state schema for exact CPU phase and verification, with explicit selection_backend=NATIVE_GPU_RASTER_DEPTH_WITH_EXACT_CPU_VERIFICATION and selection_is_gpu=true. This does not claim all calculations execute on GPU, hardware RT cores, AMD, physical fidelity or a new neural expressivity class.

## Prospective v2: independent exact candidate refinement

The previous source and data remain frozen. The [v2 profile](research/native_graphics_frontier_profile_v2_2026-10-09.json) keeps all three native repetitions, GPU geometry, full costs, precision and topology gates unchanged. Candidate refinement computes the exact selected-plane intersection, checks every closed triangle of the GPU-selected object using independent exact Gram predicates, and proves a positive local interior through the already established independent square-perimeter coverage witness. It then runs the unchanged exhaustive independent nearest-object exclusion across all surfaces. No approximate depth enters optical phase, no wrong candidate is replaced, and every coincident primitive must still match.

Four meaningful software controls pass, including rejection of a point on a closed triangle boundary with no positive interior witness. The new refinement is intended to reduce verification cost; no speed improvement is assumed before execution. [Authorization](research/native_graphics_frontier_registration_v2_2026-10-09.json) and all source bytes must be published and verified first.
