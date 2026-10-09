# Native Blender graphics geometry: frozen component trial

The user requests that the GPU perform actual 3D geometry work. This prospective profile loads the evaluated 6,656 triangles into a vertex buffer, transforms one view per geometric query with instancing, and uses rasterization and a depth buffer to select the first surface. Native GPU framebuffer readback is required. No optical weight matrix or expected closest-hit name is supplied to the shader.

The trained `.blend` is opened in Blender 4.5.14 LTS with scripts disabled, captured through the standalone add-on, and checked against the frozen native scene. The 133 rays come from the independently audited graph: this is a component audit, preceding an autonomous GPU frontier. Batches of 1, 133 and 4,096 queries each run five times, including the first run; setup, draw, synchronization and readback are included and recorded.

All core queries must match the exact closest object and distance within 0.00005 Blender units. That candidate tolerance does not relax the existing coherent field tolerance of 1e-11: exact refinement is needed before optical propagation. Controls test nearest ordering, an exactly proved previous-surface zero contact, and a miss. A separate pair of planes spaced by 2^-25 units documents finite graphics precision; it cannot establish universal correctness.

Complete disagreement is retained as a valid negative result. Environment, shader compilation, resource stop or incomplete execution yields a null metric. Limits: 300 seconds, 4,000 MiB initial free RAM, 2,500 MiB floor, 2,000 MiB owned RSS, 128 MiB evidence, 2,048 MiB total GPU memory and 80 C. The shared GPU FIFO is mandatory. Only the owned hidden Blender process may be stopped.

[Profile](research/native_graphics_geometry_profile_2026-10-09.json) and [GitHub authorization record](research/native_graphics_geometry_registration_2026-10-09.json) must be published and byte-verified before execution. External registration/IPFS remains pending without identifiers.

This uses Blender's graphics pipeline. Hardware ray tracing, OptiX, AMD, coherent GPU fields, training, physical fidelity and speed superiority are not inferred from successful rasterization.

## Attempt 01 and prospective correction

Frozen commit `6c6cb355e0354f93bb078a42f68999d4d66d4b9d` opened Blender 4.5.14 LTS with an actual NVIDIA OpenGL RTX3090 context. Admission stopped before drawing in 8.738 seconds (301.17 MiB RSS): in-memory rational coordinate tuples were compared directly against decoded JSON lists. Its metric remains null and its [raw evidence](validation/native-graphics-geometry-2026-10-09/attempt01/evidence_index.json) is preserved.

The [v2 profile](research/native_graphics_geometry_profile_v2_2026-10-09.json) compares canonical rational wires, preserving exact coordinates, object semantics and every previous numerical gate. It also saves the capture before checking identity so further mismatch is inspectable. [Authorization](research/native_graphics_geometry_registration_v2_2026-10-09.json) must again be published and verified before execution. No positive graphics result is inferred from this correction.
