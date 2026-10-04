# EXP005: exact parameter ordering from raw32 triangles (CPU opt-in)
ID PRECISION-EXACT-PARAMETER-ORDER-CPU-001. Owner Codex capacity_audit/EXP005.
Base 3b67435b5ba36c811821d1c530db1d4a4eaa08fd.

## Contract and explicit limits
New pure standard-library CPU helper; NOT a GPU/native backend, original N3DG32V1 reader,
authentication credential, scene dispatcher, ray tracer or phase/transport implementation.
Input is exactly 24 uint32: origin3, direction3, triangleA9, triangleB9.
Only finite normal rawbinary32 or positive zero; absolute coordinate <=1000000.
Reject bool/float, wrong size/type, nonfinite, subnormal, signed zero and zero direction.
Domain belongs only to this opt-in audit and does not silently change frozen fixture bounds.
Units: coordinates BU, t in the supplied unnormalized ray parameterization. Do not call t
physical distance without a direction norm. No normalization, epsilon, offset, ignoreID,
snap, threshold relaxation or modification of frozen helpers/shaders/contracts.

Compute edge/cross/dot numerators and determinant with exact Fraction arithmetic.
Normalize negative determinant by flipping all numerators. Form exact rational t/u/v;
compare t through integer cross-products, never through rounded float64 parameters.
For interior t>0,u>0,v>0,u+v<1, exact p=o+t*d must equal a+u*(b-a)+v*(c-a)
and have exactly zero plane residual. This is an exact mathematical CPU point, NOT a
native launch origin, hi-lo wire representation or uncertainty/authentication bound.
A unique candidate is local to the TWO supplied triangles. No global nearest-hit claim.

Zero determinant (degenerate OR parallel), contact t=0 and boundary remain STOP.
Any unresolved triangle prevents selecting another candidate. Both misses return local MISS.
Equal exact parameters remain genuine tie STOP without ID tie-breaking or chosen point.
Malformed input raises ValueError and yields no admissible result.
All native/nearest/visibility/phase/GPU-launch/exclusion flags stay false; phase error and
native-origin-box bounds are null; transport_hilo_implemented=false; full costs UNKNOWN_NOT_ZERO.
Returned data are independent between invocations; no import-time I/O or external writers.

## Changed method and focused regression coverage
Read pinned predecessor receipt SHA406ce6757503aa41cfc0aa6f42b4f550a401ef675294df460100f5f67501dfac
120733bytes, 431 old pins plus parent receipt=432 context pins. Never execute old producer.
Use its four FABRICATED raw bundles, not six admitted inputs/S0/S1. New exact method applied
to 4cases x 3cyclic axis rotations x 2face orders x 2windings =48 variants.
36 unique local CPU candidates preserve tA=1-delta, point coordinate delta for
delta2^-60,2^-54,2^-53. Twelve genuine zero-gap variants retain STOP.
15 malformed-input rejections; 5 geometric negatives: degeneracy/parallel/contact/boundary
STOP and miss; mutation isolation check with two separate invocations.
110 new exact triangle evaluations in the focused suite (96variants+10negatives+4mutation);
old binary64 432-node graph not rerun. No original fixture or query replay.
Suite rc0, 3.489520800008904s QA, stdoutSHAea07474e938d2440fd82f9e3095c2dfd110664529bd9049d659ce55377957676,
132939bytes. Timings are QA, NOT performance/comparable costs or a speed advantage.

## Failure preservation and next boundary
Prior binary64 synthetic false-tie/lost-point gate remains
FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION.
Earlier 72scalarErrors +16priorRows are separate metrics; 12contactSTOP remain.
PASS here only validates this exact CPU two-triangle mathematical contract.
No native promotion, phase budget, launch exclusion or hardware error claim.
Next: robust opt-in scene/coverage binding and residual/hi-lo contract, not implemented here.
Claude ACK this ID + receipt SHA and supply only existing backend/guard/native origin boxes,
SAMEINPUT scenequery S0/S1 ALLcoverage, IEEE graph, material/gauge/scale/lambda/reference bounds,
equal-work outputs and full costs, or state missing. No invented ACK or filler loads.

CPU one core/thread per child <=60s, -B, no installations. GPU/Bpy/RT/compiler/foreign writers0.
JEV security BLOCK: local fallback with no retry/bypass or remote endorsement.
GPU future only after contract/tests/commit and exclusive fresh Claude reservation,
gpuq/process/RAM/VRAM/temp telemetry, fail-closed guard and NEW job deadline;
free RAM>=4GiB after >=1024bytes/cell plus margins/temporaries, totalVRAM<=18GiB,
temp<=80C, pilot<=120s/other<=600s; noMLP32768/near-limit after0x9F.
Closed historical overnight deadline stays untouched. No push/merge/Kaggle/SDK/DrJit.
Only own4 reviewed files versioned; sharedboards/checkpoint local SINstage.
Skills testing+cognition: explicit CPU contract, focused negatives, pinned reuse, independent oracle.
Initial shell wrong cwd267, stdout warning/JSON parsing error and absolute-add failure and Windows206 command-length failure are preserved;
recoveries use explicit D cwd, select JSON output line, and the same relative native apply_patch.
No mathematical failures or criteria changed to pass.

## Independent oracle
Cramer determinant 3x3 / raw32 struct decode, without importing/executing the helper,
old producer or focused tests: 53 stored records, 106 independent triangle references,
1272 decodes, 432 verified context pins. Unique choices via sorted exact rational t,
not helper cross-product selection. Compares t/u/v/point, STOP/miss/tie, raw bundle SHA and
all false admission flags. rc0/0.22805330000119284s QA,
stdoutSHAb25a0f0fb4f40997f07dcca1b8b7d4ee66a38942d7a5f3545216e26efd57c24e.
Additional QA computations are real costs, not original-query replay or performance evidence.
Final receipt pins 435=432context+own core/test/doc; receipts do not self-hash.
