# EXP-005 — V2 egress HOST, opt-in

ID: PRECISION-OBLIQUE-PAIR64-V2-EGRESS-HOST-001. Owner: Codex, capacity_audit/EXP005.
Base: 834bb001d90dbf4ab08c11fb4752abb7b0496898. Local fallback only: JEV security-blocked, no retry or remote endorsement.

## Contract

Model precision-oblique-pair64-v2-egress-HOST-v1 accepts only CPU_UNATTESTED_BYTES,
four sealed V2 cases and an exact closed selector (case, packet digest, original scene,
literal request, shader digest, HOST-only intent). Other origins cannot gain GPU admission
by asserting a fence/guard/attestation boolean. This module does not certify any such evidence.
No runner/shader/guard, old contracts, caps, bounds or fixtures are modified.

Output is exactly 32 bytes: little-endian words TAG=0x4f444632, count=4, SOURCE count=2,
marker=1, followed by relative hi/lo. Marker is NOT PASS. Decode original finite IEEE64 bits
using integers/rationals; no floating computation, RN, compiler, geometry or producer replay.
SOURCE ingress remains 48 bytes, total SSBO 80 bytes, two sources, one relative result.
CPU expected relative is NOT uploaded as input to the shader.

For each SOURCE with sealed interval [L,U] and decoded hi+lo v:
B_SOURCE=8*max(abs(v-L),abs(v-U)) <= unchanged literal cap.
Relative interval [L0-U1,U0-L1] must equal the sealed interval. For output w:
A=abs(w-(v0-v1)); R=(relative_U-relative_L)/2;
S=sum(abs(v_j-midpoint_j));
B_conservative=8*(R+S+A); B_direct=8*max(abs(w-relative_L),abs(w-relative_U)).
Require B_direct<=B_conservative<=unchanged relative cap, then compare exact native CPU
hi/lo and sealed expected bytes. The factor 8 is the retained conservative radians-per-cycle
envelope, not a newly relaxed cap, phase computation or optical-material model.

Any missing SOURCE, mismatched original/literal, corrupted source bits, nonfinite output,
wrong extent/header, failed cap, missing/extra selector, unsupported origin or wrong model STOPs.
All acceptance is HOST_UNATTESTED_BYTES_MATCH with promotion=STOP and all GPU/authentication,
material/field/native-promotion flags false. Completeness refers only to sealed 2-SOURCE/1-relative
records, not native scene branch coverage.

## Provenance limitation and costs

Three cases (oblique, direction-scaled, shared-reference1000) have identical relative output
bytes. A copy can pass under a correct claimed selector; it still proves NO actual scene origin,
fence/barrier/readback, GPU Float64/float-controls or device execution. Wrong selector STOPs,
but selectors and hashes are identity checks, not authentication.

Parent receipts and ancestral pins are checked read-only. No replay of existing suites or compiler.
New tests retain exact inputs, fault descriptors, results, rational bounds and equal-payload witness.
Independent verifier consumes captured tests, uses a separate decoder, rebuilds all budgets and
checks failures/prohibited flags. CPU bounded one thread/affinity1/child60s.

Known counts/SSBO bytes are representation bookkeeping, not speed, efficiency or full-work costs.
Scene build, upload, dispatch, fence/readback and geometry/material/field costs remain
UNMEASURED_NOT_ZERO. No equivalent RT comparison, winner, physical optics or scale promotion.
Future GPU requires NEW exclusive job agreed with Claude, valid fail-closed guard, verifiable
deadline, telemetry and unchanged safety limits. Historical deadline remains closed; RAM previously
UNKNOWN_ACCESS_DENIED retained without retry/elevation/bypass.

Shared boards/checkpoint remain local unstaged. Version only these five reviewed own files;
no SDK/DrJit installation, foreign writers, Kaggle, push, merge or publication.
