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
