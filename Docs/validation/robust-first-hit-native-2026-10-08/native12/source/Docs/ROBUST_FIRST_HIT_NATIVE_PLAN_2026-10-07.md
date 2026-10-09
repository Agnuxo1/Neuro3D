# Point 5 — exact fail-closed first-hit native validation plan

Date: 2026-10-07. Frozen before the first native GPU dispatch.

## Scientific question

Can the point-4 scene hi/lo representation remove the known fixed-origin-bias and binary64 false-tie failures for first-hit selection while preserving exact contacts, legitimate later returns, surface triangulation equivalence, and fail-closed edge/degenerate/coplanar states?

This point does not claim physical ray uncertainty, phase correctness, full multi-bounce propagation, RT-core execution, speedup, or energy advantage.

## Frozen arithmetic contract

Every geometry/query hi/lo binary32 pair is decoded to its exact integer value scaled by 2^149. Möller–Trumbore subtractions, cross products, dot products, and hit numerators/determinants use signed 512-bit integer arithmetic. Candidate distances are ordered by exact positive rational cross-products using 1024-bit products.

There is no fixed origin bias, no t epsilon, no barycentric epsilon, no floating tie band, no global previous-primitive ignore, and no snap-to-plane repair.

Overflow, degenerate triangles and coplanar configurations stop fail-closed. Exact t=0 contact with the explicitly declared previous primitive may be excluded only for a valid departure event: mirror, t, or r. The same primitive remains eligible at every later positive distance.

Equal-distance triangles collapse to one surface only when they belong to the same scene object and their exact normals are parallel. Equal-distance candidates from different objects/surfaces remain TRUE_TIE. A unique edge/vertex hit remains BOUNDARY.

## Frozen input set

Manifest: Docs/validation/robust-first-hit-2026-10-07/inputs01/input_manifest.json
SHA-256: 1ba451212cc136442ea34a1ec9a7cefd44fdf366211f28813590f21b732ba800

Exactly 13 cases / 20 queries are required:
- 9 queries from retained real K3/K4 packets validated in point 4.
- Thin gaps 2^-53, 2^-54, and 2^-60 Blender units.
- Two coincident objects as a true-tie control.
- Exact previous-surface contact followed by a 2^-60 positive gap.
- A legitimate later return to the same previous primitive.
- A unique outer-edge hit.
- Coplanar ray.
- Degenerate triangle.
- Near-parallel direction -2^-100.
- Near-domain-limit coordinate control.

The expected result for every query is frozen in the manifest before GPU work.

## Acceptance gates

1. CPU selector/adversarial suite: 12/12 PASS.
2. Guard worker-gate suite: 4/4 PASS.
3. Pinned RTX 3090/OpenGL device through gpuq with fresh UUID, deadline, pins, resource admission and owned-process containment.
4. Exactly 20 compute dispatches and 20 complete readbacks.
5. Every input packet echoed bit-for-bit.
6. GPU status, selected primitive/object, tie mask, same-surface equivalence, exact-contact exclusion and exact t rational equal the frozen result.
7. K3/K4: all nine initial queries SELECT; equal-distance triangle pairs are equivalent triangulations of one surface.
8. Thin gaps: all three select the nearer surface; 2^-54 and 2^-60 must not collapse to a false tie.
9. Exact previous contact excluded only at t=0, then the 2^-60 next surface selected. A later positive return to the same primitive remains selectable.
10. Different-object coincidence returns TRUE_TIE; outer edge returns BOUNDARY; coplanar and degenerate controls remain fail-closed.
11. Worker inputs/code remain hash-identical; cleanup leaves zero owned processes.
12. A standard-library auditor imports none of selector/shader/Blender/GPU code, decodes the hi/lo wire independently, evaluates exact Fraction geometry and validates every retained raw readback.
13. Historical Nearest V2 and precision FAIL/STOP receipts remain unchanged.

## Resource bounds

One RTX 3090. Guard host/device reservations at most 2 GiB, at least 4 GiB host RAM remaining after reserve, projected VRAM no more than 18 GiB, temperature no more than 80 °C, work at most 100 s plus at most 10 s cleanup. gpuq provides exclusive ownership.

## Primary references

- Woop, Benthin, Wald, Watertight Ray/Triangle Intersection, JCGT 2013: https://jcgt.org/published/0002/01/05/
- NVIDIA, Solving Self-Intersection Artifacts in DirectX Raytracing: https://developer.nvidia.com/blog/solving-self-intersection-artifacts-in-directx-raytracing/
- Khronos GLSL 4.60: https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html

A PASS is limited to these finite packets, cases, implementation, GPU/build and exact arithmetic domain. It is not a universal theorem about all scene geometry or physical optics.
