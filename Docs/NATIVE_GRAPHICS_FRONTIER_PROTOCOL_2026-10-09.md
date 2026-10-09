# Native graphics frontier and coherent inference: prospective protocol

The validated graphical component is now used to construct the network from the five actual source rays. Each newly generated frontier is rendered against the evaluated 6,656 triangles through native Blender instancing, rasterization and depth. The GPU receives mesh vertices, origins, directions and the exactly proved previous zero-contact plane; it receives no precomputed reference graph, expected hit or optical matrix.

For every returned surface candidate, CPU rational predicates refine its closed triangle support and exclude all closer planar competitors independently. A wrong surface, primitive, miss or unsupported contact makes that branch incomplete and forbids fields; the CPU does not substitute a different hit. This is required by the already recorded near-plane FP32 ordering failure. Refined exact represented lengths, not approximate depth, feed coherent phase propagation.

Run three fresh exact CPU graph constructions followed by three fresh GPU-assisted constructions on the same owned Blender process and CPU affinity. Each GPU construction includes vertex packing, shader compilation, upload, frontier draw/synchronization/readback and exact verification. Retain all timings and first-run costs, with no timing acceptance threshold. Shared-host three repetitions are exploratory rather than statistical performance certification.

Positive acceptance requires 133 verified states, exact node/edge/root/topology agreement with fresh CPU and the previously captured native reference, 186 edges and 17,060 represented terminal paths. An independent full graph audit must pass. All 150 original encoded inputs must reproduce native complex fields and powers within 1e-11 and all 150 class predictions. Coherent arithmetic remains CPU and is measured separately; the GPU performs geometric selection.

Three software adversarial controls verify branch completeness from source queries, rejection of a wrong candidate without CPU replacement, and rejection of missing readback. They use an explicit mock and are not GPU evidence. Native execution uses the shared FIFO, hidden owned Blender GUI context and fixed RTX3090. The existing 300-second/4,000-MiB initial RAM/2,500-MiB floor/2,000-MiB RSS/128-MiB evidence/2,048-MiB GPU/80-C envelope is retained. Temporary files are directed to the owned D: directory.

[Profile](research/native_graphics_frontier_profile_2026-10-09.json) and [authorization](research/native_graphics_frontier_registration_2026-10-09.json) must be published and byte-verified before execution. External/IPFS identifiers remain absent. A complete rejected GPU frontier is a valid negative result with null fields; environment stops or invalid output have a null primary metric.

This tests a graphics-engine contribution to the own network. Hardware RT cores, OptiX, AMD, physical fidelity, GPU coherent arithmetic, training speed and energy are separate unproved claims.
