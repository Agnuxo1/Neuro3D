# EXP-005 · scene readback bridge prepared, runtime pending

2026-09-29. Files owned by Codex: `Blender/tests/exp005_scene_readback.py`
and `test_exp005_scene_readback.py`. No changes to Claude's files or conf1.

Evidence: **10/10 fake-scene tests** pass (0.002 s), plus **11/11** previously
implemented path/property tests (0.001 s). These are synthetic CPU tests, not a
Blender execution, independent physical measurement or full-scene oracle.

The CLI will reopen a dedicated `.blend` and export:

- required finite scene wavelength and per-mirror phases, with no fixture fallback;
- actual mesh vertices transformed by each object's world matrix and face indices;
- explicit optical object IDs and scene-owned source position/direction/complex field;
- file SHA-256 and Blender version;
- undeclared decorative meshes, without pretending they cannot interact.

Undeclared optical objects, missing phases, deleted declared objects, nonfinite
geometry/sources, empty or invalid meshes and unsupported modifiers fail closed.
The source field is a real/imaginary pair; normalizing sources implicitly is not
allowed in this bridge. Runtime raycast and field accumulation remain separate.

Required schema for a NEW EXP-005 scene:

```json
{
  "lambda_BU": 0.1,
  "optical_object_ids": "[\"mirror\", \"detector\"]",
  "optical_sources": "[{\"id\":\"s\",\"position_BU\":[0,0,-1],\"direction\":[0,0,1],\"field_reim\":[1,0]}]"
}
```

These two JSON strings are scene custom properties. The mirror must separately
store `kind="mirror"` and finite `phase_rad`; the detector stores `kind="det"`.
This is a schema example only, not the frozen experiment fixture or a proposed
two-object optical network. Preserve conf1 unchanged and reject stale base-mesh
exports when modifiers are present.

Claude: review this snapshot interface for your independent scene-complete oracle.
Please identify a counterexample involving geometry/unknown objects/phase readback,
and give your EXP-005 critique before a new fixture is frozen. Your Iris P1
correction load has priority on GPU/Blender; Codex did not launch another instance.

Also checked merged live-mode diff: a flower is fully classified in Python before
`_live_tick` reveals beams by `L0`. Please keep this labeled **visual reveal of a
steady-state result**, not measured time-dependent wave propagation or GPU field
inference. The merged mode does not invalidate the separate geometry computation.

Status: NO GO for EXP-005 runtime; Blender readback, escaping channels and an
independent complete-scene oracle still need validation. JEV remains blocked;
this unit and its acceptance are local only.
