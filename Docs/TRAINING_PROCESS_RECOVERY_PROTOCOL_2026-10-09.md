# Own training interruption and deterministic recovery: frozen protocol

Recovery must preserve an interrupted optimization trajectory, including native geometry coordinates and Adam moments. The checkpoint is written to a unique file, flushed, fsynced, and atomically replaced. Its identity binds the outer profile, original training protocol and source pins. A hash identifies bytes rather than authorizes arbitrary state.

Run an uninterrupted baseline, then terminate only a newly spawned owned training process after its checkpoint has committed 12 updates. That interrupted process must have a nonzero termination code and no completed scientific result. A third fresh process loads the preserved checkpoint, repeats the full continuous original-family proof, and recomputes all 12 previous updates deterministically before trusting the optimizer state. It then completes the original 60 updates.

Acceptance requires all 61 coordinates and losses to equal the uninterrupted run exactly, all 150 predictions to agree and power difference at most 1e-11. The actual resumed worker must reject four checkpoint adversaries: modified optimizer data with an invalid hash, stale profile identity, truncated bytes, and forged optimizer data with a self-consistent hash. The last case is rejected by deterministic replay. Original checkpoint bytes must remain unchanged.

Three meaningful software controls cover atomic round-trip, invalid identity/integrity/truncation, and a forged state that has a recomputed valid hash. A fresh whole-family proof and final scene reconstruction are counted for every complete worker. Limits are 300 seconds per stage, 1,000 seconds total, 4,000 MiB initial RAM, 2,500 MiB floor, 1,500 MiB owned RSS and 128 MiB evidence. No GPU is required for these checkpoint semantics.

[Profile](research/training_recovery_profile_2026-10-09.json) and [authorization](research/training_recovery_registration_2026-10-09.json) are published and byte-verified before any actual interruption. External/IPFS remains pending without identifiers.

This is research-worker process recovery. It does not yet establish an installed Blender resume interface, survival of a whole Blender host crash, operating-system or power-loss durability, physical fidelity, or external independent reproduction.

## Attempt 01: metadata failure before the recovery stages

Frozen `6534318d8fa61814cc5237440d5b82d0e0438a73`, 38 pins published and byte-verified before execution. The uninterrupted prerequisite worker failed in 99.8353 seconds while constructing its final result: the optimizer checkpoint identity had shadowed the affine-expression certificate identity, causing `KeyError: status`. Progress and atomic checkpoints are preserved, but there is no completed scientific result and no actual interruption/resume stage yet. The primary metric remains null. [Evidence](validation/training-recovery-2026-10-09/attempt01/evidence_index.json).

The [prospective v2 profile](research/training_recovery_profile_v2_2026-10-09.json) gives the affine and checkpoint identities distinct names. Optimization, native quantization, crash step, four adversaries and every acceptance/resource gate are unchanged. [Authorization](research/training_recovery_registration_v2_2026-10-09.json) and the revised source pins must be published and byte-verified before execution.

## Attempt 02: actual interruption and recovery passed

Frozen `8311fc8a2053dc6bcebf03c6c9a6235dd1567e34`, profile SHA `b43e881e6bf4ab7798a6b713c496045555ea8eff97dd078deedd65bbd268c3b8`, 40 pinned sources published and byte-verified before execution. The uninterrupted process completes in 96.8763 seconds. The owned interruption process atomically commits checkpoint 12 and is actually terminated with exit code 1 after 75.5020 seconds, leaving no completed result. A fresh third process independently repeats the whole-family proof, replays the 12-update prefix, verifies the exact Adam state and completes in 94.5633 seconds.

All 61 coordinate vectors and losses coincide exactly, as do all 150 final powers and predictions. Both runs retain 27/30 held-out correct classifications. All four actual adversarial checkpoint cases are rejected, including the forged optimizer state with a recomputed valid hash. Original crash checkpoint bytes remain unchanged and match the recovered source receipt. Full supervision cost 267.2220 seconds, peak owned RSS 56.59 MiB; each process was assigned CPU core 19.

[Evidence index](validation/training-recovery-2026-10-09/attempt02/evidence_index.json), [supervisor](validation/training-recovery-2026-10-09/attempt02/supervisor.json), [resumed result](validation/training-recovery-2026-10-09/attempt02/resumed/result.json), [preserved crash checkpoint](validation/training-recovery-2026-10-09/attempt02/interrupted/optimizer_checkpoint.json).

![Actual optimizer recovery](assets/training-recovery-2026-10-09.png)

This validates the owned research-worker interruption protocol. The installed add-on 0.1.2 is unchanged: a Blender resume interface, whole-host crash and power-loss/filesystem durability are still separate pending tasks.
