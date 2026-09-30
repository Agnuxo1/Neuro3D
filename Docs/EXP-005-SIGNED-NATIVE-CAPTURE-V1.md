# Signed scalar private capture V1 — CPU preparation only

New opt-in adapter, frozen signed preparation and all old shaders/contracts
unchanged. Twelve exact uint32 inputs (8 valid, 4 aborts), gate 1e-4 unchanged.
Manifest checks preparation SHA, code pins and cases before and after dispatch.
Evidence directory is exclusive; manifest and mandatory result are opened before
GPU admission. Raw readback is persisted before decoder or post-readback deadline
checks, including failed checks. Exceptions propagate, result finalizes once.

Default admission rejects. Separate outer supervisor MUST provide actual gpuq
exclusivity, live fail-closed telemetry, hard child timeout and authenticated
envelope. Fresh UTC deadline <=90s also checked against monotonic elapsed time;
RAM budget 2GiB plus 4GiB remaining floor, total VRAM <=18GiB, <=80C. Metadata and
callbacks do NOT certify operational enforcement or GPU execution. No launcher
is included and no historic night deadline is reused.

Targeted tests mock dispatch to test persistence failures/success and deadline:
they are NOT GPU, shader compilation, actual numerical decoder or native evidence.
No scene geometry, RT, conf1 promotion, physical optics or speedup is claimed.
JEV blocked; explicitly local fallback without remote endorsement.
