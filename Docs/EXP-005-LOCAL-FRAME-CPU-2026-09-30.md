# Precision audit and local-coordinate transport prototype

Status: CPU-only preparation, 30 September 2026. No GPU compilation, Blender
execution, RT acceleration, throughput benefit or larger-network gate is claimed.
The frozen Precision V3 candidate and historical shaders/runners are unchanged.

## Finding: transport changes the complex optical field

The auditor uses the actual `pack_frontier` and `texture_data` hi/lo transport,
reconstructs all triangle/source/optical inputs, then traces both complete scenes
with the triangle oracle. It never supplies computed hits or a matrix to a GPU.

The 64 synthetic float64 cases cover direct and reflected paths, gaps of
1e-8 and 2 Blender units, four world offsets, two scales and two wavelengths.
Two cases exceed the existing complex-field tolerance of 1e-4 despite retaining
their ray counts. Worst input discrepancy: 3.4924596548e-10 units; worst field
discrepancy: 0.0014629179488. A unit-intensity detector alone would conceal it.

These are CPU transport counterexamples, not measured GPU failures. They do not
certify Blender float32 mesh precision. Error against ideal, unrounded placement
is recorded separately from transport error.

## Prototype: translate the entire scene into one local frame

`local_frame_v1.py` translates every source, triangle and terminal reference by
the same first-source origin before transport. It leaves wavelength, directions,
complex source fields, optical coefficients, identities and faces unchanged.
Explicit frame metadata accompanies the result; local data must not be labelled
as raw Blender world-coordinate readback.

Both original and translated scenes must satisfy the existing ABI bounds.
The prototype neither expands those bounds nor mutates its input. It cannot
recover information already lost in world-coordinate export or Blender float32.
It is opt-in and is not imported by a GPU runner.

On the same 64 cases, the translated scene has zero transport failures, zero
world/local field-invariance failures and zero rejected cases. Maximum transport
field discrepancy: 1.3877787808e-17; measured world/local field drift: zero.
This evidence is restricted to these direct/reflected fixtures, not arbitrary
multiple sources, branching networks, grazing incidence or general coordinates.

## Independent review and strengthened gates

Claude delivered `PRECISION-004-CLAUDE.json` at 07:19:56 UTC. Codex verified its
three input hashes, six script hashes and presence of twelve artifacts. This
does not mean every reported number has been independently reproduced.

The review flags grazing self-intersections after removing the origin bias,
float32 quantization versus terminal angular tolerance, residual near-surface
resolution and insufficient coverage of the terminal threshold. These findings
keep generalization blocked; simply removing the bias is not a general repair.

Codex independently reproduced the terminal-coverage finding in its own CPU
audit. Two supplemental scenes, with terminal angles 3.0e-5 and 6.3e-5 radians,
agree with the complete-scene oracle. They reject four altered tolerances that
survive the original four controls. The frozen V3 runner is not silently amended;
these supplemental gates require a new prospective runtime contract.

## Retained evidence

- World transport: `D:/PROJECTS/.cognition/neuro3d/exp005_precision_transport_20260930_0716.json`,
  SHA256 `c6aa840760e2fdc02e5669badd592052854bc49439f69abc6a0f350f206ae587`.
- Local frame: `D:/PROJECTS/.cognition/neuro3d/exp005_local_frame_cpu_20260930_0719.json`,
  SHA256 `1febbca4d6360d2140e5784e8e1dbf3d3d619fd008fa4e442c6c12c973484d62`.
- Modal supplement: `D:/PROJECTS/.cognition/neuro3d/exp005_modal_coverage_20260930_0731.json`,
  SHA256 `97eba25ae63d84fa141b452831491ed9796d54b1229878312a9ac8b5d44de9af`.
- Peer response read: SHA256
  `db6678b71d5998eace590117ebe946f9ddf586989a0544a2ed37cfa2e294ab25`.

Initial complete CPU suite: 188 tests, 13.314 seconds. After adding the modal
supplement: eight focused tests pass, and the complete EXP-005 suite passes
190 tests in 8.848 seconds.

Reproduce without GPU/Blender:

```powershell
python -B -m unittest discover -s Blender/tests -p test_exp005_precision_transport.py
```

## Next acceptance steps

1. Independent CPU criticism of frame semantics, reference phase, multiple
   sources and grazing self-hit controls; task `PRECISION-005-CLAUDE`.
2. Retain a concrete self-hit adversary and specify safe handling. Object-wide
   self-exclusion is only permissible for a certified planar primitive, never
   for arbitrary curved or multi-surface objects that can legitimately re-hit.
3. Define frame metadata, bounds, rejection rules and supplemental gates in a
   new prospective contract before changing or compiling a native runner.
4. GPU compilation/runtime requires a new explicit window, exclusive gpuq
   reservation and fail-closed resource/deadline guard. No such load ran here.

JEV remains security-blocked. Decisions here are identified local fallback,
not remote approval. Compiled U/GEMM is a separate backend and does not replace
the project's inference directly from scene geometry.
