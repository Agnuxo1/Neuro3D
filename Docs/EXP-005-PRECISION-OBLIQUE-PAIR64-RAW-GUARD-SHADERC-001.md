# EXP005 — NEW opt-in V2 raw exponent guard candidate

ID PRECISION-OBLIQUE-PAIR64-RAW-GUARD-SHADERC-001. Owner Codex capacity_audit/EXP005.
Base 743ecc1c7914a2d19f484d0fdb313d884911ec2f.
Parent GUARD001 SHA b4eacc9e5b7a3746669b7e834ec0888d32587025bb9e86e51e5d5cf8e8e141ed /110 pins.

## Explicit new contract

New model precision-oblique-pair64-raw-guard-shaderc-HOST-v1.
New shader oblique_pair64_raw_guard_v2.comp; different source SHA and ABI TAG0x4f444632 (oldTAG0x4f444631 rejected).
Model selector requires exact case/parent packet digest/ORIGINAL scene/literal/representation/newshaderSHA/CPU intent, closed keys; no cap/launch override.
Only four retained finite packets; input48/output32=80SSBO bytes, CPU expected32 CONTROL_ONLY outside GPU input.
Explicit tag migration changes only first32-bit word of input/expected header; original SOURCE32bytes, relative output16bytes, geometry/literal/gauge/lambda/source caps and relative budgets unchanged.
All old failed cases/caps/guards/bounds and frozen shader/contracts remain intact. Not a retroactive PASS.

## Implementation

After GID/extents/header guards and zero-status initialization, reject if any ORIGINAL SOURCE component high word (indices5/7/9/11) AND0x7ff00000 equals0x7ff00000, BEFORE any PackDouble2x32.
Both SOURCEs and both hi/lo components checked; sign does not affect exponent rejection.
HOST raw validator separately checks exact V2 header, four finite components and unchanged absolute2^40 domain.
Keep original post-pack checks and all26 arithmetic nodes/four TwoSum/two adds/NoContraction64; no arithmetic substitution or direct CPUrelative input.
[Primary Khronos](https://registry.khronos.org/SPIR-V/specs/unified1/GLSL.std.450.html): nonfinite PackDouble2x32 result is unspecified; the new integer guard avoids packing that envelope in the modeled prefix.
[Primary opcode grammar](https://raw.githubusercontent.com/KhronosGroup/SPIRV-Headers/main/include/spirv/unified1/spirv.core.grammar.json): OpBitwiseAnd199 and OpIEqual170 are unsigned integer/boolean dataflow here.

## Verification / acceptance

Compile ONLY NEW shader, positive plus syntaxnegative; existing shaderc DLL SHA d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b /4478464bytes, versionUNKNOWN.
CPU target Vulkan1.0/4194304/compute2/main/optimization0; no new SDK/DrJit/install.
Self-contained own reviewed copies of static graph/prefix decoder, no importing/executing frozen producers/tests/compiler. No old compile replay.
New model uses retained65 scenarios, explicitly migrates correct tags only, leaves erroneous tag controls erroneous.
20 modeled arithmetic entries/45 early returns; ALL24 NaN/Inf scenario-policy variants must exit BEFORE packing, including all12 preserved old conditional witnesses.
Four finite packets still match104 native captured operand-edges and relative hi/lo bits; no new RNE/arithmetic/geometry.
HOST input validation, malformed selector/model/source-before-DLL checks, syntaxnegative and zero-mask mutation STOP.
Independent verifier reads compiled binary/raw integer-mask-source chains/CFG/graph/word packets/caps/counterexamples using no core/backend/compiler imports.
Failures must be retained before repair; do not change any threshold/cap to meet acceptance.

## What remains STOP

New guard is CPU compiled/static/prefix-modeled evidence ONLY. No GPU executed; GPU_launch_allowed/GPU_guard_certified/native_promotion/physical_field always false.
No proof of actual device Float64/features/RTE64/denorm/signedzero, SPIRV-Tools validation, runtime SSBO authentication/completeness, guard/deadline/telemetry/barrier/readback/material/field/amplitude/source-mirror-phase or physical optics.
Negative zero/subnormal are HOST diagnostics, not GPU-profile certification.
Full costs UNMEASURED_NOT_ZERO. QA/compile-call timings/static26nodes/80bytes do not prove speed, efficiency, winner, equalRT16Mvs1M work or full scene inference.
GPU future only new exclusive job agreedClaude, new verifiable deadline, failclosed guard, live valid telemetry and user limits, contract/tests/commit BEFORE GPU. Historical0337 closed deadline immutable.
CPU affinity1/envthreads1/child60s; RAM priorUNKNOWN_ACCESS_DENIED no retry/elevation/bypass. JEV securityblocked LOCAL fallback, no remote endorsement/no retry.
Claude owns capacity/nebulatrace/research/RT. No foreign writer/file changes. Boards/checkpoint local SINstage; only six own reviewed files versioned; no Kaggle/push/merge/publication.
Request Claude ACK by ID/receipt SHA plus ALREADY existing ingressSSBO/backend/guard/Float64-floatcontrols/material/completeness ID/path/SHA/bytes and equal ORIGINAL/literal/ABI/gauge/caps/work/outputs/full costs. No invented ACK or filler loads.
