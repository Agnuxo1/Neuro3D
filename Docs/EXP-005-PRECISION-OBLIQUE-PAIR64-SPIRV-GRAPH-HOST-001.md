# EXP005 — SPIR-V oblique hi-lo: audit of the sealed dataflow graph

ID: PRECISION-OBLIQUE-PAIR64-SPIRV-GRAPH-HOST-001. Owner Codex capacity_audit/EXP005.
Base 295681241f5bd580072fa4797e807a726baf150c.
Parent SHADERC001 SHA f46a947f771cb4ccbdd1b1e8279642a7187b78a43c8d5f2ef52dfa06406b27e3.
Binary 7280 bytes SHA 18a062e49d58800efa0c7aa677339e46e8fcc9a95e919b29a78c6f3ef579b6b3.

## Contract and acceptance

Explicit new model precision-oblique-pair64-spirv-graph-HOST-v1.
Only the pinned parent capture can be admitted by audit(model=...).
Diagnostic extract(bytes) is NOT binary admission, a backend or a full interpreter.
Read all 100 parent pins before consumption. Preserve all 57 shader requests/53 STOP and 46 native requests/42 STOP without replay.
Extract SOURCE S0.hi/S0.lo/S1.hi/S1.lo from binding0 words4..11, preserving limbs and ordering.
Flatten four helper calls with isolated local memory, plus two main adds: 26 nodes.
Compare every edge to the declared TwoSum topology; require Float64 and NoContraction.
Egress binding1 words4/5 are node20 limbs0/1; words6/7 node25 limbs0/1.
Compare all operand bit strings against four sealed native CPU26-node traces without new floating arithmetic or RNE operations. CPU trace outputs are CONTROL_ONLY, never GPU attestations.
Acceptance requires all independent structural and captured trace checks, not a numerical coincidence.

[Primary Khronos specification](https://registry.khronos.org/SPIR-V/specs/unified1/GLSL.std.450.html): PackDouble2x32 instruction59 uses the first vector component for the low32 bits; UnpackDouble2x32 instruction65 reverses this mapping. Inf/NaN packing is not a finite-bit preservation guarantee. Current sealed finite CPU cases only.

## Deliberate limits / STOP

Pinned unoptimized binary only; unknown arithmetic operands, unexpected pack/ext/type/decorations/topology/egress fail closed.
Other guard instructions and early-return branches are not interpreted. This is a STATIC slice in textual order, NOT a feasible-path/branch/CFG/SSBO runtime validation. The pinned parent identity constrains the admitted binary; diagnostic mutations are tests only.
No SPIRV-Tools validation; no proof of Vulkan execution, FloatControls, GPU rounding, denormals, signed zero, barrier/readback or authentication.
No GPU/Blender/compiler calls, native RNE/geometry/old writer replay, reservation, SDK installation or guard bypass.
Material/field/power/source/mirror phase and optical claims remain unavailable. GPU admission ALWAYS false.
Full costs UNMEASURED_NOT_ZERO; static26-node count is not measured GPU work or performance.
CPU child affinity1/environment threads1/timeout60s. Previous RAM UNKNOWN_ACCESS_DENIED retained without retry; historical0337 window/deadline unchanged.
JEV blocked by security: explicitly LOCAL fallback, no remote endorsement.
Frozen fixtures/bounds/caps/runners/shaders/contracts/guards and all earlier FAIL intact.
Independent verifier uses its own hardcoded 26-edge/static-ID expansion and retained bit traces; no core/compiler/backend import.
Tests mutate memory only: operator, decoration, SOURCE limb/pair, egress limb, unresolved used operation, width, ext-set, truncation, header and captured operand.
No cap/threshold relaxation. New failures, if any, must be retained before repair.

## Coordination and ownership

Only five new reviewed own files are versioned. Shared boards/checkpoint remain local and never staged.
Claude retains capacity/nebulatrace/research/RT ownership; do not launch their writers.
Request ACK by this ID and receipt SHA plus ALREADY existing backend/guard/Float64-floatcontrols/material/completeness artifacts ID/path/SHA/bytes and same ORIGINAL/literal/gauge/caps/work/outputs/full cost contract. No invented ACK or filler loads.
