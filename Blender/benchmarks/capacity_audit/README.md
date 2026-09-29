# Independent capacity evidence audit

Codex owns this folder; Claude owns `.cognition/neuro3d/capacity/`.
The auditor never runs a benchmark or imports a GPU runtime. It separates
execution status from correctness, reduction placement, backend and safety evidence.

Frozen v1 threshold for FUTURE incoherent intensity smoke: relative L2 error
<=0.001. Historical smoke v0 is classified provisionally, not retroactively promoted.
Near-zero references require an absolute-error rule predeclared per workload.
No neuron/channel equivalence or coherent-RT claim follows from these diagnostics.

Required producer evidence: N/M/params/batch/depth/precision, backend/device/version,
code/input/readback hashes and retained inputs W/x + actual output, resource watchdog
min RAM/max temperature, device VRAM peak, end-to-end timing with warmups/repeats.
Modes: cells = GPU pixel products + CPU row reduction; integrate = stochastic render
integration, requiring independent verification and no CPU hidden matvec.
All incoherent variants remain distinct from the coherent mirror lattice.

Use `python -B -m unittest discover -s Blender/benchmarks/capacity_audit -v`.
Read-only producer JSONL audit:
`python -B Blender/benchmarks/capacity_audit/audit.py --input SOURCE.jsonl --output REPORT.json`.
Reports and raw artifacts belong in D:/E:, not Git.

`resource_policy.py` supplies conservative fp32 inference allocation estimates
BEFORE constructing any tensor/model: weights including biases, activations,
workspace, current whole-device usage, host temporary buffers and absolute cutoff.
It refuses host-first model construction when it would violate the 4 GiB RAM floor.
It does not enforce itself: the producer must call it and run a live owned-child
watchdog (18 GiB total device, RAM >=4 GiB, <=80 C, <=600s, cutoff 06:00 UTC).
# Recuperación del 30/09/2026

`batch_readback.py` contrasta X/W/Y guardados con una referencia float64 CPU y
recomputa Iris desde las partes real/imaginaria. Valida formas, clases, split,
valores finitos y casos de referencia cero; conserva hashes de cada artefacto.
Estos hashes identifican archivos actuales, no certifican inputs de un render
pasado. Es auditoría diagnóstica, no un gate preinscrito retroactivamente.

`guarded_job.py` lanza únicamente su propio hijo con preflight de memoria,
muestreo de RAM/VRAM/temperatura, timeout y cierre 06:00 UTC. Para una carga GPU
se invoca DENTRO de `gpuq.py run`; no modifica la cola ni mata procesos ajenos.
La estimación de memoria del caso debe ser conservadora y validada previamente.
Un guard no garantiza evitar un fallo del driver entre dos muestras.

`exr_controls.py` decodifica EXR con OpenCV CPU, sin usar bpy ni el consumidor.
Contrasta cada producto por píxel y reduce filas en float64; los controles de
peso/entrada/sham se revisan desde las cuatro EXR retenidas. No calcula ondas
ni certifica RT hardware. Esta inspección posterior es diagnóstica.

