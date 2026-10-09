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

## 2. Rutas absolutas `D:/PROJECTS/...`

Pendiente de la siguiente fase de este mismo trabajo (P0-1, parte 2). Se documentará aquí cada cambio de ruta en código y configuración. Los documentos congelados y los registros de coordinación no se reescriben: se listan aquí con su ruta relativa equivalente.
