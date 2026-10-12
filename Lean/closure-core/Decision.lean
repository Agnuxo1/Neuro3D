import Std

/- T1 is purely an order lemma. No field arithmetic or floating-point
   assumption is needed. The two mixed transitivity instances explicitly
   state its order requirements; valid real/rational orders satisfy them.
   This lemma does not prove that a producer's boxes enclose its outputs. -/
namespace Neuro3D

theorem separatedBoxes {α ι : Type} [LE α] [LT α]
    [Trans (fun x y : α => x ≤ y) (fun x y : α => x < y) (fun x y : α => x < y)]
    [Trans (fun x y : α => x < y) (fun x y : α => x ≤ y) (fun x y : α => x < y)]
    (power lower upper : ι → α) (winner : ι)
    (lowerValid : ∀ i, lower i ≤ power i)
    (upperValid : ∀ i, power i ≤ upper i)
    (separation : ∀ i, i ≠ winner → upper i < lower winner) :
    ∀ i, i ≠ winner → power i < power winner := by
  intro i different
  exact trans (trans (upperValid i) (separation i different)) (lowerValid winner)

#print axioms separatedBoxes
end Neuro3D
