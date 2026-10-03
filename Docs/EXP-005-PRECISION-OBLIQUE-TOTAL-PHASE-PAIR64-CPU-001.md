# EXP-005 — CPU native pair64 total declared phase

ID PRECISION-OBLIQUE-TOTAL-PHASE-PAIR64-CPU-001, Codex capacity_audit/EXP005.
Base3160738b02b3d662e50780afb1750baf75ba9b50. Opt-in precision-oblique-total-phase-pair64-CPU-v1.
Representation TOTAL_DECLARED_PHASE_PAIR64_CPU_NOT_GPU_ABI. LOCAL JEV fallback blocked/no retry.

Reads pinned SOURCE-MATERIAL-INTERVAL001 captures, not old geometry/tests/encoders/writers.
Closed selector: registry case, exact phase-request digest, ORIGINAL/literal, representation and CPU intent.
Parent STOP never runs new arithmetic. Nine admitted parent overlays remain declared only.
Three explicitly NEW own variants: mu=1/10 point; gamma0=2^-120 point; mu=1/10 with material radius
(cap/8 - maxSOURCE geometric error) exactly filling the old analytic SOURCE cap. Caps unchanged.

New native CPU encoding for mid(gamma0), mid(gamma1), mid(mu):
hi=RN64(q), lo=RN64(q-exact(hi)), retaining raw words and residual error abs(exact(hi)+exact(lo)-q).
Six parameter RN64 casts. Four new pair additions (SOURCE propagation+gamma, then+mu for each SOURCE),
then pair subtraction of the two totals; each 26 explicit native +/- operations via four TwoSum plus
two adds, total130 new arithmetic RN64. Unary sign negation exact, not an RN add/sub.
No Fraction-to-output cast or copied total-phase result; output comes from native arithmetic.
Every operation records operand/output IEEE words and exact observed rounding error.
TwoSum identity checked over exact decoded operands at each helper.

Each SOURCE bound:
8*(geometric pair error to retained interval + gamma radius + common mu radius
+ gamma encoding error + mu encoding error + observed first pair-add error + second pair-add error).
Direct distance of actual total pair to ORIGINAL total interval must not exceed conservative bound,
and conservative bound must satisfy ORIGINAL SOURCE cap. Emit ALL three rows only after every SOURCE
and relative cap passes. Diagnostics/words/trace survive STOP.

Relative bound:
8*(maxdistance of SOURCE propagation pair difference to ORIGINAL relative interval
+ gamma radii0+1 + gamma encoding errors0+1 + ALL SOURCE pair-add errors + relative pair-sub error).
Same encoded mu cancels algebraically only; its encoding error and uncertainty remain charged to
each SOURCE. Per-SOURCE addition errors never cancel by assumption. Original geometric/native
rounding evidence and all prior FAILs remain retained, not rerun or erased.

Boundary control is analytically admitted but transport has a nonzero mu=1/10 encoding error:
new conservative SOURCE bound exceeds unchanged cap -> STOP and zero emitted rows.
This does not refute the earlier rational-only model: it adds the missing encoding/arithmetic stage.
Tiny gamma2^-120 can be lost by pair addition; measured error remains nonzero even when cap still fits.
No loosening thresholds, no reinterpretation of old STOP or silent ORIGINAL/overlay replacement.

New tests retain complete word traces, all parent statuses, new variants and closed-selector negatives.
Independent oracle reads sealed captures, decodes words as rationals, checks each RN64 result by exact
midpoint/neighbor tie-even comparisons, reconstructs 26-node graph per pair operation, EFT identities,
encoding and ALL budgets; it does not replay native arithmetic or producers.

CPU arithmetic only: no material/scene authentication, optical phase/field/power, trigonometry,
modulo, encoding into Blender/Vulkan, GPU RNE or V2 total-phase implementation. All promotion/GPU/
physical/native flags false; amplitude/field/power None. V2_total_phase_backend_bound false ALWAYS.
QA timings/operation counts are bookkeeping, not speed/efficiency or equivalent RT work.
Full costs UNMEASURED_NOT_ZERO. One CPU thread/affinity1/child60s.

Only five own reviewed files versioned. Frozen runners/shaders/contracts/guards/fixtures/bounds/caps
and failures intact; boards/checkpoint local unstaged. JEV securityblocked no retry/aval, historical
deadline closed/immutable, RAMUNKNOWN_ACCESS_DENIED retained without bypass. No GPU/Blender/reservation,
SDK/DrJit/install/Kaggle/push/merge/foreign writers. Future GPU requires explicit new same-work backend,
contract/tests/commit and separate Claude reservation/telemetry/fail-closed guard/new deadline.
Request existing same-ORIGINAL-overlay material/backend/guard/ABI artifacts by ID/path/SHA/bytes.

## Captured final validation

Final suite: 46 unique cases, 11 admitted CPU declared phase, 35 STOP; 12 cases computed,
including the cap-boundary STOP with all diagnostics retained. Final-suite census only:
1560 new RN64 arithmetic nodes and 72 parameter casts; initial failed suite also executed
arithmetic and is NOT included in this census. No all-turn aggregate timing/cost claim.
Initial suite rc1 retained with full stderr and initial test source: own test identifier
wrong_model collided with the sealed parent's wrong_model. Repair changed only the test
identifier to native_wrong_model and added a pre-execution uniqueness check; no budget,
threshold, core arithmetic or expected STOP became PASS through relaxed criteria.
Independent rational oracle PASS proves all captured native words are nearest ties-even
at each operation and encoding, exact graph topology, source/relative bounds and 131 pins.
This proves the captured CPU operations only, not any GPU Float64/float-controls policy.
