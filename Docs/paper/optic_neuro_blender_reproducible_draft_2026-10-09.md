# OpticNeuroBlender: auditable coherent scalar learning from evaluated Blender geometry

**Research draft, 9 October 2026. Not submitted or externally peer reviewed.** Author list and affiliations require confirmation before submission. This manuscript reports the current bounded evidence rather than claiming completion of the broader research programme.

## Abstract

We implement a coherent scalar optical classifier whose propagation and trainable phases originate from evaluated Blender geometry. A rational geometric state graph preserves every nonzero admitted branch and merges only identical future optical states. An independently written auditor checks nearest intersections, branch coverage and local surface neighbourhoods. The captured demonstrator contains 104 admitted objects, five sources, eight terminal modes and 16 paired mirror-translation parameters. Its complete graph has 133 states, 186 edges and 17,060 terminal path occurrences. Independent outward-rounded rational field composition bounds the errors of observed outputs and permits decisions only when power intervals separate. Geometry-driven training achieves 27/30 held-out Iris predictions after 60 fixed updates; actual Blender save/reopen inference reproduces all 150 predictions. On a prospectively fixed Wine split, three initializations obtain 33/37, 30/37 and 28/37, compared with 32/37 for matched-input linear and quadratic classifiers. Actual NVIDIA complex128 inference and gradients agree with CPU references, but small batches are slower and an equivalent dense baseline is more efficient. A declared Gaussian scalar wave reference exposes a finite-window failure, retained before a separately frozen remedial study. Physical-network fidelity, AMD execution, exceptional novelty and independent expert replication remain unestablished.

## 1. Question and falsifiable scope

The operational question is whether an accessible scene editor can serve as a reproducible instrument for an own optical neural model, with traceable geometry, coherent fields, learning and useful numerical certificates. The represented model is ideal, scalar, monochromatic, lossless planar optics in a homogeneous medium. It is not a calibrated photonic processor or a complete Maxwell model.

The certificate claim is falsifiable: one independently verified exact represented-model output outside a claimed enclosure, one invalid certified decision, or one unbounded omitted nonzero admitted branch refutes that claim. Completeness, geometric correctness, enclosure correctness and classifier accuracy are separate acceptance conditions. A solver that rejects every useful input does not demonstrate utility. A timeout is not a zero optical field or a scientific success.

The original 90-second pilot was executed without extending its deadline and remains inconclusive. The exact indexed variant also timed out. Subsequent finite-state graph, training, GPU and wave protocols were distinct, frozen and published before execution under explicit human GitHub authorization. External registration/IPFS remains an additional pending route; no external identifier is claimed, and a later timestamp would not retrospectively preregister earlier observations.

## 2. Model, units and representation

### 2.1 Evaluated scene ingress

The capture reads Blender's evaluated dependency graph: represented mesh vertices, triangle indices, instance transforms, object identities, resolved input/parameter/detector bindings and scene unit metadata. Hexadecimal floating-point values preserve exposed numbers. Rational arithmetic constructs world geometry from those represented values. This defines an exact affine represented model; it does not certify the unobserved geometry intended by an author or reproduce every rounding operation in Blender's native transform/render pipeline.

The current scene admits 104 optical objects and 6,656 triangles, five sources, eight terminal modes and 32 coordinate bindings, grouped into 16 pairs of mirrors. Coordinates and wavelength use Blender units (BU); λ is the represented value of 0.1 BU. Scene display scale is not measured physical calibration. Reported powers are normalized scalar modal powers, not calibrated watts.

### 2.2 Coherence and detector semantics

Inputs are explicit complex amplitudes in one common launch-phase reference. The temporal convention is exp(−iωt); propagation contributes exp(+i2πL/λ). Declared mirrors and splitters use explicit phase/sign conventions. Summing intensities from independently labelled sources would remove cross terms and implement a different classifier. Fluence alone does not determine the complex field.

For a terminal mode, the field is the coherent sum of its admitted path contributions and power is its squared magnitude. Geometrical mode projection and completeness precede readout. The three class detectors are fixed. An estimated argmax is not automatically certified: certification requires the winning lower power bound to exceed every competing upper bound. Zero input and overlapping bounds retain an unknown decision.

### 2.3 Complete finite-state propagation

A state identifies represented origin, direction and previous optical plane. Two states merge only when these quantities are exactly identical, so their future propagation operator is identical. Every nonzero transmission/reflection remains an edge. Only mathematically exact zero coefficients omit an edge. Cycles, unresolved intersections, missing support or resource limits produce incomplete status with no fabricated field.

An exact conservative object-AABB index narrows candidate work without changing the closed triangle queries. Shared triangle vertices do not become artificial optical edges: an independent projected square-perimeter witness checks an interior neighbourhood of the union of coincident triangles. Nearest-hit and branch auditing uses a separate implementation. The captured complete graph has 133 states and 186 edges while preserving 17,060 terminal path occurrences. This is a representation of the admitted scalar network, not a proof that a real optical device has only those physical paths.

### 2.4 Geometry-driven derivatives and training

For fixed plane normals and admitted paired translations, ray/plane intersections yield exact affine origin, hit and segment-length derivatives. A merge is admitted only when its incoming affine origin derivatives agree. The phase derivative follows from the geometrically derived optical length. Own coherent forward derivatives propagate through every graph edge; power derivatives use 2 Re(E* ∂E/∂d). No historical analytic weight matrix supplies the trained field or its gradients.

Training minimizes cross entropy of the three detector powers divided by a fixed loss temperature. Adam updates 16 mirror-pair world-X translations. Proposed positions are quantized to Blender's represented native float32 coordinates and constrained around a declared untrained centre. Every evaluated optimizer state is independently audited; a fresh final geometric rebuild checks the affine computation. Finite differences and a separate functional autograd reference are software/numerical controls, not rigorous universal gradient certificates.

### 2.5 Capacity limitation

At fixed geometry, the network is linear in complex input: E = Ux. Detection introduces a quadratic readout. For real input, one detector has P = xᵀQx with Q = aaᵀ + bbᵀ when its field row is a + ib. Consequently Q is positive semidefinite with rank at most two; a difference between two such powers has rank at most four. For complex input, the corresponding Hermitian detector matrix has rank at most one. These algebraic restrictions hold independently of a numerical rank threshold.

The current model has no intermediate optical nonlinear activation and does not establish universal neural approximation. Normalizing the common input power is part of the declared encoding, shared with the classical comparisons. A dense matrix compiled from the graph's five basis responses is an equivalent fixed-geometry baseline, useful for auditing and cost comparison.

## 3. Independent numerical checks

The independent output enclosure uses rational outward rounding at 128 bits, interval π from Machin series with remainder, square-root bounds from integer arithmetic and exact rational Taylor evaluation with explicit remainders. Complex sums and powers are composed through the audited graph. This bounds an already observed native output against the exact represented model rather than claiming that every libm or GPU execution has the same error.

The first enclosure was valid but too loose: field L1 bound 1.51×10⁻⁷ and power bound 1.93×10⁻⁷ exceeded the fixed 10⁻¹¹ budgets. It remains archived. The revised exact-midpoint Taylor composition was published before the secondary recomputation, with the budgets unchanged. The final maximum bounds were 4.9383434427813286×10⁻¹⁵ for complex-field L1 error and 3.1372973883238074×10⁻¹⁵ for power error. The represented unit-input decision R1 had a lower margin of 0.18933601504039158. A separately written 90-digit full-graph composition fell inside every reported interval. The rational construction supplies inclusion; the high-precision computation is a cross-check.

These certificates do not fill missing budgets for intended geometry, native transform preimages, uncertain physical parameters, polarization, diffraction, detector coupling or material calibration. Those errors remain unknown. The unit-input decision certificate is not a certificate of all Iris or Wine predictions.

## 4. Learning and generalization experiments

### 4.1 Iris geometry training and native roundtrip

The declared Iris split contains 120 training and 30 held-out examples. Training-only min/max preprocessing maps four features to four coherent sources plus a fixed coherent reference, with joint unit input power and no held-out clipping. Iris was previously examined in the project, so this experiment is not presented as a new blind discovery.

Historical learned delays were reset to an explicit untrained absolute geometry before initialization. Sixty fixed Adam updates decreased training loss from 6.2554405 to 0.3097067; training accuracy was 110/120 and held-out accuracy 27/30. All 61 represented states passed their geometry audits. The maximum initial loss-gradient finite-difference discrepancy was 1.4746713×10⁻⁶ against a 10⁻⁴ tolerance. Final fresh-geometry field reconstruction differed by at most 4.6194484×10⁻¹⁶ against 10⁻¹¹. Full worker cost was 369.43 s, including 349.67 s of geometric auditing.

Actual Blender 4.5.14 applied the final native coordinates, saved a new file, reopened it with script execution disabled, recaptured geometry and rebuilt the own inference graph. All 150 observed powers had maximum difference zero and all predictions matched. The original .blend remained unchanged. This proves a bounded local native roundtrip, not external replication.

### 4.2 Prospectively fixed Wine comparison

Wine contains 178 examples and 13 measurements. The official original files and hashes are retained with attribution and licensing. Four features were fixed before training: alcohol, malic acid, ash and alkalinity of ash. One stratified split fixed 141 training and 37 held-out examples, and three initializations fixed seeds 1049, 1050 and 1051. The same training-only encoding, sources, class labels and split were used for all models. No held-out result selected an initialization, feature subset, step count or hyperparameter.

Linear softmax used 15 nominal coefficients; quadratic softmax used the 15 unique input monomials and 45 nominal coefficients. Both optimized a declared convex L2-regularized objective using fixed L-BFGS-B controls. Their function families differ from a passive optical network, so matching data does not establish equal physical constraints or capacity.

| Model | Training correct | Held-out correct | Held-out Wilson 95% interval |
| --- | ---: | ---: | ---: |
| Geometric, seed 1049 | 117/141 | 33/37 | 75.3–95.7% |
| Geometric, seed 1050 | 108/141 | 30/37 | 65.8–90.5% |
| Geometric, seed 1051 | 105/141 | 28/37 | 59.9–86.6% |
| Linear softmax | 120/141 | 32/37 | 72.0–94.1% |
| Quadratic softmax | 121/141 | 32/37 | 72.0–94.1% |
| Training majority | 56/141 | 15/37 | 26.3–56.5% |

All 183 geometry states and three final rebuilds passed. Maximum initial gradient discrepancy was 5.473×10⁻⁶; fresh field difference was at most 5.882×10⁻¹⁶. The complete worker cost was 1114.17 s, including 1054.49 s of geometric audits. Baseline fits took 5.58 ms and 4.71 ms after imports, with imports included only in the total worker cost.

The three runs share the same 37 held-out observations and cannot be pooled as 111 independent trials. Paired exploratory exact McNemar p-values against either baseline were 1, 0.5 and 0.125, without multiple-comparison correction. No optical superiority is demonstrated. The spread across initializations shows sensitivity, and the single public-data split does not establish external blind or zero-shot generalization.

![All three Wine runs and matched comparisons](../assets/wine-geometry-and-baselines-2026-10-09.png)

## 5. Actual NVIDIA execution and total-cost limits

The actual RTX 3090 was fixed by device UUID and admitted through the shared FIFO queue. Torch 2.6.0+cu124 with CUDA 12.4 and driver 581.29 evaluated complex128 fields, powers and the own 16-parameter Jacobians for 60 prepublished complex probes. Exact geometry and phase-argument preparation remained on CPU; this was not GPU triangle tracing. A separate functional autograd reference checked the weighted-loss derivative.

Maximum CUDA/NumPy differences were 3.61×10⁻¹⁶ in field, 3.89×10⁻¹⁶ in power, 5.55×10⁻¹⁴ in field Jacobian and 3.55×10⁻¹⁴ in power Jacobian; the autograd discrepancy was 1.56×10⁻¹³. Independent rational certification of these 60 observed GPU probes gave field L1 bound ≤2.9356883×10⁻¹⁵ and power bound ≤1.3807709×10⁻¹⁵. Fifty-nine represented argmax decisions were certified; zero input remained unknown.

| Batch | Cached graph CPU, ms | Cached graph CUDA, ms | Equivalent dense CPU, ms | Equivalent dense CUDA, ms |
| --- | ---: | ---: | ---: | ---: |
| 1 | 14.45 | 24.50 | 0.071 | 0.435 |
| 150 | 17.43 | 27.06 | 0.499 | 0.559 |
| 2048 | 75.00 | 25.72 | 8.597 | 0.897 |

These are synchronized warm medians of five fixed repetitions for the same input/output contracts, including fields, powers and Jacobians. Preparation, transfers and complete worker costs are retained separately. The whole GPU benchmark worker cost was 6.72 s; peak RSS was 996.10 MiB and peak reserved CUDA memory 112 MiB.

Small graph batches are slower on CUDA, and the dense baseline is more efficient at all reported sizes. Warm batch scaling is not structural graph scaling, full native geometry-training speedup, host/device energy measurement or photonic-device efficiency. AMD hardware was not available and has not been executed.

## 6. Separate wave-reference experiment

An original coherent complex128 angular-spectrum solver propagates a declared Gaussian boundary field in a homogeneous outgoing scalar Helmholtz half-space. Its continuum reference is independently implemented Fourier–Bessel/Hankel quadrature with analytic Gaussian spectrum and separate quadrature refinement. A paraxial Gaussian solution is an additional approximation reference. The transverse integral of |E|² in a circular aperture is the declared observable; it is not a vector Poynting flux or a captured detector's modal-coupling measurement.

The fixed family uses waist 0.1 BU, aperture radius 0.15 BU, wavelengths 0.1/0.025/0.00625 BU and propagation distances 1/2/4 BU. The first 36 observations completed, but the λ=0.1 BU, z=4 BU case failed the fixed 2×10⁻⁶ radial-field tolerance at window 16 BU: difference 2.2311874×10⁻⁶. Refining 512²/1024²/2048² at that window left the same error. This negative result was published before any remedial trial.

A separately frozen adaptive family used windows 32/64 BU and grids 1024²/2048²/4096², with unchanged scientific tolerances and a larger declared RAM envelope. All nine physical cases passed their prefixed gates. Maximum radial-field differences were 4.0866539×10⁻⁷ at window 32 and 9.2920364×10⁻⁸ at window 64, in the 65 checked points. Aperture integration remained sensitive to spatial resolution; the coarse 1024²/32 mesh had maximum fraction error 0.00289647, retained rather than called precise. Fine and expanded meshes satisfied their own gates. Complete remedial cost was 133.05 s, peak RSS 1866.79 MiB.

Quadrature refinement is numerical convergence evidence, not a rigorous universal FFT error bound. This Gaussian mode was not inferred from the network capture. The separate study therefore characterizes a declared propagation regime without establishing full-network physical fidelity or providing a correction factor for its detector powers.

![Retained negative and separately frozen remedial wave family](../assets/gaussian-wave-remedial-2026-10-09.png)

## 7. Installation, replication and artefact status

The standalone own Blender addon packages the original solver dependency closure, semantic contracts, own trained example, dataset, source provenance and integrity manifest. Its UI uses explicit coherent inputs, background Blender jobs, owned cancellation, stale-result rejection, completed-result recovery and new-file saving. Original implementations and immutable historical ZIPs are retained.

Two native attempts are retained with null metrics: a version-string/preflight failure before installation, and a successful isolated installation followed by an incorrect complex serialization handoff. ZIP 0.1.1 corrects that handoff with the already used coherent wire converter. Its third native audit passed all nine predefined controls in 729.01 s with peak aggregate RSS 573.49 MiB. Own training actually ran inside background Blender, audited all 61 states and reproduced the previous 27/30 held-out predictions, loss trajectory and all 150 powers with observed difference zero. Stale inputs/geometry, real cancellation, completed-job recovery, atomic apply, copy/reopen and modified-result rejection also passed. A subsequent shutdown log contains a double-unregister RuntimeError after the audit explicitly unregistered a still-enabled addon. It does not change the nine numerical/control outcomes, but idempotent lifecycle handling remains open and will require a separately retained fix and test.

Every bounded scientific record includes a published profile, source hashes, raw outcomes and evidence index. Reproducing old protocols requires their corresponding commit or archived preimages; current source evolution must not be substituted silently. A clean local installation is distinct from an execution in an independent environment, and both are distinct from a replication performed and interpreted by independent researchers. The latter has not been obtained. No specialist critique, journal submission, external registration receipt or physical experiment is asserted.

## 8. Related work and novelty boundary

Trainable coherent photonic networks and diffractive optical learning predate this implementation. [Shen et al.](https://arxiv.org/abs/1610.02365) and [Lin et al.](https://arxiv.org/abs/1804.08711) establish that context. [Kawata and Hirose](https://doi.org/10.1364/OL.28.002524) is an earlier coherent path-difference learning precedent. These works prevent presenting optical learning itself as our novelty.

[Ho et al.](https://arxiv.org/html/2412.09774v2) combines ray and diffraction-based optical modelling with optimization and coherent demonstrations, an important closest-method comparison. Its image-formation conventions and sampling scope cannot simply replace the common-coherence multi-input readout here. [Chromatix](https://github.com/chromatix-team/chromatix) provides a separate differentiable wave-optics precedent. We have not installed or benchmarked it in this study.

[DeepG](https://ggndpsngh.github.io/files/neurips19-deepg.pdf) and [QA-IBP](https://ojs.aaai.org/index.php/AAAI/article/view/26747) show related certification precedents for geometric transformations and quantized inference. Their reviewed scopes do not establish exact optical triangle-path equivalence, but they prevent broad claims that combining geometry, decisions or actual arithmetic certification is automatically unprecedented. [Matsushima and Shimobaba](https://doi.org/10.1364/OE.17.019662) is a known angular-spectrum sampling-method reference; this work does not claim to have implemented its band-limited method or completed a full-text review of that paper. [Steck's optics notes](https://atomoptics.uoregon.edu/~dsteck/teaching/optics/optics-notes.pdf) support the declared Gaussian conventions.

The current literature register has 194 raw entries, 175 unique identities and 30 completed extraction records; 106 requested extractions remain pending. These counts are historical audit status, not an exhaustive absence-of-prior-art proof. The implemented combination is original code and an integration contribution. Exceptional scientific originality, exceptional importance and durable impact have not been demonstrated. A defensible novelty claim requires closer matched comparisons and independent expert assessment.

## 9. Conclusions and open tests

The bounded evidence supports an own geometry-driven coherent scalar classifier, exact admitted branch coverage, useful certificates of observed represented outputs, own gradients/training, local native Blender roundtrip and actual NVIDIA evaluation. It also exposes meaningful limitations: optical comparisons do not show superiority, small CUDA batches are slower, finite FFT windows can fail, and the current passive readout has restricted quadratic capacity.

The remaining research programme includes bounded input/parameter uncertainty and native-transform error budgets, complete trained-batch certification, broader geometry/task families, structural scaling and ablations, full-cost and energy measurements, actual AMD execution, completed standalone acceptance, independent-environment reproduction, outside expert replication, full-network physical modelling and calibrated measurements when physical-device claims are sought. None is replaced by a prize aspiration or by a passing software test.

## Data, code and reproduction map

Repository: [Agnuxo1/Neuro3D](https://github.com/Agnuxo1/Neuro3D), branch `codex/neuro3d-scientific-closure-20261008`; [draft PR 6](https://github.com/Agnuxo1/Neuro3D/pull/6). Software license: MIT; Wine data attribution/license: [UCI Wine](https://archive.ics.uci.edu/dataset/109/wine), DOI [10.24432/C5PC7J](https://doi.org/10.24432/C5PC7J). No third-party optical implementation is bundled in the own addon.

| Evidence | Protocol / method | Raw record |
| --- | --- | --- |
| Represented output intervals | [method and limitations](../OBSERVED_GRAPH_OUTPUT_CERTIFICATION_2026-10-09.md) | [analysis02 index](../validation/observed-graph-output-enclosure-2026-10-09/analysis02/evidence_index.json) |
| Own Iris training | [frozen protocol](../CAPTURED_GEOMETRY_TRAINING_PROTOCOL_2026-10-09.md) | [training result](../validation/captured-geometry-training-2026-10-09/attempt01/worker/result.json) |
| Actual native save/reopen | [native reproduction](../TRAINED_GEOMETRY_BLENDER_REPRODUCTION_2026-10-09.md) | [native result](../validation/trained-geometry-blender-reproduction-2026-10-09/attempt01/worker/result.json) |
| Wine and matched baselines | [comparison](../WINE_GENERALIZATION_COMPARISON_2026-10-09.md) | [complete result](../validation/wine-comparison-2026-10-09/attempt01/worker/result.json) |
| Actual NVIDIA | [benchmark](../TRAINED_GRAPH_NVIDIA_BENCHMARK_2026-10-09.md) | [indexed evidence](../validation/trained-graph-cuda-2026-10-09/attempt01/evidence_index.json) |
| Gaussian negative/remedial | [original](../GAUSSIAN_WAVE_REFERENCE_PROTOCOL_2026-10-09.md), [remedial](../GAUSSIAN_WAVE_REMEDIAL_PROTOCOL_2026-10-09.md) | [original result](../validation/gaussian-wave-reference-2026-10-09/attempt01/worker/result.json), [remedial result](../validation/gaussian-wave-remedial-2026-10-09/attempt01/worker/result.json) |
| Standalone addon acceptance | [versioned protocol, failures and lifecycle limitation](../OWN_BLENDER_ADDON_PROTOCOL_2026-10-09.md) | [nine-control native result](../validation/own-blender-addon-2026-10-09/attempt03/worker/result.json) |

Publication commits fixed before experiments are recorded in each linked protocol. Hashes and preimages must be checked before interpreting or rerunning a result. External expert review and author approval of a submission-ready manuscript remain pending.
