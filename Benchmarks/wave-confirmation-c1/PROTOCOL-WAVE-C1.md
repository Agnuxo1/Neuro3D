# WAVE-C1 protocol: prospective confirmation of the diffraction-inclusive path model

**Committed before execution.** Date: 12 October 2026. Branch `claude/closure-guide-v2-20261012`, built on `74325cc` (Codex closure branch). Guide v2, step C (sections 7.1-7.3). New identifier; the closed `EXP-005-*` chain and the frozen P1-7 files are not modified.

Owner-facing summary: P1-7 refuted the scalar path model without diffraction (E_max 0.0269 / 0.0275 > 0.02). An exploratory diagnostic suggested that adding free Gaussian diffraction brings E_max to about 0.005. This protocol tests that explanation prospectively against a **different, mesh-free solver**, with the **same continuous device** at every numerical resolution and **all 21 preregistered phases**. The confirmation is **not blind**: the exploratory P1-7 values are known and are stated below as predictions.

## 1. Decisions taken with JEV

Consultation on 12 October 2026 (`provenance=jev`, model `jev-1.13.0`): reference solver = exact planar angular spectrum (confidence 1.0); primary budget unchanged from P1-7 (0.94); extension to a cascade and the captured-network regime (0.16, low: included as declared secondary analyses because they cost seconds of CPU and can falsify the model further). Record: `Docs/closure-20261012/claude/jev-wave-c1.json`.

## 2. Reference solver (independent of the P1-7 FDTD)

`angular_spectrum_wave.py`, verified by `test_angular_spectrum_wave.py` (11 tests, none of them uses the configuration below):

- 2D scalar Ez (TM in the P1-7 naming; s-polarization at the film), lambda = 1, exp(-i w t).
- Exact plane-wave propagation; exact operators of **infinite** planar elements normal to x: lossless slab (Airy coefficients, checked equal to the project's 1D TMM `calibracion.rt_1d` to 1e-14) and perfect conductor (r = -1).
- Beams follow the declared element order; evanescent vacuum components are discarded and their largest relative magnitude is reported.
- **Idealization declared in advance:** element truncation and edge diffraction are absent. The P1-7 elements are 40 lambda long, with 4.7 % edge amplitude for w = 8 lambda; the difference this can make is part of what the FDTD cross-check (section 6) measures, not something this solver resolves.
- No mesh represents the device. Resolution refers only to the spectral sampling of the y axis and to the periodic window.

## 3. Device and primary configuration (fixed)

| Item | Value |
|---|---|
| Splitter | Slab n = 2.537430764948469, d = 0.25, centre plane x = 0 for both passes (S1 and S2). This is the project's analytic 50/50 design at 45 degrees (`validacion-onda/calibracion_45.json`, `n_nominal`); it is not recalibrated per resolution |
| Mirrors | Perfect conductor faces at x = +a_A and x = -a_B, a_A = 30/sqrt2 |
| Phases | a_B = a_A + j/(20 sqrt2), j = 0..20: effective path difference exactly j lambda/20 (21 phases) |
| Input | Exact Helmholtz beam, waist profile exp(-s^2/w^2), w = 8, waist through (0, 0), direction 45 degrees |
| Ports | Lines x = +25 (P1) and x = -25 (P2); P1-7 port mode (width w sqrt2, carrier K/sqrt2) centred at y = 2 a_A + 25; power P = abs(c)^2 with the P1-7 overlap definition |

## 4. Models under test (no fitted parameter)

Both use the frozen P1-7 formula `mzi_fdtd.haz_ideal` (equality checked by a regression test), mirrors -1, waist at (0, 0), and the device's own centre-plane coefficients `r_c, t_c` at ky = K/sqrt2. No per-point phase or power alignment is allowed.

- **M0**: P1-7 preregistered model, no path diffraction.
- **M1**: same model with free paraxial diffraction in one transverse dimension (P1-7 exploratory diagnostic).

## 5. Hypotheses, numerical budgets and decision

- **H-C1 (primary):** E_max(M1) = max over 21 phases and 2 ports of abs(P_solver - P_M1) <= 0.02. Prediction from the known diagnostic: about 0.005.
- **H-C0 (replication of the P1-7 refutation):** E_max(M0) > 0.02. Prediction: about 0.027.
- **Solver self-consistency (must hold before any model decision):** reference sampling N = 8192 over a 512-lambda window (dy = 1/16, y_min = -186); variants N = 2048 and 4096 (same window) and a 1024-lambda window (y_min = -442, N = 8192). The maximum abs(delta P) between the reference and every variant must be <= 1e-9. This is far stricter than the P1-7 refinement budget 0.005, which is kept as the comparison reference. Energy balance abs(flux_out/flux_in - 1) <= 1e-9 for every phase. Temporal convergence does not apply (exact frequency-domain steady state).
- **Decision:** if a solver budget fails, both hypotheses are INCONCLUSIVE. Otherwise H-C1 is CONFIRMED in the declared regime if its inequality holds and REFUTED if not; H-C0 is REPLICATED or NOT REPLICATED.
- **Reported for every phase:** complex modal amplitudes of solver, M0 and M1; powers; errors; wrapped phase difference solver-model (UNKNOWN when either amplitude is <= 0.05); P1 + P2 (modal deficit); flux balance.

## 6. Secondary analyses (declared now, reported whatever their outcome)

**S1, cross-solver check of the archived P1-7 FDTD points.** For every archived geometry (`validacion-onda/resultados/mzi_fdtd_{16,24}_kXX.json`, 30 points), rebuild positions with the frozen `mzi_fdtd.geometria` and inject the same paraxial source profile (continuum carrier). Three splitter variants: (i) slab with the FDTD index of that mesh; (ii) ideal angle-independent splitter with the FDTD-calibrated centre-plane r, t of that mesh (`calibracion_fdtd_45.json`); (iii) the continuous 50/50 slab of section 3. **H-C2:** variant (ii) agrees with the archived FDTD powers within 0.005 at all 30 points and both ports. Agreement supports the P1-7 explanation (free diffraction plus splitter coefficients); disagreement quantifies FDTD discretization and truncation effects above 0.005. Variants (i) and (iii) are descriptive.

**S2, sub-network: two cascaded MZIs.** Stage 1 is the primary device with effective path difference in {0, 1/4, 1/2}; its +x output feeds stage 2, an identical device whose splitter plane is x = 30, with a_B2 = a_A + j/(20 sqrt2), j = 0..20 (63 configurations). Final ports x = 30 +/- 25, mode centres y = 4 a_A + 55. **H-C3:** E_max(M1) <= 0.02 over 63 configurations and 2 ports. Same numerical budgets with variants N = 4096 and window 1024. Prediction: M0 fails by more than in the single MZI (about 190 lambda of propagation); no prediction is made for M1.

**S3, diffraction-validity regime of the captured network.** From the captured scene and graph of `Docs/validation/native-deferred-training-2026-10-09/attempt01/worker/initial_native_{scene,graph}.json` (104 objects, 133 states, 17,060 terminal paths, lambda_BU from the scene): every terminal path length L, and every element's in-plane aperture D (smaller principal in-plane extent times abs(cos) of the incidence angle). Declared criteria for a circular 3D Gaussian beam without refocusing: no-diffraction power error 1 - 1/(1 + zeta^2/4) <= 0.02, i.e. zeta = L lambda/(pi w^2) <= 0.2857; per-axis clipping <= 1e-3, i.e. D/2 >= 1.6449 w. A path is **in regime** if some w satisfies both. Reported: distributions of L/lambda, D/lambda, the fraction of paths in regime at the captured lambda_BU, and the largest lambda_BU for which every path is in regime. The 3D criterion is the separable extension of the 2D law tested above; it is a modelling statement, not validated by this 2D confirmation.

## 7. Execution, stopping rule and integrity

- One execution of `run_wave_c1.py` on CPU, one thread, after this protocol is committed and pushed. Environment, command, exit code, wall time and SHA256 of every source and output are recorded.
- No parameter in sections 3-6 changes after execution. A crash caused by a coding error may be fixed and rerun with identical parameters; the fix and the failed run are recorded as a deviation.
- Negative or inconclusive results are published unchanged. A different device, regime, or budget requires a new identifier and protocol.

## 8. Known limitations (before execution)

2D scalar model; infinite planar elements (no edge diffraction); lossless dielectric and ideal conductor; single wavelength; w = 8 lambda only for the primary; the 3D regime analysis uses a model criterion. A confirmation here would establish the diffraction-inclusive path model in this regime and geometry family; it would **not** validate the captured 104-object network physically, nor any fabricated device.
