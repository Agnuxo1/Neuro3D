# G1 protocol: geometry traversal versus compiled operator (CPU ablation)

**Committed before execution.** 12-13 October 2026. Guide v2 step G (section 11.1: "compile U from the responses to the five bases"; mandatory ablation "geometry vs compiled operator"). Record id `EXP-006-G1-20261013-001`. CPU only, one BLAS thread, run after HA-K1 has finished.

## Routes (same represented model, same outputs)

- **R_graph:** `AffineGeometryNetwork.forward` over the 133-state captured graph for the whole input batch (CPU, Python/NumPy), the route used for historical CPU training and audits.
- **R_compiled:** compile U (8 x 5) and its 16 tangents dU/dtheta from one `forward` call on the five basis inputs, then evaluate fields as X U^T and field tangents as X (dU/dtheta)^T (agent_support `compile_operator`/`apply_operator` semantics). U must be recompiled whenever theta, geometry, materials or wavelength change; that cost is measured and charged.

This is a declared route change inside one linear model, not an RT-hardware or GPU result.

## Measurements

- Captured network as in HA-K1 (`initial_native_{scene,graph}.json`), theta = 0 and theta from `default_rng(7)` uniform in [-0.035, 0.035]^16.
- Batches 1, 150 and 4096 of encoded inputs from `default_rng(4242)` (four U(0,1) features plus constant 1, unit norm).
- **Equivalence (must hold before any timing claim):** max abs field difference <= 1e-12 and max abs field-tangent difference <= 1e-9 (relative to tangents of order 100) at both theta.
- **Timing:** for each batch and for inference (no tangents) and a training step (fields and tangents), 15 repetitions with alternating route order; `time.perf_counter`; medians and interquartile ranges. The compiled route is reported twice: per call with a cached U, and including the recompilation needed after every parameter update.
- Host load is not controlled (other user processes may run); results are local measurements on this machine, not a scaling law.

## Hypothesis and decision

- **H-G1:** with recompilation charged every call, R_compiled is at least 2x faster than R_graph for batches 150 and 4096, both for inference and for a training step. Prediction: much more than 2x, because R_graph's cost grows with the batch inside the 133-state loop while R_compiled pays the loop once on five inputs.
- Decision: CONFIRMED if equivalence holds and the median speed ratio is >= 2 in all four (batch, mode) cells; REFUTED if equivalence holds and any cell is < 2; INCONCLUSIVE if equivalence fails.
- Descriptive: batch 1 ratios, cached-U ratios, compile cost.

## Scope

A CPU ablation of the represented scalar model. It says nothing about native Blender, GPU, RT cores, energy or physical optics, and it does not change any historical result.
