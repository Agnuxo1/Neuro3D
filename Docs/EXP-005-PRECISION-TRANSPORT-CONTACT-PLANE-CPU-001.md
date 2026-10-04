# EXP005: transport point box -> exact plane residual (CPU opt-in)
ID PRECISION-TRANSPORT-CONTACT-PLANE-CPU-001. Codex capacity_audit/EXP005.
Base863f77e7ad58111c96911e611d93dd2af5485ab8.

## Contract and scope
New pure CPU helper, no old producer/shader/helper imported or executed.
Input six uint32 interleaved hi/lo words for xyz, nine raw32 triangle vertices,
three raw32 direction words and OPTIONAL three signed rational error intervals.
Geometry/direction must be normal or +0; subnormal point wire produces STOP.
Strict uint32 types, finite/canonical +0, abs<=1e6. Rational errors canonical,
integers<=4096bits, denominator>0, signed intervals ordered and resulting box abs<=1e6.
This opt-in domain does not widen frozen fixture bounds or conf1.
None budget means UNKNOWN, never zero: STOP_MISSING_DECLARED_POINT_BUDGET.
All budget values are CALLER-DECLARED CPU hypotheses, not authenticated native bounds.

Literal point is EXACT rational sum of both raw32 limbs, without binary64 collapse.
For each axis, box=literal point+[declared_error_lower,declared_error_upper].
Residual metadata from another audit is not silently inserted, zeroed or discarded.
Given n=(b-a)x(c-a), residual R=n dot(box-a) uses signed interval products.
Nondegenerate plane and nonzero D=n dot(direction) give tau=hull(-R/D).
No normalization. R has units BU^3 if vertices/point are BU, since n is BU^2;
tau is the given ray parameter, NOT physical length. D has units BU^3/parameter.
R=[0,0] -> CPU_ZERO_PLANE_CONTACT_ONLY.
R excludes0 -> CPU_STRICT_PLANE_SEPARATION_ONLY.
R includes0 with width -> CPU_UNCERTAIN_PLANE_CONTACT_STOP.
Degenerate plane / zero D -> STOP. Malformed data -> ValueError, no admission.

These conditions concern the INFINITE PLANE only: NO barycentric/interior proof,
triangle hit/launch exclusion/nearest/full coverage/S0S1/native origin authentication.
All GPU/native/budget-auth/triangle/exclusion/visibility/phase flags remain false;
phase bound null, fullcosts UNKNOWN_NOT_ZERO. The helper does NOT repair point wire.
No epsilon, snapping, ignoreID, threshold/cap/conf1 change or native budget creation.

## Changed method and saved evidence reuse
Parent hi-lo receipt SHAfdf61608eaa7e1bcb025983feeba3b2067cab5eb8f754de385944d3edc10f6db,
109555bytes;439parent pins+parentreceipt=440context. Saved exact-order and hi-lo captures
provide three FABRICATED gap cases2^-60,2^-54,2^-53 at axis0/order0/winding0.
Point rawwords/rawstageSHA and triangle words come from matching stored evidence, not
six admitted originals/SOURCE/native readback. No intersection/transport-rounding rerun.

Five modes per case: literal exact point with explicit zero CPU error, missing error budget,
deliberately lost x word with zero error, lost x with signed uncertain [-delta,+delta],
and known CPU signed correction [delta,delta]. The last is a CONDITIONAL synthetic box,
NOT repair/snap/native credential: wire stays0 and its earlier failure remains retained.
Literal/correction R=0,tau=0; loss R=-16delta,tau=-delta; uncertain R=[-32delta,0],
tau=[-2delta,0]. Negative tau is behind the supplied direction, not a new forward hit.
Missing budget STOP. No native/exclusion flag enabled for ANY mode.

15stored mode audits +3geometric/wire controls=18records, plus two mutation-isolation calls
=20helper invocations. Parallel D0,degenerate plane,subnormal wire all STOP.
10 malformed rejections; return mutations do not contaminate subsequent invocations.
Suite rc0/0.2429301999945892s QA/stdoutSHAba457d92f3a92dbb9e39789e872f79710fecbd5e2a6dfbee1275f9b745b0eef5,
84944bytes. PASS focused CPU contract only; timing NOT performance/equal-work benchmark.

## Retained boundaries and coordination
Prior FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION unchanged;
72prior scalarErrors +16priorRows are SEPARATE,12contactSTOP untouched.
Hi-lo's24binary64-collapse losses and8boundarySTOP preserved in its pinned receipt.
No proof of original uncertainty/source coverage or physical optical phase.
Next: authenticated scene/source/coverage/native point+geometry budgets and device component
consumption/IEEE/guard before promoting any plane condition to actual triangle launch control.
Claude ACK ID+receiptSHA; existing backend/guard/SAMEINPUT S0S1 ALLcoverage/native origin box/
material-gauge-scale-lambda-reference length/phase/full equal-work outputs-costs or missing.
No invented ACK/filler loads. RT16Mvs1M/different outputs/extrapolation NOT equal comparison/redRT.
U/GEMM not a silent substitute for inference from scene.

CPU1thread/affinity1/child<=60s/-B; numerical/hash/IO/oracle costs real UNKNOWN_NOT_ZERO.
GPU/Bpy/RT/compiler/oldproducer/originalqueries/intersectionreplay0; no installation/push/merge/Kaggle.
Frozen runners/shaders/contracts/fixtures conf1/v0/v4/0119/0315/nearestV2 unchanged.
JEV securityBLOCK fallbackLOCAL, no retry/bypass/remote endorsement.
GPU future requires new exclusive Claude job/livegpuq-processes-RAMVRAMtemp/failclosedguard/
newdeadline;freeRAM>=4GiB after>=1024bytes/cell+margins,VRAMtotal<=18GiB,temp<=80C,
pilot120/others600,noMLP32768/near-limit0x9F. Historical overnight window/deadline CLOSED unchanged.
Own4 only versioned; sharedboards/checkpoint local SINstage.
Skills testing+cognition: new explicit interval condition and reuse of pinned saved data.
Initial read failed to print Unicode arrow under CP1252 (rc1); ASCII JSON read repaired display
only before new math. Preserve failure; no computation/gate/threshold changed.

## Independent oracle
Cofactor plane normal and 3x3 oriented-volume determinants at all eight box corners,
plus saved rawstage/triangle/direction/point wire links; no helper/test/oldproducer execution.
18records:6zero-plane CPU conditions (3literal+3synthetic signed offsets),3strict separations,
3uncertainSTOP,3missing-budgetSTOP,1parallelSTOP,1degenerateSTOP,1subnormalSTOP.
104corner values and12tau intervals checked,440contextpins. rc0/0.23137020001013298s QA,
stdoutSHA6b2558771bcbad88ad4fe684c2dca1bd9c04b288ff95c5b6a995a30e6dca0639.
These real additional computations are QA, not original intersections or comparable benchmark.
Final pins443=440context+ownCore/Test/Doc; receipt does not self-hash.
