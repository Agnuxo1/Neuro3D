# REWRITE-REPORT (P0-1 parte 2)

Repo D:/PROJECTS/9_NEBULA_NEW, sin commit ni add. Variable de entorno: NEURO3D_COGNITION_DIR (por defecto REPO_ROOT/.cognition).

## Resumen
- Archivos cambiados: 41 de 41 (rewrite-targets.txt). Líneas: +171 / -49.
- py_compile de los 41: OK.
- Congelados (17): SHA-256 idéntico a HEAD (17/17).
- Ningún .json ni .md tocado por esta tarea. Aparece `Docs/PATH_MAP.md` modificado y `Docs/WORKSPACE.md`, `Tools/workspace/` sin seguimiento: NO son de esta tarea (los cambió otro proceso).
- Reglas: 1 (REPO_ROOT con parents[N]: .cognition/x -> 2, Blender/tests -> 2, capacity_audit y research/optical_mesh -> 3), 2 y 3 (NEURO3D_COGNITION / "<X>"), 6 (import os añadido antes de `from pathlib import Path` cuando faltaba).
- Los tempfile con dir=... y los `directory = ... if os.name == 'nt'` conservan el subdirectorio (neuro3d, neuro3d-sequential-20261008) y crean la carpeta con mkdir(parents=True, exist_ok=True) justo antes de usarla (helper de una línea). Para dir='D:/PROJECTS/.cognition' se usa NEURO3D_COGNITION.

## Líneas por archivo (git diff --numstat)
| .cognition/neuro3d-mega-geometry-20261005/existing-p03-scene-invariants-oracle.py | +5 / -2 |
| .cognition/neuro3d-mega-geometry-20261005/existing_p03_backend_scope_oracle.py | +5 / -2 |
| .cognition/neuro3d-mega-geometry-20261005/existing_p03_cost_scope_final_integrity.py | +5 / -2 |
| .cognition/neuro3d-mega-geometry-20261005/existing_p03_cost_scope_oracle.py | +5 / -2 |
| .cognition/neuro3d-mega-geometry-20261005/next_chord_length_oracle.py | +2 / -1 |
| .cognition/neuro3d-mega-geometry-20261005/next_position_box_oracle.py | +2 / -1 |
| Blender/benchmarks/capacity_audit/exp005_peer_phaseB_gate_probe.py | +4 / -1 |
| Blender/benchmarks/capacity_audit/robust_first_hit_gpu_guard_v1.py | +3 / -1 |
| Blender/benchmarks/capacity_audit/scene_hilo_gpu_guard_v1.py | +3 / -1 |
| Blender/benchmarks/capacity_audit/test_pilot_watchdog_v1.py | +5 / -1 |
| Blender/research/optical_mesh/blender_mesh_scene.py | +2 / -1 |
| Blender/tests/exp005_cascade_diagnose.py | +4 / -1 |
| Blender/tests/exp005_complete_peer_review.py | +4 / -1 |
| Blender/tests/exp005_departure_replay_audit.py | +4 / -1 |
| Blender/tests/exp005_history_coplanar_review.py | +4 / -1 |
| Blender/tests/exp005_history_job_plan.py | +4 / -1 |
| Blender/tests/exp005_normal_residual_audit.py | +4 / -1 |
| Blender/tests/exp005_origin_enclosure_audit.py | +5 / -2 |
| Blender/tests/exp005_peer_field_replay.py | +4 / -1 |
| Blender/tests/exp005_relative_power_budget_audit.py | +4 / -1 |
| Blender/tests/exp005_rt_capability_review.py | +4 / -1 |
| Blender/tests/exp005_rt_finalization_review.py | +4 / -1 |
| Blender/tests/exp005_rt_report_audit.py | +4 / -1 |
| Blender/tests/exp005_scene_length_audit.py | +4 / -1 |
| Blender/tests/pr003_fresh_recompute.py | +4 / -1 |
| Blender/tests/test_captured_pilot_supervision_v1.py | +4 / -1 |
| Blender/tests/test_exp005_departure_replay.py | +4 / -1 |
| Blender/tests/test_exp005_history_artifact_data.py | +4 / -1 |
| Blender/tests/test_exp005_history_job_plan.py | +5 / -1 |
| Blender/tests/test_exp005_origin_enclosure.py | +5 / -2 |
| Blender/tests/test_external_cpu_reproduction_profile_v1.py | +4 / -1 |
| Blender/tests/test_frozen_geometry_training_v1.py | +5 / -1 |
| Blender/tests/test_frozen_indexed_profile_v1.py | +4 / -1 |
| Blender/tests/test_frozen_own_addon_profile_v1.py | +4 / -1 |
| Blender/tests/test_frozen_own_addon_profile_v2.py | +4 / -1 |
| Blender/tests/test_frozen_own_addon_profile_v3.py | +4 / -1 |
| Blender/tests/test_frozen_wave_profile_v1.py | +4 / -1 |
| Blender/tests/test_frozen_wave_profile_v2.py | +4 / -1 |
| Blender/tests/test_frozen_wine_profile_v1.py | +5 / -1 |
| Blender/tests/test_iris_native_admission_v1.py | +7 / -2 |
| Blender/tests/test_own_blender_runtime_v1.py | +6 / -2 |

## Literales conservados (regla 4)
- `.cognition/neuro3d-mega-geometry-20261005/existing_p03_backend_scope_oracle.py` línea 20: la clave 'D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states_v2.py' dentro de `result['code_sha256'][...]` se conserva: indexa un recibo congelado (p03_cuda_result.json). La lectura del archivo (línea 19) sí usa NEURO3D_COGNITION.
- Fuera de los 41 archivos no se ha tocado nada. Quedan sin cambios como constantes no ligadas a D:/PROJECTS: BLENDER = D:/TOOLS/Blender/... en los dos guards (otra ruta absoluta, fuera del alcance de la regla).
- Búsqueda final: `grep D:/PROJECTS` sobre los 41 devuelve solo la línea anterior.

## Pruebas (python -m unittest discover -v -s Blender/tests -p "test_*.py", NEURO3D_COGNITION_DIR=D:/PROJECTS/.cognition)
| Ejecución | Ran | fallos | errores | omitidas |
|---|---|---|---|---|
| ANTES snapshot git archive HEAD (head-raw.txt) | 1816 | 4 | 63 | 3 |
| DESPUÉS repo (after-raw.txt) | 1818 | 4 | 56 | 3 |
| DESPUÉS sin variable (without-env-raw.txt) | 1801 | 4 | 71 | 3 |
Listas: head-bad.txt, after-bad.txt, without-env-bad.txt (ERROR:/FAIL: ordenadas); head-results.txt y after-results.txt (pasa/falla por prueba, parseo aproximado; la referencia exacta son los *-bad.txt y los *-raw.txt).

### Diferencias ANTES vs DESPUÉS
El conjunto de fallos DESPUÉS es un subconjunto estricto del de ANTES; 7 pruebas fallan solo en el snapshot:
- test_exp005_history_job_plan.HistoryJobPlanCPU (setUpClass): 'incomplete frozen dependency pins'. El recibo congelado contiene rutas absolutas de D:\PROJECTS\9_NEBULA_NEW; el snapshot vive en otra ruta, así que no puede coincidir.
- 6 pruebas de test_scalar_job_launcher_cpu.LauncherTests: 'frozen child dependency changed', mismo motivo (rutas absolutas en pins).
No hay ninguna prueba que pase en HEAD y falle después de los cambios (comprobado en dos ejecuciones completas; una primera ejecución DESPUÉS mostró 4 errores extra de pins de iris.csv y fallos de RAM/Job, ver abajo).
Observaciones de método:
- Blender/demo_lattice_iris/iris.csv está en CRLF en el árbol de trabajo (HEAD lo tiene en LF, eol=lf); el snapshot lo tenía en LF. Para comparar en igualdad de condiciones copié el iris.csv del repo al snapshot y repetí la ejecución ANTES (la primera, con LF, queda en head-raw-run1-LFiris.txt). Es una condición previa del árbol de trabajo, no un efecto de mis cambios; explica los errores 'pin mismatch: iris.csv' que están en ANTES y DESPUÉS.
- Pruebas dependientes de RAM libre/tiempo (test_windows_job_tree_control_CPU_v1, test_own_blender_runtime_v1, test_scalar_job_launcher_cpu): la primera ejecución DESPUÉS (after-raw-run1.txt) tuvo varios errores extra por 'Se requieren 4000 MiB de RAM libre' y START_FAILED_CLOSED; en aislamiento pasan en snapshot y en repo, y la segunda ejecución completa no los muestra.

### Pruebas que dependen de artefactos externos (sin NEURO3D_COGNITION_DIR, REPO_ROOT/.cognition no tiene los artefactos)
15 errores adicionales respecto a DESPUÉS con variable (fallan por falta de artefactos en REPO_ROOT/.cognition/neuro3d):
test_exp005_departure_replay, test_exp005_history_artifact_data, test_exp005_history_job_plan, test_exp005_origin_enclosure (setUpClass); test_exp005_rt_report (setUpClass); test_exp005_normal_residual (2); test_exp005_rt_finalization (4); test_captured_pilot_supervision_v1 (3); test_exp005_history_coplanar (1). Lista exacta: `diff after-bad.txt without-env-bad.txt`.
Nota: no hay omisión explícita (skip) con mensaje claro; fallan por excepción de archivo.

## Pendiente para el coordinador
- Los 41 archivos cambian de SHA-256; si algún recibo congelado o prueba fija el hash de alguno de ellos, aparecería como fallo en DESPUÉS: no se observó ninguno (conjunto de fallos DESPUÉS ⊆ ANTES).
- Ejecutar `git diff` para revisar. Archivos auxiliares en este directorio: head-snapshot/ (puede borrarse), *-raw.txt, *-bad.txt, numstat.txt.
