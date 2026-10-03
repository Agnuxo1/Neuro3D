# EXP-005: total declared phase CPU egress contract

ID PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-EGRESS-HOST-001.
Base615b412c0355294f7d9d46559ee621793fdd2463; owner Codex capacity_audit/EXP005.
Opt-in precision-oblique-total-phase-pair64-egress-HOST-v1. Local JEV fallback blocked/no retry.

This is a NEW CPU word serialization/comparison contract, NOT GPU code, a GPU launch contract,
an optical field implementation, or replay of the total-phase producer.
Read sealed TOTALPHASE001 receipt SHAacc107cb584dba1d7845584ac1040569fa3a2dd4be7d2f9c39d702d2ce06b6c3
and its 131 pins, lossless final test capture and independent PRE. Old failures remain pinned.
Native producer RN64 operations and costs belong to its captured scope, NOT new computations.

64-byte little-endian envelope: four uint32 header fields followed by six IEEE64 raw words.
Header: CPU-only TAG0x43545031, word_count6, SOURCE_count2, marker1.
Payload fixed order S0.total.hi/lo, S1.total.hi/lo, (S0.total-S1.total).hi/lo.
SOURCE identity/branch/phase overlay/ORIGINAL/literal/gauge/caps stay bound through closed selector.
Selector keys: case, native_request_sha256, phase_request_sha256, original_scene_sha256,
literal_request_sha256, abi_tag, intent=HOST_CPU_TOTAL_PHASE_EGRESS_ONLY.
No subset, reordering, extra launch or cap override. Reject bool tag and stale/cross-case identity.
Header and supplied selector are NOT scene, device, fence or provenance authentication.
The seven-field selector is a separate sidecar; 64bytes is raw envelope size ONLY,
not a measurement of serialization/selector/full application costs.
V2 TAG0x4f444632/count4/32-byte propagation output cannot masquerade as this total-phase envelope.
No shader or V2 contract changed. A future GPU implementation requires its own new contract.

Public compare(model,request,raw_bytes,origin), export(model,request) load only sealed evidence.
No caller evidence override. Private _compare/_packet helpers are diagnostic fixtures only.
Only CPU_UNATTESTED_BYTES origin admitted. Export copies captured native words after the same gates;
it never recalculates phase, imports producers, uploads anything or authenticates its bytes.
All 35 parent STOP outcomes reject before raw decode/export, including the native cap-boundary STOP.
ALL_SOURCE finite raw exponent checks BEFORE arithmetic decoding/budget/equality; no float conversion.

Candidate SOURCE value = exact decoded hi+lo.
delta_j = abs(candidate_total_j - sealed_native_total_j).
SOURCE conservative_rad = sealed_native_SOURCE_conservative_rad + 8*delta_j.
Relative conservative_rad = 8*(sealed geometric_error + gamma radii + gamma encoding errors
+ ALL SOURCE addition errors + delta0+delta1
+ abs(candidate_relative - (candidate_SOURCE0-candidate_SOURCE1))).
The candidate relative arithmetic residual replaces, not adds to, the original measured relative
subtraction residual. Original interval endpoints and literal caps remain unchanged.
Direct_rad = 8*maxdistance(candidate, original declared total interval endpoints).
Require direct<=conservative for each row. ALL SOURCE caps then relative cap, all inclusive.
Then exact 64-byte native expected equality, not just approximate fit.
Only all gates admit three rows/raw_hex; any STOP emits none, keeps budget diagnostics if computed.
Tiny within-cap bit mutations fail native equality, proving cap fit is necessary but not enough.

Duplicate exact total-phase byte payloads across distinct selectors are a retained witness:
copied matching bytes under correctly rebound selector can match numerically but remain UNATTESTED.
Selector from a different case fails identity; byte match alone never proves provenance.
No artificial hash/signed fence or physical attestation added.

Tests cover sealed 46 inputs/35 parent STOP, exports, malformed selector/origin/model/header/extent,
24 signed infinity/NaN words across every payload slot, SOURCE subset/hi-only/reorder,
relative zero, within-cap wrong words, copied-equal witness and stale selector.
Independent verifier uses a separate integer bit-string IEEE decoder, midpoint/radius bounds,
restores evidence from parent capture, checks requests/mutations/exact words, atomic output,
all false flags, public API AST, full captures and pins. No native producer/compiler/FP replay.

All GPU/physical/native-promotion/scene-material/fence flags false; amplitude/field/power None.
Costs complete UNMEASURED_NOT_ZERO; 64bytes counts layout only, no speed/efficiency/RT equivalence.
CPU1thread/affinity1/child60s. GPU/Blender/newRN/geometry/compiler/reservations0.
Historical window closed/deadline immutable; RAMUNKNOWN_ACCESS_DENIED no retry/elevation/bypass.
Frozen conf1/v0/v4/0119/0315/nearestV2, runners/shaders/contracts/guards/bounds/caps/FAIL intact.
Version only own5; shared boards/checkpoint local SINstage. No SDK/DrJit/install/Kaggle/push/merge.
Request Claude existing TOTALphase backend/material/completeness/guard/ABI/float-controls/readback
artifacts by ID/path/SHA/bytes with same ORIGINAL/overlay/work/output/full costs, not filler loads.
