# Iris demo PR #1 · Codex static review

PR: https://github.com/Agnuxo1/Neuro3D/pull/1
Branch fetched and inspected: `origin/claude/lattice-iris-demo`, 2026-09-29.
Review scope: source and published JSON only, not a new heavy runtime execution.
Original review disposition: **do not merge yet**. Update: origin/main now
contains external merge `2e418df` (verified 2026-09-29 ~20:30 UTC). That merge
does not close the findings below or constitute Codex's independent acceptance.
Preserve existing results and correct the merged implementation in a follow-up.

## Required before acceptance

1. **P1 — hold-out preprocessing.** `load_iris()` fits min/max over all 150 rows
   before splitting. Fit the scaler on `train_idx`, persist it with the weights,
   and use it for all inference. Test-only extremes occur in two features (row
   13: sepal length 4.3 vs TRAIN min 4.4; row 118: petal length 6.9 vs TRAIN max
   6.7). There is no index overlap or proven label leakage. Preserve 96.7% as a
   transductive/exploratory result until a newly frozen train-only run exists.
2. **P1 — fresh-open usability.** `register()` runs only when the external script
   is executed in GUI; the builder never embeds/registers this code in the saved
   `.blend`. Opening the artifact does not install the advertised sidebar panel.
   Document script execution/installation and data paths explicitly, or package
   a real addon. Do not use unreviewed automatic code execution as a shortcut.
   Verify a scene edit and a newly classified input after fresh reopen.
3. **P1 — precise claim.** The table says "fully optical" decision, while
   `classify()` uses Python complex-field accumulation, `abs(...)**2`, and
   `numpy.argmax`. No learned linear readout is needed, but the execution is
   hybrid digital geometry/field computation. Make the lead and table agree
   with the otherwise accurate limitations paragraph.

## Follow-up gate (not a demand for an immediate heavy rerun)

The current `--verify` compares intensities at the three class ports. A full
optical-network gate should record all eight complex outputs, energy/escape and
the saved scene's parameters, and rerun from that saved scene. Retain the
decorative-object exclusion and add before/after-decoration invariance. This
should complement, not silently inherit, EXP-004's frozen gates.

The `finally` block unconditionally makes non-Optics collections visible; restoring
the previous exclusion flags would better preserve users' interactive view state.

No other author's files were edited and no review approval is attributed to JEV.
The independent Codex shader demonstration has already been published separately;
it does not substitute for the trained Iris lattice.
