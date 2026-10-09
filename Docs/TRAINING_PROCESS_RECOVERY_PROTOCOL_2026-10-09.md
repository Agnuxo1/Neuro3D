# Own training interruption and deterministic recovery: frozen protocol

Recovery must preserve an interrupted optimization trajectory, including native geometry coordinates and Adam moments. The checkpoint is written to a unique file, flushed, fsynced, and atomically replaced. Its identity binds the outer profile, original training protocol and source pins. A hash identifies bytes rather than authorizes arbitrary state.

Run an uninterrupted baseline, then terminate only a newly spawned owned training process after its checkpoint has committed 12 updates. That interrupted process must have a nonzero termination code and no completed scientific result. A third fresh process loads the preserved checkpoint, repeats the full continuous original-family proof, and recomputes all 12 previous updates deterministically before trusting the optimizer state. It then completes the original 60 updates.

Acceptance requires all 61 coordinates and losses to equal the uninterrupted run exactly, all 150 predictions to agree and power difference at most 1e-11. The actual resumed worker must reject four checkpoint adversaries: modified optimizer data with an invalid hash, stale profile identity, truncated bytes, and forged optimizer data with a self-consistent hash. The last case is rejected by deterministic replay. Original checkpoint bytes must remain unchanged.

Three meaningful software controls cover atomic round-trip, invalid identity/integrity/truncation, and a forged state that has a recomputed valid hash. A fresh whole-family proof and final scene reconstruction are counted for every complete worker. Limits are 300 seconds per stage, 1,000 seconds total, 4,000 MiB initial RAM, 2,500 MiB floor, 1,500 MiB owned RSS and 128 MiB evidence. No GPU is required for these checkpoint semantics.

[Profile](research/training_recovery_profile_2026-10-09.json) and [authorization](research/training_recovery_registration_2026-10-09.json) are published and byte-verified before any actual interruption. External/IPFS remains pending without identifiers.

This is research-worker process recovery. It does not yet establish an installed Blender resume interface, survival of a whole Blender host crash, operating-system or power-loss durability, physical fidelity, or external independent reproduction.
