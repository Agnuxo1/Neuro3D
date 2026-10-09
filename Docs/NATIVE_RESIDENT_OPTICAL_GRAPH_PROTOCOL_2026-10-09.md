# Actual-surface local coefficients and resident optical graph

**Experimental; no successful native execution is claimed when this protocol is frozen.** This variant addresses the measured overhead of the existing per-frontier pipeline while keeping the optical computation tied to the captured Blender scene.

1. Open the actual learned Blender scene, capture evaluated geometry and build the source-driven GPU graph. Independently audit the complete133state/17,060path geometry.
2. Query each of the133current captured surfaces on the native FP64 optical shader with unit incoming field. Retain selected triangles, distance, local first/second complex branches and exact incoming field/derivative echoes. These actual GPU-derived **local coefficients** are uploaded with admitted topology; no CPU global transfer matrix enters the inference shader.
3. For each coherent input, a fragment executes the133state optical graph, local complex multiplication and Kahan merges. Read all eight complex detector fields as native integer words. A separate draw verifies all five incoming binary64 channels by exact bit echo.
4. Require zero/source-only/global-quarter-turn/relative-source-half-turn controls and all six CPU/GPU equal-output comparisons at batches1/150/4096. Field and power discrepancies must remain within1e-11 and every decision must equal both the own CPU geometryDAG and the recorded learned model. Repeated observations are cost probes, not new generalization data.

The geometry generation, captured scene/material representation and wavelength invalidate the coefficient cache when changed. Coefficient derivation, shader setup, fresh geometry and independent audit are included as separate measured setup costs; each inference arm includes its own packets, draws, exact input echoes and readback. Native Kahan arithmetic must pass the independent comparison; algebraic factorization does not establish a numeric certificate.

The original validated forward/differentiable engines and installer remain unchanged. This variant validates **inference only**; it does not establish gradients, training, physical flux, AMD portability, total advantage or a novel universal architecture. WholeGPU power samples include display and other activity.

The prospective resource envelope matches the preceding scaling trial:900seconds worker,4,000MiB preflight freeRAM,2,500MiB host floor,2,000MiB ownedRSS,256MiB evidence,8GiB totalGPU memory and80C. Admission uses the existing sharedFIFO; waiting for other owners is not native execution. The12hour task deadline also limits when this trial can start. Every failure or admission timeout is retained without changing the frozen method.

[Frozen profile](research/native_resident_graph_profile_2026-10-09.json) · [Registration](research/native_resident_graph_registration_2026-10-09.json) · [Engine](../Blender/blender_lab/native_resident_optical_graph_v1.py) · [Worker](../Tools/audit_native_resident_graph_v1.py) · [Supervisor](../Tools/run_frozen_native_resident_graph_v1.py).

## Actual first native attempt: framebuffer limit, NULL

Publication564dae98/profiledc077d1/120pins were verified13:27UTC, followed by sharedFIFO admission13:37:27UTC. The actual capturedgraph and independent audit complete; native localcoefficient derivation/shadercreation reached. Blender rejects eight colorattachments: `AttributeError: too many attachments, max is 6`. No coherent resident outputs or speedresult accepted. Alloriginalrawhashes verified and retained. [Original evidence](validation/native-resident-graph-2026-10-09/attempt01/evidence_index.json). A separatev2 protocol must use two four-mode outputpasses plus an inputechopass, within sixattachments; the originalv1/profile remains unchanged.
