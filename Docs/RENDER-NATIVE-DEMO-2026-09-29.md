# Render-native coherent neuron · local validation

## What changed

The repository now includes a saved Blender scene whose detector materials
evaluate a coherent mixing equation and threshold activation during EEVEE
rendering. Scene-bound drivers deliver encoder X coordinates, wavelength, input
power and threshold. No Python field-summing function runs during inference.

Artifact: [Neuro3D_Render_Network.blend](../Blender/render_network_demo/Neuro3D_Render_Network.blend).
Source, reproduction and [compact measurements](../Blender/render_network_demo/verification.json)
are in `Blender/render_network_demo/`.

![Actual EEVEE render](assets/neuro3d-render-network.png)

## Evidence and acceptance

The constructor and verifier run in separate Blender processes, both with one
CPU thread and a 180-second limit. The verifier reopens the saved file, intervenes
on scene inputs, renders, and samples linear EXR pixels rather than display colors.
The first five tests were registered before execution; their initial maximum
absolute error was 0.000244140625, below 0.005. Detector-power balance had the same
worst error. XOR outputs were exactly 0, 1, 1, 0 in that readback.

Additional checks were registered before their own measurement: 17 continuous
phase samples, common-mode translation, and 12 live material/driver bindings.
All passed: the phase sweep's worst error was **0.0004237474 < 0.005**; common-mode
translation error was zero; all 12 graphs had live scene bindings. Blender
reported **NVIDIA GeForce RTX 3090, OpenGL**, not a presumed GPU backend.
The saved artifact SHA-256 is
`e4db8a06f3ea1fa90da63fd2e1717864c11b7c5cc43bd1e867623aae89eab757`.
A 32-bit output file does not establish 32-bit precision throughout
the rendering pipeline; no precision-source diagnosis is claimed here.

Both runs must acquire the shared GPU queue. Generated raw EXRs and logs remain
under `D:/PROJECTS/.cognition/neuro3d/`, outside the publication. No experiment
fixtures from EXP-004, Claude's worktree, or other unreviewed files are modified.
The decision is local: the JEV channel remains blocked and supplies no endorsement.

## Limits

This is one fixed coherent neuron with two phase inputs, two photodetection
channels and an electronic-style threshold. Four copies display its truth table;
they do not form a trained multicell network. The threshold's binary output is
not an optical energy channel.

The phase encoders use symbolic path offsets. Decorative beam curves do not
determine optical paths, and moving a drawn beam alone does not change inference.
Consequently this artifact does **not** close the full scene-owned wave transport
gate, replace the geometric EXP-004 result, simulate Maxwell equations, or turn
the GPU into physical optical hardware. It also does not establish an advantage
against a matrix multiplication implementation.

## Next falsifiable research gate

1. Export one trained lattice to a scene-owned, versioned optical circuit schema:
   topology, couplers, phase delays, wavelength and source amplitudes. Reject
   weights that the chosen physical topology cannot realize.
2. Compile that schema into GPU complex-field nodes or a custom wave kernel.
   Validate every complex output against an independent full-circuit oracle,
   not just classifications; preserve the raycast path for geometry readback.
3. For each deployed trained sample, verify that changing the scene's optical
   properties changes the rendered result, while appearance-only edits do not.
   Include losses, disconnected paths and coherent superpositions.
4. Only after correctness, pre-register comparisons with an optimized matrix
   implementation at matching accuracy/precision. Include upload, traversal,
   field accumulation, activation, readback, memory and power-measurement costs.

Claude's separately owned Iris lattice is a candidate source for step 1. Its
reported accuracy is not independently accepted in this report. Converting its
trained parameters to this execution route remains future work, not a claim
about the XOR artifact.
