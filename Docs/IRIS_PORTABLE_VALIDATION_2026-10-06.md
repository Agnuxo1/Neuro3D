# Iris portable artifact validation - 2026-10-06

## Result
PASS: the regenerated Blender artifact was copied outside the repository and
checked in a separate Blender 4.5.14 LTS process with automatic scripts disabled.
The embedded source, CSV and trained parameters match source commit
63dee34675f0b1de1e032b3b91a87ac09b2eced3. The copied binary SHA-256 is
7130f5e46b0fb9785f6b692478d3892d59671f15d010598130a1537d6e973f3b.

All 150 rows were classified once using Blender scene.ray_cast and Python complex
field accumulation. Training: 117/120; held-out test:
29/30. The split/scaler were checked from the embedded CSV
and saved state. The analytical comparison uses model_U and encode from the demo;
this is not a new independent physical oracle.

## Measured gates

| Metric | Maximum observed | Existing limit |
|---|---:|---:|
| scene_vs_model_max_power_diff | 6.051319723e-05 | 0.001 |
| outputs_complex_vs_model_max | 8.586676299e-05 | 0.001 |
| power_balance_max_err | 6.369019626e-05 | 0.0002 |
| escape_max | 0 | 1e-08 |
| save_reopen_max | 0 | 1e-08 |

Decoration invariance was measured separately by the exporter before saving:
0 on sample 71.
The reopened-file comparison uses that same sample's eight fields and powers.
It is not mislabeled as a 150-row save/reopen comparison.

## Portability controls
- The verifier executed the embedded Text as a module without __file__.
- External source/CSV/weights opens were blocked during all 150 classifications.
- Both missing embedded data controls raised the required explicit exception and
  restored the original Text data. They performed no additional classifications.
- Missing binary hash, incorrect binary hash and incorrect embedded-source hash
  were rejected before classification. Each replaced an older successful report.
- The panel and all three operator types registered; the classify operator's
  step property was verified as an integer with default 1. This is an RNA check,
  not a visual interaction test.

## Cost and limits
Classification wall time: 306.431443s;
ray casts: 8,405,660. The owned process used one core/thread.
Peak working set: 210,030,592 bytes.
Total launcher wall time: 309.386200s.

No training or renderer was executed for this validation. It does not establish
native GPU inference, RT-core usage, physical optical behavior, energy advantage,
generalization beyond this fixed Iris split, or external scientific replication.
Interactive rebuilding with conflicting names is the next roadmap point.

## Reproduce
From the Iris demo directory, using a fresh background Blender process:
1. Run export_portable_blender.py with --output and --manifest paths.
2. Copy only the resulting blend and manifest to a directory outside the repo.
3. Run verify_portable_blender.py with --blend, --manifest and --report.
4. Run test_portable_failure_blender.py with the same inputs and --output-dir.
Use --threads 1 and --disable-autoexec. Each script receives its options after
Blender's -- separator. A nonzero process exit or incomplete report is a failure.

## Evidence
- [Portable manifest](../Blender/demo_lattice_iris/renders/portable_manifest.json)
- [All 150 rows](../Blender/demo_lattice_iris/portable_verification.json)
- [Summary and negative controls](validation/iris-portable-2026-10-06.json)
- [Exporter](../Blender/demo_lattice_iris/export_portable_blender.py)
- [Independent process verifier](../Blender/demo_lattice_iris/verify_portable_blender.py)
- [Failure controls](../Blender/demo_lattice_iris/test_portable_failure_blender.py)

Blender reference: https://docs.blender.org/manual/en/4.5/advanced/scripting/security.html
