# Full-cost comparison of geometric point audits and a continuous proof

Prepared before execution; human GitHub sequence authorization applies. External/IPFS identifiers remain null.

The [already published independent whole-family proof](GLOBAL_TRAINING_FAMILY_PROTOCOL_2026-10-09.md) establishes the prerequisite. This new [profile](research/geometry_reuse_training_profile_2026-10-09.json) runs two fresh workers sequentially on the same CPU core, with identical Iris120/30 data, 60 updates, initializer, own loss/gradient/Adam/native quantization and final independent geometric rebuild.

The original worker checks geometry at 61 optimizer states. The optimized worker independently audits the base, derives and compares all exact affine expressions, executes the entire continuous region proof afresh, and checks exact parameter membership at each of 61 states. This distinction is explicit in raw result schemas. The initial finite-difference perturbations are also checked. A proof failure, membership escape or incomplete output prohibits reuse. No earlier certificate is loaded to exclude proof overhead from timing.

Acceptance requires identical represented coordinates at every state, loss difference <=1e-11 at every state, final power difference <=1e-11 and all150 decisions equal, as well as unchanged numerical training gates. Loss-drop failure is a valid metric0; invalid/incomplete/parity-failed comparison has null metric. There is no prespecified minimum speedup: report the observed full ratio even if slower. One pair supplies no statistical timing interval.

Fixed per-worker cap900 s/total1900 s, one CPU, RAM >=4000 MiB/floor2500, RSS <=1500 MiB, aggregate evidence128 MiB. CPU proof/membership/final reconstruction costs are retained; no GPU or energy claim. Exact-family adversarial tests reject tampered/missing coefficients and the first represented value outside a box. Original code and evidence are retained.

Outcome at preparation: not executed. No optimized Blender add-on or physical fidelity claim follows from this external own-worker comparison.

## Resultado de la pareja completa

Perfil SHA `7ab66f8c775ce251d961c7ed8a7ed8cf20a7b948ab082ee8766fede6f9e11a70`, publicado en `aaf32b0003d947d1226ebfac95de96c8ffad67c0`; 34 fuentes y Git remoto verificados antes de ejecutar. Ambos workers completan las 60 actualizaciones, obtienen 110/120 y 27/30 aciertos, y coinciden exactamente en las coordenadas y la pérdida de cada uno de los 61 estados. Las 150 decisiones y todas las potencias finales también coinciden, diferencia máxima cero.

Coste completo: **393.11026100 s** con 61 auditorías puntuales frente a **90.92916110 s** con una nueva prueba continua y 61 comprobaciones exactas de pertenencia. Razón observada **4.323258×**, pareja total 484.317024 s, RSS agregado 70.129 MiB. La nueva prueba independiente cuesta 70.645067 s y la reconstrucción final 17.640743 s; las 61 comprobaciones de pertenencia cuestan 0.004205 s. El tiempo de prueba no se excluyó ni se cargó desde el resultado anterior.

Esta es una pareja en una máquina compartida, sin intervalo estadístico de tiempos, medida de energía ni garantía de velocidad universal. La optimización es una reutilización de una prueba continua exacta, no una reducción del contrato geométrico. No se incorpora aún al ZIP 0.1.2 ni establece rendimiento de NVIDIA/AMD. [Supervisor](validation/geometry-reuse-training-2026-10-09/attempt01/supervisor.json), [resultado optimizado](validation/geometry-reuse-training-2026-10-09/attempt01/reuse/result.json), [prueba ejecutada de nuevo](validation/geometry-reuse-training-2026-10-09/attempt01/reuse/continuous_family_proof.json), [índice](validation/geometry-reuse-training-2026-10-09/attempt01/evidence_index.json).
