# Neuro3D · optical lattice classifier (Iris), living in a Blender scene

![setosa](renders/iris_setosa.jpg)

A small optical neural network whose computation happens in a Blender scene. The only
trained parameters are the **positions of 16 mirror delay lines**, and every prediction is
made by **ray tracing the scene**.

| | |
|---|---|
| Network | 16 Mach–Zehnder cells (beam splitters, mirrors, one movable roof delay per cell) tiled on a 4 × 4 lattice, giving 8 optical modes |
| Task | Iris flowers (3 species), 4 features encoded as light amplitudes, plus one constant reference beam (an optical bias) |
| Decision | fully optical: the brightest of three detectors is the class, with no linear read-out layer |
| Training | inside Blender, numpy + Adam on 18 parameters (16 mirror delays, reference amplitude, temperature), about 36 s |
| Inference | `scene.ray_cast` from every source, splitting the ray tree at every beam splitter, then a coherent sum of `amp·e^{ikL}` at each detector |
| Hold-out accuracy (30 flowers) | **96.7 %** (train 98.3 %), measured by ray tracing the scene |
| Scene vs. training model | max power difference 4.1e-5 (float32 ray tracing) |
| Cost | ≈ 56 000 ray casts and ≈ 2 s per flower on one CPU thread |

<p>
<img src="renders/iris_versicolor.jpg" width="49%"> <img src="renders/iris_virginica.jpg" width="49%">
</p>

The beams are drawn with an emission proportional to the **coherent power** on each segment,
as computed by the ray tracer. The detector percentages are the measured detector powers.

## Run it

Headless (train, verify every flower by ray tracing, render three examples):

```bash
python run_blender.py "<path>/blender.exe" --train --verify --render renders
```

Live, in the Blender GUI:

```bash
blender renders/neuro3d_iris_lattice.blend --python neuro3d_iris_demo.py
```

The viewport opens in the camera view in rendered mode and the network **runs live**. Each
flower is ray-traced through the scene at that moment (about 2 s), the beams light up in
order of optical path length as the light propagates, and then the class detectors glow and
the prediction appears. The same *Play / Pause*, *Previous / Next* and *Build trained lattice*
controls are in **3D View › Sidebar (N) › Neuro3D**.

Tested with Blender 4.5 LTS (EEVEE Next for the render, numpy bundled with Blender).

## What is and is not claimed

* The scene **is** the network. Change a mirror and the prediction changes; the trained
  parameters exist only as object positions.
* Blender's ray tracer supplies which optic each ray hits and the path lengths. The wave
  interference (complex amplitudes) is summed in Blender's Python from those lengths:
  Blender does not simulate wave optics. This is a **simulation** of a free-space optical
  network, not a physical photonic measurement, and it claims no speed or energy advantage.
* The lattice geometry and the ray-traced path sum were validated separately against two
  independent CPU oracles, with interventions, a sham control, an ablation, and save/reopen
  gates (project experiment EXP-004 conf1).
* Iris is a toy task. The hold-out set is fixed (seed 0) and was not used for training or
  for choosing restarts.

Files: `neuro3d_iris_demo.py` (scene, training, ray-traced inference, render, panel),
`trained_lattice.json` (trained mirror delays), `scene_verification.json` (ray-traced
accuracy and model agreement), `iris.csv` (Fisher's Iris data, public domain).
