# Claude closure campaign on guide v2: what was done, what it shows, what remains

Date: 12-13 October 2026. Branch `claude/closure-guide-v2-20261012`, built on Codex's `codex/closure-guide-v2-20261012` (`74325cc`) without editing Codex's files or checkout. Every experiment had its protocol committed and pushed to GitHub before execution; every run is single, logged and hashed; negatives are kept. Evidence levels follow guide section 35.

## Results

| Step | Deliverable | Result | Level |
|---|---|---|---|
| C | WAVE-C1 prospective confirmation with an independent mesh-free solver ([results](../../../Benchmarks/wave-confirmation-c1/RESULTS-WAVE-C1.md)) | Diffraction-inclusive path model **confirmed** (Emax 0.0040 <= 0.02, same continuous device, 21 exact phases); no-diffraction model refutation **replicated** (0.0281); archived FDTD within 0.0048; two-MZI cascade 0.0044 | L2, plus L3 rerun on Linux CI |
| C | Captured-network regime | **0 of 17,060 paths** in the diffraction-free regime at lambda = 0.1 BU; about 790x shorter lambda needed | L2 (model criterion) |
| K/F | HA-K1 teacher-student capacity ([results](../../../Benchmarks/geometry-capacity-k1/RESULTS-HA-K1.md)) | Decision dimension 12 (geometry) / 26 (free linear) / 29 (quadratic); four inert translations; H-A1 **supported** (+0.051, Holm p 0.0039); H-A2 **opposite** to the prediction | L2 |
| G | G1 compiled operator ([results](../../../Benchmarks/compiled-operator-g1/RESULTS-G1.md)) | Equivalent to 7e-16; H-G1 **refuted** (1.14x with recompilation); cached operator 29-1583x faster | L2 |
| L | Lean T2-T5 ([source](../../../Lean/closure-core/Bounds.lean)) | Compiled in core Lean 4.34, standard axioms only; recompiled on Linux CI | Machine-checked |
| O | Red team by an independent verifier agent ([report](RED-TEAM-WAVE-C1-LEAN.md)) | No number refuted; four statements corrected by dated notes | Agent review, not human |
| P | Section-18 records ([registry](experiment-registry-claude.json)) | Three records, zero validation problems | Integrity |
| Q | CI `claude-closure-cpu.yml` | WAVE-C1 rerun within 8.9e-16; Lean T1-T5 compiled | L3 environment check |
| A/J | Successor manifests, canonical record (append-only), manuscript v3 and PDF, README, claims and status addenda | Consolidated; manifests still report open fronts (exit 2 by design) | - |

## What changes in the scientific picture

1. The P1-7 negative is now explained and the explanation is confirmed with a solver that cannot share FDTD errors: diffraction, not a coding fault, is what the no-diffraction model misses.
2. The captured Blender scene, as represented, is far from any regime where its ray model is a faithful wave description. Physical claims require a rescaled geometry or a diffraction-inclusive network model; this is the main new constraint on the project's physical ambitions.
3. The captured geometry measurably restricts the free linear optical class and wastes a quarter of its trained parameters. Expressiveness is not where an advantage can come from.
4. A cached compiled operator is the fast route for fixed geometry; recompiling per step is only worth it for large batches.

## Still open (owner or external dependencies marked)

- Native GPU resident-graph divergence, external NVIDIA and actual AMD runs, isolated energy (the GPU was busy with another queued job throughout this session).
- EEGNet H2 (host RAM floor), real-data reserved tasks for H-A, H-B certificate coverage, H-D energy and latency.
- Full-network wave validation, 3D and vector effects, physical demonstrator (owner decision D0, partner).
- Mathlib instantiation of T2-T5 (download needs the owner's OK), real/complex and operator-norm links.
- Sealed labels and human red team (owner), specialist critique, real authorship and CRediT (owner), DOI and Software Heritage, independent replication and adoption (third parties).

No novelty, superiority, physical device, external review or award is claimed.
