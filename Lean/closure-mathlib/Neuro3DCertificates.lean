/-
Neuro3D certificate lemmas T1-T5 over ℝ and ℂ, with Mathlib.

This file is the real/complex counterpart of `Lean/closure-core/Bounds.lean`
(which proves the scaled integer versions without Mathlib).  Every theorem is
proved without `sorry`; the file ends with `#print axioms` for each one.

What is proved is purely mathematical: these lemmas say nothing about whether
the numbers emitted by any Neuro3D producer satisfy the hypotheses.
-/
import Mathlib

open Matrix ComplexConjugate
open scoped BigOperators

namespace Neuro3D

/-! ## T1. Decision boxes -/

/-- T1. If each score `P i` lies in its certified box `[lower i, upper i]` and
every rival's upper bound is strictly below the winner's lower bound, the
winner `w` strictly beats every rival. -/
theorem decisionBox {ι : Type*} (lower upper P : ι → ℝ) (w : ι)
    (hbox : ∀ i, lower i ≤ P i ∧ P i ≤ upper i)
    (hsep : ∀ i, i ≠ w → upper i < lower w) :
    ∀ i, i ≠ w → P i < P w := fun i hi =>
  lt_of_le_of_lt (hbox i).2 (lt_of_lt_of_le (hsep i hi) (hbox w).1)

/-! ## T2. Power perturbation -/

/-- T2 in any seminormed additive group. -/
theorem powerPerturbation_general {E : Type*} [SeminormedAddCommGroup E]
    (Eobs Etrue : E) (A e : ℝ) (hA : ‖Eobs‖ ≤ A) (he : ‖Etrue - Eobs‖ ≤ e) :
    |‖Etrue‖ ^ 2 - ‖Eobs‖ ^ 2| ≤ 2 * A * e + e ^ 2 := by
  have hd : |‖Etrue‖ - ‖Eobs‖| ≤ e := (abs_norm_sub_norm_le Etrue Eobs).trans he
  have htri : ‖Etrue‖ ≤ ‖Etrue - Eobs‖ + ‖Eobs‖ := by
    simpa using norm_add_le (Etrue - Eobs) Eobs
  have hs0 : 0 ≤ ‖Etrue‖ + ‖Eobs‖ := add_nonneg (norm_nonneg _) (norm_nonneg _)
  have hs : ‖Etrue‖ + ‖Eobs‖ ≤ 2 * A + e := by linarith
  have he0 : 0 ≤ e := (norm_nonneg _).trans he
  rw [sq_sub_sq, abs_mul, abs_of_nonneg hs0]
  calc (‖Etrue‖ + ‖Eobs‖) * |‖Etrue‖ - ‖Eobs‖| ≤ (2 * A + e) * e :=
        mul_le_mul hs hd (abs_nonneg _) (by linarith [norm_nonneg Eobs])
    _ = 2 * A * e + e ^ 2 := by ring

/-- T2 over ℂ: `|‖E_true‖² - ‖E_obs‖²| ≤ 2 A e + e²`. -/
theorem powerPerturbation (Eobs Etrue : ℂ) (A e : ℝ)
    (hA : ‖Eobs‖ ≤ A) (he : ‖Etrue - Eobs‖ ≤ e) :
    |‖Etrue‖ ^ 2 - ‖Eobs‖ ^ 2| ≤ 2 * A * e + e ^ 2 :=
  powerPerturbation_general Eobs Etrue A e hA he

/-! ## T3. Neumann tail -/

section Neumann

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜]
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]

/-- Iterates of a contraction decay geometrically. -/
theorem norm_pow_apply_le (A : E →L[𝕜] E) (b : E) (r : ℝ) (hA : ‖A‖ ≤ r) :
    ∀ k : ℕ, ‖(A ^ k) b‖ ≤ r ^ k * ‖b‖ := by
  have hr : 0 ≤ r := (norm_nonneg A).trans hA
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
    rw [pow_succ']
    change ‖A ((A ^ k) b)‖ ≤ _
    calc ‖A ((A ^ k) b)‖ ≤ ‖A‖ * ‖(A ^ k) b‖ := A.le_opNorm _
      _ ≤ r * (r ^ k * ‖b‖) := mul_le_mul hA ih (norm_nonneg _) hr
      _ = r ^ (k + 1) * ‖b‖ := by ring

/-- The geometric majorant of the tail beyond `K` has sum `r^(K+1) ‖b‖ / (1-r)`. -/
theorem hasSum_tail_majorant (r c : ℝ) (K : ℕ) (hr0 : 0 ≤ r) (hr1 : r < 1) :
    HasSum (fun k : ℕ => r ^ (K + 1) * c * r ^ k) (r ^ (K + 1) * c / (1 - r)) := by
  have h := (hasSum_geometric_of_lt_one hr0 hr1).mul_left (r ^ (K + 1) * c)
  simpa [div_eq_mul_inv] using h

/-- T3 (summability). If `‖A‖ ≤ r < 1` the Neumann series `∑ A^k b` converges absolutely. -/
theorem neumann_summable [CompleteSpace E] (A : E →L[𝕜] E) (b : E) (r : ℝ) (hA : ‖A‖ ≤ r) (hr1 : r < 1) :
    Summable (fun k : ℕ => (A ^ k) b) := by
  have hr0 : 0 ≤ r := (norm_nonneg A).trans hA
  refine Summable.of_norm_bounded ((summable_geometric_of_lt_one hr0 hr1).mul_right ‖b‖) ?_
  intro k
  exact norm_pow_apply_le A b r hA k

/-- T3 (every partial tail). For every `K` and `m`,
`‖∑_{k=K+1}^{K+m} A^k b‖ ≤ r^(K+1) ‖b‖ / (1-r)`. -/
theorem neumann_partialTail (A : E →L[𝕜] E) (b : E) (r : ℝ) (hA : ‖A‖ ≤ r) (hr1 : r < 1)
    (K m : ℕ) :
    ‖∑ k ∈ Finset.range m, (A ^ (K + 1 + k)) b‖ ≤ r ^ (K + 1) * ‖b‖ / (1 - r) := by
  have hr0 : 0 ≤ r := (norm_nonneg A).trans hA
  calc ‖∑ k ∈ Finset.range m, (A ^ (K + 1 + k)) b‖
      ≤ ∑ k ∈ Finset.range m, ‖(A ^ (K + 1 + k)) b‖ := norm_sum_le _ _
    _ ≤ ∑ k ∈ Finset.range m, r ^ (K + 1) * ‖b‖ * r ^ k := by
        apply Finset.sum_le_sum
        intro k _
        calc ‖(A ^ (K + 1 + k)) b‖ ≤ r ^ (K + 1 + k) * ‖b‖ := norm_pow_apply_le A b r hA _
          _ = r ^ (K + 1) * ‖b‖ * r ^ k := by rw [pow_add]; ring
    _ ≤ r ^ (K + 1) * ‖b‖ / (1 - r) :=
        sum_le_hasSum _ (fun k _ => by positivity) (hasSum_tail_majorant r ‖b‖ K hr0 hr1)

/-- T3 (infinite tail, `tsum`). `‖∑'_{k>K} A^k b‖ ≤ r^(K+1) ‖b‖ / (1-r)`. -/
theorem neumann_tsumTail (A : E →L[𝕜] E) (b : E) (r : ℝ) (hA : ‖A‖ ≤ r) (hr1 : r < 1)
    (K : ℕ) :
    ‖∑' k : ℕ, (A ^ (K + 1 + k)) b‖ ≤ r ^ (K + 1) * ‖b‖ / (1 - r) := by
  have hr0 : 0 ≤ r := (norm_nonneg A).trans hA
  refine tsum_of_norm_bounded (hasSum_tail_majorant r ‖b‖ K hr0 hr1) ?_
  intro k
  calc ‖(A ^ (K + 1 + k)) b‖ ≤ r ^ (K + 1 + k) * ‖b‖ := norm_pow_apply_le A b r hA _
    _ = r ^ (K + 1) * ‖b‖ * r ^ k := by rw [pow_add]; ring

/-- T3 (truncation error of the Neumann solution). On a Banach space, the
error of truncating `x = ∑' A^k b` after the term `K` is at most
`r^(K+1) ‖b‖ / (1-r)`. -/
theorem neumann_truncation [CompleteSpace E] (A : E →L[𝕜] E) (b : E) (r : ℝ)
    (hA : ‖A‖ ≤ r) (hr1 : r < 1) (K : ℕ) :
    ‖(∑' k : ℕ, (A ^ k) b) - ∑ k ∈ Finset.range (K + 1), (A ^ k) b‖
      ≤ r ^ (K + 1) * ‖b‖ / (1 - r) := by
  have hs := neumann_summable A b r hA hr1
  rw [← hs.sum_add_tsum_nat_add (K + 1), add_sub_cancel_left]
  simp_rw [Nat.add_comm _ (K + 1)]
  exact neumann_tsumTail A b r hA hr1 K

end Neumann

/-! ## T4. Detector rank -/

/-- T4, real input: one detector form `Q = a aᵀ + b bᵀ` has rank at most 2.
Proof: `Q = M Mᵀ` with `M = [a b]` an `n × 2` matrix. -/
theorem detectorRankTwo {n : ℕ} (a b : Fin n → ℝ) :
    (vecMulVec a a + vecMulVec b b).rank ≤ 2 := by
  set M : Matrix (Fin n) (Fin 2) ℝ := Matrix.of fun i k => ![a i, b i] k with hM
  have h : vecMulVec a a + vecMulVec b b = M * Mᵀ := by
    ext i j
    simp [hM, Matrix.mul_apply, Fin.sum_univ_two, vecMulVec_apply]
  rw [h]
  exact (rank_mul_le_left M Mᵀ).trans (rank_le_width M)

/-- T4, complex input: the Gram form `H i j = conj (u i) * u j` is Hermitian. -/
theorem gramHermitian {n : ℕ} (u : Fin n → ℂ) :
    (Matrix.of fun i j => conj (u i) * u j).IsHermitian := by
  show Matrix.conjTranspose _ = _
  ext i j
  simp [Matrix.conjTranspose_apply, mul_comm]

/-- T4, complex input: the Gram form `H i j = conj (u i) * u j` has rank at most 1. -/
theorem gramRankOne {n : ℕ} (u : Fin n → ℂ) :
    (Matrix.of fun i j => conj (u i) * u j).rank ≤ 1 := by
  have h : (Matrix.of fun i j => conj (u i) * u j) = vecMulVec (star u) u := by
    ext i j; simp [vecMulVec_apply]
  rw [h]
  exact rank_vecMulVec_le _ _

/-- T4, difference of two real detectors: rank at most 4.
Proof: `Q₁ - Q₂ = M N` with `M = [a b c d]` (`n × 4`) and `N = [a b -c -d]ᵀ`. -/
theorem detectorDifferenceRankFour {n : ℕ} (a b c d : Fin n → ℝ) :
    ((vecMulVec a a + vecMulVec b b) - (vecMulVec c c + vecMulVec d d)).rank ≤ 4 := by
  set M : Matrix (Fin n) (Fin 4) ℝ := Matrix.of fun i k => ![a i, b i, c i, d i] k with hM
  set N : Matrix (Fin 4) (Fin n) ℝ := Matrix.of fun k j => ![a j, b j, -c j, -d j] k with hN
  have h : (vecMulVec a a + vecMulVec b b) - (vecMulVec c c + vecMulVec d d) = M * N := by
    ext i j
    simp [hM, hN, Matrix.mul_apply, Fin.sum_univ_four, vecMulVec_apply]
    ring
  rw [h]
  exact (rank_mul_le_left M N).trans (rank_le_width M)

/-! ## T5. Passivity -/

/-- T5 for any contraction of a normed space. -/
theorem contraction_normSq_le {𝕜 : Type*} [NontriviallyNormedField 𝕜]
    {E : Type*} [NormedAddCommGroup E] [NormedSpace 𝕜 E]
    (U : E →L[𝕜] E) (hU : ‖U‖ ≤ 1) (x : E) : ‖U x‖ ^ 2 ≤ ‖x‖ ^ 2 := by
  have h : ‖U x‖ ≤ ‖x‖ :=
    calc ‖U x‖ ≤ ‖U‖ * ‖x‖ := U.le_opNorm x
      _ ≤ 1 * ‖x‖ := mul_le_mul_of_nonneg_right hU (norm_nonneg x)
      _ = ‖x‖ := one_mul _
  exact pow_le_pow_left₀ (norm_nonneg _) h 2

/-- T5 on `EuclideanSpace ℂ ι`: an operator of norm at most one never increases
total power `‖x‖² = ∑ |x_i|²`. -/
theorem passiveEuclidean {ι : Type*} [Fintype ι]
    (U : EuclideanSpace ℂ ι →L[ℂ] EuclideanSpace ℂ ι) (hU : ‖U‖ ≤ 1)
    (x : EuclideanSpace ℂ ι) : ‖U x‖ ^ 2 ≤ ‖x‖ ^ 2 :=
  contraction_normSq_le U hU x

/-- `‖z‖² = (re z)² + (im z)²` for a complex number. -/
theorem sq_norm_eq_re_im (z : ℂ) : ‖z‖ ^ 2 = z.re ^ 2 + z.im ^ 2 := by
  rw [Complex.sq_norm, Complex.normSq_apply]; ring

/-- T5, concrete symmetric two-port `E1 = t x1 + r x2`, `E2 = r x1 + t x2`
with `|t|² + |r|² ≤ 1` and `Re(t conj r) = 0`: total output power never
exceeds total input power.  (Exact identity: output power equals
`(|t|² + |r|²)(|x1|² + |x2|²) + 4 Re(t conj r) Re(x1 conj x2)`.) -/
theorem splitterPassive (t r x1 x2 : ℂ) (hS : ‖t‖ ^ 2 + ‖r‖ ^ 2 ≤ 1)
    (hc : (t * conj r).re = 0) :
    ‖t * x1 + r * x2‖ ^ 2 + ‖r * x1 + t * x2‖ ^ 2 ≤ ‖x1‖ ^ 2 + ‖x2‖ ^ 2 := by
  have hc' : t.re * r.re + t.im * r.im = 0 := by
    simp only [Complex.mul_re, Complex.conj_re, Complex.conj_im] at hc; linarith
  simp only [sq_norm_eq_re_im, Complex.add_re, Complex.add_im, Complex.mul_re,
    Complex.mul_im] at hS ⊢
  have hX : 0 ≤ x1.re ^ 2 + x1.im ^ 2 + (x2.re ^ 2 + x2.im ^ 2) := by positivity
  have h1 := mul_le_mul_of_nonneg_right hS hX
  have h2 : (t.re * r.re + t.im * r.im) * (x1.re * x2.re + x1.im * x2.im) = 0 := by
    rw [hc', zero_mul]
  nlinarith [h1, h2]

end Neuro3D

#print axioms Neuro3D.decisionBox
#print axioms Neuro3D.powerPerturbation_general
#print axioms Neuro3D.powerPerturbation
#print axioms Neuro3D.norm_pow_apply_le
#print axioms Neuro3D.hasSum_tail_majorant
#print axioms Neuro3D.neumann_summable
#print axioms Neuro3D.neumann_partialTail
#print axioms Neuro3D.neumann_tsumTail
#print axioms Neuro3D.neumann_truncation
#print axioms Neuro3D.detectorRankTwo
#print axioms Neuro3D.gramHermitian
#print axioms Neuro3D.gramRankOne
#print axioms Neuro3D.detectorDifferenceRankFour
#print axioms Neuro3D.contraction_normSq_le
#print axioms Neuro3D.passiveEuclidean
#print axioms Neuro3D.sq_norm_eq_re_im
#print axioms Neuro3D.splitterPassive
