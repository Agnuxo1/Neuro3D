# G1 results: compiling the operator is not a 2x speed-up when it must be recompiled every call

Protocol committed and pushed before execution: `PROTOCOL-G1.md`, commit `b857779` (GitHub activity: 2026-10-12T22:05:46Z). Executed after HA-K1 finished, 2026-10-12 22:38:20-22:38:35 UTC, exit 0, one CPU thread (CPython 3.13.7, NumPy 2.2.6, Intel64 Family 6 Model 85). Raw output `results/G1_RESULTS.json`, log `results/run01.log`. No deviation. Host load was not controlled.

## Equivalence (required before timing)

| theta | max field difference | max tangent difference (tangents up to about 60) |
|---|---|---|
| 0 | 6.1e-16 | 5.4e-14 |
| random in the box | 6.8e-16 | 4.6e-14 |

Both are far inside the 1e-12 and 1e-9 budgets: the compiled operator and its 16 tangents reproduce the graph traversal.

## Timing (medians of 15 alternating repetitions)

| Cell | Graph traversal | Compiled, recompiled each call | Compiled, cached U | Ratio with recompile | Ratio with cached U |
|---|---|---|---|---|---|
| inference, batch 1 | 16.6 ms | 13.9 ms | 0.011 ms | 1.20 | 1583 |
| training step, batch 1 | 16.6 ms | 16.0 ms | 0.018 ms | 1.04 | 912 |
| inference, batch 150 | 15.3 ms | 13.4 ms | 0.019 ms | **1.14** | 792 |
| training step, batch 150 | 23.5 ms | 18.6 ms | 0.48 ms | **1.26** | 49 |
| inference, batch 4096 | 24.3 ms | 15.0 ms | 0.20 ms | **1.63** | 122 |
| training step, batch 4096 | 508 ms | 31.1 ms | 17.4 ms | **16.3** | 29 |

Compiling U with its tangents costs 15.2 ms (median), the same order as one graph traversal.

## Decision

**H-G1 REFUTED**: the smallest decisive ratio is 1.14 (inference, batch 150), below the preregistered 2. The prediction assumed the traversal cost grew with the batch inside the 133-state loop; in fact the traversal is vectorized over the batch, so its cost is dominated by the fixed per-state Python loop, which the compiled route also pays when it recompiles. Only the training step at batch 4096, where the traversal carries (states x batch x 16) tangent arrays, gains 16x.

## What follows

- With **fixed geometry** (inference after training, certificate replay, repeated evaluation), a cached U is 100-1600 times faster than the traversal on this CPU, at identical outputs. This is the declared compiled-operator route of guide section 11.1, distinct from graphical or RT execution.
- During **geometry training**, recompiling U and its tangents per step pays off only for large batches.
- Nothing here concerns GPU, RT cores, energy or physical optics, and the historical GPU-slower-than-CPU result is unchanged.
