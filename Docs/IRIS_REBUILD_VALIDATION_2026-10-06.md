# Iris repeated-scene reconstruction validation - 2026-10-06

## Result and scope
Source validation: PASS. The portable artifact refresh remains pending at this
intermediate source checkpoint of roadmap point 3.

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
are deliberately rejected rather than accepted as zero-output classifications.

## Execution limits
Each Blender job ran in a separate background process through the existing
bounded CPU launcher: one core/thread, 2 GiB process memory budget, at least 4 GiB
host free RAM and an explicit deadline. Launcher receipts retain the observed
time and memory telemetry. These are CPU tests; they establish neither a native
GPU result nor physical optical behavior or external scientific replication.

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
