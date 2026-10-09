# Native graphics: secondary packet and call-count audit

This prospective **secondary CPU analysis** audits the published six-pair scaling experiment and replays the packet-building operation. It does not execute graphics, generate new classification evidence, or modify the previously validated GPU engines.

The original uniform packet contains 256 rows of 128 bytes: 14 finite binary64 scalars and two padding words. A NumPy candidate constructs the same little-endian, zero-padded layout. Every replayed packet must match the original bytes; signed zero, subnormals, extreme finite values, invalid extents and nonfinite values are checked. The candidate remains **not integrated or validated in native GPU execution**.

Actual archived GL stage counts and captured-surface receipts must reconcile with the chunk extents for batches 1, 150 and 4096, two repeats each. Logical upload/download extents and source-derived API calls are reported separately from hardware counters. They do not measure PCIe bandwidth or identify the cause of the observed GPU runtime.

The CPU microbenchmark uses archived actual incoming fields and matching exact captured rays, cycles the 150 rows and applies exact quarter turns. This is a synthetic replay of the packet shapes, not a byte transcript of the earlier scaling experiment. It measures packet generation only, with two alternating orders for each size; input-list construction, digest checking, resource upload and coherent merging are excluded. No speed threshold is used for acceptance.

The new secondary envelope is 300 seconds, one CPU core, 512 MiB preflight free RAM, 256 MiB host floor, 512 MiB owned RSS and 16 MiB evidence. It does not relax any preceding GPU protocol. Every result, including failure, is retained. The GitHub sequence authorization applies; external registry/IPFS identifiers remain absent.

[Frozen profile](research/native_packet_workload_profile_2026-10-09.json) · [Registration](research/native_packet_workload_registration_2026-10-09.json) · [Worker](../Tools/audit_native_packet_workload_v1.py) · [Supervisor](../Tools/run_frozen_native_packet_workload_v1.py) · [Unintegrated packet candidate](../Blender/blender_lab/optical_uniform_packet_v1.py).

## Next architecture hypothesis

With admitted geometry, wavelength and materials fixed, the local scalar model has `E_out = C E_in`, `J_out = C J_in + C_j E_in`. A future graphics implementation can derive **local coefficients from actual GPU-selected surfaces**, cache them by geometry generation and optical parameters, and propagate fields through GPU graph passes. The CPU must not inject a global expected transfer matrix. Candidate invalidation, coherent sums, field/gradient budgets and independent decision certificates must be revalidated before any release or performance assertion. Algebraic factorization alone does not prove equivalence of native floating-point arithmetic.
