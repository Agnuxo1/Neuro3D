# HA-K1 protocol: does the captured geometry restrict the decision functions?

**Committed before execution.** Date: 12 October 2026 (UTC). Guide v2 step K, hypothesis H-A (section 25); step F capacity (section 10.1). Experiment record id `EXP-006-HA-K1-20261012-001`. CPU only, one thread.

## 1. Question and nested classes

For the historical encoding (four features in [0, 1] on sources r0, r1, c0, c1, a constant 1 on c2, unit input power) and the three historical decision detectors det.R0-R2:

- **F_quad**: argmax_j x^T Q_j x with arbitrary symmetric Q_j.
- **F_lin**: argmax_j abs(W_j x)^2 with arbitrary complex W (3 x 5). With real input each detector form has rank <= 2 (Lean `detectorRankTwo`).
- **F_geom**: the captured 104-object network (`initial_native_{scene,graph}.json` of the native deferred training) with its 16 paired mirror translations, evaluated by the CPU `AffineGeometryNetwork`, translations in [-0.035, 0.035] BU around the captured base.

F_geom is a subset of F_lin, which is a subset of F_quad. The question is how much each restriction costs on tasks that the larger class solves exactly.

## 2. Already known before this protocol (deterministic computation, not a test)

Computed on 12 October 2026 while preparing this protocol and recomputed by the runner: the Jacobian of the three detector quadratic forms with respect to the 16 translations has rank **12** at 20 random points of the box; parameters `c03, c13, c23, c33` have **exactly zero** effect on det.R0-R2. Modulo the decision invariances (common shift of all forms, common positive scale) the local decision dimension is **12** for F_geom, **26** for F_lin and **29** for F_quad. Fresh exact graph rebuilds kept the captured topology at both box corners and 5 random points (19 s each). These values motivate the predictions below; they were not obtained from the data of this experiment.

## 3. Tasks (synthetic, generated fresh per seed; no historical data)

For seeds s = 0..9: features f ~ U(0,1)^4 from `default_rng(1000 + s)`, 400 training and 2000 test inputs, x = (f1, f2, f3, f4, 1)/norm. Teachers from `default_rng(2000 + s)`:

- **T_lin**: W = (N(0,1) + i N(0,1))/sqrt2, labels argmax abs(W x)^2.
- **T_quad**: Q_j = (A_j + A_j^T)/2 with A_j ~ N(0,1)^(5x5).
- **T_geom**: theta* ~ U(-0.035, 0.035)^16 on the captured network (realizable control).

## 4. Students (fixed hyperparameters; no tuning on test data)

- **S_quad**: multinomial logistic regression on the 15 monomials x_k x_l (k <= l), scikit-learn lbfgs, C = 100, max_iter = 5000.
- **S_lin**: `agent_support/closure_limits.train_detector_classifier`, modes = 3, passive = False, steps = 600, learning_rate = 0.05, scale = 20; 3 restarts (seeds 3000 + 10 s + k); the restart with the lowest final training loss is kept.
- **S_geom**: Adam on the 16 translations with the network's own cross-entropy gradient, temperature 0.05 (historical profile), learning rate 0.002 BU, 400 steps, translations clipped to the box after each step; 3 restarts from U(box) (seeds 3000 + 10 s + k); lowest final training loss kept.

Every teacher theta* and every kept student theta is checked by a fresh exact `build_graph` rebuild of the materialized geometry; a kept theta whose topology differs from the captured graph is reported INVALID and the next-best valid restart is used (none valid: NULL for that seed).

## 5. Hypotheses and decision

Primary metric: test accuracy. Paired units: the 10 seeds.

- **H-A1 (geometry restriction):** on T_lin, delta = acc(S_lin) - acc(S_geom) > 0. Prediction: mean delta > 0.05.
- **H-A2 (passive linear restriction):** on T_quad, delta = acc(S_quad) - acc(S_lin) > 0. Prediction: positive.
- Test: one-sided Wilcoxon signed-rank over seeds; Holm over {H-A1, H-A2} at alpha = 0.05; paired bootstrap 95 % interval over seeds (`closure_statistics.paired_bootstrap`, 10,000 draws, seed 0). **SUPPORTED** if the Holm-adjusted p < 0.05 and the interval's lower end > 0; **OPPOSITE** if the upper end < 0; otherwise **INCONCLUSIVE**.
- **Control C-A3 (optimizer adequacy):** on T_geom, mean acc(S_geom) >= 0.95. If it fails, H-A1 is reported as confounded by optimization, whatever its p-value.
- Descriptive: every student on every teacher, the majority-class rate, final training losses and the theta checks.

## 6. Budget, stopping and integrity

One execution of `capacity_k1.py`, CPU, one BLAS thread, wall-time limit 2 h; if exceeded, completed seeds are reported and the rest are NULL. Code, protocol, inputs and outputs are hashed. No hyperparameter changes after execution; a crash caused by a coding error may be fixed and rerun with identical parameters, recorded as a deviation.

## 7. Scope

Synthetic teacher tasks measure representational restriction and optimizer reach, not generalization on real data, physical fidelity (WAVE-C1 found the captured scene outside the diffraction-free regime at its represented wavelength) or utility. The captured network is evaluated through its represented scalar model on CPU, not natively in Blender or on GPU.
