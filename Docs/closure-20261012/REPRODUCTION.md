# Reproduction profiles and data boundary

The support kit is independent of historical benchmark and Blender Python
environments. On CPython 3.12 install `agent_support/requirements-closure.txt`;
for the selected existing CPU regressions also install scikit-learn 1.7.2 and
mpmath 1.3.0. Execute from the repository root:

```bash
python -m unittest discover -s agent_support -p 'test_*.py' -v
python Tools/run_closure_regressions_v1.py --out /your/D-or-E-root/cpu-run01
python -m unittest Blender.tests.test_closure_comparators_v1 -v
python -m unittest Blender.tests.test_validacion_onda_portable_v2 -v
python agent_support/support_demo_v2.py --out /your/D-or-E-root/support-control01.json
python agent_support/closure_v2.py --repo . --manifest agent_support/frontier-manifest.json
```

The frontier check returns **2** while fronts remain unresolved; this is the
expected refusal to claim project completion. A support control receipt is
synthetic CPU evidence, not a Blender/GPU or physical-network run.

For historical reproduction, use the original exact commit and fixtures named
in each receipt. The two pinned import-time-chdir modules remain historical:
`test_validacion_onda.py` and `nested/predict_var.py`. Their portable successors
have separate names and do not overwrite the frozen source hashes. Run
historical snapshots in their own processes and environments, rather than
mixing their import state into current production tests.

The complete EEG comparator implementation uses the owner's legitimately
accessible `Xtr`, `ytr`, `run` and saved optical fold-index files; it never loads
`Xte`. Raw EEG, labels and raw derivative NPZ results remain in the owner's
local cognition workspace until redistribution conditions are verified. This
public delivery contains execution hashes, aggregate/subject accuracy results,
code and the original data-acquisition/reproduction instructions, not an
invented public dataset. Existing access is required to replay the study.

```bash
python Benchmarks/eeg-motor-imagery/comparativa-anidada/run_nested_comparators_v1.py \
  --method fbcsp --data /legitimate/data --optical-raw /legitimate/optical/raw/full \
  --out /new/cpu/fbcsp --subjects S001 S002 S003 S004 S005 S006 S007 S009 S010 S011 S012 S014 S016 S017 S018 S019 S020
python Benchmarks/eeg-motor-imagery/comparativa-anidada/analyze_comparators_v1.py \
  --optical-raw /legitimate/optical/raw/full --fbcsp /new/cpu/fbcsp --out /new/comparison.json
```

EEGNet must first finish one complete fold under a newly frozen resource
profile. The first attempt was interrupted by the host RAM floor and has no
timing estimate. Do not project its duration or silently treat missing H2 as a
successful comparison. The original three-hour policy remains unchanged.

For the archived native-coefficient CPU ablation:

```bash
python Tools/diagnose_resident_archive_v1.py --out /new/resident-archive-diagnostic
```

This needs only the published historical readbacks and CPU; it does not run or
repair the native GPU shader. New native trials retain actual FIFO admission,
hardware identity, the original numeric thresholds and prospective source pins.
