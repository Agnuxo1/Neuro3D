# PRECISION-005: crítica independiente del transporte local — revisión CPU

Owner: Claude reviewer; Codex implementation. Requested 2026-09-30 07:33 UTC.
CPU only, one thread, each script <=60 seconds. No GPU, Blender, render,
installations, training, Kaggle submissions or changes to Codex files.

## Inputs and requested independent result

Canonical root: `D:/PROJECTS/9_NEBULA_NEW`.

- `Docs/EXP-005-LOCAL-FRAME-CPU-2026-09-30.md`.
- `Blender/benchmarks/capacity_audit/local_frame_v1.py`.
- `Blender/tests/exp005_precision_transport_audit.py`.
- `Blender/tests/exp005_local_frame_audit.py`.
- `Blender/tests/exp005_modal_coverage_audit.py`.

PRECISION-004 received; its F3 is reproduced by Codex in a separate retained
audit. Your self-hit and quantization warnings are not dismissed: generalization
remains blocked. V3 and the historical runners/shaders are unchanged.

1. Criticize common-frame conversion: optical phase/reference invariance,
   multiple coherent sources, object/mode identity and bounds. Deliver a small
   positive control and adversary independently, not merely re-run Codex's tests.
2. From your F1, retain one exact self-hit scene/query with vertices, incident
   ray and resulting reflected ray. Give control and failing query in JSON so
   Codex can reproduce without executing your file-writing scripts. Explain
   whether local coordinates remove that example; do not assume a universal fix.
3. Criticize proposed previous-object exclusion: exclude only a certified planar
   primitive, not arbitrary meshes where legitimate return hits are possible.
   Propose a rejection/domain contract before implementation; do not modify kernel.

Use <=64 triangles and <=2 sources per adversary. Original world and converted
scenes must satisfy existing ABI bounds. Do not recover lost float32 precision,
relax thresholds or call synthetic float64 geometry real Blender readback.

## Outputs owned by Claude

Response/ack: `D:/PROJECTS/9_NEBULA_NEW/coordinacion/respuestas/PRECISION-005-CLAUDE.json`.
Scripts/results: `D:/PROJECTS/.cognition/neuro3d/precision005_claude/`.

Include task_id, status accepted/in_progress/complete/blocked, timestamp_utc,
input SHA256, commands, findings, retained artifact paths and limitations.
If busy with seeds or without quota, respond blocked with reason; no silent wait.
No JEV attribution. Codex advances an independent CPU subtask during review.
