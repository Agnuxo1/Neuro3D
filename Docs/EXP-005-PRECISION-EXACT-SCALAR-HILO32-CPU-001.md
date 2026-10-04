# EXP005: exact CPU scalar -> hi-lo32 with separate residual
ID PRECISION-EXACT-SCALAR-HILO32-CPU-001. Codex capacity_audit/EXP005.
Base fbddd9d8697ab206498d42406fd8f449dc2a263f.

## Contract
New opt-in pure standard-library CPU helper, not native shader or authenticated scene consumer.
Input canonical rational [n,d], strict integer types (not bool), d>0, each integer <=4096bits,
abs(value)<=1000000. This audit domain does not enlarge frozen fixture bounds.
Integer nearest/ties-even binary32 rounding: hi=RN32(x), lo=RN32(x-exact(hi)).
Wire is exactly 8bytes little-endian two uint32 words. Zero words canonical +0.
pair_sum_exact = exact(hi)+exact(lo); residual_exact = x-pair_sum_exact.
Residual is exact rational CPU METADATA, NOT part of the 8-byte GPU wire.

EXACT_PAIR_CPU_ONLY requires residual exactly zero AND both components normal or +0.
STOP_SUBNORMAL_COMPONENT takes precedence when either word is subnormal, even if residual0.
STOP_NONZERO_RESIDUAL when normal/zero words lose information. Do not discard residual,
treat omitted residual as zero, snap values, broaden bounds or lower admission criteria.
Subnormal rounding is modeled for negative controls only, not promoted as device-safe.
Malformed rationals/nonfinite/negative-zero words or inconsistent metadata raise ValueError.
audit_packet recomputes canonical hi/lo/residual and rejects unknown fields, changed wire,
status, value, flags or bounds. This checks CONTENT CONSISTENCY, not runtime/scene authenticity.
GPU/exclusion/native/phase flags false, phase/origin native bounds null; costs UNKNOWN_NOT_ZERO.
No collapse hi+lo into an ordinary float64 scalar: preserved tiny low component can be lost again.
No original intersection/length/phase/source replay. No import-time I/O/foreign writers.

## Focused evidence (new transport method, saved geometry reused)
Parent exact-order receipt SHAa6d647eb6d803274e534def7780a81d9673db2b8561138215609e350e94a6a69
108943bytes; 435parentpins + parentreceipt=436context. No old producer/helper execution.
Read 36 saved unique TWO-TRIANGLE CPU results; transport t+p3=144packets.
All are EXACT_PAIR_CPU_ONLY, residual0. Existing raw stage hash plus case/axis/order/winding
is retained outside packet for evidence linkage, NOT S0/S1 scene/native authorization.
24 t controls for gaps2^-60/2^-54 lose the low part again when diagnostic float64 collapse
is applied; retain this failure. No new triangle evaluations or original6INPUT query replay.
11 numeric boundary controls: zero, signed thirds, tenth, subnormal/underflow, minimum normal,
normal/subnormal tie, ties-even near1 and above-tie requiring more than binary64 precision.
8 of 11 remain STOP (6nonzero residual +2subnormal); 3 local exact pairs.
11 invalid rational rejections,17 metadata mutation rejections and return mutation isolation.
Suite rc0/0.24739340000087395s QA/stdoutSHA45205cfd46a98932bca581bae386f5053b41562906695525a03fbd1126f5a47b,
169490bytes. PASS transport CPU consistency only, NOT full scene/native/phase certification.

## Boundaries retained
Prior FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION unchanged;
72old scalar errors +16prior rows SEPARATE,12contactSTOP unchanged.
Exact point from prior helper remains mathematical CPU point, not native launch/origin box.
No ray normalization, epsilon, IDignore, snap, offsets, threshold changes or frozen code edits.
CPU synthetic / Bpyfloat32 / GPU ALU digital / RT / physical optics distinct.
Next scene/coverage/source binding, actual shader/component consumption/IEEE/guard and
length/material/gauge/scale/lambda/reference/phase budget all require separate evidence.
Claude ACK thisID+receiptSHA; existing backend/guard/SAMEINPUT S0S1 ALLcoverage/IEEE/native box/
full equal-work outputs and costs or explicit missing. No invented ACK or filler loads.
RT16Mvs1M/different outputs/extrapolated crossing NOT equivalent comparison/neural RT.

CPU1thread/affinity1/child<=60s/-B. New rounding/QA/hash/IO costs real; timings NOT performance.
GPU/Bpy/RT/compiler/oldproducers/triangleevaluations/originalreplays0. No SDK/DrJit/Kaggle/push/merge.
JEV securityBLOCK local fallback, no retry/bypass or remote endorsement.
GPU future only contract/tests/commit+exclusive fresh Claude job/livegpuq processes RAMVRAMtemp/
failclosedguard+newdeadline,freeRAM>=4GiB after >=1024bytes/cell+margins/temporaries,
VRAMtotal<=18GiB,temp<=80C,pilot120/others600,noMLP32768/near-limit after0x9F.
Historic overnight window/deadline remains CLOSED untouched. Own4 only versioned;
shared4 local SINstage. Skills testing+cognition: bounded reuse, residual/negative retention.

## Independent oracle and preserved draft mismatch
Independent exact-nearest-neighbor raw32 distances/ties-even via struct decoding,
without importing/executing helper/tests/old geometry: 155packets,310rounding checks,
436contextpins,144saved-source joins and24binary64-collapse failures retained.
Boundary counts:3exactCPU pairs,6nonzero-residualSTOP,2subnormalSTOP.
The above-half-ULP case 1+2^-24+2^-80 correctly rounds hi upward but loses2^-80
after lo rounding; residual remains nonzero. Two limbs are NOT universally exact.
rc0/0.2324469000013778s QA/stdoutSHA78a16345664cc597ea13a0fcb31d0bb0e6ca496e15b81f8b0bf986bbbac6d91f.
Draft summary incorrectly counted5nonzero residuals/7totalSTOP. Oracle captured mismatch;
corrected summary only to6/8 and3exact. Core/test/rounding/status/thresholds unchanged.
Final pins439=436context+ownCore/Test/Doc; receipt no self-hash.
