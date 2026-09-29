# Neuro3D · Render-native coherent neuron

A small, self-contained Blender demonstration: two scene-owned phase inputs feed
an ideal coherent mixer, two square-law photodetectors and a threshold activation.
Four copies show XOR (dark port) and equality/XNOR (bright port) for
phase-encoded inputs 00, 01, 10 and 11. This is a fixed
optical-inspired neuron, not a trained general-purpose neural network.

Unlike the earlier hybrid raycast experiments, **material nodes calculate the
interference and activation during an EEVEE render**. Python builds the artifact
and reads test images; it does not sum fields during inference. CPU-evaluated
drivers still supply scene parameters to GPU shader uniforms.

## Use

Open `Neuro3D_Render_Network.blend` in Blender 4.5 and press F12. No add-on,
external model or running Python inference script is required. In Object
Properties, change the X coordinate of `Phase_A_0` by 0.05 Blender units: the first
output should turn on. Scene custom properties expose `wavelength_BU`,
`input_power` and `threshold`. The graph is editable in the Shader Editor.

The phase encoders are **symbolic path offsets**, not ray-traced mirrors. The
diagram's lines are explanatory geometry, not the source of transport lengths.
No claim of diffraction, physical optical computation, trained intelligence,
GPU efficiency or speed superiority is made. A renderer still does numerical
arithmetic. This complements, rather than replaces, the frozen EXP-004 geometry
experiments and the independent trainable Iris demonstration.

## Frozen tests (before first render)

The saved scene is reopened in a fresh Blender process. Linear 32-bit EXR pixels
at detector centers must match independent expectations within 0.005 absolute
power. Both analog ports must conserve the supplied power within the same bound.

| Intervention | Dark-port power across four lanes | Binary output |
|---|---|---|
| Baseline | 0, 1, 1, 0 | 0, 1, 1, 0 |
| First A encoder X +0.05 BU | 1, 1, 1, 0 | 1, 1, 1, 0 |
| First A encoder Y +0.15 BU (visual sham) | 0, 1, 1, 0 | 0, 1, 1, 0 |
| Wavelength 0.1 → 0.2 BU | 0, 0.5, 0.5, 0 | 0, 0, 0, 0 |
| Input power 1 → 0.5 | 0, 0.5, 0.5, 0 | 0, 0, 0, 0 |

The ideal dark-port equation is `P/2 * (1 - cos(2π(xA-xB)/λ))`; its complement
feeds the bright detector. Activation is dark power > 0.6. Test expectations
are only reference values, never written into shader output sockets.

Additional gates, pre-registered before their own first execution: a 17-point
phase sweep over one wavelength, common-mode translation of both encoders by
0.0317 BU, and a structural check of all 12 live detector shader graphs. These
use the same 0.005 bound. The binary output is an electronic-style activation;
it is not a third optical energy channel and is excluded from energy balance.

Published measurements are in [verification.json](verification.json). Rendering
times include readback and file I/O and are not a performance comparison.
Validated on Blender 4.5.14 LTS / RTX 3090 / OpenGL: five initial controls,
17 phase samples, common-mode translation and 12 live shader graphs passed.
Worst phase-sweep error: 0.0004237474 (absolute linear power, limit 0.005).

## Reproduce

Reserve GPU/RAM with the shared queue before executing these bounded commands.
Run the build and verification in separate Blender processes:

```text
blender --background --threads 1 --python-exit-code 1 --python build_demo.py -- --blend Neuro3D_Render_Network.blend
blender --background --threads 1 --python-exit-code 1 --python verify_demo.py -- --blend Neuro3D_Render_Network.blend --evidence evidence --preview preview.png
```

Build and verification each require their own resource reservation if run separately.
Do not interpret shader test success as validation of geometric propagation.
