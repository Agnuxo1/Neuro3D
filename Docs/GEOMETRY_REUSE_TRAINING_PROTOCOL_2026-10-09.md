# Full-cost comparison of geometric point audits and a continuous proof

Prepared before execution; human GitHub sequence authorization applies. External/IPFS identifiers remain null.

The [already published independent whole-family proof](GLOBAL_TRAINING_FAMILY_PROTOCOL_2026-10-09.md) establishes the prerequisite. This new [profile](research/geometry_reuse_training_profile_2026-10-09.json) runs two fresh workers sequentially on the same CPU core, with identical Iris120/30 data, 60 updates, initializer, own loss/gradient/Adam/native quantization and final independent geometric rebuild.

The original worker checks geometry at 61 optimizer states. The optimized worker independently audits the base, derives and compares all exact affine expressions, executes the entire continuous region proof afresh, and checks exact parameter membership at each of 61 states. This distinction is explicit in raw result schemas. The initial finite-difference perturbations are also checked. A proof failure, membership escape or incomplete output prohibits reuse. No earlier certificate is loaded to exclude proof overhead from timing.

Acceptance requires identical represented coordinates at every state, loss difference <=1e-11 at every state, final power difference <=1e-11 and all150 decisions equal, as well as unchanged numerical training gates. Loss-drop failure is a valid metric0; invalid/incomplete/parity-failed comparison has null metric. There is no prespecified minimum speedup: report the observed full ratio even if slower. One pair supplies no statistical timing interval.

Fixed per-worker cap900 s/total1900 s, one CPU, RAM >=4000 MiB/floor2500, RSS <=1500 MiB, aggregate evidence128 MiB. CPU proof/membership/final reconstruction costs are retained; no GPU or energy claim. Exact-family adversarial tests reject tampered/missing coefficients and the first represented value outside a box. Original code and evidence are retained.

Outcome at preparation: not executed. No optimized Blender add-on or physical fidelity claim follows from this external own-worker comparison.
