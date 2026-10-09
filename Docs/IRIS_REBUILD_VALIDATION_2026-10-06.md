# Iris repeated-scene reconstruction validation - 2026-10-06

## Result and scope
Roadmap point 3: all execution gates PASS. The source correction and its refreshed
portable artifact have both been verified. The committed source used to export
this artifact is 7c037702486ae9ab153f605edab432b85c44ba0d.

The same regression suite failed six of seven cases on source commit
5b2e9c5475ddb60fb8d36c15bff270533980f926 and passes all seven after correction.
The empty-scene coherent escape control passes in both versions.
The corrected source SHA-256 is 6b5b32434679ae4da9410afbeeeee2c25a614eaf4b2776892aa8fb907617592d.

The separate minimal reproduction retained a clean sample-71 baseline, then
measured zero detected power, unit escaped power and an incorrect class when an
existing Optics collection caused the new collection to become Optics.001.
A second complete construction raised a missing det_R0.001 material KeyError.
These failures are preserved, not replaced by the successful reports.

## Corrections
- Resolve the active scene's optical collection by its saved mapping and datablock identity.
- Store logical detector IDs independently of Blender display names; reject duplicate
  or invalid identities and broken declared collection mappings.
- Give new scenes their own mutable material map. Resolve detector presentation
  materials through the active detector's actual object material slot.
- Accept unambiguous legacy detector names. Reject a detector material used by
  another scene before modifying its emission; rebuilding supplies separate materials.
- Preserve exclusion flags for every affected layer collection, restoring parents
  before descendants, including when ray tracing raises an exception.
- Stop and clear live state before rebuilding. Bind GUI-started live sessions to
  their initiating scene before scheduling; stop if the active scene changes.

The optical geometry, constants, learned parameters, analytical model and numerical
acceptance thresholds are unchanged.

## Numerical and preservation checks
10 recorded numeric probes cover rows [0, 71, 149].
They compare all eight complex outputs and powers with the analytical model,
class prediction, escaped power and power balance. The scene-preservation checks
cover object/data identities, transforms, material sockets and exclusion flags.
They run after construction, display updates, detector dimming and manual animation
ticks. Manual ticks do not register real timers or claim mouse-click GUI testing.

| Metric | Maximum observed | Existing limit |
|---|---:|---:|
| Complex field vs model | 6.67249939543e-05 | 1e-3 |
| Power vs model | 3.55530719299e-05 | 1e-3 |
| Power balance error | 5.78011726791e-05 | 2e-4 |
| Escaped power | 0 | 1e-8 |
| Same-geometry complex field change | 0 | 1e-8 |

All 230 recorded assertions in the seven-case regression pass.
Five additional compatibility/rejection cases pass, as do the seven pre-existing
Blender control groups and four CPU verification-gate tests.
The legacy test removes the new metadata from a real constructed scene; it checks
classification and display without the new identifiers. Invalid and shared states
are rejected at the relevant boundary: invalid metadata during classification,
and shared detector emission materials before presentation modifies them.

## Execution limits
Each Blender job ran in a separate background process through the existing
bounded CPU launcher: one core/thread, 2 GiB process memory budget, at least 4 GiB
host free RAM and an explicit deadline. Launcher receipts retain the observed
time and memory telemetry. These are CPU tests; they establish neither a native
GPU result nor physical optical behavior or external scientific replication.


## Refreshed portable artifact
A fresh Blender process reopened a copy outside the repository and executed only
the embedded source and assets. It classified all 150 rows once: training
117/120,
held-out test 29/30.
There were no prediction disagreements with the analytical model.
Both missing-asset controls and all three invalid-manifest/stale-report controls pass.
Comparing all 150 recorded rows with the point-2 artifact gives a maximum field
change of 0 and power change of 0, with no
prediction changes (existing invariance limit 1e-8). This reuses the retained
measurements and does not perform additional classifications.

| Portable metric | Maximum observed | Existing limit |
|---|---:|---:|
| Complex field vs model | 8.5866762993e-05 | 1e-3 |
| Power vs model | 6.05131972315e-05 | 1e-3 |
| Power balance error | 6.36901962561e-05 | 2e-4 |
| Escaped power | 0 | 1e-8 |
| Export/reopen field difference, sample 71 | 0 | 1e-8 |

Exporter decoration invariance on sample 71: 0.
The binary SHA-256 is 5884c6fa4cc8cee22dd99e2f4aeaf8f0e44ae44dba85d4f2447868d3d4d58c22.
The all-row report SHA-256 is ee7eaa6e71f5c3c36e54c7d13a00706e7610f6197735957c47275281f4167b17.
The bounded verifier took 334.427126 seconds in total and
performed 8,405,660 ray casts. It did not render or retrain.

- [Frozen point-3 manifest](validation/iris-rebuild-2026-10-06/portable-manifest.json)
- [Frozen point-3 all-row report](validation/iris-rebuild-2026-10-06/portable-verification.json)
- [Point-2 historical receipt archive](validation/iris-portable-point02-2026-10-06/provenance.json)

Internal read-only review accepted the source correction, all 150 rows, raw
hashes and historical comparison with no blocking findings. This is internal
verification, not external scientific replication.

The original point-2 binary remains available in Git at commit 5b2e9c5. Its receipt
bytes are archived separately; later artifacts do not replace that historical
evidence or retroactively change its source version.

## Reproduce
From Blender/demo_lattice_iris, run the following scripts in separate fresh
background Blender processes, with --factory-startup --disable-autoexec --threads 1
and --python-exit-code 1:
- test_rebuild_blender.py -- --report <new-path>.json
- test_rebuild_contract_blender.py -- --report <new-path>.json
- test_review_blender.py

Run python -m unittest -v test_verification_cpu.py for the four CPU gates.
For a RED reproduction, use the same rebuild test against the historical source
and dataset from 5b2e9c5 in an isolated checkout. Retain each report under a new path.

## Evidence and references
- [Summary and hashes](validation/iris-rebuild-2026-10-06.json)
- [Original failures](validation/iris-rebuild-2026-10-06/red-full.json)
- [Corrected regression](validation/iris-rebuild-2026-10-06/green.json)
- [Compatibility and rejection contracts](validation/iris-rebuild-2026-10-06/contracts.json)
- [Blender data-block naming and ownership](https://docs.blender.org/manual/en/4.5/files/data_blocks.html)
- [Blender API guidance on data names and references](https://docs.blender.org/api/4.5/info_gotchas_internal_data_and_python_objects.html)
