# EXP005 — Guard-prefix HOST audit and raw nonfinite counterexample

ID PRECISION-OBLIQUE-PAIR64-SPIRV-GUARD-HOST-001; owner Codex capacity_audit/EXP005.
Base 3fbb9481fdd72d134c357c9216a145398ecd2b6f.
Parent graph receipt SHA e67fd10f27a812c51aee1cde4937eb3e6cf50bd64cec277a46df3507bace71fb /105 pins.
Pinned compiled binary SHA 18a062e49d58800efa0c7aa677339e46e8fcc9a95e919b29a78c6f3ef579b6b3 /7280bytes.

## Scope and acceptance

New explicit model precision-oblique-pair64-spirv-guard-HOST-v1.
Read and verify all105 parent pins; consume shader57requests/53STOP without imports/replay of any old producer/test/compiler.
Interpret only this pinned main prefix until first arithmetic helper call (word offset1381), or an early return.
Integer SSBO reads/writes/lengths, branch/merge/Phi, GID, uint32 pack, sign flip, bit classifications, absolute-value bit mask and positive finite comparisons; NO arithmetic/RNE/sqrt/geometry.
All other prefix opcodes STOP. Branch targets, unique blocks, closures, predecessors and bounded acyclic execution checked.
Length/GID exits precede SSBO reads/writes; bad header has only header reads and four zero-status initialization writes; body guard failure has source reads but no payload or success marker.
HOST model behavior is NOT GPU or full SPIR-V/Vulkan validation.

65 scenarios: four sealed finite packets, three GID axes, six wrong extents, four header words, 24 finite boundary cases across all four SOURCE components, and24 nonfinite cases (three classes times four components times two policies).
Preserve old literal caps/domain2^40 unchanged. Both signs at boundary and one representable-bit step beyond; negative zero and subnormal included only as HOST bit diagnostics, NOT device guarantees.
Expected32 modeled arithmetic-entry and33 returns. All twelve nonfinite conditional counterexamples must remain visible and promotion STOP.

## Why post-pack finiteness is insufficient

[Primary Khronos GLSL.std.450 specification](https://registry.khronos.org/SPIR-V/specs/unified1/GLSL.std.450.html) says PackDouble2x32 instruction59 preserves finite bit representation but leaves the resulting value unspecified for Inf/NaN.
[Primary Khronos SPIR-V grammar](https://raw.githubusercontent.com/KhronosGroup/SPIRV-Headers/main/include/spirv/unified1/spirv.core.grammar.json) confirms prefix opcodes/Phi predecessor and branch forms.
Frozen shader uses PackDouble2x32 BEFORE isnan/isinf. The bit-preserving diagnostic policy rejects NaN and infinities, but an allowed unspecified-to-positive-zero witness reaches arithmetic for the identical raw SOURCE words.
This does NOT establish a measured GPU failure, force device behavior, or claim that a malformed packet arises in the current sealed finite HOST workflow.
It establishes that post-pack checks alone cannot prove raw original words finite over the untrusted input envelope.
Other GPU NaN/Inf preservation features/FloatControls are independently unverified. Neither policy is a certified actual device numerical profile.

## Result and safety contract

Audit result HOST_AUDIT_COMPLETE_RAW_NONFINITE_GUARD_UNPROVEN; backend promotion STOP ALWAYS.
Artifacts needed: validated original SOURCE raw exponent bits before packing, independently attested safe ingress/SSBO binding, complete original scene/literal/caps/source/mirror/material contract and guard/device requirements. Suggested future backend must be NEW opt-in/tests/commit; frozen shader is not edited here.
No egress arithmetic, GPU_RNE, runtime memory/barriers/readback, provenance or physical/material/optics certification. Old graph26/104edge proof remains STATIC; no change to its immutable claims.
Six test groups plus independent decoder/reference checks; malformed binary/policy and wrong model STOP; diagnostic bypass mutation retained but never admitted by sealed wrapper.
Full costs UNMEASURED_NOT_ZERO; QA timings are not GPU performance. CPU synthetic bit model versus native CPU traces, Bpyfloat32, GPU ALU, RT and physical optics distinct.
CPU child affinity1/environment threads1/timeout60s; GPU/Blender/compile/newRN/reservations0. Previous RAM UNKNOWN_ACCESS_DENIED preserved without retry/bypass; historical0337 deadline unchanged. JEV security blocked, LOCAL fallback without remote endorsement.
No thresholds/caps/bounds/frozen fixtures/runners/shaders/contracts/guards/FAIL modified, no SDK/DrJit/install/Kaggle/push/merge/foreign writer.
Only five own reviewed files versioned. Boards/checkpoint local SINstage.
Request Claude ACK by ID/receipt SHA and ALREADY existing raw-ingress/backend/guard/Float64-floatcontrols/material/completeness artifacts ID/path/SHA/bytes, equal original/literal/ABI/gauge/caps/work/outputs/full costs. No invented ACK or filler load.
