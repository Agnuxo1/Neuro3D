# EXP-005 · first CPU unit, not runtime acceptance

2026-09-29. Owner: Codex. Files: `Blender/tests/exp005_scene_properties.py` and
`test_exp005_scene_properties.py`.

Executed: `python -B Blender/tests/test_exp005_scene_properties.py`.
Result: **11/11**, 0.001 s reported by unittest, no Blender/GPU or scientific stack.

The decoder requires a positive finite `lambda_BU` and explicit finite phases
for every mirror. Missing values, unknown roles/objects, incompatible events,
invalid distances and incomplete paths fail closed. Each supplied path preserves
the coefficient, incident field and outgoing field at every hit. The snapshot
is immutable after decoding. This is digital Python arithmetic on synthetic
inputs, not scene readback or a scene-complete oracle.

A contract correction was exposed by a two-hit synthetic counterexample:
perturbing one mirror's phase by 0.1 multiplies a path hitting it twice by
`exp(0.2i)`, not `exp(0.1i)`. G1 now counts hits; if the frozen geometry permits
at most one, the eventual trace must demonstrate that restriction.

Claude: independently check the sign/reflection convention and repeated-hit
case, then critique EXP-005's remaining gates. Please propose a standalone
complete-scene oracle without importing this consumer. No changes to conf1 or
your Iris worktree are requested. Runtime, escape ledger and gate freezing remain
pending. No decision is attributed to JEV; its consultation remains blocked.
