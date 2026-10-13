# Profile: nested EEGNet comparator on GPU (H2)

- **Identity:** EXP-006-EEGNET-GPU-H2-20261013-001
- **Written:** 2026-10-13, before any execution of this profile. Committed and pushed before the first GPU ticket.
- **Parent protocol:** `../PREREGISTRO-EEG.md` (fixed 2026-10-10, commit 69db25c), frozen runner `../run_nested_comparators_v1.py` (sha256 `3215b859...122a`) and analyzer `../analyze_comparators_v1.py` (sha256 `ac621a9f...3625`), both from commit 7e239aa. None of these files is modified.
- **Authorization:** GPU use authorized by the owner (Fran) for this hypothesis. All GPU work goes through the owner's FIFO queue (`gpuq.py run`), one small ticket at a time.
- **Predecessors kept as they are:** EXP-006-EEGNET-PILOT-20261012-001 and -002. Both were CPU pilots and both stopped at the 700 MiB host-RAM floor. Their metrics are NULL. Neither one is reused for timing or results.

## 1. What is unchanged

The successor runner `run_nested_eegnet_gpu_v2.py` imports v1 rather than copying or editing it, and checks v1's hash before it runs. The following come from v1 and the preregistration without any change:

- Data: `S###.npz` fields `Xtr`, `ytr`, `run` from the owner's local workspace (`D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/data`). The hidden Kaggle `Xte` is never read. Raw EEG and labels are never copied into the repository.
- Outer LORO folds (50) and inner LORO folds (64) come from `nested_bench.py`. Each run checks them for exact equality with the saved optical folds (`work/nested/raw/full/S###.npz`) and tests for leakage.
- Architecture: EEGNet-8,2 from `bench.py` (F1=8, D=2, F2=16, p=0.5). Input is 8x1250, scaled by the training-only per-channel standard deviation. Training uses AdamW and BCE with logits.
- Grid: 36 configurations = lr {1e-3, 3e-3, 1e-2} x batch {16, 32} x weight decay {1e-3, 1e-2} x snapshot epoch {30, 60, 90}. These are 12 trajectories of 90 epochs per training set. The default is lr 3e-3, batch 32, wd 1e-2, epoch 60.
- Seeds: `torch.manual_seed(k)` for the outer fold k and `100 + 10k + j` for inner fold j. Initial weights and mini-batch order are drawn from the seeded CPU generator, exactly as in v1.
- Selection: lowest pooled internal-validation BCE (`v1.choose`). An exact tie, or no valid inner fold, falls back to the default. N1 is selected before the external test labels are read.
- Stored NPZ schema: identical to v1, so the frozen analyzer reads it unchanged. One extra key, `gpu_meta`, holds timing and environment.

## 2. Declared deviation

| Item | Preregistration | This profile |
|---|---|---|
| Device | CPU only, 2 threads, max 2 processes, no GPU or queue | **CUDA (RTX 3090) when available**, 1 process, 2 CPU threads, through the gpuq FIFO queue |
| Dropout masks | CPU generator | CUDA generator (seeded by the same `torch.manual_seed`) |
| Numerics | CPU float32 kernels | cuDNN/cuBLAS float32 kernels |

Determinism settings recorded in every output: `cudnn.deterministic=True`, `cudnn.benchmark=False`, `torch.use_deterministic_algorithms(True, warn_only=True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`. Some GPU kernels may still be nondeterministic. Because dropout and the kernels differ, **the results may differ numerically from a CPU run of the same protocol.** A CPU run with the same seeds would not reproduce them bit for bit. The torch, CUDA and cuDNN versions, the GPU name and the source hashes are stored in each subject's `gpu_meta` and in `results/`.

The only re-implemented function is `fit_eegnet`, which moves the model and tensors to the device. Its arithmetic is otherwise the same. Initial weights are created on CPU and then moved to the device.

## 3. Three-hour policy (preregistration section 8)

1. **Measure first.** Ticket `neuro3d:eegnet-h2-pilot` runs the first complete external fold of S001 with `--pilot`, covering all 36 configurations. The fold has 24 trainings and 6 480 optimizer steps. Its NPZ is marked `pilot` and is never analysed.
2. **Project.** `project_cost_v2.py` multiplies the measured wall seconds per optimizer step by the exact step count of every training of all 17 subjects (405 000 steps in total, computed from the `run` field only), then adds 60 s per subject ticket. The rate and the projection are written to `results/cost-projection.json` before the full run starts.
3. **Decide mechanically.**
   - If the projected total is 3 h or less, all 17 subjects run, one gpuq ticket per subject, in ascending order.
   - If the projection is above 3 h, the preregistered partial strategy applies. Complete subjects run in ascending identifier order while the cumulative projected cost stays within 3 h. H2 is then evaluated only on those subjects, with the optical line restricted to the same subjects. The result is labelled **"partial"**, and no superiority is claimed for the 17-subject population.
   - The 3 h budget counts our tickets' execution wall time only. Queue waiting does not count. One sequential process is used, a stricter setting than the preregistered 2 processes. During execution, a subject is not started if the actual elapsed execution time plus its projected cost would exceed 3 h.
4. Pilot outputs are timing only and are never mixed into results. The full S001 run repeats the first fold from scratch.

## 4. Resource limits

- gpuq ticket requests: `--vram 3 --ram 3` (GB). The queue starts a ticket only when the GPU is idle and the VRAM and RAM are free. Other projects' jobs may be ahead of ours, and waiting is expected.
- Inside the runner:
  - Host available RAM is checked every 10 epochs. Below 700 MiB, the runner stops with `HOST_RAM_FLOOR` (the same floor as the CPU pilots).
  - The per-ticket wall-clock limit is 5 400 s (`DEADLINE`).
  - An interrupted subject writes nothing and is reported as incomplete.
- Raw outputs: `D:/PROJECTS/.cognition/neuro3d-closure-20261012/eeg-eegnet-gpu-h2/{pilot,full}/`, outside the repository. Only per-subject accuracies, hashes, timing and the analysis JSON go into `results/`.
- If CUDA is unavailable, or the queue does not free within about 4 h, the outcome is recorded as **BLOCKED**, with the exact reason, in `RESULTS-EEGNET-GPU-H2.md`.

## 5. Analysis and the unchanged H2 decision rule

The frozen `analyze_comparators_v1.py` runs with `--eegnet`. It computes:

- **Primary estimator: N1.** d = optical N1 minus EEGNet N1, per subject.
- A 95% subject bootstrap interval: 10 000 resamples, `default_rng(0)`, percentiles 2.5 and 97.5.
- A two-sided Wilcoxon test (`zero_method="wilcox"`), with Holm adjustment over the preregistered family {H1, H2}.

The decision rule is unchanged:

- **Superior** if the CI lower bound is above 0.
- **Equivalent** if the whole CI lies within [-0.02, +0.02].
- **Inconclusive** otherwise. "Inferior" is used only as a description, when the CI lies entirely below 0.
- If the result is superior but the Holm p is 0.05 or more, the note "Wilcoxon does not confirm" is added.

The secondary estimators (N1b, N2, N3, MEANgrid) are exploratory. H1 (FBCSP) is recomputed from the same frozen raw FBCSP outputs so that Holm covers both hypotheses.

## 6. Scope and limitations carried forward

- These are known subjects, evaluated with within-session LORO on one dataset of 17 subjects and 8 channels. There are no blind or new subjects.
- The optical grid was chosen while the same LORO results were visible, and it includes `free`, a digital unconstrained matrix rather than a realizable unitary mesh. A win for "the optical line" therefore does not show that the physical part is responsible.
- There is one seed per training. GPU numerics deviate from the preregistered CPU device.
- An earlier, unpublished CPU EEGNet attempt from 2026-10-10 exists in the owner's workspace (`neuro3d-audit/eeg/raw/eegnet`, S001 and S002, different runner schema). It is not used for any decision here.
