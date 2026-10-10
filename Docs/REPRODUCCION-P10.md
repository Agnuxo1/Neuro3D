# Reproduccion desde cero (P10), 2026-10-09

Alcance: commit `1064825` (origin/main de https://github.com/Agnuxo1/Neuro3D.git). CPU, sin GPU, sin Blender/bpy,
sin instalar paquetes. Registros crudos fuera del repo: `D:\PROJECTS\.cognition\neuro3d-audit\p10\`.

## Entorno
Windows 10, Python 3.13.7. Versiones exactas en `requirements-lock-20261009.txt` (paquetes importados por Benchmarks\ y Tools\):
numpy 2.2.6, scipy 1.15.1, scikit-learn 1.4.0, pytest 9.1.1, matplotlib 3.10.0, psutil 6.1.1, pillow 10.4.0,
mpmath 1.3.0, torch 2.6.0+cu124. (`bpy`, `addon_utils` y los modulos propios solo aparecen en scripts de Blender: no reproducibles aqui.)
Aviso: el plugin de pytest `nengo` (4.1.0, no esta en el lock) es incompatible con pytest 9 (`startdir`); hay que desactivarlo con `-p no:nengo`.
Riesgo de entorno mixto: el user-site (numpy, scipy, pytest, matplotlib, torch, nengo) sobrescribe a `C:\Python313\Lib\site-packages`
(scikit-learn, psutil, pillow, mpmath). Con `python -I` salen otras versiones (numpy 1.26.4, pytest 8.4.1, torch 2.7.1+cu118) y el lock no lo dice.
`cv2`, `glfw` y `moderngl` solo se usan en `Blender\` (fuera del alcance declarado).

## Como reproducir (bash)
```bash
export PYTHONDONTWRITEBYTECODE=1 TMP='D:\tmp\tmp-p10' TEMP='D:\tmp\tmp-p10'
git clone -c core.autocrlf=false https://github.com/Agnuxo1/Neuro3D.git /d/tmp/neuro3d-clean-20261009
cd /d/tmp/neuro3d-clean-20261009 && git rev-parse --short HEAD        # 1064825
python -m pytest -p no:cacheprovider -p no:nengo -q -rfEs <--ignore de bpy/torch/GPU> Blender/tests Benchmarks/validacion-onda
(cd Benchmarks/coste-completo && python compilar_coste.py && git status --short .)   # vacio = identico
(cd Benchmarks/lineas-base/resultados && sha256sum -c SHA256SUMS.txt)  # ver nota de formato
(cd Benchmarks/limite-lectura && sha256sum -c resultados/SHA256SUMS.txt)
(cd Benchmarks/limite-lectura && python analisis.py)                   # ~330 s CPU, 1 proceso
```
IMPORTANTE: clonar con `core.autocrlf=false`. En Windows con la config por defecto (autocrlf=true) los `.txt` (listas SHA256SUMS y
logs) salen en CRLF, porque `.gitattributes` solo fija `eol=lf` para py/json/md/etc.: `sha256sum -c` falla (28 hashes de logs en
lineas-base, y los nombres de limite-lectura con `\r`). Se ha anadido `**/SHA256SUMS.txt text eol=lf` a `.gitattributes` (sin commitear);
PENDIENTE: la comprobacion con autocrlf=true solo es posible tras el commit.

## Clon
`git clone` de origin: HEAD = `1064825` (= origin/main = HEAD local). Arbol limpio tras checkout con autocrlf=false.

## Pruebas (detalle en `pruebas-clon.txt`)
| Config del clon | pasadas | falladas | errores | omitidas | subtests ok |
|---|---|---|---|---|---|
| autocrlf=false | 1688 | 71 | 47 | 1 | 501 |
| autocrlf=true (defecto Windows) | 1679 | 84 (no firme) | 47 | 1 | 497 |

La cifra 84 de autocrlf=true NO es firme: `pytest-raw-autocrlf-true.txt` contiene dos resumenes (74 failed / 1685 passed y 84 failed / 1679 passed; dos corridas escribieron al mismo fichero) y `fallos-autocrlf-true.txt` esta vacio (0 bytes). "13 mas por CRLF" no esta demostrado (con 74 serian 3). Falta una sola corrida limpia, en serie, guardando los fallos.
Omitidos: 17 archivos de Blender/tests (3 importan bpy/addon_utils/torch, 14 con GPU/CUDA/Blender en el nombre);
`Benchmarks/eeg-motor-imagery/.../test_nested_groups.py` (necesita datos EEG crudos no incluidos); 1 skip propio (`NEURO3D_EEG_RAW` no definida).
Desglose de los 118 fallos/errores (autocrlf=false; una linea `E  ` por caso en `pytest-raw.txt`; 71 failed + 47 errors):
| Categoria | Casos |
|---|---|
| `FileNotFoundError` en `.cognition\` dentro del repo | 32 |
| Pines y dependencias (54 `ValueError` + 1 `KeyError` `parent_oblique`) | 55 |
| `sealed_dependency_identity` | 15 |
| `torch` interop threads (dependen del orden de ejecucion) | 5 |
| `FileNotFoundError` otros | 7 |
| `AssertionError` | 4 |
| Total | 118 |

Los 7 `FileNotFoundError` otros: 3 rutas relativas `Blender\tests\test_existing_p03_backend_scope...` (probable `os.chdir` de `test_validacion_onda.py` al importar), 3 `tmp*\job\launcher_final.json`, 1 `eeg...\logs\full_persubject.log` (ignorado por git, ausente del clon).
Los 4 `AssertionError`: `0 != 4` (test_axial_native_presence_stops:114), `True is not false` (test_axial_tree_completeness_cpu:147), `False is not true` (test_exp005_retained_ledger_intervals:139) y `1.1703e-08 not less than 1e-08` (test_exp005_peer_fusion_bridge_cpu:26).
El `AssertionError` numerico (1,17e-8 frente a 1e-8) NO esta investigado: puede ser una diferencia real (version de numpy/scipy o CPU).
Los 8 `START_FAILED_CLOSED` (contencion por job object de Windows) solo aparecen en la corrida autocrlf=true (0 en `pytest-raw.txt`); encajan con concurrencia, no con CRLF.
Los pines pueden ser deriva real entre archivos pinados y fuente editada, o estado local no versionado; queda por separar (los 87 de pines y `.cognition` no distinguen ambos casos).
Riesgo de orden de tests: `test_validacion_onda.py` hace `os.chdir` al importar y rompe rutas relativas de otras pruebas; los 5 de `torch` tambien dependen del orden.

## Reproducciones con SHA-256
| Elemento | Resultado |
|---|---|
| `coste-completo/compilar_coste.py` (45 filas, 11 sin E_UB) | COINCIDE: TABLA-COSTE.json 2191834e..., TABLA-COSTE.md b057dfad..., INFORME-P1-9.md 2616b94f..., SHA256SUMS.txt f97f33b4... (git status limpio) |
| `coste-completo/SHA256SUMS.txt` (5 archivos) | COINCIDE (5/5) |
| `lineas-base/resultados/SHA256SUMS.txt` (183 archivos) | COINCIDE 183/183 comparando hash con el archivo (autocrlf=false) |
| `lineas-base/verificar_hashes.py --check` | Antes FALLABA SIEMPRE por dos causas: (1) formato (`hash  nombre` publicado frente a `hash *nombre` generado) y (2) cobertura: solo cubria 39 de las 183 lineas. Corregido (sin commitear): acepta ambos formatos y comprueba las 183 lineas; `--check` sale con codigo 0 (`OK 183/183`). Prueba: `Blender/tests/test_verificar_hashes.py` |
| `limite-lectura/resultados/SHA256SUMS.txt` (6 entradas) | COINCIDE 6/6; las rutas son relativas a `limite-lectura\`, no a `resultados\` (hay que ejecutar desde ahi) |
| `limite-lectura/analisis.py` (329 s) | NO coincide en SHA-256 de RESULTADOS_LIMITE.json/.md/resultados_raw.json ni de SHA256SUMS.txt, solo por tiempos: en RESULTADOS_LIMITE.json 1 campo (`segundos_totales` 144.4 -> 329.3) y en resultados_raw.json 80 campos `seg`. Todas las cifras (precisiones, rangos, perdidas, gradiente) son identicas a nivel de float |
Las cifras de tiempo de `TABLA-COSTE` dependen de `limite-lectura` (filas 35-36: 71.3/73.0 s publicado): tras volver a ejecutar `analisis.py`, `compilar_coste.py` da otra tabla. Orden correcto: comprobar coste antes de repetir el analisis, o restaurar con `git checkout`.
Archivos publicados sin tocar; el clon se restauro a HEAD tras las comparaciones.

## No reproducido y por que
- Tests con bpy/Blender/GPU (17 archivos), y todo `Blender/` ejecutable: sin bpy ni GPU por regla del encargo.
- `eeg-motor-imagery`, `benchmark-v1`, `escala-modos`, `lineas-base` (entrenamientos), `validacion-onda` (solver/FDTD, >10 min de CPU) y
  `capacidad-aprendizaje` (solo preregistro): omitidos por duracion o datos crudos ausentes; solo se verificaron sus hashes publicados.
- Torch en CUDA: no usado.

## Rutas absolutas restantes (busqueda `D:[/\]` en Benchmarks\ y Tools\, texto)
54 lineas en 12 archivos en el arbol de trabajo. Procedencia:
- 20 lineas en 6 archivos en commits (lo que ve el clon): AUDIT-EEG-NESTED.md 6, INFORME-NESTED.md 6, MANIFEST-SHA256.txt 2, AUDIT-P0-4.md 2, `Tools/unreal_preflight_v1.py` 1, `Tools/workspace/Initialize-Neuro3DWorkspace.ps1` 3. El unico codigo en commit es `unreal_preflight_v1.py:43` (candidato opcional `D:/TOOLS/Unreal/UE_5.6`).
- 32 lineas en 4 logs ignorados por git (no estan en el clon): seeds5 17, full_persubject 8, predict_var 6, full_shard0 1.
- 2 lineas sin commitear: `Benchmarks/validacion-onda/control_fijo/run_control.py:18` (codigo; trabajo no commiteado, no del commit `1064825`) e `INFORME-CONTROL.md:21`.
Ademas, 32 pruebas dependen de un `.cognition\` dentro del repo clonado.

Sumas regeneradas (HEAD e75cf3c): las tres sumas `Benchmarks/escala-modos/resultados/SHA256SUMS.txt`, `Benchmarks/escala-modos/sensibilidad/SHA256SUMS.txt` y `Benchmarks/validacion-onda/control_fijo/resultados/SHA256SUMS.txt` se regeneraron sobre el contenido commiteado (LF) porque las copias de trabajo estaban en CRLF; antes validaban 0 de 45, 5 de 6 y 2 de 17; despues, todas (45/45, 6/6 y 17/17). En escala-modos/resultados las rutas son ahora relativas a esa carpeta (`../analisis.py`, `log_malla.txt`, ...). `Benchmarks/capacidad-aprendizaje/resultados/SHA256SUMS.txt` no se toco y valida 45 de 45.
