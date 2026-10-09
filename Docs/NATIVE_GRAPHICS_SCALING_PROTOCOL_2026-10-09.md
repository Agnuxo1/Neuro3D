# Native graphical optical inference: prospective equal-output batch scaling

Use the completed saved/reopened nativeGPU-trained scene, unchanged scalar model and source/mode order. Recapture actual geometry; reconstruct133states using captured-triangle GPU selection; independently audit all nearest intersections and closed surface neighbourhoods. Measure capture, graph, proof, CPUgeometry-network setup and GPUshader compilation separately.

Frozen sizes1/150/4096 use cyclically repeated original150 encodedIris inputs with one common exact quarter-turn phase per row. These are deterministic throughput inputs, not new independent examples or generalization. Both arms consume identical complex128 amplitudes and return all8complexfields/modalpowers/3classargmax. CPU computes its own geometry-derived scalar DAG, without a dense precomputed transfer matrix. GPU computes captured-plane distance/phase in the alreadyvalidated nativeFP64 fragment shader, with CPU topology and compensated coherent merging. CurrentGPUzero-tangent/echo overhead remains included; no fabricated optimized kernel timing. Tile limit150 preserves the admitted producer kernel envelope.

For each size: actual geometrycache reset, then fixed CPU→GPU pair followed by GPU→CPU pair. Thus firstGPUarm is candidate-cache cold and second warm. Inputs/package/pose/output preparation is recorded consistently; GPUtile packing/coherent merging are included in its timed arm. Full setup and complete process cost remain separately available. Field and power discrepancies must remain≤1e-11; every decision must equal both the CPU and previouslyobserved learned-model decision. All primitive/distance/value/tangent bit-echo andGLerror gates remain active. Raw modaloutputs and everybatchreadbackhash are retained.

SharedFIFO,900s,4,000MiB RAMpreflight/2,500MiB floor,2,000MiB ownedRSS,256MiB evidence,8,192MiB wholeGPUmemory/80°C/oneCPUcore. Record whole physicalGPU utilization/memory/temperature/powerdraw at approximately1Hz. These samples include display/otheractivity, cannot isolate opticalkernelenergy, and must not be equated with photonic-device efficiency. Two pairs are descriptive observations, not broad statistical speed evidence. No threshold relaxation; failure/null retained. Publish/verify main+scientificbranch before trial under continuingGitHubauthorization; external/IPFS remains pending.

[Profile](research/native_graphics_scaling_profile_2026-10-09.json), [receipt](research/native_graphics_scaling_registration_2026-10-09.json), [complete trained native model](NATIVE_DEFERRED_GRAPHICS_TRAINING_PROTOCOL_2026-10-09.md), [previous equal state forward/deferred negative result](NATIVE_DEFERRED_GRAPHICS_STATE_PROTOCOL_2026-10-09.md).

## Original first scaling attempt retained: RAM-floor null

Profiled72b1d77/116pins and publication31591b9 were verified before sharedFIFO execution. Two1-input arms and the first150-input arm passed modal-field/power/decision gates; the fourth arm was interrupted when hostavailableRAM crossed the unchanged2500MiB floor. Preflight8257.35MiB; ownedBlender peak357.25MiB; wholeGPUmemory at most928MiB. Full supervision51.313518s, complete six-pair resultNULL. Partial timings are not a completed performance result, and no cause is assigned to a particular unrelated application without recorded evidence.

Retain the exact profile, limits, allpartial outputs and resourcefailure. A repeat can use the same immutable profile after a separatelyrecorded reversible working-set reclamation; no threshold, method or testselection changes. [Original rawhashes and supervisor](validation/native-graphics-scaling-2026-10-09/attempt01/evidence_index.json).

## Actual same-profile repeat: complete numerical comparison accepted

The original RAM-floor failure remains unchanged/null. Publication72e367e/profiled72b1d77/116pins was reverified before a fresh shared-FIFO repeat of exactly the same method, limits and inputs. Oldapplication resident pages were reclaimed reversibly before the repeat; no windows/processes were terminated. Preflight10633.97MiB; no causal attribution of the earlier RAM fluctuation to an application or the success to reclamation is made. All six CPU/GPU pairs complete with all8 modalfields/powers and everyclassdecision equivalent. These are4247 deterministic repeatedinput positions per repeat, not8494 new independent examples.

| Batch | CPU first / second (s) | GPU cold / warm (s) |
|---|---|---|
| 1 | 0.026787700 / 0.020903600 | 0.592881500 / 0.335261400 |
| 150 | 0.020159900 / 0.031941500 | 4.027876400 / 3.458444000 |
| 4096 | 0.024341800 / 0.026418100 | 98.006908500 / 97.720299400 |

Maximum field difference7.50104996543e-14, power difference7.21644966006e-15. The actual current graphical implementation is slower in every measured pair; no speedup is established. ItsGPU timings include validzero-tangent/echo draws, hostpacking and CPUcoherentmerges. The CPU geometryDAG reuses eachgeometry-derived node phase within a batch; it receives no precomputedtransfermatrix. This compares actual equivalent-output implementations, not equallyoptimized hardware limits.

Complete worker-launch-to-exit supervision239.213143s, nativeworker231.850553s, peak ownedRSS364.48MiB. Actualcapture1.742281s; freshGPUgraph11.196749s; independentexactgraphaudit9.346555s; CPUsetup0.099648s; GPUcompile0.455664s. FIFOwait/preflight/sourcecopy/publication are not part of timed inference arms.

Native triangle surfacequeries399; opticalfragments includingechoes2259404; ownedGLstages81689, all pass. 189 actual wholeGPU utilization/memory/temperature/power samples are retained; display and otheractivity are included. They are not isolatedkernelenergy, photonicdevice efficiency or RTcounters.

[All rawhashes and same-profile receipt](validation/native-graphics-scaling-2026-10-09/attempt02/evidence_index.json), [modaloutputs and costs](validation/native-graphics-scaling-2026-10-09/attempt02/worker/result.json), [actualGPU surface provenance](validation/native-graphics-scaling-2026-10-09/attempt02/worker/actual_surface_provenance.json), [wholeGPUtelemetry](validation/native-graphics-scaling-2026-10-09/attempt02/supervisor.json).
