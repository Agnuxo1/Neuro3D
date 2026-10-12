# Red-team report: WAVE-C1 and Lean T2-T5 (guide v2 step O)

Date: 12-13 October 2026. Reviewer: an independent verifier agent (Claude Sonnet, `cog-verifier`) launched with the artefacts and the protocol only, without the producer's reasoning, read-only on the repository; scratch scripts outside the repository. This is adversarial review by a different agent, **not** independent human review or external replication. Producer: Claude (Opus) on branch `claude/closure-guide-v2-20261012`.

## Verdict summary

No headline number was refuted. Four statements were weakened and have been corrected by dated notes (original text retained):

| # | Claim | Verdict | Evidence produced by the red team | Action |
|---|---|---|---|---|
| 1 | M1 residual attributed to paraxial treatment of the displaced beam | WEAKENED (wrong attribution) | Ideal constant splitter: solver vs M1 about 3e-5 at j = 0, 10, 20; real slab 0.0013 / 0.0014 / 0.0040 | Correction note in `RESULTS-WAVE-C1.md`: residual is the slab's angular dependence |
| 2 | Lean T3 "homogeneous, rational by scaling" | WEAKENED | Lean proof (standard axioms only) that the Int hypotheses force an eventually-zero sequence; theorem not vacuous (8, 4, 2, 1, 0, ... with p = 1, q = 2) | README clarification: transfer per fixed (K, m) by truncation and scaling |
| 3 | Two-MZI cascade | WEAKENED (scope) | Infinite planes applied in declared order; mirror planes of both stages would cross other beams; finite 40-lambda elements avoid collisions by hand check; dark configurations reach total power 3e-6 | Scope note in `RESULTS-WAVE-C1.md` |
| 4 | Clipping constant 1.6449 in the protocol | Minor | Code computes 1.64526 | Note in `RESULTS-WAVE-C1.md` |

## Attacks that survived

- Airy slab formula, centre-plane conversion and PEC sign: independent 4x4 boundary-condition solve, difference <= 6e-16 for 5 ky values and 2 thicknesses; abs(r)^2 = 0.49999999999999944 at 45 degrees.
- Independent MZI recomputation by direct beta-quadrature (own Jacobian, no FFT, no `Grid`): max power difference 1.4e-13 over 21 phases and 2 ports.
- M0/M1 equal the frozen P1-7 `haz_ideal` with no fitted parameter: 84 values within 1e-9; Emax(M0) = 0.028131, Emax(M1) = 0.004012.
- Energy balance 3.3e-16, self-consistency 2.7e-15; full rerun in a temporary folder with `compare_rerun.py`: difference 0.0; 11 solver tests pass.
- FDTD cross-check with a different window (640 lambda, N = 10240): equal to the runner within 3e-15; 0.004821 against the archived FDTD over 30 points.
- Cascade: 16 of 63 configurations recomputed independently within 1.2e-13; Emax(M1) 0.004407, Emax(M0) 0.1066; unchanged on the 42 informative configurations.
- Captured-network regime: 17,060 paths by dynamic programming; L/lambda 110.69-523.95; all 104 elements are 4-lambda planar squares (detectors 3 lambda), projected aperture 2.83 lambda; zeta_max 0.2857 and clip ratio 1.6453 re-derived; lambda_max 1.2658e-4 BU, factor 790.04. The 2D law at zeta = 0.47 gives 2.7 %, matching the observed 2.8 %. The largest allowed waist (0.86 lambda) is not paraxial, which makes the criterion conservative in favour of the stated conclusion.
- Preregistration integrity: hashes of protocol, solver and runner match commit `7327b67`; `sha256sum -c` passes. The reviewer could not check push-before-run; GitHub's activity API shows the branch creation with `7327b67` at 21:43:23Z and the run started at 21:43:30Z.
- Lean `Bounds.lean`: exit 0, only `propext`, `Classical.choice`, `Quot.sound`; no `sorry`, `admit` or `native_decide`. T2 SURVIVED without weakening; T4 SURVIVED (`hermitianRankOne` covers principal minors only, as stated); T5 SURVIVED (sufficient, not necessary, conditions; declared).

## Not verified by the red team

The physical cause of variant (iii) fitting the FDTD better than (ii); the PNG figures.

Side effect reported: running `lean` outside the project folder made elan install toolchain v4.35.0 in the user's home; the repository is unaffected and pinned to v4.34.0.
