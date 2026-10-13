# Results: nested EEGNet comparator on GPU (H2)

**Identity:** EXP-006-EEGNET-GPU-H2-20261013-001
**Profile:** `PROFILE-EEGNET-GPU-H2.md`, committed and pushed before execution in 4dc75a8. The cost projection and driver were committed in a45f32f, before the full run.
**State on 2026-10-13: BLOCKED.** 10 of 17 subjects are complete. H2 has not been evaluated.

## 1. Blocking reason (exact)

At 2026-10-13T06:39:36Z the owner authorized a GPU pause of every queue job whose name starts with `neuro3d`, `opticneuro` or `optic-neuro`. The pause is recorded in `D:/PROJECTS/.cognition/gpu_queue/pause_registry.json`:

- `active: true`
- `reason: "Villa Anzuelo voices have explicit GPU priority until completion"`
- `manual_resume_only: true`
- checkpoint: `D:/PROJECTS/.cognition/neuro3d-gpu-pause-20261013-villa/checkpoint.json`

The pause suspended two of our processes, and their threads remain suspended:

- the per-subject driver `drive_full_v2.py` (pid 47232);
- the waiting gpuq ticket `neuro3d:eegnet-h2-S012` (pid 19256), which was enqueued at 06:11:59Z and never started. Its ticket file was moved to the pause folder's `deferred_tickets/`.

This agent did not resume, restart or kill any process. Doing so would override an explicit owner decision. No GPU work ran outside the queue.

## 2. What was executed

| Step | Result |
|---|---|
| CUDA | Available. torch 2.6.0+cu124, CUDA 12.4, cuDNN 90100, NVIDIA GeForce RTX 3090, Python 3.13.7. |
| Determinism | `cudnn.deterministic=True`, `cudnn.benchmark=False`, `use_deterministic_algorithms(True, warn_only=True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`. No determinism warnings were raised in any subject. |
| Pilot (ticket `neuro3d:eegnet-h2-pilot`) | S001, first external fold, all 36 configurations: 24 trainings, 6 480 steps, **63.8 s** wall time (50.2 s of training). Peak CUDA allocation was 101 MiB. NPZ sha256 `5ea07c97...2612`, timing only, never analysed. The earlier CPU pilots stopped on the RAM floor and gave no timing. |
| Projection (`results/cost-projection.json`) | 0.00984 s per step x 405 000 steps + 60 s per ticket = **1.39 h for all 17 subjects**, within the 3 h limit. The preregistered rule therefore selected the **complete** 17-subject run, not the partial strategy. |
| Full run (one gpuq ticket per subject) | 10 subjects are complete: S001-S007 and S009-S011. Every ticket exited with rc=0. Execution time was **1 037.6 s (0.29 h)**, against a projected 0.79 h for the same subjects. Queue waits between tickets ran from 10 to 54 min, because other projects' jobs were interleaved. |
| Remaining | S012, S014 and S016-S020: 7 subjects, about 25 380 steps each, roughly 13 min of GPU time in total at the measured rate. |
| Host RAM | The minimum available host RAM seen inside the runner was 2 439 MiB. The 700 MiB floor was never reached. |

Per-subject execution seconds, step counts and raw-NPZ sha256 hashes are recorded in `results/execution-status.json`. The raw NPZ outputs (logits, fold indices and labels) stay in the owner's local workspace at `D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-eegnet-gpu-h2/`. They are not redistributed, and `Xte` was never read.

## 3. H1 / H2

- **H2 (optical N1 vs EEGNet N1): NOT EVALUATED (BLOCKED).** No accuracy, estimator or contrast was computed or inspected for the 10 completed subjects. This avoids an interim look and optional stopping.
  - The interruption is not the preregistered 3 h partial rule, which did not trigger. A 10-subject analysis now would therefore not be a preregistered "partial" result.
  - H2 must be evaluated once, on all 17 subjects, after the GPU pause ends.
- **H1 (optical N1 vs FBCSP N1):** unchanged from the published `Docs/closure-20261012/eeg-comparison.json`:
  - "superior": difference +0.0499, 95% CI [0.0148, 0.0868], Wilcoxon p = 0.0245;
  - the Holm p of 0.0489 was computed with H2 set to p = 1, as the family rule requires while H2 is unavailable;
  - the final Holm value will be recomputed over {H1, H2} once H2 exists.

## 4. How to finish once the owner resumes the Neuro3D GPU queue

When the owner's resume helper restores the deferred S012 ticket and resumes pid 47232 and pid 19256, the driver continues by itself through S020. If the suspended processes are instead discarded, rerun the driver (it skips completed subjects). Never run two drivers at the same time.

```
python Benchmarks/eeg-motor-imagery/comparativa-anidada/gpu-h2/drive_full_v2.py \
  --projection Benchmarks/eeg-motor-imagery/comparativa-anidada/gpu-h2/results/cost-projection.json \
  --data D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/data \
  --optical-raw D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/raw/full \
  --out D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-eegnet-gpu-h2/full \
  --journal D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-eegnet-gpu-h2/full-journal.jsonl
python Benchmarks/eeg-motor-imagery/comparativa-anidada/analyze_comparators_v1.py \
  --optical-raw D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/raw/full \
  --fbcsp D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-fbcsp-full \
  --eegnet D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-eegnet-gpu-h2/full \
  --out Benchmarks/eeg-motor-imagery/comparativa-anidada/gpu-h2/results/eeg-comparison-h1h2-gpu.json
python Benchmarks/eeg-motor-imagery/comparativa-anidada/gpu-h2/summarize_v2.py \
  --raw D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-eegnet-gpu-h2/full \
  --analysis Benchmarks/eeg-motor-imagery/comparativa-anidada/gpu-h2/results/eeg-comparison-h1h2-gpu.json \
  --published Docs/closure-20261012/eeg-comparison.json \
  --out Benchmarks/eeg-motor-imagery/comparativa-anidada/gpu-h2/results/eegnet-gpu-subjects.json
```

The 3 h budget still has 2.71 h of execution time left, so the complete plan stands. The H2 decision rule is unchanged (profile section 5).

## 5. Deviations and limitations

- **Device:** GPU instead of the preregistered CPU. Dropout masks come from the CUDA generator, and the cuDNN/cuBLAS float32 kernels differ from the CPU ones. Results may differ numerically from a CPU run, and a GPU rerun may not be bitwise identical. The run used one sequential process, through the gpuq FIFO queue.
- **Scope of any future H2 result:**
  - known subjects only, within-session LORO, one dataset of 17 subjects with 8 channels, and no blind data;
  - the optical grid was chosen while the same LORO results were visible, and it includes `free`, a digital unconstrained matrix rather than a realizable unitary mesh. A win for the optical line therefore does not show that the physical mesh is responsible;
  - one seed per training.
- **Prior unpublished CPU outputs:** an earlier CPU EEGNet attempt from 2026-10-10 (`neuro3d-audit/eeg/raw/eegnet`, S001 and S002, different runner schema) exists in the owner's workspace. It is not used here.
