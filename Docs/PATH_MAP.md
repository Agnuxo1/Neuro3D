# Mapa de rutas (PATH_MAP)

Este documento registra cada ruta cuyo contenido cambió de sitio durante la integración de `origin/main` en el repositorio local (2026-10-09). Ninguna versión se ha borrado: los dos lados están en el historial y el lado movido conserva sus bytes exactos.

## 1. Conflictos add/add resueltos (40)

Criterio: la versión canónica (ruta original) es la del lado con más dependencias. Para código, cuenta importadores por nombre de módulo; para el resto, cuenta referencias por nombre de archivo. Empate: se conserva la versión de `origin/main`. Un archivo que importa un módulo en conflicto sigue el lado canónico de ese módulo. La versión movida conserva sus bytes, salvo la línea de importación cuando su módulo también se movió.

Puntuación L/O: local / origin. Hash: SHA-256 (16 primeros caracteres) de la versión movida tal como se guardó.

| Ruta canónica | Lado canónico | Ruta de la versión movida | Lado movido | Criterio | Bytes | SHA-256 movida |
|---|---|---|---|---|---|---|
| `Blender/benchmarks/capacity_audit/original_SOURCE_query_packet_CPU_v1.py` | local | `Blender/benchmarks/capacity_audit/original_SOURCE_query_packet_CPU_v1_origin_20261006.py` | origin | importadores 3/1 | 6122 | `5ab941e2633af2ad` |
| `Blender/research/exp003/fixture.json` | origin | `Blender/research/exp003/fixture.local-20261009.json` | local | referencias 9/11 | 2862 | `0680c09df1cc9358` |
| `Blender/research/optical_mesh/results_cpu.json` | origin | `Blender/research/optical_mesh/results_cpu.local-20261009.json` | local | referencias 1/2 | 4410 | `f1f8284c241de0f1` |
| `Blender/research/optical_mesh/results_cpu_noleak.json` | origin | `Blender/research/optical_mesh/results_cpu_noleak.local-20261009.json` | local | referencias 2/3 | 4405 | `da3ccd3dd8c82a53` |
| `Blender/research/optical_mesh/results_cuda.json` | origin | `Blender/research/optical_mesh/results_cuda.local-20261009.json` | local | referencias 2/3 | 3187 | `f85fd22e2ae415b7` |
| `Blender/research/optical_mesh/run_exp.py` | origin | `Blender/research/optical_mesh/run_exp_local_20261009.py` | local | importadores 0/0 | 6082 | `febc4db982106863` |
| `Blender/research/optical_mesh/train_save.py` | origin | `Blender/research/optical_mesh/train_save_local_20261009.py` | local | importadores 0/0 | 2012 | `3b15e0a7541aa5e5` |
| `Blender/tests/test_original_SOURCE_query_packet_CPU_v1.py` | local | `Blender/tests/test_original_SOURCE_query_packet_CPU_v1_origin_20261006.py` | origin | importadores 0/0; sigue a original_SOURCE_query_packet_CPU_v1 | 6709 | `e6b3b43b530a2a54` |
| `coordinacion/respuestas/CAPACIDAD-CLAUDE-2026-09-30.md` | origin | `coordinacion/respuestas/CAPACIDAD-CLAUDE-2026-09-30.local-20261009.md` | local | referencias 3/3 | 6746 | `c2fe14623dfc9081` |
| `coordinacion/respuestas/EXP-005-REVISION-CLAUDE.md` | origin | `coordinacion/respuestas/EXP-005-REVISION-CLAUDE.local-20261009.md` | local | referencias 1/2 | 3979 | `2471a9ceacbd600b` |
| `coordinacion/respuestas/FIELD-ORACLE-CLAUDE.json` | local | `coordinacion/respuestas/FIELD-ORACLE-CLAUDE.origin-20261006.json` | origin | referencias 97/96 | 2712 | `c54d1f2d5a5146b7` |
| `coordinacion/respuestas/HISTORY-LINEAGE-CLAUDE.json` | origin | `coordinacion/respuestas/HISTORY-LINEAGE-CLAUDE.local-20261009.json` | local | referencias 3/4 | 4104 | `853cb2ecb563c276` |
| `coordinacion/respuestas/MI-ANIDADA-CLAUDE-2026-09-30.md` | origin | `coordinacion/respuestas/MI-ANIDADA-CLAUDE-2026-09-30.local-20261009.md` | local | referencias 2/3 | 8300 | `85909c5ef26f51c7` |
| `coordinacion/respuestas/MOTOR-ESCALA-ESTADOS-CLAUDE-2026-09-30.md` | origin | `coordinacion/respuestas/MOTOR-ESCALA-ESTADOS-CLAUDE-2026-09-30.local-20261009.md` | local | referencias 1/2 | 8350 | `4910718a2d38b4f7` |
| `coordinacion/respuestas/P0-1-FUSION-CLAUDE.json` | origin | `coordinacion/respuestas/P0-1-FUSION-CLAUDE.local-20261009.json` | local | referencias 3/4 | 17021 | `144c9a0e856e53e8` |
| `coordinacion/respuestas/P0-3-SCENE-STATES-CLAUDE.json` | origin | `coordinacion/respuestas/P0-3-SCENE-STATES-CLAUDE.local-20261009.json` | local | referencias 3/4 | 7570 | `205dde84b1746f94` |
| `coordinacion/respuestas/P0-3-SCENE-STATES-CUDA-CLAUDE.json` | local | `coordinacion/respuestas/P0-3-SCENE-STATES-CUDA-CLAUDE.origin-20261006.json` | origin | referencias 5/2 | 6781 | `b31215b524528b0a` |
| `coordinacion/respuestas/P0-4-RT-EQUAL-CLAUDE.json` | origin | `coordinacion/respuestas/P0-4-RT-EQUAL-CLAUDE.local-20261009.json` | local | referencias 3/4 | 6102 | `c0080c49c404d7b1` |
| `coordinacion/respuestas/P0-CRONOLOGIA-ERRATA-CLAUDE.json` | origin | `coordinacion/respuestas/P0-CRONOLOGIA-ERRATA-CLAUDE.local-20261009.json` | local | referencias 1/2 | 2721 | `7988490f3a0c2919` |
| `coordinacion/respuestas/P0-FUSION-BRIDGE-002-CLAUDE.json` | origin | `coordinacion/respuestas/P0-FUSION-BRIDGE-002-CLAUDE.local-20261009.json` | local | referencias 3/4 | 11221 | `6af0effd149b58bd` |
| `coordinacion/respuestas/P0-FUSION-POLICY-004-CLAUDE.json` | origin | `coordinacion/respuestas/P0-FUSION-POLICY-004-CLAUDE.local-20261009.json` | local | referencias 1/2 | 4667 | `06afba5bc0c21fa3` |
| `coordinacion/respuestas/P0-FUSION-POLICY-006-CLAUDE.json` | origin | `coordinacion/respuestas/P0-FUSION-POLICY-006-CLAUDE.local-20261009.json` | local | referencias 3/4 | 5682 | `6ab036b3547c595d` |
| `coordinacion/respuestas/P0-FUSION-POLICY-008-CLAUDE.json` | origin | `coordinacion/respuestas/P0-FUSION-POLICY-008-CLAUDE.local-20261009.json` | local | referencias 3/4 | 6825 | `d4c0ea6c8c5a8e34` |
| `coordinacion/respuestas/PHASE-COMPENSATED-CRITIQUE-CLAUDE.json` | origin | `coordinacion/respuestas/PHASE-COMPENSATED-CRITIQUE-CLAUDE.local-20261009.json` | local | referencias 4/5 | 4620 | `55bfcf2ce76bb894` |
| `coordinacion/respuestas/PHASE-SIGNED-CAPTURE-010-CLAUDE.json` | origin | `coordinacion/respuestas/PHASE-SIGNED-CAPTURE-010-CLAUDE.local-20261009.json` | local | referencias 23/24 | 4797 | `f867f7bc75c953ba` |
| `coordinacion/respuestas/PRECISION-004-CLAUDE.json` | origin | `coordinacion/respuestas/PRECISION-004-CLAUDE.local-20261009.json` | local | referencias 5/5 | 8697 | `61c3c099c8bb28a4` |
| `coordinacion/respuestas/PRECISION-005-CLAUDE.json` | origin | `coordinacion/respuestas/PRECISION-005-CLAUDE.local-20261009.json` | local | referencias 24/25 | 10812 | `c8afd752f4814a04` |
| `coordinacion/respuestas/PRECISION-006-CLAUDE.json` | origin | `coordinacion/respuestas/PRECISION-006-CLAUDE.local-20261009.json` | local | referencias 24/25 | 8921 | `9ef924612dc0d4b9` |
| `coordinacion/respuestas/PRECISION-006-REDUCTION-CLAUDE.json` | origin | `coordinacion/respuestas/PRECISION-006-REDUCTION-CLAUDE.local-20261009.json` | local | referencias 25/26 | 8079 | `2536c5307e63be55` |
| `coordinacion/respuestas/PRECISION-COMPLETE-001-CLAUDE.json` | local | `coordinacion/respuestas/PRECISION-COMPLETE-001-CLAUDE.origin-20261006.json` | origin | referencias 100/99 | 6175 | `e146c62499472c26` |
| `coordinacion/respuestas/RESUMEN-NOCHE-CLAUDE-2026-09-30.md` | origin | `coordinacion/respuestas/RESUMEN-NOCHE-CLAUDE-2026-09-30.local-20261009.md` | local | referencias 0/2 | 4145 | `13a9d7e969cd0d7d` |
| `coordinacion/respuestas/RT-CAP-002-CLAUDE.json` | origin | `coordinacion/respuestas/RT-CAP-002-CLAUDE.local-20261009.json` | local | referencias 3/4 | 10226 | `cb917152bf12a77a` |
| `coordinacion/respuestas/RT-CAP-003-CLAUDE.json` | origin | `coordinacion/respuestas/RT-CAP-003-CLAUDE.local-20261009.json` | local | referencias 2/3 | 5885 | `4c69829debcab3a8` |
| `coordinacion/respuestas/RT-CAP-004-CLAUDE.json` | origin | `coordinacion/respuestas/RT-CAP-004-CLAUDE.local-20261009.json` | local | referencias 1/2 | 3602 | `7c26c62823e23417` |
| `coordinacion/respuestas/RT-CAP-005-CLAUDE.json` | origin | `coordinacion/respuestas/RT-CAP-005-CLAUDE.local-20261009.json` | local | referencias 2/3 | 3172 | `50651adac705b01d` |
| `coordinacion/respuestas/RT-CAP-006-CLAUDE-FINAL.json` | origin | `coordinacion/respuestas/RT-CAP-006-CLAUDE-FINAL.local-20261009.json` | local | referencias 26/27 | 4480 | `c9ce72bdfab331b0` |
| `coordinacion/respuestas/RT-CAP-006-CLAUDE.json` | origin | `coordinacion/respuestas/RT-CAP-006-CLAUDE.local-20261009.json` | local | referencias 2/3 | 2579 | `e26efd4eb5eb914b` |
| `coordinacion/respuestas/RT-CYCLES-VS-BRUTA-CLAUDE-2026-09-30.md` | origin | `coordinacion/respuestas/RT-CYCLES-VS-BRUTA-CLAUDE-2026-09-30.local-20261009.md` | local | referencias 4/5 | 3194 | `afe2a8615bfc88f8` |
| `coordinacion/respuestas/RT-EQUAL-001-CLAUDE.json` | origin | `coordinacion/respuestas/RT-EQUAL-001-CLAUDE.local-20261009.json` | local | referencias 22/23 | 6459 | `3c2ef87e9b6e4680` |
| `coordinacion/respuestas/TRACE-ORACLE-CLAUDE.json` | origin | `coordinacion/respuestas/TRACE-ORACLE-CLAUDE.local-20261009.json` | local | referencias 1/2 | 3420 | `ba40eb2fd636e3af` |

Nota sobre el módulo de consolidación: `Docs/validation/consolidation-2026-10-06.json` registra `sha256 5ab941e2…` para `original_SOURCE_query_packet_CPU_v1.py` de origen. Esa versión está hoy en `Blender/benchmarks/capacity_audit/original_SOURCE_query_packet_CPU_v1_origin_20261006.py` con el mismo hash. Para el test de origen, `Blender/tests/test_original_SOURCE_query_packet_CPU_v1.py` (sha `e6b3b43b…`) queda en `..._origin_20261006.py` con una única línea distinta (la importación del módulo movido). El texto original sigue en el commit `63dee34`.

## 2. Rutas absolutas `D:/PROJECTS/...` en código Python

Inventario en HEAD (5401e1d): 58 archivos .py contienen rutas absolutas. Se separan en dos grupos según si su SHA-256 aparece en algún recibo JSON congelado del repositorio.

### 2.1 Reescritos (41): ya no dependen de D:/PROJECTS

Regla: raíz del repositorio = `Path(__file__).resolve().parents[N]`; artefactos externos = `NEURO3D_COGNITION_DIR` (por defecto `<repo>/.cognition`). Ver `Docs/WORKSPACE.md`.

| Archivo | Cambio |
|---|---|
| `.cognition/neuro3d-mega-geometry-20261005/existing-p03-scene-invariants-oracle.py` | rutas relativas / variable de entorno |
| `.cognition/neuro3d-mega-geometry-20261005/existing_p03_backend_scope_oracle.py` | rutas relativas / variable de entorno |
| `.cognition/neuro3d-mega-geometry-20261005/existing_p03_cost_scope_final_integrity.py` | rutas relativas / variable de entorno |
| `.cognition/neuro3d-mega-geometry-20261005/existing_p03_cost_scope_oracle.py` | rutas relativas / variable de entorno |
| `.cognition/neuro3d-mega-geometry-20261005/next_chord_length_oracle.py` | rutas relativas / variable de entorno |
| `.cognition/neuro3d-mega-geometry-20261005/next_position_box_oracle.py` | rutas relativas / variable de entorno |
| `Blender/benchmarks/capacity_audit/exp005_peer_phaseB_gate_probe.py` | rutas relativas / variable de entorno |
| `Blender/benchmarks/capacity_audit/robust_first_hit_gpu_guard_v1.py` | rutas relativas / variable de entorno |
| `Blender/benchmarks/capacity_audit/scene_hilo_gpu_guard_v1.py` | rutas relativas / variable de entorno |
| `Blender/benchmarks/capacity_audit/test_pilot_watchdog_v1.py` | rutas relativas / variable de entorno |
| `Blender/research/optical_mesh/blender_mesh_scene.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_cascade_diagnose.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_complete_peer_review.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_departure_replay_audit.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_history_coplanar_review.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_history_job_plan.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_normal_residual_audit.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_origin_enclosure_audit.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_peer_field_replay.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_relative_power_budget_audit.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_rt_capability_review.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_rt_finalization_review.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_rt_report_audit.py` | rutas relativas / variable de entorno |
| `Blender/tests/exp005_scene_length_audit.py` | rutas relativas / variable de entorno |
| `Blender/tests/pr003_fresh_recompute.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_captured_pilot_supervision_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_exp005_departure_replay.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_exp005_history_artifact_data.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_exp005_history_job_plan.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_exp005_origin_enclosure.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_external_cpu_reproduction_profile_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_geometry_training_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_indexed_profile_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_own_addon_profile_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_own_addon_profile_v2.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_own_addon_profile_v3.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_wave_profile_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_wave_profile_v2.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_frozen_wine_profile_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_iris_native_admission_v1.py` | rutas relativas / variable de entorno |
| `Blender/tests/test_own_blender_runtime_v1.py` | rutas relativas / variable de entorno |

### 2.2 Congelados (17): byte a byte, sin edición

Su SHA-256 aparece en recibos publicados; cambiarlos rompería la cadena de evidencia. Para ejecutarlos se requiere el diseño de carpetas de `Docs/WORKSPACE.md` (uniones creadas con `Tools/workspace/Initialize-Neuro3DWorkspace.ps1`).

| Archivo | SHA-256 (16) |
|---|---|
| `.cognition/neuro3d-mega-geometry-20261005/candidate_total_phase_oracle.py` | `c906aa476d727918` |
| `.cognition/neuro3d-mega-geometry-20261005/detector_connection_residual_oracle.py` | `009517caa274ddf9` |
| `Blender/benchmarks/capacity_audit/axial_reference_closure_cpu_v1.py` | `15f31f0b0d7bb38c` |
| `Blender/benchmarks/capacity_audit/axial_scene_closure_cpu_v1.py` | `45fa5d81fc54d68e` |
| `Blender/benchmarks/capacity_audit/exp005_peer_fusion_bridge_cpu.py` | `8d11b89d417a8081` |
| `Blender/benchmarks/capacity_audit/exp005_peer_phaseB_binding_probe.py` | `c8f65aea33e48686` |
| `Blender/benchmarks/capacity_audit/exp005_peer_phaseB_policy_probe.py` | `5c73b3c66355bf4c` |
| `Blender/benchmarks/capacity_audit/oblique_existing_evidence_inventory_HOST_v1.py` | `2de317fc4ed2d170` |
| `Blender/benchmarks/capacity_audit/scalar_job_supervisor_v1.py` | `60c174a00c4e407c` |
| `Blender/tests/exp005_phase_peer_probe.py` | `4abc6f3eed5baad2` |
| `Blender/tests/exp005_rt_pilot006_retained_audit.py` | `14a7a22213cd652a` |
| `Blender/tests/exp005_rt_readback_review.py` | `85d0c96713fa15b7` |
| `Blender/tests/test_axial_native_evidence_contract.py` | `c481ffeab79157bc` |
| `Blender/tests/test_existing_p03_backend_scope_HOST_v1.py` | `a78fc4e556f4230e` |
| `Blender/tests/test_existing_p03_cost_scope_HOST_v1.py` | `bcfc6c986eaa878b` |
| `Blender/tests/test_existing_p03_scene_invariants_HOST_v1.py` | `50453ca9829037e8` |
| `Blender/tests/test_exp005_retained_ledger_intervals.py` | `3bd2d170ffc54fa5` |

### 2.3 Raíces externas referenciadas (no están en git)

| Raíz esperada | Referencias en código | Presente en la máquina de origen |
|---|---|---|
| `D:/PROJECTS/.cognition/neuro3d` | 57 | sí |
| `D:/PROJECTS/.cognition/neuro3d-sequential-20261008` | 13 | sí |
| `D:/PROJECTS/.cognition/gpu_queue` | 3 | sí (herramienta de cola GPU) |

### 2.4 Copias de scripts dentro de `Docs/validation/`

Git las marca como binarias y contienen rutas absolutas. Son copias de evidencia congeladas: no se modifican.

Vease tambien `Docs/WORKSPACE.md` (diseno de carpetas y procedimiento de reproduccion).

### 2.5 Dependencia externa: ejecutable de Blender

Los dos guardas GPU (`robust_first_hit_gpu_guard_v1.py` y `scene_hilo_gpu_guard_v1.py`) contienen `BLENDER = D:/TOOLS/Blender/...`. Es el ejecutable de Blender, no un artefacto del proyecto. Queda fuera de la regla de reescritura y se documenta como dependencia del equipo de trabajo; no está en git.

### 2.6 Informe de la reescritura

El informe completo (antes/después de las pruebas, literales conservados y diferencias) está en `Docs/validation/p0-1-rutas-2026-10-09/REWRITE-REPORT.md`.

