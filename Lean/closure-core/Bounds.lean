/- Guide v2 lemmas T2-T5 in core Lean 4.34 (no Mathlib), stated over Int.

   Every statement is homogeneous in its scaled quantities, so it holds for
   rationals after multiplying all of them by one common positive denominator.
   Real and complex instantiations, operator norms, infinite sums and the
   difference-of-detectors rank bound need Mathlib and remain open.
   Proved here:
   * T2 power perturbation: |P_true - P_obs| <= 2 A e + e^2 for complex fields
     given as real and imaginary parts.
   * T3 Neumann tail (scaled): a nonnegative sequence with q n(k+1) <= p n(k),
     0 <= p < q, has every partial tail beyond K bounded by
     (p/q)^(K+1) n(0) / (1 - p/q).
   * T4 rank: every 3x3 minor of a a^T + b b^T vanishes (real input, one
     detector has rank <= 2); every principal 2x2 minor of the Hermitian Gram
     form of one complex row vanishes (Lagrange identity, complex input).
   * T5 passivity: a two-port with |t|^2 + |r|^2 <= 1 and Re(t conj r) = 0
     (lossless symmetric splitter when equality holds) never increases total
     output power. -/
namespace Neuro3D

theorem sqNonneg (a : Int) : 0 ≤ a * a := by
  rcases Int.le_total 0 a with h | h
  · exact Int.mul_nonneg h h
  · have h' : 0 ≤ -a := by omega
    have := Int.mul_nonneg h' h'
    grind

theorem absLeOfSqLe {s t : Int} (ht : 0 ≤ t) (h : s * s ≤ t * t) : s ≤ t ∧ -t ≤ s := by
  constructor
  · rcases Int.le_total s t with h1 | h1
    · exact h1
    · by_cases heq : s = t
      · omega
      · have hlt : t < s := by omega
        have := Int.mul_self_lt_mul_self ht hlt
        exact absurd (Int.lt_of_lt_of_le this h) (Int.lt_irrefl _)
  · by_cases hneg : -t ≤ s
    · exact hneg
    · have hlt : t < -s := by omega
      have h2 := Int.mul_self_lt_mul_self ht hlt
      have e : (-s) * (-s) = s * s := by grind
      rw [e] at h2
      exact absurd (Int.lt_of_lt_of_le h2 h) (Int.lt_irrefl _)

/-- T2. Observed field a + i b with |E_obs| <= A; error u + i v with |error| <= e. -/
theorem powerPerturbation (a b u v A e : Int) (hA : 0 ≤ A) (he : 0 ≤ e)
    (hobs : a * a + b * b ≤ A * A) (herr : u * u + v * v ≤ e * e) :
    ((a + u) * (a + u) + (b + v) * (b + v)) - (a * a + b * b) ≤ 2 * A * e + e * e ∧
    -(2 * A * e + e * e) ≤ ((a + u) * (a + u) + (b + v) * (b + v)) - (a * a + b * b) := by
  have lag : (a * a + b * b) * (u * u + v * v)
      = (a * u + b * v) * (a * u + b * v) + (a * v - b * u) * (a * v - b * u) := by grind
  have h1 : (a * u + b * v) * (a * u + b * v) ≤ (a * a + b * b) * (u * u + v * v) := by
    rw [lag]; exact Int.le_add_of_nonneg_right (sqNonneg _)
  have h2 : (a * a + b * b) * (u * u + v * v) ≤ (A * A) * (e * e) :=
    Int.mul_le_mul hobs herr (Int.add_nonneg (sqNonneg u) (sqNonneg v)) (sqNonneg A)
  have h3 : (A * A) * (e * e) = (A * e) * (A * e) := by grind
  have cs : (a * u + b * v) * (a * u + b * v) ≤ (A * e) * (A * e) := by
    rw [← h3]; exact Int.le_trans h1 h2
  have bound := absLeOfSqLe (Int.mul_nonneg hA he) cs
  have expand : ((a + u) * (a + u) + (b + v) * (b + v)) - (a * a + b * b)
      = 2 * (a * u + b * v) + (u * u + v * v) := by grind
  have pos : 0 ≤ u * u + v * v := Int.add_nonneg (sqNonneg u) (sqNonneg v)
  have hAe : 2 * A * e = 2 * (A * e) := by grind
  rw [expand, hAe]
  generalize a * u + b * v = X at bound
  generalize u * u + v * v = Y at herr pos
  generalize A * e = Z at bound
  generalize e * e = E2 at herr
  omega

/-- Partial tail n(K+1) + ... + n(K+m). -/
def tailSum (n : Nat → Int) (K : Nat) : Nat → Int
  | 0 => 0
  | m + 1 => tailSum n K m + n (K + m + 1)

theorem tailInvariant (n : Nat → Int) (p q : Int) (K : Nat)
    (hstep : ∀ k, q * n (k + 1) ≤ p * n k) :
    ∀ m, (q - p) * tailSum n K (m + 1) + p * n (K + m + 1) ≤ q * n (K + 1) := by
  intro m
  induction m with
  | zero =>
    have e : (q - p) * tailSum n K (0 + 1) + p * n (K + 0 + 1) = q * n (K + 1) := by
      simp [tailSum]; grind
    omega
  | succ m ih =>
    have hs := hstep (K + m + 1)
    have e : (q - p) * tailSum n K (m + 1 + 1) + p * n (K + (m + 1) + 1)
        = (q - p) * tailSum n K (m + 1) + q * n (K + m + 1 + 1) := by
      simp only [tailSum]; grind
    rw [e]
    have e2 : K + m + 1 + 1 = K + (m + 1) + 1 := by omega
    generalize (q - p) * tailSum n K (m + 1) = X at ih ⊢
    generalize q * n (K + m + 1 + 1) = Y at hs ⊢
    generalize p * n (K + m + 1) = Z at hs ih
    omega

theorem geometricDecay (n : Nat → Int) (p q : Int) (hp : 0 ≤ p) (hq : 0 ≤ q)
    (hstep : ∀ k, q * n (k + 1) ≤ p * n k) :
    ∀ k, q ^ k * n k ≤ p ^ k * n 0 := by
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
    have hqk : 0 ≤ q ^ k := Int.pow_nonneg hq
    have s1 : q ^ k * (q * n (k + 1)) ≤ q ^ k * (p * n k) := Int.mul_le_mul_of_nonneg_left (hstep k) hqk
    have s2 : p * (q ^ k * n k) ≤ p * (p ^ k * n 0) := Int.mul_le_mul_of_nonneg_left ih hp
    have e1 : q ^ (k + 1) * n (k + 1) = q ^ k * (q * n (k + 1)) := by rw [Int.pow_succ]; grind
    have e2 : q ^ k * (p * n k) = p * (q ^ k * n k) := by grind
    have e3 : p * (p ^ k * n 0) = p ^ (k + 1) * n 0 := by rw [Int.pow_succ]; grind
    rw [e1]; rw [e2] at s1; rw [← e3]; exact Int.le_trans s1 s2

/-- T3, scaled form: with r = p/q this is S_tail <= r^(K+1) n(0) / (1 - r) for every partial tail. -/
theorem neumannTail (n : Nat → Int) (p q : Int) (K m : Nat) (hp : 0 ≤ p) (hpq : p < q)
    (hn : ∀ k, 0 ≤ n k) (hstep : ∀ k, q * n (k + 1) ≤ p * n k) :
    (q - p) * q ^ (K + 1) * tailSum n K m ≤ q * (p ^ (K + 1) * n 0) := by
  have hq : 0 ≤ q := by omega
  have hqK : 0 ≤ q ^ (K + 1) := Int.pow_nonneg hq
  have base : (q - p) * tailSum n K m ≤ q * n (K + 1) := by
    cases m with
    | zero => simp [tailSum]; exact Int.mul_nonneg hq (hn _)
    | succ m =>
      have := tailInvariant n p q K hstep m
      have hpn : 0 ≤ p * n (K + m + 1) := Int.mul_nonneg hp (hn _)
      generalize (q - p) * tailSum n K (m + 1) = X at this ⊢
      generalize p * n (K + m + 1) = Z at this hpn
      omega
  have scaled := Int.mul_le_mul_of_nonneg_left base hqK
  have decay := Int.mul_le_mul_of_nonneg_left (geometricDecay n p q hp hq hstep (K + 1)) hq
  have e1 : (q - p) * q ^ (K + 1) * tailSum n K m = q ^ (K + 1) * ((q - p) * tailSum n K m) := by grind
  have e2 : q ^ (K + 1) * (q * n (K + 1)) = q * (q ^ (K + 1) * n (K + 1)) := by grind
  rw [e1]; rw [e2] at scaled; exact Int.le_trans scaled decay

/-- T4, real input: Q = a a^T + b b^T; any 3x3 minor (rows r, columns c) vanishes, so rank Q <= 2. -/
theorem detectorRankTwo (x1 x2 x3 y1 y2 y3 z1 z2 z3 w1 w2 w3 : Int) :
    let q := fun (x y z w : Int) => x * z + y * w
    q x1 y1 z1 w1 * (q x2 y2 z2 w2 * q x3 y3 z3 w3 - q x2 y2 z3 w3 * q x3 y3 z2 w2)
    - q x1 y1 z2 w2 * (q x2 y2 z1 w1 * q x3 y3 z3 w3 - q x2 y2 z3 w3 * q x3 y3 z1 w1)
    + q x1 y1 z3 w3 * (q x2 y2 z1 w1 * q x3 y3 z2 w2 - q x2 y2 z2 w2 * q x3 y3 z1 w1) = 0 := by
  intro q
  simp only [q]
  grind

/-- T4, complex input: H_ij = conj(u_i) u_j; the principal 2x2 minor |u_i|^2 |u_j|^2 - |H_ij|^2 vanishes. -/
theorem hermitianRankOne (ai bi aj bj : Int) :
    (ai * ai + bi * bi) * (aj * aj + bj * bj)
      - ((ai * aj + bi * bj) * (ai * aj + bi * bj) + (ai * bj - bi * aj) * (ai * bj - bi * aj)) = 0 := by
  grind

/-- T5. Two-port E1 = t x1 + r x2, E2 = r x1 + t x2 with scale S (t, r stand for t/S, r/S). -/
theorem splitterPassive (tr ti rr ri x1r x1i x2r x2i S : Int)
    (hcoef : tr * tr + ti * ti + rr * rr + ri * ri ≤ S * S) (horth : tr * rr + ti * ri = 0) :
    ((tr * x1r - ti * x1i + rr * x2r - ri * x2i) * (tr * x1r - ti * x1i + rr * x2r - ri * x2i)
      + (tr * x1i + ti * x1r + rr * x2i + ri * x2r) * (tr * x1i + ti * x1r + rr * x2i + ri * x2r)
      + (rr * x1r - ri * x1i + tr * x2r - ti * x2i) * (rr * x1r - ri * x1i + tr * x2r - ti * x2i)
      + (rr * x1i + ri * x1r + tr * x2i + ti * x2r) * (rr * x1i + ri * x1r + tr * x2i + ti * x2r))
    ≤ (S * S) * (x1r * x1r + x1i * x1i + x2r * x2r + x2i * x2i) := by
  have expand :
      (tr * x1r - ti * x1i + rr * x2r - ri * x2i) * (tr * x1r - ti * x1i + rr * x2r - ri * x2i)
      + (tr * x1i + ti * x1r + rr * x2i + ri * x2r) * (tr * x1i + ti * x1r + rr * x2i + ri * x2r)
      + (rr * x1r - ri * x1i + tr * x2r - ti * x2i) * (rr * x1r - ri * x1i + tr * x2r - ti * x2i)
      + (rr * x1i + ri * x1r + tr * x2i + ti * x2r) * (rr * x1i + ri * x1r + tr * x2i + ti * x2r)
      = (tr * tr + ti * ti + rr * rr + ri * ri) * (x1r * x1r + x1i * x1i + x2r * x2r + x2i * x2i)
        + 4 * (tr * rr + ti * ri) * (x1r * x2r + x1i * x2i) := by grind
  rw [expand, horth]
  have hN : 0 ≤ x1r * x1r + x1i * x1i + x2r * x2r + x2i * x2i :=
    Int.add_nonneg (Int.add_nonneg (Int.add_nonneg (sqNonneg _) (sqNonneg _)) (sqNonneg _)) (sqNonneg _)
  have := Int.mul_le_mul_of_nonneg_right hcoef hN
  simpa using this

#print axioms powerPerturbation
#print axioms neumannTail
#print axioms detectorRankTwo
#print axioms hermitianRankOne
#print axioms splitterPassive
end Neuro3D
