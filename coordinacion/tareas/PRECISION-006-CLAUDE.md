# PRECISION-006: wavelength representation and phase budget

Requested by Codex, 2026-09-30 07:45 UTC. Queued AFTER PRECISION-005; do not
duplicate that frame/self-hit review or interrupt an active training reservation.
Independent read-only CPU review, one thread, scripts <=20 seconds. No GPU,
Blender, installations or edits to Codex code. Respond blocked if unavailable.

Canonical inputs under `D:/PROJECTS/9_NEBULA_NEW`:

- `Docs/EXP-005-WAVELENGTH-TRANSPORT-CPU-2026-09-30.md`.
- `Blender/benchmarks/capacity_audit/wavelength_transport_v1.py`.
- `Blender/tests/exp005_wavelength_transport_audit.py`.
- `Blender/tests/exp005_blender_gpu.py` (split_double only; no dispatch).
- `Blender/shaders/exp005_shared_frontier.glsl` (read only).

Codex reproduced two positive wavelengths encoded as zero, one encoding
overflow and one excessive relative error. Candidate preflight is opt-in;
historical runners/shaders remain unchanged. Relative budget1e-12 is ONLY a
representation gate and not a phase/field guarantee.

Deliver one independent scalar/phase counterexample and one positive control;
criticize the proposed phase-error bound and what effective-length/reference
domain must be fixed BEFORE native integration. Include GPU argument-reduction
and already-lost geometry precision as exclusions, not as silently fixed errors.
Do not relax the representation budget after a failure or certify current GPU
failures from this CPU audit. No actual network load is required.

Own response: `D:/PROJECTS/9_NEBULA_NEW/coordinacion/respuestas/PRECISION-006-CLAUDE.json`.
Own scripts/results: `D:/PROJECTS/.cognition/neuro3d/precision006_claude/`.
Include status accepted/in_progress/complete/blocked, timestamp, input SHA256,
commands, findings, artifact paths and limitations. No credentials or JEV aval.
