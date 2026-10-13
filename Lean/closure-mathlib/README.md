# Neuro3D certificate lemmas over ℝ and ℂ (Mathlib)

`Neuro3DCertificates.lean` proves the guide-v2 certificate lemmas T1-T5 over the
real and complex numbers with Mathlib. It complements
`Lean/closure-core/Bounds.lean` (integer versions in core Lean, no Mathlib),
which is left unchanged. No `sorry`, no `admit`, no new `axiom`.

## Toolchain and pinned versions

| Item | Value |
|---|---|
| `lean-toolchain` | `leanprover/lean4:v4.34.0` (Lean commit `293d5d0c0c3f3dded4688b3ccd6a33939ac5102b`, Lake 5.0.0-src+293d5d0) |
| Mathlib | tag `v4.34.0`, commit `5ed2965256430c3649e86755f9576b54eca72435` (from `lake-manifest.json`) |
| Mathlib `lean-toolchain` | `leanprover/lean4:v4.34.0` (identical) |
| Platform | Windows 10, x86_64-w64-windows-gnu |

Prebuilt Mathlib oleans were downloaded with Mathlib's cache tool (run
automatically by `lake update`); nothing in Mathlib was built from source. The
only module compiled locally is `Neuro3DCertificates`.

## Commands

All caches stay off `C:`; `.lake/` is git-ignored.

```bash
cd Lean/closure-mathlib
export MATHLIB_CACHE_DIR=D:/PROJECTS/.cognition/lean-cache/mathlib
export XDG_CACHE_HOME=D:/PROJECTS/.cognition/lean-cache/xdg
export LAKE_CACHE_DIR=D:/PROJECTS/.cognition/lean-cache/lake
lake update          # resolves Mathlib v4.34.0 and runs `lake exe cache get`
lake exe cache get   # only needed if the oleans are missing
lake build           # compiles Neuro3DCertificates.lean, prints #print axioms
```

`lake build` result: `Build completed successfully (8925 jobs)`, exit code 0,
no warnings or errors; the local module took 114 s (loading all of Mathlib
from a busy disk dominates).

## Statements proved

All names are in namespace `Neuro3D`.

**T1, decision boxes (ℝ).**
`decisionBox (lower upper P : ι → ℝ) (w : ι) (hbox : ∀ i, lower i ≤ P i ∧ P i ≤ upper i) (hsep : ∀ i, i ≠ w → upper i < lower w) : ∀ i, i ≠ w → P i < P w`.

**T2, power perturbation (ℂ).**
`powerPerturbation (Eobs Etrue : ℂ) (A e : ℝ) (hA : ‖Eobs‖ ≤ A) (he : ‖Etrue - Eobs‖ ≤ e) : |‖Etrue‖ ^ 2 - ‖Eobs‖ ^ 2| ≤ 2 * A * e + e ^ 2`.
It is the instance of `powerPerturbation_general`, which holds in any
seminormed additive group.

**T3, Neumann tail.** For `A : E →L[𝕜] E` on a normed space over a nontrivially
normed field, `b : E`, `‖A‖ ≤ r`, `r < 1`:
- `norm_pow_apply_le`: `‖(A ^ k) b‖ ≤ r ^ k * ‖b‖` for every `k`;
- `neumann_summable` (with `[CompleteSpace E]`): `Summable (fun k => (A ^ k) b)`;
- `neumann_partialTail`: for every `K m`, `‖∑ k ∈ Finset.range m, (A ^ (K + 1 + k)) b‖ ≤ r ^ (K + 1) * ‖b‖ / (1 - r)`;
- `neumann_tsumTail`: `‖∑' k, (A ^ (K + 1 + k)) b‖ ≤ r ^ (K + 1) * ‖b‖ / (1 - r)`;
- `neumann_truncation` (with `[CompleteSpace E]`, i.e. a Banach space): `‖(∑' k, (A ^ k) b) - ∑ k ∈ Finset.range (K + 1), (A ^ k) b‖ ≤ r ^ (K + 1) * ‖b‖ / (1 - r)`.
- helper `hasSum_tail_majorant`: `HasSum (fun k => r ^ (K + 1) * c * r ^ k) (r ^ (K + 1) * c / (1 - r))` for `0 ≤ r < 1`.

This closes the operator-norm link and the infinite-sum limit that the integer
version left open (Mathlib's `hasSum_geometric_of_lt_one`,
`Summable.of_norm_bounded`, `tsum_of_norm_bounded`, `sum_le_hasSum`,
`Summable.sum_add_tsum_nat_add`).

**T4, detector rank.**
- `detectorRankTwo (a b : Fin n → ℝ) : (vecMulVec a a + vecMulVec b b).rank ≤ 2` (via `Q = M Mᵀ`, `M` of size `n × 2`);
- `gramHermitian (u : Fin n → ℂ) : (Matrix.of fun i j => conj (u i) * u j).IsHermitian`;
- `gramRankOne (u : Fin n → ℂ) : (Matrix.of fun i j => conj (u i) * u j).rank ≤ 1`;
- `detectorDifferenceRankFour (a b c d : Fin n → ℝ) : ((vecMulVec a a + vecMulVec b b) - (vecMulVec c c + vecMulVec d d)).rank ≤ 4` (via `Q₁ - Q₂ = M N`, `M` of size `n × 4`).

**T5, passivity.**
- `contraction_normSq_le (U : E →L[𝕜] E) (hU : ‖U‖ ≤ 1) (x : E) : ‖U x‖ ^ 2 ≤ ‖x‖ ^ 2` (any normed space);
- `passiveEuclidean (U : EuclideanSpace ℂ ι →L[ℂ] EuclideanSpace ℂ ι) (hU : ‖U‖ ≤ 1) (x) : ‖U x‖ ^ 2 ≤ ‖x‖ ^ 2`;
- `splitterPassive (t r x1 x2 : ℂ) (hS : ‖t‖ ^ 2 + ‖r‖ ^ 2 ≤ 1) (hc : (t * conj r).re = 0) : ‖t * x1 + r * x2‖ ^ 2 + ‖r * x1 + t * x2‖ ^ 2 ≤ ‖x1‖ ^ 2 + ‖x2‖ ^ 2`;
- helper `sq_norm_eq_re_im (z : ℂ) : ‖z‖ ^ 2 = z.re ^ 2 + z.im ^ 2`.

## `#print axioms` output (from `lake build`)

```
'Neuro3D.decisionBox' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.powerPerturbation_general' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.powerPerturbation' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.norm_pow_apply_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.hasSum_tail_majorant' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.neumann_summable' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.neumann_partialTail' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.neumann_tsumTail' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.neumann_truncation' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.detectorRankTwo' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.gramHermitian' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.gramRankOne' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.detectorDifferenceRankFour' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.contraction_normSq_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.passiveEuclidean' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.sq_norm_eq_re_im' depends on axioms: [propext, Classical.choice, Quot.sound]
'Neuro3D.splitterPassive' depends on axioms: [propext, Classical.choice, Quot.sound]
```

Only the three standard axioms appear; there is no `sorryAx`.

## What these proofs do not establish

- That the numbers a Neuro3D producer emits satisfy the hypotheses: that the
  boxes in T1 are sound, that `A` and `e` in T2 are real bounds for the
  measured fields, that the propagation operator really has `‖A‖ ≤ r < 1` in
  T3, that a detector is of the form `a aᵀ + b bᵀ` in T4, or that a simulated
  element has `‖U‖ ≤ 1` or `|t|² + |r|² ≤ 1`, `Re(t conj r) = 0` in T5.
- Floating-point arithmetic. All statements are over exact ℝ and ℂ; rounding
  in a producer's computation has to be bounded separately.
- Any link between Lean objects and the shader or Python code (no code
  extraction or refinement proof).
- In `neumann_tsumTail` without `CompleteSpace`, a non-summable series has
  `tsum = 0` by convention, so the bound is only informative on a Banach space,
  where `neumann_summable` and `neumann_truncation` apply.

Machine record: `Docs/closure-20261012/claude/lean-mathlib-record.json`.
