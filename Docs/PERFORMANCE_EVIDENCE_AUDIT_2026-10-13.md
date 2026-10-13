# Performance evidence and README history audit

Date: 13 October 2026. Audited main:
`d69810cbebebb34599338e6d59193887ba10a9d1`. Comparison with Codex's
`74325cc5e0c2d36e5785e3f0fee2ab4c8b69dec6` and the original result commits.
This is a read-only source/history and arithmetic audit; no GPU experiment or
training was rerun. Full machine-readable evidence is in
[the audit record](research/readme_performance_audit_2026-10-13.json).

## Findings

1. **The audited positive and negative result files were preserved.** Across
   eight historical sets, 541 original file blob identities remain unchanged;
   none was deleted. The continuous-proof training archive has 50 such files,
   trained-graph CUDA 40, refined native frontier 93, native scaling 170,
   resident rejection 175, packet optimization 6, original G1 result 1 and
   the cost/energy study 6. Between the Codex cutoff and audited main there is
   no changed file under `Docs/validation` and no deleted path in the entire diff.
   Independently recomputed SHA256 checks match 47 pins from the reuse-training
   supervisor and 169 from the native-scaling evidence index.
2. **The README did omit a real positive result.** Commit
   `a87033959245eab28186273573812f6e1074ee1c` published the continuous-proof
   speed improvement on 9 October. The README reorganization in
   `d38a02da590c690185bda0f38e05f4d63ac858c4` later that day removed its
   paragraph. The original protocol, raw results, plots and historical README
   remained. This omission predates the 12-13 October closure campaign. The
   current revision restores its prominence without changing any number.
3. **The negative native graphics timings are arithmetically correct for
   that route.** All six original pairs have GPU time greater than CPU time,
   at batches 1, 150 and 4096. Their files are byte-identical to the original
   publication at `7cce9f0`; they do not refute a faster alternative CUDA or
   compiled-operator route. The resident field rejection likewise retains its
   original 6.376147888196662e-8 observation and unchanged 1e-11 budget.
4. **The G1 hypothesis is narrower than “optimization works.”** Its published
   rule requires at least 2x in *all four* batch/mode cells, charging recompilation.
   Recomputed decisive ratios are 1.1427, 1.2623, 1.6252 and 16.3330; therefore
   that conjunction fails. Every one of the six measured cells nevertheless
   has a median improvement, and the cached route is faster still. A failed
   universal >=2x prediction must not be described as “no improvement.”
5. **Energy savings versus a physical conventional chip are not established
   in these records.** P1-9 explicitly discloses no power measurement and
   computes a declared proxy `CPU process seconds * 14 W`. Its 45-row table has
   no arithmetic inconsistency in that formula. However, dividing a package
   TDP by ten cores does not itself certify a physical per-process power bound.
   Those values cannot establish measured joules per inference or a device
   energy advantage. Native GPU telemetry is whole-device/display telemetry,
   not isolated optical hardware or matched CPU-process energy.

## Positive performance results, retained with scope

| Experiment | Verified calculation | Interpretation |
|---|---|---|
| Fresh continuous geometric proof versus 61 point audits | 393.110261 / 90.9291611 = **4.323258x** | Complete paired CPU training workers; identical represented states, losses, final powers and 150 decisions; proof overhead included. One pair, no timing confidence interval or energy measurement. |
| Trained graph CUDA, 2048 inputs | 75.001900 / 25.723200 ms = **2.915730x** | Warm same-program graph calculation of fields, powers and both Jacobians. Including recorded input transfer/readback gives 2.755954x. Cold setup is separate; cached dense CPU/CUDA baselines are faster still. |
| G1 cached operator, inference cells 1/150/4096 | **1583.37x / 792.45x / 121.46x** | Warm field evaluation with fixed geometry and cached U, against graph traversal; initial compilation excluded from warm calls. Not full physical inference or complete classification cost. |
| G1 4096 fields/tangents with recompilation | 508.281000 / 31.119900 ms = **16.332990x** | Requested fields and field tangents; not a complete loss/optimizer/audit cycle. |
| Byte-identical CPU packet candidate | **2.014 / 2.420x** at batch150; **2.497 / 2.450x** at batch4096 | Packing only. Single-row candidate is slower, and GPU integration has not been validated. |
| Refined combined native construction route | About **2.85x** versus the older CPU builder | Preserved result, but refinement algorithm changed as well as the candidate backend. The later identical-refinement CPU/GPU ablation does not isolate a GPU speed advantage. |

The working coherent network, certified numerical outputs, actual geometry
learning, installed recovery and diffraction-inclusive WAVE-C1 confirmation
are additional positive results. Their numerical/model limits remain in their
original records; a performance outcome from one route does not overwrite them.

## Cost boundary and attribution

G1's timed compiled functions return fields and field tangents. Its graph
`forward` also computes powers and power tangents, although the runner discards
them. This is a comparison of routes for the requested field outputs, with
different incidental work; it is not a matched end-to-end classifier benchmark.
No power/detector/loss/optimizer/geometry-capture costs should be silently
assigned zero when reporting a broader inference or training claim.

Commit author names identify repository metadata, not which model executed an
action or why. The checked history establishes a front-page omission and
preserved data. It does not establish deliberate manipulation, operator intent
or a failure in another application's internal harness.

## Reproduction commands

```bash
git diff --name-status 74325cc d69810c -- Docs/validation
git log --all -G '4[.,]32|393[.,]11|90[.,]92' -- README.md
git show a870339:Docs/validation/geometry-reuse-training-2026-10-09/attempt01/supervisor.json
git show d69810c:Benchmarks/compiled-operator-g1/results/G1_RESULTS.json
```

These commands inspect preserved records. They do not repeat the hardware or
training measurements. Check the JSON's exact blob comparisons and hash results
before extending the finding beyond the audited files and commits.
