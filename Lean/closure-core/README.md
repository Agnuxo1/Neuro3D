# Formal core scope

`Decision.lean` states the T1 decision-box lemma using only the two explicit
mixed-order transitivity requirements. It can be instantiated for valid real
or rational orders; it does not assert that an implementation generated valid
boxes. Toolchain is fixed to the already installed Lean 4.34.0; this is separate
from the openai/math guide reference toolchain 4.34.1.

```bash
lean Decision.lean
```

Check the retained compilation output and `#print axioms` before claiming
verification. T2-T5 and the Mathlib-real/complex instantiations remain open.
No `sorry`, external theorem catalogue or shader verification is implied.

## Addendum 12 October 2026 (Claude): T2-T5 in core Lean

`Bounds.lean` proves T2 (power perturbation), T3 (scaled partial Neumann tail),
T4 (rank <= 2 of one real-input detector form; rank-one principal minors of the
complex Gram form) and T5 (passive symmetric two-port) over `Int`, without
Mathlib. Command `lean Bounds.lean` exits 0; `#print axioms` lists only
`propext`, `Classical.choice` and `Quot.sound`. The statements are homogeneous,
so they hold for rationals after scaling by a common denominator. Still open:
real/complex instantiation with Mathlib, the operator-norm link for T3, the
infinite-sum limit, the rank <= 4 bound for a detector difference, and any
statement that a producer's numbers satisfy these hypotheses. Record:
`Docs/closure-20261012/claude/lean-bounds.json`.
