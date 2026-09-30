# Wavelength transport must fail closed

CPU-only candidate, 30 September 2026. This work uses the continuity and focused
feature-testing workflows to retain counterexamples and test an independent,
opt-in preflight. It does not alter historical shaders, runners or raw ABI gates.
No GPU, Blender, render, SDK installation or peer writer was executed.

## Reproduced input failure

The frozen `pack_frontier` accepts positive finite wavelengths without requiring
that the actual two-float32 hi/lo encoding preserves them. A CPU audit of the
real `split_double` transport found the following in eight adversarial inputs:

- 1e-46 and 1e-300 Blender units encode as hi=lo=0.
- 1e39 is accepted by raw preflight but its encoding raises `OverflowError`.
- 1e-40 encodes with relative discrepancy 5.389888524e-6.
- .125, 1e-6, 1e-30 and 1e30 remain positive and satisfy the prospective
  representation budget of 1e-12.

These extremes are robustness tests, not a claim that the project uses such
wavelengths in its current validated fixtures. No historical GPU failure is
inferred. The unchanged shared shader divides by reconstructed hi+lo when
calculating propagation phase, so rejecting a collapsed wavelength is required
before dispatch rather than relying on a later output check.

## Opt-in candidate

`wavelength_transport_v1.checked_wavelength` requires an explicit relative
representation budget. It validates the original scalar, invokes the actual
frozen splitter, rejects encoding overflow/nonfinite/zero, and rejects excessive
relative discrepancy. It preserves the encoded hi/lo values without changing
the wavelength or silently substituting a default. No existing runner imports it.

The eight-input audit rejects four problematic inputs and retains all results.
Five focused regression tests pass, including invalid scalars, explicit/missing
budgets, exact controls and underflow/overflow counterexamples.

## Crucial limit: this is not an optical phase certificate

A small relative wavelength error can still produce unacceptable phase error
over a long path. In exact real arithmetic, with wavelength lambda and decoded
lambda_prime, an effective path bounded by L_max contributes at most

`2*pi*L_max*abs(lambda_prime-lambda)/(lambda*lambda_prime)`

to unwrapped phase error from wavelength encoding alone. This excludes geometry
quantization, path-length accumulation, initial field/reference error and GPU
phase range reduction. A future native contract needs a predeclared path/phase
budget and rejection domain; acceptance by this helper is not permission to run
the full positive-finite wavelength domain. No length is computed by this helper.

## Retained evidence and reproduction

Final manifest includes seven source hashes:
`D:/PROJECTS/.cognition/neuro3d/exp005_wavelength_transport_20260930_0744.json`.
SHA256 `ef6b5978be1d72d0d937744d3897ab63e55adf4b99363d931e0c6d23b513c3e6`.
The initial report0741 is retained; report0744 adds dependency hashes without
changing the numerical experiment.

```powershell
python -B -m unittest discover -s Blender/tests -p test_exp005_wavelength_transport.py
```

Next: independent criticism after PRECISION-005, followed by a new prospective
transport/phase contract before any native integration. New GPU authorization,
resource guard and exclusive reservation remain mandatory. JEV is blocked by
security review; this is local evidence without remote approval.
