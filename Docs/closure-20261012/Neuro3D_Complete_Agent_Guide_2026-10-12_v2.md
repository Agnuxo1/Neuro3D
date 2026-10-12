# Neuro3D: guía completa de ejecución y cierre científico para un agente

**Fecha:** 12 de octubre de 2026. **Autor de la guía:** preparación técnica para Francisco Angulo de Lafuente. **Idioma del documento:** español; todo el código nuevo del anexo está en inglés.

**Repositorio objetivo:** https://github.com/Agnuxo1/Neuro3D. **Base examinada:** `69db25ce7b04a98e24609bcd539c5041f269658d`, publicado el 10 de octubre. **Referencia matemática examinada:** https://github.com/openai/math, commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, del 8 de octubre.

Esta guía sirve para que otro agente continúe el proyecto con instrucciones concretas, controles y código de apoyo completo. No informa de que las tareas pendientes ya se hayan ejecutado. El anexo contiene herramientas comprobadas para oráculos geométricos, intervalos, sumas coherentes, comparación estadística, controles de ondas y trazabilidad. El backend nativo, el complemento y los entrenamientos completos existentes se obtienen del repositorio fijado; no se duplican miles de archivos ni se reemplazan por un programa de demostración.

> **Revisión v2 (12 de octubre de 2026, tarde).** Esta revisión es aditiva: el texto original se conserva íntegro y los once bloques de código del anexo son idénticos byte a byte (SHA256 en §22.3). Las correcciones y precisiones aparecen como notas «Revisión v2» junto al pasaje afectado; ninguna borra el original, y cuando una nota corrige un dato, prevalece la nota. Las secciones 22 a 39 son nuevas: comprobaciones ejecutadas, fe de erratas, qué exige una contribución de nivel Nobel, pasos K–R, referencias localizadas y un kit v2 con 24 regresiones adicionales. Lo que esta revisión afirma haber comprobado se ejecutó sobre `Agnuxo1/Neuro3D@69db25c` y `openai/math@fd4aeeb`; lo no comprobado se declara en §22.2.

## 1. Encargo que debe recibir el agente

Continúa Neuro3D desde la versión fijada, conserva la evidencia histórica y completa secuencialmente los frentes de esta guía. Antes de cada experimento, publica o compromete un protocolo identificable con fuentes, condiciones, semillas, métricas, tolerancias y regla de parada. Implementa cambios terminados, con documentación y código nuevo en inglés. Ejecuta los controles que correspondan al cambio, registra también resultados negativos y consolida documentación, interfaz y artículo.

El resultado buscado es un instrumento científico útil, delimitado, reproducible y preparado para crítica especializada. La aspiración de una aportación de nivel Nobel exige originalidad, relevancia y contraste independiente; ningún script, número de pruebas o presentación acredita ese reconocimiento por sí solo. Una investigación terminada puede contener hipótesis refutadas si el alcance y las conclusiones son correctos.

> **Revisión v2.** Lo que exige esa aspiración se concreta en §24 (criterios observables, situación actual de Neuro3D y decisión estratégica D0, que corresponde al propietario) y en los pasos K–R (§25–§33). Ninguno convierte la aspiración en resultado: fijan qué evidencia haría falta y cómo podría refutarse.

Trabaja sobre una rama y un directorio propios. Comprueba cambios concurrentes antes de editar. Usa `D:\PROJECTS` y `E:\Proyecto-concursos` en la estación del propietario, y una raíz explícita configurable en otras máquinas. No uses `C:` para nuevas simulaciones, cachés, entornos o artefactos grandes. No borres, renormalices ni republiques como nuevos los recibos congelados. La cadena `EXP-005-*` está cerrada: crea otro identificador para trabajo nuevo.

Avanza sin confirmaciones rutinarias dentro del trabajo técnico autorizado. Si faltan datos legítimos, hardware, una medida física o revisión por terceros, registra `BLOCKED`, explica la dependencia y sigue con los frentes independientes. No inventes resultados, identidades de revisores, permisos de datos, sellos de registro ni identificadores IPFS. No envíes correos, invitaciones, solicitudes editoriales ni documentación a terceros por iniciativa propia: prepara la entrega para que el propietario decida su envío.

Si una decisión técnica relevante no queda resuelta por evidencia, consulta JEV mediante la conexión disponible, conservando pregunta, respuesta, fecha, procedencia y confianza. Una respuesta de JEV es asesoramiento, no una prueba científica. Si no hay conexión, registra esa limitación y decide según el protocolo y la evidencia; no finjas haberlo consultado.

> **Revisión v2.** Registra cada consulta a JEV con `question`, `answer`, `date`, `provenance` y `confidence`; `validate_experiment_record` (§38) comprueba esos campos dentro de `jev_consultations`. Lo mismo vale para las evaluaciones de otros agentes (JEV, Codex u otros): son asesoramiento y auditoría útiles, no evidencia. No ajustes afirmaciones, umbrales ni conclusiones para mejorar una puntuación; si un evaluador señala un error, reprodúcelo, corrígelo con una nota fechada y conserva el rastro.

## 2. Qué existe y qué no debe confundirse

| Línea | Evidencia publicada | Límite que sigue vigente |
|---|---|---|
| Red capturada de Blender | 104 objetos, 6.656 triángulos, cinco fuentes, ocho modos; 133 estados y 17.060 ocurrencias de caminos terminales | Una familia escalar admitida, no todos los caminos de Maxwell ni cualquier escena imaginable |
| Aprendizaje geométrico | 16 parámetros, 60 actualizaciones y 61 capturas reales; guardado y reapertura | Topología, fusiones coherentes, pérdida y Adam siguen en CPU |
| Clasificación Iris | 110/120 entrenamiento y 27/30 test en una división ya utilizada | Las 150 observaciones mezclan entrenamiento y test; no son 150 ejemplos ciegos nuevos |
| Certificación numérica final | Cotas publicadas de campo y potencia; 150 decisiones separadas, 137 etiquetas correctas y 13 incorrectas | Decisión numéricamente certificada no significa etiqueta correcta ni fidelidad física |
| GPU residente | Ejecución real con eco binario de las cinco entradas | Error de campo `6.376147888196662e-8`, mayor que `1e-11`; variante rechazada |
| GPU y lotes | Seis pares 1/150/4096 con salidas equivalentes | La ruta gráfica es más lenta en todos esos pares; preparación y prueba también cuentan |
| Interfaz distribuida | Complemento CPU 0.1.3 y recuperación exacta ante una interrupción concreta del propietario | GPU en la interfaz, cortes eléctricos e interrupciones repetidas siguen pendientes |
| Wine ampliado | Media óptica 0,7910 frente a SVM 0,8676 en el benchmark publicado | No hay superioridad general establecida |
| Malla auxiliar de 64 modos | Digits: 0,9492; logística ajustada: 0,9703 | Modelo Clements auxiliar, no la geometría capturada de Neuro3D |
| Ondas P1-7 | Error máximo 0,026926 en λ/16 y 0,027519 en λ/24; límite 0,02 incumplido | Refutación acotada del modelo sin difracción de camino en ese régimen; red completa pendiente |
| EEG | Evidencia anidada y un preregistro nuevo de comparadores | La matriz libre no es una malla pasiva realizable; N1 y N2 no son intercambiables |
| Reproducción | Ejecuciones automáticas CPU y Blender en Linux externo | No sustituyen interpretación independiente humana; auditoría amplia de `1064825`: 71 fallos y 47 errores |
| Artículo | Borrador inglés de 14 páginas con fuentes | Autores pendientes, figuras enlazadas en el PDF y resultados recientes sin consolidar; no enviado ni revisado |

Fuentes de estas cifras: [registro de aceptación](https://github.com/Agnuxo1/Neuro3D/blob/69db25ce7b04a98e24609bcd539c5041f269658d/Docs/research/optic_neuro_blender_acceptance_v1.json), [estado conjunto](https://github.com/Agnuxo1/Neuro3D/blob/69db25ce7b04a98e24609bcd539c5041f269658d/Docs/PROJECT_STATE_AND_REMAINING_WORK_2026-10-09.md), [P1-7](https://github.com/Agnuxo1/Neuro3D/blob/69db25ce7b04a98e24609bcd539c5041f269658d/Benchmarks/validacion-onda/INFORME-EJECUCION-P1-7.md), [64 modos](https://github.com/Agnuxo1/Neuro3D/blob/69db25ce7b04a98e24609bcd539c5041f269658d/Benchmarks/escala-modos/INFORME-EJECUCION-P2-10.md), [reproducción P10](https://github.com/Agnuxo1/Neuro3D/blob/69db25ce7b04a98e24609bcd539c5041f269658d/Docs/REPRODUCCION-P10.md).

El resumen conjunto y el registro canónico están fechados el 9 de octubre y todavía llaman en curso a trabajos publicados después. La primera tarea de consolidación debe corregir esa diferencia temporal, conservando el texto y la evidencia histórica. Las cifras de la auditoría de `1064825` no se presentan como una ejecución de toda la suite en `69db25c`.

> **Revisión v2 — comprobación de la tabla.** Cada cifra se contrastó con archivos de `69db25c`. 104 objetos, 6.656 triángulos, 5 fuentes, 8 modos, 133 estados y 17.060 caminos: `Docs/SCIENTIFIC_ACCEPTANCE_REPORT_2026-10-09.md`. 16 parámetros, 60/61, 110/120, 27/30, 137/13, los pares 1/150/4096, el complemento 0.1.3 y la tolerancia `1e-11`: ese informe y `Docs/PROJECT_STATE_AND_REMAINING_WORK_2026-10-09.md`. `6.376147888196662e-8`: `Docs/NATIVE_RESIDENT_OPTICAL_GRAPH_PROTOCOL_2026-10-09.md`. Wine 0,7910 frente a SVM 0,8676: `Benchmarks/benchmark-v1/resultados/RESULTADOS_BENCHMARK_V1.md`. Digits 0,9492 frente a 0,9703: `Benchmarks/escala-modos/sensibilidad/resultados_sensibilidad.md`. P1-7: 0,026926 y 0,027519 redondean `0.02692643372060144` y `0.02751899213404152` de `Benchmarks/validacion-onda/resultados/RESULTADOS_VALIDACION.json`; el diagnóstico 0,0051/0,0046 está en el informe P1-7 y R = 0,58322 frente a 0,49702 en ese informe y en `control_fijo/resultados/RESULTADOS_CONTROL.md`. 71 fallos y 47 errores: `Docs/REPRODUCCION-P10.md`. El PDF del borrador tiene 14 páginas. No se encontró ninguna discrepancia. Un dato del informe P1-7 que la tabla omite: con los coeficientes r y t de un divisor 50/50 ideal, E_max sube a 0,0543; mide fidelidad del divisor, no coherencia modelo–solver, y no debe mezclarse con el E_max primario.

## 3. Fuentes de autoridad y orden de trabajo

Lee al inicio `Docs/GOVERNANCE.md`, `Docs/PROJECT_STATE_AND_REMAINING_WORK_2026-10-09.md`, `Docs/research/optic_neuro_blender_acceptance_v1.json`, `Docs/WORKSPACE.md`, `Docs/PATH_MAP.md`, `Docs/REPRODUCCION-P10.md` y los `AGENTS.md` que existan en el checkout de trabajo. No había `AGENTS.md` en el árbol fijado durante esta revisión; una versión posterior puede añadirlo.

> **Revisión v2.** Comprobado el 12-oct-2026: `69db25c` seguía siendo el HEAD de `main`, no contiene `AGENTS.md` y todos los documentos de esta lista existen. Si `main` avanza, aplica la regla del §4.1: conserva esta base para los resultados históricos y abre otro checkout para el commit nuevo.

El JSON canónico tiene **diez prioridades**. La lista conjunta tiene **once frentes**. El mapa histórico tiene **26 puntos**. Son tres vistas distintas, con numeraciones diferentes. El manifiesto auxiliar del anexo usa los once frentes y nunca sustituye ni cambia automáticamente los estados del JSON canónico.

| Paso de ejecución | Frente conjunto | Dependencia y entrega |
|---|---|---|
| A | 1: estado y procedencia | Inventario, contradicciones resueltas, matriz de afirmaciones y fuentes |
| B | 10: reproducción | Entornos separados, fixtures públicos, suite vigente limpia y archivo histórico accesible |
| C | 7: ondas | Nueva confirmación de difracción, convergencia del mismo dispositivo y validación progresiva de la red |
| D | 2: motor gráfico | Primera divergencia localizada, corrección versionada y equivalencia completa |
| E | 3 y 4: geometría y error | Familia adversa, presupuesto completo y decisiones UNKNOWN justificadas |
| F | 5 y 6: capacidad y generalización | Modelo delimitado, tareas nuevas y comparadores con ajuste equivalente |
| G | 8: rendimiento y hardware | Coste completo, escalado, ablaciones, energía y ejecución externa real |
| H | 9: producto y recuperación | Backend aceptado integrado, fallos controlados y usabilidad comprobada |
| I | 11: novedad e impacto | Comparación de métodos cercanos; aplicación útil demostrada con alcance explícito |
| J | 1 y 10: entrega final | Artículo actualizado, figuras incorporadas, paquete reproducible y crítica externa |

Termina cada paso o registra una dependencia externa concreta antes de pasar al siguiente. No repitas auditorías que no aporten nueva evidencia ni cambien una decisión. Conserva el rechazo de una variante y desarrolla una versión nueva; no relajes a posteriori sus tolerancias.

> **Revisión v2 — pasos añadidos.** Los pasos K–R amplían el orden anterior sin reemplazarlo:
>
> | Paso | Contenido | Sección | Cuándo |
> |---|---|---|---|
> | K | Pregunta central y teoría falsable (H-A a H-D) | §25 | Después de A; antes de F y G |
> | L | Teoría fundamental y núcleo verificado en Lean | §26 | En paralelo con C–F |
> | M | Demostrador físico (solo con D0-B) | §27 | Después de C y K |
> | N | Energía y latencia extremo a extremo | §28 | Con G |
> | O | Análisis ciego, equipo rojo y Registered Reports | §29 | Antes de cualquier ensayo confirmatorio nuevo |
> | P | Error a nivel de programa e inferencia secuencial | §30 | Transversal desde A |
> | Q | Réplica independiente y archivo abierto | §31 | Con J |
> | R | Autoría, uso de IA y ética | §32 | Con J y antes de cualquier dato humano nuevo |

## 4. Preparación del espacio y extracción del código

### 4.1. Checkout limpio en Windows

Ejecuta lo siguiente desde PowerShell. Crea un checkout nuevo y falla si ya existe; no toca un repositorio donde otro agente pueda estar trabajando.

```powershell
$projectRoot = 'D:\PROJECTS\Neuro3D-closure-20261012'
if (Test-Path $projectRoot) { throw 'The isolated checkout already exists.' }
New-Item -ItemType Directory -Force 'D:\PROJECTS' | Out-Null
git -c core.autocrlf=false clone https://github.com/Agnuxo1/Neuro3D.git $projectRoot
if ($LASTEXITCODE -ne 0) { throw 'Clone failed.' }
Set-Location $projectRoot
git checkout -b scientific-closure-20261012 69db25ce7b04a98e24609bcd539c5041f269658d
if ($LASTEXITCODE -ne 0) { throw 'Checkout failed.' }
git config core.autocrlf false
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:PIP_CACHE_DIR = 'D:\PROJECTS\pip-cache'
$env:NEURO3D_COGNITION_DIR = 'D:\PROJECTS\.cognition'
New-Item -ItemType Directory -Force 'D:\PROJECTS\Neuro3D-closure-runs' | Out-Null
git rev-parse HEAD
git status --short
```

Para una continuación posterior, conserva esa base para reproducir los resultados históricos y crea otro checkout del nuevo commit explícito. No reemplaces silenciosamente las fuentes de un experimento anterior por `main` actual.

> **Revisión v2.** Estos comandos PowerShell no se ejecutaron en Windows en esta revisión. El clon y el checkout de `69db25c` sí se ejecutaron en Linux y dieron un árbol limpio de 9.317 archivos.

### 4.2. Entornos

Usa tres entornos separados: **kit de apoyo** en CPython 3.12, **reproducción histórica** con las versiones efectivamente usadas por cada protocolo, y **Blender 4.5.14 LTS** con su Python/NumPy incorporados. No instales paquetes en el Python de Blender para hacer pasar pruebas del entorno de benchmarks. No se debe considerar `requirements-lock-20261009.txt` un lock universal: describe un entorno Windows mixto y contiene Torch con un sufijo CUDA que exige su distribución correspondiente.

Copia esta guía a `D:\PROJECTS\Neuro3D_Complete_Agent_Guide_2026-10-12.md`. Copia íntegramente el bloque `extract_support.py` del anexo a `D:\PROJECTS\Neuro3D-extract-support.py`. El nombre del script es una decisión de instalación; no hay funciones por completar. Después:

```powershell
py -3.12 'D:\PROJECTS\Neuro3D-extract-support.py' 'D:\PROJECTS\Neuro3D_Complete_Agent_Guide_2026-10-12.md' --root 'D:\PROJECTS\Neuro3D-closure-20261012' --write
if ($LASTEXITCODE -ne 0) { throw 'Support extraction failed.' }
Set-Location 'D:\PROJECTS\Neuro3D-closure-20261012'
py -3.12 -m venv .venv-support
if ($LASTEXITCODE -ne 0) { throw 'CPython 3.12 is required for this support environment.' }
$supportPython = Join-Path (Get-Location) '.venv-support\Scripts\python.exe'
& $supportPython -m pip install -r agent_support\requirements-closure.txt
if ($LASTEXITCODE -ne 0) { throw 'Support dependencies could not be installed.' }
& $supportPython -m unittest discover -s agent_support -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Support regressions failed.' }
& $supportPython agent_support\closure_evidence.py --repo . inventory --out 'D:\PROJECTS\Neuro3D-closure-runs\inventory-initial.json'
```

En Linux, usa una raíz de proyecto explícita y los mismos archivos extraídos:

```bash
python3.12 -m venv .venv-support
.venv-support/bin/python -m pip install -r agent_support/requirements-closure.txt
PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 .venv-support/bin/python -m unittest discover -s agent_support -p 'test_*.py' -v
```

Si Python, Blender, un compilador o un paquete exacto no están disponibles, el agente debe instalar o localizar la dependencia en esa raíz y registrar la versión. La guía no presupone que esas herramientas ya existan en cualquier equipo.

> **Revisión v2 — secuencia Linux completa.** El bloque Linux anterior omite la extracción y el cambio de directorio. Secuencia equivalente al bloque de Windows, con rutas explícitas que el agente elige:
>
> ```bash
> ROOT=/srv/neuro3d/Neuro3D-closure-20261012
> GUIDE=/srv/neuro3d/Neuro3D_Complete_Agent_Guide_2026-10-12_v2.md
> EXTRACTOR=/srv/neuro3d/Neuro3D-extract-support.py
> git -c core.autocrlf=false clone https://github.com/Agnuxo1/Neuro3D.git "$ROOT"
> cd "$ROOT" && git checkout -b scientific-closure-20261012 69db25ce7b04a98e24609bcd539c5041f269658d
> python3.12 "$EXTRACTOR" "$GUIDE" --root "$ROOT" --write
> python3.12 -m venv .venv-support
> .venv-support/bin/python -m pip install -r agent_support/requirements-closure.txt
> PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 .venv-support/bin/python -m unittest discover -s agent_support -p 'test_*.py' -v
> ```
>
> El kit v1 dio 33/33 con CPython 3.12.3, NumPy 2.3.5 y SciPy 1.17.0, y con CPython 3.13.16, NumPy 2.5.3 y SciPy 1.18.1. Si usas esta revisión, extrae desde el archivo `_v2` o cópialo con el nombre de destino del bloque de Windows: el extractor acepta cualquier nombre de guía.

### 4.3. Datos y recursos

Restaura los artefactos históricos desde la copia legítima del propietario usando el procedimiento de `Docs/WORKSPACE.md`. Para publicar reproducción nueva, elimina su condición de caché privado imprescindible: distribuye fixtures mínimos permitidos, generadores deterministas, hashes y un procedimiento para obtener los datos restringidos. Un hash de un archivo inaccesible identifica bytes, pero no hace reproducible el experimento.

Los perfiles GPU históricos fijan ruta/hash de Blender, UUID, nombre de GPU, suelo de RAM, límites y admisión por una cola externa. En particular, los lanzadores inspeccionados esperan una sola RTX 3090. Para el rig de seis tarjetas selecciona una GPU por **UUID** y construye un perfil nuevo que compruebe de verdad esa selección; no reutilices `gpu_sample()` que exige una sola fila ni simules admisión asignando manualmente `GPUQ_HOLDER=1`.

La reserva de memoria y la cancelación pertenecen al proceso y sus descendientes propios. No detengas otros trabajos ni mates todas las instancias de Blender. La prioridad de GPU del propietario no justifica falsear una reserva, una medición o un permiso de la estación.

> **Revisión v2.** `gpu_sample()` está definido en trece lanzadores `Tools/run_frozen_native_*` (por ejemplo, `Tools/run_frozen_native_resident_graph_v3.py`) y `GPUQ_HOLDER` aparece en esos trece, en dos lanzadores CUDA (`Tools/run_frozen_geometry_cuda_training_v1.py` y `Tools/run_frozen_trained_graph_cuda_v1.py`) y en `Blender/tests/exp005_signed_scalar_child.py`, `Blender/tests/test_signed_scalar_child_cpu.py` y `Blender/benchmarks/capacity_audit/scalar_job_supervisor_v1.py`. Revisa todos antes de escribir el perfil nuevo de seis tarjetas, para que ninguno siga exigiendo una sola GPU sin que lo sepas.

## 5. Paso A: consolidar estado, afirmaciones y procedencia

1. Genera el inventario con el código del anexo. Anota el HEAD exacto, archivos ausentes y módulos que cambian el directorio al importarse.
2. Lee los informes nuevos P1-7, control fijo, F4, P2-10, sensibilidad de logística y el preregistro EEG. Identifica qué sí se ejecutó, qué sigue siendo exploratorio y qué es solamente un plan.
3. Crea `Docs/closure-20261012/CLAIMS.md` con una fila por afirmación: modelo/familia, datos, resultado, fuente, SHA256, tipo de evidencia, interpretación permitida y limitación.
4. Actualiza mediante un commit el JSON canónico, README y resumen conjunto, según `Docs/GOVERNANCE.md`. Añade una entrada nueva al tablón sin editar las antiguas. No conviertas el piloto original de 90 segundos, que permanece NULL, en un éxito retrospectivo.
5. Marca F4 y 64 modos como estudios de malla auxiliar. Marca las observaciones EEG de `free` como modelo digital libre. Retira cualquier extrapolación de sus resultados a una red pasiva capturada o a un dispositivo fabricado.
6. Explica que el control con `n` fijo estabiliza E_max, pero su divisor grueso no está calibrado 50/50: `R≈0,583` frente a `R≈0,497`. No mezcles coherencia entre modelo/solver y fidelidad del divisor.

**Cierre:** cada cifra pública enlaza un resultado publicado y comprobado; no hay contradicción temporal sobre simulaciones en curso, superioridad, GPU residente o revisión externa. Los negativos aparecen en resumen y artículo. El manifiesto auxiliar conserva separados sus once frentes del JSON de diez prioridades.

> **Revisión v2.** Para el punto 1, el detector `module_scope_chdir` de `closure_evidence.py` encuentra en `69db25c` dos módulos, no uno (nota v2 del §6.1).

## 6. Paso B: reproducción desde cero y pruebas fiables

### 6.1. Reparaciones concretas

La auditoría P10 agrupa 118 fallos/errores: 32 por `.cognition`, 55 por pines/dependencias, 15 por identidad sellada, cinco por configuración de hilos Torch, siete por otros archivos ausentes y cuatro aserciones. Clasifica cada caso de nuevo en la base actual; no uses esa clasificación histórica como excusa para omitirlos.

> **Revisión v2 — categorías comprobadas y línea base en `69db25c`.** El desglose 32/55/15/5/7/4 coincide con `Docs/REPRODUCCION-P10.md` (Windows, pytest, commit `1064825`). Línea base nueva en `69db25c`, Linux: `python -m unittest discover -s Blender/tests -p "test_*.py"` con CPython 3.13.16, NumPy 2.5.4, SciPy 1.18.1, mpmath 1.4.1 y psutil, sin torch, sklearn ni bpy, y sin `NEURO3D_COGNITION_DIR`, da 1.344 pruebas, 5 fallos, 241 errores y 4 omitidas. Clasificación de los 246 casos: 122 por `.cognition` ausente; 50 por otros archivos ausentes; 15 `sealed_dependency_identity`; 35 de pines, dependencias congeladas o claves de recibos; 9 de control de procesos propio de Windows; 8 por módulos ausentes (torch 5, sklearn 2, bpy 1); 5 de colectores y relojes de trabajos GPU; 2 de la supervisión del piloto capturado. No es comparable uno a uno con P10 (otro commit, sistema y ejecutor), pero muestra el mismo patrón: el grueso depende de estado local y pines, no de aserciones numéricas. Aparte de cachés `__pycache__` ignorados por git, la suite no creó ni modificó archivos.

`Blender/tests/test_validacion_onda.py` ejecuta `os.chdir(RAIZ)` al importar. Elimina ese efecto en una versión no congelada o crea su sucesora si está pinada. Resuelve las lecturas de sus dependencias con `Path(__file__)` o rutas que reciban como argumento. La prueba de regresión debe comprobar que importar el módulo no cambia `Path.cwd()` y que ejecutar el resto de pruebas antes/después da el mismo resultado. Encapsular el problema con un `chdir` global en otro archivo no lo resuelve.

> **Revisión v2 — dos casos y un matiz.** El detector del kit encuentra dos `chdir` de importación en `69db25c`: `Blender/tests/test_validacion_onda.py:8` y `Benchmarks/eeg-motor-imagery/codigo/work/nested/predict_var.py:7`; el segundo fija además `FREQS` y `WIN` en `os.environ`. El cambio de directorio ocurre antes de las importaciones siguientes, así que persiste aunque la importación falle después (comprobado: sin `psutil` la importación se interrumpe con el directorio ya cambiado). Un fallo de recolección puede, por tanto, contaminar las pruebas posteriores.

Centraliza la política de hilos Torch al inicio de cada proceso; no invoques repetidamente `set_num_interop_threads` después de arrancar trabajo paralelo. Aísla ensayos incompatibles en procesos nuevos. El core del kit no usa Torch; su presencia en comparadores EEG o auditorías no obliga a adoptarlo como backend final.

Separa **pruebas vigentes**, **reproducciones de snapshots históricos**, **Blender nativo**, **GPU NVIDIA**, **GPU AMD**, **datos restringidos** y **experimentos largos**. Los pines históricos se validan contra sus fuentes históricas, no contra un módulo sucesor editado. No regeneres un pin para ocultar una dependencia rota. Registra la categoría y la justificación de cada exclusión.

### 6.2. Primera suite CPU

Tras instalar el entorno correspondiente al checkout, ejecuta estas regresiones existentes, con un proceso nuevo y desde la raíz:

```bash
python -m unittest Blender/tests/test_governance_consistency.py -v
python -m unittest Blender/tests/test_coherent_state_graph_v1.py -v
python -m unittest Blender/tests/test_state_graph_enclosure_v1.py -v
python -m unittest Blender/tests/test_surface_union_interior_v1.py -v
python -m unittest Blender/tests/test_robust_first_hit_exact_v1.py -v
python -m unittest Blender/tests/test_affine_geometry_network_v1.py -v
python -m unittest Blender/tests/test_escala_modos.py -v
python -m unittest Blender/tests/test_verificar_hashes.py -v
```

Una suite nueva de cierre debe añadir la ejecución de los componentes vigentes en orden normal e inverso y en otro directorio. Las pruebas externas que no tengan recursos devuelven `BLOCKED` o un skip explicado; el resumen no debe convertirlas en PASS. El conteo de pruebas aprobadas incluye su selección exacta.

> **Revisión v2 — resultado.** Las ocho regresiones pasan en `69db25c` en un único entorno limpio (Linux, CPython 3.12.3, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.7.2, mpmath 1.3.0), cada archivo en un proceso nuevo: 6, 8, 7, 8, 12, 5, 6 y 3 pruebas, 55 en total. `test_state_graph_enclosure_v1` necesita `mpmath` y `test_escala_modos` necesita scikit-learn (`load_digits`). El lock del proyecto no sirve para instalarlas: pip no puede resolver juntos sus `numpy==2.2.6`, `scipy==1.15.1` y `scikit-learn==1.4.0`. El workflow existente `.github/workflows/cpu-tests.yml` solo admite ejecución manual y no instala dependencias; en un entorno vacío equivalente da 1.259 pruebas, 5 fallos y 237 errores, 29 de ellos por módulos ausentes. El workflow sucesor `neuro3d_selected_cpu.yml` (§38) ejecuta estas ocho con dependencias fijadas y acciones fijadas por SHA; todavía no se ha ejecutado en GitHub.

**Cierre:** clon limpio y fuentes fijadas; todas las pruebas vigentes obligatorias pasan; los snapshots históricos se reproducen con sus fixtures y fuentes; hashes LF coherentes; ausencia de estado local oculto; otro entorno regenera resultados numéricos y decisiones dentro de los presupuestos fijados. Los tiempos se conservan como mediciones nuevas, no se exigen hashes idénticos a los de otra máquina.

## 7. Paso C: confirmar difracción y validar el modelo de ondas

### 7.1. Resultado que debe respetarse

El modelo sin difracción de camino incumple el límite de P1-7 en el régimen estudiado. El diagnóstico que añade propagación gaussiana mejora E_max a aproximadamente 0,0051/0,0046, pero fue exploratorio. Formula ahora una **confirmación nueva**, indicando que esos resultados ya se conocen. No la llames prueba ciega del hallazgo anterior.

Archivos a estudiar: `Benchmarks/validacion-onda/fdtd2d.py`, `mzi_fdtd.py`, `calibracion_fdtd.py`, `analisis_validacion.py`, `PREREGISTRO-P1-7.md`, `PREREGISTRO-P1-7-CONTROL.md` y los informes/resultados. `haz_ideal(..., difraccion=True)` ya existe; evita duplicar una corrección sin comprobar su dimensión, fase y normalización.

> **Revisión v2 — control independiente.** El propagador de espectro angular del kit (`closure_wave.py`), sin aproximación paraxial, reproduce la pérdida que el informe atribuye a la difracción libre: con w = 8λ y z = 95λ, el solapamiento con el modo de cintura es 0,973181, frente a 0,973210 de la fórmula paraxial 1/√(1+ζ²/4) con ζ = 2z/(kw²) ≈ 0,4725. La diferencia, 2,9·10⁻⁵, no cambia al ampliar ventana y malla, y es la corrección no paraxial. Confirma el número del diagnóstico en espacio libre; no valida el FDTD ni el divisor. Regresión en `test_closure_v2.py`.

### 7.2. Protocolo nuevo, completo y prospectivo

Fija antes de ejecutar: geometría física, índice/materiales, espesor, posición de cintura, convención temporal, fuente incidente, proyección compleja, planos de medida, PML, pasos temporales, ventanas DFT, mallas, fase y salidas. Mantén como referencia los presupuestos `E_max≤0,02` y diferencia de refinamiento `≤0,005` de P1-7. Justifica cualquier presupuesto nuevo con el margen de la tarea; no lo elijas porque pase el diagnóstico conocido.

Usa **el mismo dispositivo continuo** al refinar: no cambies `n`, dimensiones ni fuente para forzar R=T=0,5 en cada malla. Documenta cómo cada rejilla representa ese dispositivo. Refina a tres resoluciones cuando sea viable, además de dominio y PML; dos valores similares de E_max no separan todos los errores. La estimación de orden del anexo es diagnóstica, no una cota rigurosa ni una garantía de estar en régimen asintótico.

El barrido anterior tiene 12/18 posiciones discretas, no las 21 fases equiespaciadas del plan original. Para la confirmación elige una implementación que represente las 21 geometrías físicas fijadas: desplazamiento subcelda contrastado, fuente/fase equivalente derivada de la geometría, o un solver independiente que admita esa representación. No interpoles resultados y los cuentes como simulaciones. Un barrido restringido a posiciones de malla es una familia distinta y debe declararse así.

> **Revisión v2.** Según el informe, la diferencia de camino por celda es √2·h (0,0884λ a λ/16 y 0,0589λ a λ/24). Como √2 es irracional, ninguna malla permite, con traslaciones enteras, los 21 desfases jλ/20 exactos en esa geometría a 45°. Opciones para la confirmación, cada una preregistrada como lo que es: desplazamiento subcelda contrastado; fase equivalente en la fuente derivada de la geometría; o un dispositivo de otra familia con espejo a incidencia normal (tipo Michelson), donde la diferencia de camino es 2h por celda y una malla λ/40 da pasos exactos de λ/20. Si el coste crece como h⁻³ (2D más tiempo), esa malla costaría unas 4,6 veces la de λ/24: es una estimación por escalado que hay que medir. Un Michelson no es un MZI; su resultado no se transfiere sin justificación.

Mide el **campo complejo**, la amplitud modal, las potencias, el desfase circular y el balance energético adecuado al modelo. Cerca de un puerto oscuro la fase es indefinida; aplica el suelo prospectivo y conserva `None/UNKNOWN`. No alinees una fase libre distinta para cada punto usando los resultados del test. No normalices retrospectivamente la potencia total a uno para ocultar pérdidas de proyección o difracción.

La fórmula de haz de una dimensión transversal tiene factor de amplitud `sqrt(w0/w)` y Gouy `atan(z/zR)/2`; en dos dimensiones transversales son `w0/w` y `atan(z/zR)`. El anexo ofrece el primer caso y un propagador angular espectral independiente para control en espacio libre. Ni ese propagador FFT periódico ni el haz paraxial contienen el divisor, espejos, PML o la red entera.

### 7.3. Solver independiente y extensión a la red

Contrasta al menos vacío, película/divisor, espejo, MZI, una celda de la red, una subred y finalmente la red admitida. Meep es una opción de referencia electromagnética independiente: su documentación explica suavizado subpíxel y sus limitaciones. Úsalo con materiales, fuente y observable equivalentes; no afirmes que una comparación entre modelos distintos es un error numérico. Conserva scripts, versión y grids completos.

Para cada componente distingue error de discretización, dominio/PML, régimen transitorio, calibración, proyección, aproximación escalar/paraxial y error del modelo. Añade polarización/3D cuando la afirmación lo requiera. Ejecutar un MZI correctamente no valida por transferencia la red de 104 objetos.

**Cierre:** nueva confirmación aceptada o refutada con campo complejo y geometría invariables; todas las fases previstas contabilizadas; convergencia espacial, temporal y de frontera; negativos conservados; régimen de validez de la red completa cuantificado o explícitamente limitado. La tesis de simulador puede cerrarse con un régimen restringido bien demostrado; no con una fidelidad física universal sin evidencia.

## 8. Paso D: corregir el grafo óptico residente GPU

### 8.1. Localizar la primera divergencia antes de optimizar

Conserva los tres intentos rechazados y crea una versión nueva. Puntos principales: `Blender/blender_lab/native_resident_optical_graph_v2.py`, `native_graphics_gradient_v2.py`, `native_graphics_gradient_network_v2.py`, `Tools/audit_native_resident_graph_v3.py` y `Tools/run_frozen_native_resident_graph_v3.py`.

El shader residente recibe coeficientes locales obtenidos por consultas GPU reales, la topología admitida, cinco entradas y ocho salidas. Exporta, para cada uno de los 133 estados, identidad de superficie/primitiva, origen/dirección, parámetro/distancia, fase, coeficientes local primero/segundo, campo entrante, contribuciones salientes, sumas y correcciones. Conserva los bits antes/después de cada transporte. El anexo localiza la primera divergencia en una traza que cumpla ese contrato; no decide su causa por sí solo.

Ejecuta tres controles que aislen causas: **coeficientes GPU + recorrido CPU**, **coeficientes CPU declarados como control + recorrido GPU**, y **coeficientes GPU + recorrido GPU**. El segundo es una ablación de aritmética; no se publica como transporte desde superficies GPU. Mantén idénticos entradas, objetos, topología, λ, orden y suma de ramas. Solo después distingue generación de coeficientes, empaquetado, UBO/readback, recorrido y reducción.

Comprueba el tamaño y alineación exactos de cada paquete, offsets, índices de los cinco canales, orden topológico, terminales, eco de coeficientes y duplicación de contribuciones en pasadas. En la implementación actual hay dos draws para recuperar ocho puertos y uno para eco: no deben acumular dos veces un resultado ni usar un estado residual. El eco de entradas aprobado no demuestra corrección de coeficientes ni del recorrido.

### 8.2. Precisión hi/lo y aritmética nativa

Transporta palabras altas/bajas o bits binary64 sin una conversión intermedia a float32. Prueba la reconstrucción como racional exacto y el eco bit a bit. Una pareja hi/lo no recupera información que Blender ya perdió al almacenar un vértice en float32: el contrato debe separar geometría intención, geometría representada y words efectivamente enviadas.

Si se implementa aritmética de expansiones, verifica sus condiciones de error-free transforms, overflow/subnormales, FMA y optimización del compilador en el hardware real. No atribuyas automáticamente al shader las garantías de una emulación CPU. Usa predicados filtrados con fallback exacto como ruta explícita, midiendo su coste; no llames GPU puro a una selección geométrica corregida silenciosamente en CPU.

La reducción coherente preserva campos y sus derivadas. Integra sumas compensadas o por árbol con presupuesto independiente; conserva las contribuciones no nulas aunque su potencia individual sea pequeña. Diagnostica el error `6,38e-8`; no lo atribuyas a float32, Kahan, un driver o una caché sin un control que lo discrimine.

> **Revisión v2.** Dos técnicas establecidas ayudan a discriminar la causa del `6,38e-8`. (1) Reducción exacta y reproducible: acumular en punto fijo entero con bits suficientes, o con el esquema de ReproBLAS, hace la suma independiente del orden y del paralelismo; si la divergencia desaparece con ella, la causa estaba en la reducción. (2) Intersección *watertight* (Woop, Benthin y Wald, 2013), que Cycles incorporó, evita huecos entre triángulos vecinos en coma flotante. Si emulas doble precisión con pares float-float en GLSL, marca esas operaciones con el calificador `precise` cuando el dialecto de shaders de Blender lo admita, para impedir reasociaciones y contracciones, y compruébalo con vectores de prueba en el hardware real. Registra backend gráfico (OpenGL o Vulkan) y versión del driver: el compilador del shader cambia con ambos.

### 8.3. Pruebas de aceptación

Exige campos complejos, potencias, logits, Jacobianos cuando corresponda y decisiones, no solo argmax. Conserva el presupuesto de campo/potencia `1e-11` de la variante anterior como referencia; el certificado de cada salida debe soportar además su margen. Ejecuta controles de fase global, fase relativa, constructivo/destructivo/cuadratura, canal cero, todos cero y fases extremas. Repite los seis pares 1/150/4096 y el entrenamiento completo de 61 estados cuando se afirme entrenamiento nativo residente.

La caché se invalida por geometría evaluada, transformaciones/instancias, materiales, fuentes, detectores, coherencia, λ, parámetros, layout y versión de código. Guarda una identidad canónica, no `repr(scene)` como único contrato público. La ruta aceptada y la variante experimental deben tener estados de UI distintos.

**Cierre:** primera divergencia explicada y corregida; todas las salidas y etapas cumplen; oráculo independiente; fuentes/perfiles nuevos congelados; ejecución nativa real. La ventaja de rendimiento se evalúa después y puede resultar negativa sin invalidar la equivalencia numérica.

## 9. Paso E: geometría adversa y presupuesto completo de error

### 9.1. Familia geométrica obligatoria

Genera una familia prospectiva con huecos positivos ultrafinos, huecos inferiores a ULP, costuras compartidas, bordes exteriores, contactos t=0, autoimpactos, retorno al mismo objeto, casi paralelos, degenerados, empates entre superficies distintas, instancias con escala no uniforme, coordenadas grandes y caminos pequeños que cancelen caminos grandes. Fija las geometrías como racionales y sus conversiones nativas; incluye casos no representables cuyo resultado correcto sea rechazo/UNKNOWN.

El oráculo del anexo realiza selección first-hit **exacta sobre los valores suministrados**, conserva empates/contactos y reconoce triángulos coincidentes de un mismo plano/objeto. No prueba una vecindad interior del soporte ni la completitud de un BVH; para eso usa/amplía `surface_union_interior_v1.py`, `exact_object_index_v1.py` y la auditoría independiente ya existente. No excluyas un objeto entero para evitar autoimpactos: distingue la primitiva de partida, el contacto demostrado y un impacto posterior legítimo.

> **Revisión v2 — rutas y oráculo.** `surface_union_interior_v1.py` no existe en `69db25c`: la prueba `Blender/tests/test_surface_union_interior_v1.py` importa `select` y `vector` de `Blender/benchmarks/capacity_audit/robust_multipath_v1.py`, y `exact_object_index_v1.py` está en ese mismo directorio. Además, `exact_first_hit` del kit devuelve UNKNOWN en cuanto encuentra un triángulo degenerado o coplanar, aunque esté detrás del origen o más lejos que un impacto ya probado (reproducido: un degenerado en t = 50 anula un impacto válido en t = 1). `exact_first_hit_v2` (§38) usa que el parámetro del rayo es lineal sobre el triángulo: un primitivo diferido solo bloquea si el rango exacto de proyecciones de sus vértices corta [0, t_mejor]. En 573 casos aleatorios en los que v1 no encontró primitivos diferidos, v2 devuelve exactamente lo mismo que v1.

Si dos ramas se fusionan, demuestra igualdad de estado y de operador futuro; para gradientes también de las tangentes relevantes. Sumar intensidades elimina interferencia y cambia la función. Si se descartan ramas, aporta una cota de **suma de amplitudes** omitidas que abarque todas las descartadas; un umbral por potencia individual no basta.

Los ciclos deben devolver estado incompleto/unsupported mientras no exista un modelo de realimentación admitido. Para cerrar una recurrencia física lineal, deriva `E=(I-A)^{-1}b`, acredita existencia/estabilidad y acota la cola. Si una norma certificada satisface `||A||≤r<1`, la cola de Neumann tras K es a lo sumo `r^(K+1)||b||/(1-r)`. Un radio espectral estimado numéricamente no equivale a esa norma certificada; un ciclo ideal sin pérdidas puede ser resonante. No publiques un límite de pasos arbitrario como recorrido completo.

> **Revisión v2.** La cota de la cola exige una norma inducida (submultiplicativa y compatible con la de b) y la misma para A y para b. Si A se acota en otra norma, convierte con constantes de equivalencia explícitas.

### 9.2. Cadena de incertidumbre

Mantén presupuestos separados: captura/preimagen; cuantización; transformación; dirección; selección/empate; reflexión; longitud óptica; λ/índice/material; fase; producto complejo; reducción; detector; decisión; gradiente; y modelo físico. Un certificado posterior de salidas observadas no prueba por sí solo todos los operadores nativos posibles.

Para un camino con λ positiva, una cota conservadora de perturbación de fase es:

$$|\delta\phi|\le 2\pi\left(\frac{|\delta L|}{\lambda_{\min}}+\frac{L_{\max}|\delta\lambda|}{\lambda_{\min}^2}\right)+|\delta\phi_{\mathrm{material}}|.$$

Si el medio no es uniforme, L representa longitud óptica o incluye de forma explícita el índice; no uses longitud geométrica como sustituto. La sensibilidad de selección de rama necesita su propio margen. Fuera de una caja topológica admitida, subdivide o devuelve UNKNOWN.

> **Revisión v2.** En la cota de fase, λ_min y L_max se toman sobre toda la caja de incertidumbre, no en el valor nominal, y λ debe ser positiva en toda ella; así la cota se sigue del teorema del valor medio aplicado a φ = 2πL/λ.

Para un campo observado con cota `A≥|E_obs|` y error `e≥|E_true-E_obs|`:

$$|P_{true}-P_{obs}|\le 2Ae+e^2.$$

Certifica una clase solo si su límite inferior de potencia supera todos los superiores competidores. Si los intervalos se solapan, conserva UNKNOWN. Usa cotas absolutas cerca de cancelación; el error relativo es indefinido en un cero.

El código racional del anexo encadena coordenadas→longitud→fase→campo→potencia→decisión. Incluye pi mediante Machin, raíces con integer arithmetic y restos de Taylor; no toma `math.pi` como exacto. Sirve de control independiente y para casos pequeños. Para los 17.060 caminos, utiliza el DAG y los intervalos existentes, con refinamiento/precisión adaptativos: no expandas sin necesidad todos los caminos con Fraction.

> **Revisión v2 — crecimiento de los racionales.** Medido con el kit v1: el radio de un solo fasor llega a 16.399 bits de denominador, la potencia de un campo oscuro de dos caminos a 33.379 bits y 64 caminos tardan 1,05 s. Ese crecimiento hace inviable incluso la verificación independiente de subredes medianas. `tighten` redondea los extremos hacia fuera a una rejilla 2^-bits, conservando la inclusión, y `unit_phasor_v2` y `coherent_field_v2` lo aplican tras cada operación y eligen el orden de Taylor según la precisión pedida: en las pruebas, ≤ 161 bits por extremo y anchuras < 2^-100.

Para gradientes, define qué derivada existe: el modelo continuo admitido, la extensión geométrica elegida o la función cuantizada nativa. La cuantización hace discontinuidades; no llames a diferencias finitas de una extensión una derivada universal del programa. Acota todas las tangentes que se reivindiquen y conserva cambios de rama/UNKNOWN.

**Cierre:** presupuestos derivados de entradas y operaciones reales; todas las ramas cubiertas o descartadas con cota; decisiones robustas con margen; separación explícita de errores desconocidos del modelo físico y de medidas. No se exige afirmar robustez donde el problema realmente sea indeterminado.

## 10. Paso F: capacidad, entrenamiento, generalización y EEG

### 10.1. Qué puede representar el modelo

Con geometría fija, el campo es lineal: `E=U(θ)x`. Un detector con entrada real tiene `P=xᵀQx`, `Q=aaᵀ+bbᵀ`, rango a lo sumo dos; una diferencia entre dos detectores tiene rango a lo sumo cuatro. Una cascada pasiva no introduce activaciones intermedias. Conserva ese límite y el papel de codificación/normalización.

> **Revisión v2.** Con codificación compleja (fase en la entrada), cada detector es P = xᴴ(uᴴu)x, una forma hermítica de rango 1. Y como argmax |cWx|² = argmax |Wx|² para todo c > 0, en decisiones `argmax` la clase libre y la pasiva coinciden: la pasividad solo restringe con ganancia de detección o presupuesto de fotones fijos. La comparación informativa es la de H-A (§25): formas cuadráticas generales frente a la clase lineal, y la clase lineal frente a la realizable por la geometría. `train_detector_classifier`, `project_passive`, `numerical_jacobian` y `effective_rank` (§38) dan el comparador y la dimensión local de U(θ).

Comprueba condicionamiento, rango, isometría, cajas robustas y reinicios. La isometría de los ocho puertos del modelo representado no equivale a conservación del flujo físico calibrado. Si introduces no linealidad, pérdidas, entrenamiento interno o recurrencia, formula un modelo nuevo, identifica sus operaciones y compara su aportación; no reutilices certificados del modelo pasivo.

F4 tiene sensibilidad al ruido y límites de inferencia: un criterio sobre estimaciones puntuales no acredita por sí solo equivalencia estadística. Un p=1 en diez diferencias cero carece de información para demostrar igualdad. Usa márgenes e intervalos fijados, y corrección de multiplicidad cuando corresponda.

### 10.2. Evaluación general

Separa desarrollo, validación y una prueba final que no se use para elegir arquitectura, fases, reinicio o codificador. Iris y las divisiones ya observadas de Wine/Digits son históricos o exploratorios. No los transformes en datos confirmatorios por cambiar el nombre del script.

Elige tareas nuevas donde la certificación geométrica tenga utilidad: decisiones sensibles a fase, transferencia a nuevas perturbaciones de geometría, detección de entradas fuera de contrato y variaciones de iluminación/coherencia. Incluye un caso deliberadamente difícil o negativo. Justifica el tamaño de muestra con el efecto/margen buscado y la unidad estadística; nuevos puntos geométricos no son nuevas observaciones biológicas.

Iguala entradas, preprocessing, número de parámetros relevante, presupuesto de búsqueda, precisión y entrenamiento de comparadores. Reajusta preprocessing **dentro** de cada fold interno. Incluye operador matricial equivalente, logística afinada, cuadrático y modelos adecuados a la tarea. No exijas CNN/Transformer en una tarea donde no tengan el mismo objetivo.

La sensibilidad publicada de 64 modos identifica sobre-regularización de la logística original. Repite con búsqueda interna de todos los modelos. Mantén separada esa malla auxiliar de la implementación desde escena capturada; para incorporar Breast Cancer/Digits a Neuro3D hay que definir y ejecutar realmente fuentes/detectores/encoding compatibles, no trasladar resultados de otra arquitectura.

Las divisiones 80/20 repetidas se solapan. Usa un modelo de incertidumbre adecuado; el anexo ofrece la corrección aproximada de resampling y un bootstrap **por unidades independientes**, no una excusa para bootstrap de splits dependientes. Para varias hipótesis, ajusta multiplicidad y reporta tamaños de efecto. La inexistencia de significación no demuestra equivalencia.

> **Revisión v2.** Para equivalencia, el intervalo que se pasa a `comparison_label` debe ser de nivel 1−2α (90 % para α = 0,05), el que corresponde a TOST; para diferencias direccionales, el habitual 1−α. Usar el mismo intervalo para las dos lecturas mezcla dos pruebas distintas. `tost_paired` (§38) devuelve ambos p-valores unilaterales y el intervalo adecuado. Si un protocolo quiere mirar resultados conforme llegan, usa el proceso-e de §30 en lugar de repetir pruebas clásicas.

### 10.3. EEG: completar el preregistro vigente

Lee `Benchmarks/eeg-motor-imagery/comparativa-anidada/PREREGISTRO-EEG.md`. La comparación principal allí fijada es **N1**, selección interna por sujeto/pliegue; el 0,7274 de N2 pertenece a otra selección y no se usa como primario de H1/H2. Verifica fold por fold los índices almacenados, normalización, CSP y selección; no accedas a etiquetas del test oculto.

Implementa los módulos completos de ejecución/analizador que falten con las funciones existentes `outer_folds`, `inner_folds`, `csp_filters` y EEGNet de `bench.py`. Rejillas: FBCSP cuatro conjuntos de bandas por nueve C; EEGNet tres lr por dos lotes por dos decay por tres snapshots; 36 configuraciones por familia. El preregistro contiene valores, semillas y desempates exactos: consérvalos.

> **Revisión v2 — rutas.** `outer_folds` e `inner_folds` están en `Benchmarks/eeg-motor-imagery/codigo/work/nested/nested_bench.py` (líneas 43 y 48); `csp_filters` (línea 125) y la clase `EEGNet` (línea 96), en `Benchmarks/eeg-motor-imagery/codigo/work/bench.py`. `nested/predict_var.py` cambia de directorio y fija `FREQS` y `WIN` en `os.environ` al importarse: no lo importes desde otros módulos ni desde pruebas.

Mide un pliegue antes de lanzar las horas de trabajo, tal como permite el plan ya fijado. Si el coste supera tres horas, conserva la estrategia parcial predeclarada por sujetos completos y la restricción de conclusión. Reporta FBCSP/EEGNet en el mismo bucle anidado, el sesgo residual del diseño óptico conocido y los resultados de la subfamilia físicamente realizable por separado.

La regla vigente combina intervalos y Holm de forma imperfecta: conserva su conclusión primaria y añade sensibilidad con control de multiplicidad de intervalos como análisis distinto. No cambies el primario tras ver resultados. La próxima confirmación debe resolver prospectivamente esa política. Explica la diferencia entre puntuación pública Kaggle y LORO; para generalización a sujetos/sesiones nuevos hacen falta datos nuevos legítimos.

> **Revisión v2.** Generalizar a sujetos o sesiones nuevos con datos propios exige aprobación previa de un comité de ética, consentimiento informado y tratamiento conforme al RGPD. El agente no recoge datos humanos; prepara el protocolo para que el propietario lo tramite (§32).

**Cierre:** tareas nuevas con test reservado, preprocessing sin fuga, selección equivalente, medidas de incertidumbre válidas, negativos y semillas completos. La utilidad puede ser certificación, robustez o coste; no es obligatorio ganar en todas las exactitudes, pero toda ventaja reivindicada debe estar probada.

## 11. Paso G: rendimiento, energía, escalado y ablaciones

### 11.1. Primero identifica el cuello de botella

Instrumenta captura, transformación/triangulación, BVH/candidatos, prueba exacta, generación de coeficientes, packing, allocation, uploads, compilación, kernel, sincronización, readback, suma, detector, pérdida y actualización. Usa timers de GPU sincronizados y reloj monótono para coste total. Los contadores lógicos de bytes no son tráfico PCIe medido.

El resultado existente tiene mucha preparación, asignaciones/readbacks y trabajo gráfico por muestra. Prueba buffers persistentes, packing, lotes, recorrido residente corregido y reutilización de pruebas de una familia continua. Desactiva una optimización por vez y conserva salidas equivalentes. Mide el beneficio a 1, 150 y 4096 entradas y en escenas nuevas, sin elegir únicamente el lote favorable.

Como comparador indispensable, compila `U` desde las respuestas a las cinco bases de la geometría admitida. `compile_operator`/`apply_operator` del anexo implementan esa operación para un forward lineal completo. Invalida U al cambiar geometría/materiales/λ y mide recomputación y prueba. La multiplicación matricial cacheada es una ruta declarada distinta del trazado gráfico directo; su velocidad no se atribuye a hardware RT.

Para derivadas reutilizables, construye `∂U/∂θ_j` desde bases y tangentes geométricas comprobadas, y valida `∂E/∂θ_j=(∂U/∂θ_j)x`. No sustituyas el entrenamiento desde geometría por un W libre sin advertir que es otro modelo.

### 11.2. Diseño de medición

Fija tamaños por triángulos, objetos, estados, caminos, fuentes, modos, parámetros, profundidad y lote de forma independiente. El tamaño funcional y el coste son observables distintos. Alterna órdenes CPU/GPU y repite con bloques de sesión para estimar variación; un par en una máquina cargada es una medida local, no una ley de escalado.

Mide frío/caliente, entrenamiento completo, auditoría obligatoria, RAM/VRAM pico y recursos de terceros. Compara con BLAS optimizado CPU/GPU a la misma precisión y contrato. Reporta el punto de cruce si existe; reporta ausencia si no existe. Alta utilización de GPU no acredita aceleración.

Ablaciones mínimas: coherencia vs suma de intensidades; fase relativa y sham; entrenamiento vs parámetros fijos; geometría vs operador compilado; GPU vs CPU; BVH/instancias/caché/packing/lotes; precisión simple/doble/hi-lo; reducción naive/compensada/árbol. Para recurrencia o nuevas activaciones añade sus controles específicos. Cada variante conserva el mismo test y presupuesto; si cambia el modelo, descríbela como tal.

Mide energía de host y GPU, incluyendo captura/prueba/lectura; identifica consumo de pantalla y actividad ajena. Usa telemetría y, si existe, medidor externo con incertidumbre y línea base. No etiquetes vatios de toda una RTX como energía del kernel aislado ni como eficiencia fotónica. Si no se puede aislar, ese resultado sigue `BLOCKED/PARTIAL` para la afirmación de eficiencia.

> **Revisión v2.** `closure_limits.py` calcula escalas de referencia (energía del fotón, kT·ln 2, presupuesto de fotones por Poisson) para situar las mediciones; no son cotas de ningún dispositivo ni sustituyen la medición extremo a extremo de §28.

NVIDIA externo exige otra ejecución real de la ruta gráfica. AMD exige hardware AMD real, backend compatible y recibo; no sustituirlo por disponibilidad de API, emulación ni ejecución NVIDIA. Si no hay equipo, empaqueta el experimento y registra la dependencia.

**Cierre:** equivalencia numérica y costes completos comparables, ablaciones causales, escalado útil, mediciones externas según la afirmación. Si no hay ventaja global, una conclusión negativa queda publicada y el producto no se anuncia como acelerador.

## 12. Paso H: complemento terminado y recuperación duradera

Conserva la distribución 0.1.3 e implementa una sucesora. Revisa `Blender/addon/optic_neuro_blender_v013/{__init__.py,bootstrap.py,model.py,runtime.py,worker_v3.py}`. No añadas a ese ZIP un backend rechazado ni cambies sus bytes conservando la misma versión/hash.

Integra el backend gráfico aceptado con selección explícita CPU/híbrido/GPU, contrato visible de entradas coherentes, estado de geometría y diagnóstico científico. La UI no debe llamar fotones a un replay del DAG ni presentar imágenes Cycles como campos complejos. Mantén decisiones numéricas y decisiones certificadas diferenciadas.

Verifica crear/abrir, editar/capturar, inferir, entrenar, cancelar solo el worker propio, recuperar, aplicar atómicamente, guardar copia, reabrir y exportar. Rechaza datos/resultados obsoletos tras cambios en escena, fuentes, λ, paquete o entorno. No sobrescribas una escena del propietario ni apliques un entrenamiento parcial.

Versiona checkpoints con estado de Adam, paso, parámetros, RNG, identidad de inputs/captura/código, recibos y sumas. Para durabilidad usa archivo temporal, flush/fsync, reemplazo atómico y persistencia de metadatos cuando el sistema lo permita. No prometas durabilidad eléctrica por tener `rename` atómico. Prueba interrupciones repetidas de un trabajo ya reanudado, pérdida del dueño, worker perdido, contexto GPU perdido, lectura truncada, disco lleno, datos alterados y recuperación en otra instalación.

Los cortes eléctricos se ensayan en una VM o un entorno sacrificial con archivos de prueba y una definición verificable de persistencia; no provoques un corte en el ordenador de trabajo. Las pruebas de usabilidad requieren personas reales y tareas definidas; un test automático no es un participante humano.

**Cierre:** instalación limpia de la sucesora, backend aceptado, todos los flujos y fallos controlados, checkpoints íntegros y límites de durabilidad explícitos. Interrupción en checkpoint12 sigue como evidencia histórica acotada.

## 13. Paso I: antecedentes, novedad y utilidad demostrable

La búsqueda histórica/ampliada no encontró cierta combinación dentro de su alcance. No constituye prueba de ausencia universal de antecedentes. Completa textos, suplementos, código y métodos cercanos; no clasifiques un artículo como leído íntegramente por un resumen producido por otro modelo o por ausencia de una palabra clave.

Contrasta al menos redes coherentes entrenables, difracción/óptica diferenciable, trazado no secuencial diferenciable, ray tracing certificado con intervalos, compilación matricial y certificación de decisiones. Para cada método: hipótesis físicas, variables entrenadas, geometría, manejo de ramas, aritmética, incertidumbre, tareas, coste total, licencias y código reproducible. Identifica límites compartidos y diferencias verificadas.

> **Revisión v2 — antecedentes concretos que contrastar** (localizados, §37): renderizado diferenciable (Dr.Jit/Mitsuba 3; Jakob et al., 2022), el antecedente informático más cercano a «renderizar como computar» con gradientes; redes neuronales físicas entrenadas con retropropagación (Wright et al., 2022); retropropagación in situ en fotónica integrada (Pai et al., 2023); límites energéticos de redes ópticas (Hamerly et al., 2019) y su demostración con menos de un fotón por multiplicación (Wang et al., 2022); la perspectiva de óptica profunda (Wetzstein et al., 2020); y el diseño de mallas universales (Clements et al., 2016), modelo de la malla auxiliar de 64 modos. Para cada uno, documenta qué comparte con Neuro3D y qué no, citando secciones concretas.

Formula una contribución falsable: por ejemplo, certificación conjunta de geometría capturada, transporte coherente y decisión con cobertura útil y menor coste de prueba para una familia declarada. El comparador debe poder rechazar la ventaja si desaparece al igualar alcance y precisión. Originalidad de implementación e integración son aportaciones legítimas, pero se separan de un descubrimiento físico nuevo.

Prepara un caso de uso que necesite esa capacidad: márgenes críticos, detección de geometrías fuera de contrato o comparación reproducible de una red óptica. Reporta cobertura de certificados, anchura, coste y decisiones correctas/incorrectas/UNKNOWN por separado. Adopción e impacto duradero requieren evidencia posterior; no se marcan PASS porque el código se haya publicado.

## 14. Evaluación concreta de los avances de openai/math

### 14.1. Alcance de esta revisión

Se examinaron README, catálogo de 372 familias, mapa de 719 manuscritos, catálogo Lean y fuentes primarias seleccionadas. Se leyeron los enunciados/introducciones de Steinitz–Bergström, Fourier, local smoothing y multiplicación matricial, y el endpoint/configuración de Comparator de Steinitz. No se verificaron aquí 719 demostraciones ni se compiló la biblioteca Lean. La presencia en `formalization.yaml` es evidencia de un artefacto publicado, no de una verificación que este agente haya ejecutado.

El repositorio advierte que los resultados están en diferentes etapas de verificación y que algunos no formalizados pueden tener problemas. Esta guía usa esos manuscritos como resultados **reportados por sus autores** y como candidatos de investigación. Antes de hacer depender una conclusión de ellos, comprueba enunciado, pruebas, hipótesis, axiomas y verificación independiente de la versión fijada.

| Familia | Relación con Neuro3D | Decisión práctica |
|---|---|---|
| **097: Steinitz–Bergström euclídeo** | Acota prefijos de sumas vectoriales con signos o permutaciones bajo hipótesis concretas | Candidato para estudiar estabilidad de sumas coherentes; el texto dice que la construcción es existencial y no ofrece un algoritmo eficiente/online |
| **130: DFT por debajo de n log n** | Se refiere a una transformación usada por referencias de ondas | No sustituir FFT de producción: aritmética compleja exacta, coeficientes irrestrictos y raíces suministradas; constantes enormes y sin cruce útil/numerical stability demostrado |
| **107: exponente matricial ≤9/4** | Puede interesar a operadores y lotes muy grandes | No da un kernel competitivo para la matriz 8×5 o lotes actuales; evaluar BLAS y estructura antes de un resultado asintótico |
| **079: local smoothing 3D** | Cotas de evolución de ondas en espacio euclídeo | Línea teórica opcional; no es una cota puntual de error FDTD ni de un dispositivo con interfaces, PML y detectores |
| **094: reducción de dimensión en Lp** | Podría orientar codificaciones o exploración de datasets | Una inmersión de distancias no conserva automáticamente fase, interferencia ni la matriz óptica; cualquier cambio de encoding es otro ensayo |
| **017: exponente de irracionalidad de π** | Coincide nominalmente con la fase 2πL/λ | No mejora directamente el cálculo certificado de seno/coseno ni justifica pi en float; conservar reducción de rango y cotas numéricas |
| **362: Vlasov–Maxwell relativista** | Trata un sistema electromagnético acoplado a partículas | No tiene transferencia directa demostrada a la red fotónica pasiva ni al FDTD escalar de este proyecto |

### 14.2. Ensayo útil derivado de Steinitz, sin atribuirle garantías falsas

Representa cada contribución de campo como `(Re z, Im z)`; para campo y todas las tangentes puede considerarse un vector de dimensión mayor, siempre con norma y escala declaradas. No cambies signos ópticos para satisfacer un teorema de signing: eso modifica la física. La consecuencia de permutación requiere suma cero; un detector genérico no cumple esa hipótesis automáticamente.

Como **inferencia de ingeniería**, prueba si una permutación de contribuciones reduce prefijos y error de redondeo sin cambiar campos/gradientes, frente a fsum y árbol. El anexo incorpora una heurística greedy completa con coste O(N²) y presupuesto de 4096 términos para diagnóstico. No la llames implementación del teorema ni la despliegues como optimización masiva sin medir ese coste. Usa controles constructivos, destructivos y de muchos términos pequeños; registra términos idénticos y permisos de reordenación.

Objetivo del experimento: menor error observado o cotas más estrechas a igual campo, con coste completo aceptable. Recházalo si la ventaja desaparece ante suma compensada/árbol o si solo funciona en un detector seleccionado. Un teorema existencial puede orientar una pregunta sin suministrar el algoritmo necesario para cerrarla.

> **Revisión v2.** Si la reducción es exacta o compensada (fsum, superacumulador; nota v2 del §8.2), el orden de los términos deja de influir y el ensayo de permutaciones pierde objeto; solo tiene sentido donde la reducción no pueda hacerse exacta. Para ese caso, la introducción de la familia 097 cita un preprint de 2026 de Dutta, Jha y Jiang con cotas eficientes de ordenación de suma cero: es un comparador algorítmico más adecuado que la heurística greedy. Esta revisión solo leyó la cita; lee el preprint antes de usarlo.

### 14.3. Verificación Lean que debe ejecutar el agente cuando corresponda

Clona la referencia en otro directorio, fija `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` y conserva `lean/lean-toolchain`, `lake-manifest.json`, catálogo y registros. Sigue la documentación de Comparator para instalar **comparator, landrun y lean4export**. Compila solo módulos relevantes; no intentes cargar toda la biblioteca en 32 GB por defecto.

Desde `lean/`, con esas herramientas ya instaladas:

```bash
lake update
lake exe cache get
lake env comparator ComparatorChallenges/SteinitzBergstrom.json
lake env comparator ComparatorChallenges/UniformFourier.json
lake env comparator ComparatorChallenges/MatrixMultiplication.json
lake env comparator ComparatorChallenges/SubpolynomialLp.json
```

Registra los cambios de dependencias que pueda producir `lake update`; conserva el lock original y el efectivo. Comprueba tanto el build del módulo como el enunciado del challenge y los axiomas usados. En Steinitz el endpoint publicado es `OAI.EuclideanSteinitzBergstrom.main`, archivo `OAI/Analysis/Steinitz/Main.lean`, y Comparator permite `propext`, `Quot.sound` y `Classical.choice`. Verifica el cierre transitivo, no únicamente que el último archivo no contenga `sorry`.

Targets publicados: `OAI.PowerSaving.transform_main`, `OAI.MatrixMultiplication.complex_omega_le_nine_quarters` y `OAI.SubpolynomialLp.source_main`. Para 079 no se encontró el manuscrito principal en el catálogo consultado; registra esa ausencia dentro de ese catálogo, sin convertirla en prueba de que nunca pueda existir una formalización.

> **Revisión v2 — comprobado en `fd4aeeb`.** `MatrixMultiplication.json` declara tres teoremas (`complex_omega_le_nine_quarters`, `complex_alpha_gt_93_div_200` y `complex_rectangular_omega_lt_523_div_250`) y `UniformFourier.json` dos (`transform_main` y `convolution_main`); los cuatro challenges permiten exactamente `propext`, `Quot.sound` y `Classical.choice`. Comprueba todos los `theorem_names`, no solo el citado. Toolchain: `leanprover/lean4:v4.34.1`. El README del repositorio indica que alrededor del 42 % de los resultados principales tienen formalización. `main` seguía en `fd4aeeb` el 12-oct-2026.

Incluso una demostración formal completa del teorema abstracto no verifica un shader, errores de memoria/float, los supuestos de un dispositivo ni una mejora de tiempo. No es necesario importar código Apache-2.0 de `openai/math` para usar las herramientas originales del anexo. Si se incorpora código ajeno, conserva su licencia, avisos y procedencia.

### 14.4. Matemáticas establecidas con aplicación inmediata

Prioriza predicados filtrados y expansiones para signos geométricos (Shewchuk), sumas/productos compensados y error-free transforms (Ogita–Rump–Oishi), intervalos/MPFR con redondeo dirigido, modelos afines/Taylor para dependencias y pruebas de familias, y reducción/caché del operador lineal. Son técnicas anteriores al catálogo nuevo y no se presentan como descubrimientos de 2026.

Para geometría, adapta los predicados al signo que realmente requiere ray-triangle/nearest, preservando casos límite. Para sumas, verifica condiciones del compilador y overflow. Para MPFR, especifica modo y precisión; alta precisión sin una cota o un redondeo dirigido no es automáticamente un intervalo válido. El código racional del anexo permite un control pequeño sin dependencia MPFR.

## 15. Paso J: artículo, figuras y entrega científica

Actualiza primero afirmaciones y resultados; después recompila la presentación. El artículo principal debe describir problema, contribución delimitada, modelo, método, teoría/certificación, experimentos, comparadores, incertidumbre, negativos y límites. Lleva historia detallada de intentos y perfiles al suplemento. No omitas el resultado negativo de ondas o los comparadores afinados porque debiliten una narrativa de superioridad.

Completa autores/afiliaciones/contribuciones con identidades reales y acuerdo de quienes firman. Añade bibliografía BibTeX trazable y citas normales, además de enlaces de reproducción. Figuras mínimas: arquitectura con fronteras CPU/GPU; escena y contrato; error por etapa y márgenes; generalización con incertidumbre; costes completos y ablaciones; convergencia de ondas/campo complejo; negativos y régimen de validez. Cada figura se genera de datos fijados, con script, unidades y SHA256. Un render decorativo no sustituye una medida.

> **Revisión v2.** Para roles CRediT y declaración del uso de IA, sigue §32; para comprobar referencias, `extract_identifiers` y `resolve_identifiers` (§38). En `69db25c` no hay `CITATION.cff`; la licencia del código es MIT (`LICENSE`).

`Tools/build_scientific_tex_draft_v1.py` convierte actualmente una línea de imagen en `Linked figure:`. Implementa un builder sucesor que incorpore **PNG/PDF de datos** como figuras, resuelva rutas y títulos, y soporte bibliografía. No borres la fuente/builder histórica. Puede usarse Pandoc con citeproc o LaTeX directamente; conserva versión y comando. Convierte los GIF a paneles/frames PNG con procedencia y una leyenda que describa correctamente el replay.

Ejecuta dos compilaciones cuando el motor lo necesite, comprueba errores/overfull boxes y enlaces, renderiza **todas las páginas** e inspecciona tablas, fuentes, ecuaciones, referencias, figuras y saltos. Comprueba que el PDF incluya gráficos legibles, que los autores no estén pendientes y que coincida con el estado actual del artículo. Recompilar un PDF antiguo no incorpora resultados nuevos.

Prepara una release de código y complemento sucesor con pruebas de instalación, hashes, datos permitidos, scripts completos, fuentes del artículo, figuras y un mapa de reproducción por perfil. El README debe separar resultado científico, instalación, ejecución y límites. El paquete de revisión debe pedir comprobaciones capaces de refutar las afirmaciones; no solo una opinión estética.

Entrega a un investigador externo código/datos/perfiles para que ejecute e interprete resultados sin tus cachés. Registra identidad, conflictos y cambios que proponga. Una ejecución GitHub Actions fuera del equipo es contraste de entorno; no una revisión científica humana independiente. No declares artículo enviado, aceptado o revisado antes de que exista la evidencia correspondiente.

**Cierre:** documento definitivo coherente con el código/resultados; figuras incorporadas y verificadas; release reproducible; crítica especializada documentada y resuelta dentro de su alcance. El envío a una revista y cualquier comunicación externa se preparan como acciones concretas separadas.

## 16. Línea física opcional y frontera con Silice-Neuro3D-Cube

Para cerrar Neuro3D como simulador no hace falta fabricar un procesador. Para afirmar un dispositivo fotónico real sí hacen falta plataforma/materiales/unidades, calibración de fuentes/coherencia/detectores, geometría y tolerancias medidas, ruido/deriva/pérdidas medidos, demostrador físico con predicciones y controles, coste de toda la cadena y réplica externa. La simulación de ruido supuesto no se publica como una distribución medida.

> **Revisión v2.** Esta línea es opcional para el cierre como simulador (D0-A) y obligatoria para cualquier aspiración del nivel descrito en §24 (D0-B). §27 y §28 la desarrollan.

Si se decide esa línea, valida el mínimo sistema que distinga la contribución de alternativas conocidas; una franja de interferencia por sí sola acredita interferencia conocida. La GPU realiza cálculo electrónico aunque simule fotónica. Clasificación o aprendizaje físico exige entradas nuevas, adquisición cruda y separación de operaciones ópticas/electrónicas.

Silice-Neuro3D-Cube conserva sus contratos y trabajos: T96/Q4, modos, fronteras, campo y fases, y perfiles medidos. No copies un PASS entre repositorios sin demostrar equivalencia del modelo y observable. El agente de Neuro3D prepara un contrato de interfaz para intercambiar resultados, sin apropiarse del cierre de otro proyecto.

## 17. Cobertura de los 26 puntos históricos

| Punto | Dónde se ejecuta/cierra en esta guía |
|---|---|
| 1. Admisión first-hit | B y E; conservar cierres acotados y validar nuevas representaciones |
| 2. First-hit robusto | D/E; casos originales y familia adversa, comparación de selección |
| 3. Multicamino completo | D/E; cobertura de ramas, contactos, retornos y ciclos explícitos |
| 4. Error integral | E; captura hasta decisión y gradiente, con incertidumbre y UNKNOWN |
| 5. Fusión/reducción/descarte | D/E/G; igualdad de operador futuro y cotas de amplitud descartada |
| 6. Red completa GPU | D; buffers nativos, salidas completas, 61 estados cuando se reivindique aprendizaje |
| 7. RT coherente en Blender | D/H; transporte propio; no equivalencia automática con Cycles |
| 8. Supervisión/fallos | B/D/H; recursos, dueño, GPU, cancelación y recibos |
| 9. Reproducción desde cero | B/J; fixtures, entornos, perfiles, datos y tercero |
| 10. Interacción/documentación | A/H/J; flujos de UI y estado coherente |
| 11. Aportación falsable | A/I; hipótesis útil y comparador que pueda refutarla |
| 12. Revisión sistemática | I/14; textos/métodos/código y alcance de lectura |
| 13. Teoría/límites | E/F; capacidad pasiva, rango, tangentes y estabilidad |
| 14. Generalización | F; test reservado y tareas/datos nuevos |
| 15. Baselines equivalentes | F/G; ajuste, encoding, precisión y coste |
| 16. Costes completos | G; fases, recursos, energía y medición de incertidumbre |
| 17. Escalado funcional | G; geometría, canales, modos, lote y calidad por separado |
| 18. Ablaciones causales | D/F/G; mismo protocolo y controles de precisión/modelo |
| 19. Plataforma/régimen físico | C/16; materiales y solver acorde a la afirmación |
| 20. Ruido/tolerancias medidas | 16; adquisición física, no parámetros supuestos |
| 21. Experimento físico mínimo | 16; predicciones discriminativas y controles |
| 22. Cálculo/aprendizaje físicos | 16; inferencia/adaptación reales y costes completos |
| 23. Línea de sílice | 16; contrato de colaboración, sin transferir cierres sin equivalencia |
| 24. Réplica independiente | B/J/16; entorno externo y juicio humano/laboratorio distinguidos |
| 25. Artículo/crítica | J; manuscrito/figuras/bibliografía y revisión real |
| 26. Consecuencia científica | I/J; problema útil demostrado e impacto posterior, sin garantía de premio |

## 18. Registro por experimento, parada y criterio final

Cada nuevo ensayo conserva: ID, hipótesis y alternativa; versión/protocolo previo; lista completa de fuentes y SHA256; captura/inputs/calibración; entorno/driver/dispositivo; semillas/folds; presupuesto de recursos y deadline; comandos exactos; stdout/stderr/código de salida; todos los resultados, incluidos fallos; oráculo independiente; decisión según regla fijada; desviaciones; limitaciones; y enlace al commit publicado. Una ficha de coordinación no sustituye ese resultado.

> **Revisión v2.** `validate_experiment_record` (§38) comprueba los campos de esta lista, el formato de commits y hashes, que un registro decidido cite su commit publicado, que un PASS tenga oráculo independiente y regla prospectiva, que ningún identificador nuevo use la cadena cerrada `EXP-005-*` y los campos de las consultas a JEV.

Estados operativos: `OPEN`, `PARTIAL`, `PASS`, `FAIL`, `BLOCKED`, `UNKNOWN`, `NOT_APPLICABLE` con alcance. El registro canónico sigue su vocabulario propio de `Docs/GOVERNANCE.md`; no introduzcas estos estados auxiliares directamente donde el esquema canónico no los permita.

Antes de arrancar una simulación larga, confirma que su protocolo ya está comprometido, que el hardware elegido está reservado de verdad y que la hipótesis puede cambiar una decisión. Si el trabajo excede el límite, conserva NULL/incompleto; una ampliación requiere otro ensayo prospectivo. No normalices automáticamente, descartes resultados adversos ni elijas semillas por test para cerrar un objetivo.

El cierre se valida por alcance: instrumento computacional, backend concreto, generalización concreta, rendimiento concreto y tesis física opcional. No marques `full_project_complete=true` mientras haya trabajo restante dentro del alcance prometido. Novedad e importancia excepcional requieren evaluación independiente; no se marcan por inferencia de un agente a partir de tests.

> **Revisión v2.** Los frentes de frontera F1–F9 (§24–§33) se registran en `frontier-manifest.json` y se verifican con `closure_v2.py`, separados de los once frentes y del JSON canónico. F5 (réplica) y F9 (adopción) exigen además un registro de evidencia externa fijado: un agente no puede cerrarlos con sus propias ejecuciones.

El script `closure_evidence.py` verifica integridad del manifiesto auxiliar, no verdad física ni calidad de un revisor. Usa su salida junto con los verificadores científicos y los criterios anteriores. Una integridad aprobada con frentes OPEN no es cierre completo.

## 19. Referencias primarias y procedencia matemática

- [OpenAI math: README fijado](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/README.md), [catálogo](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/CONTENTS.md), [formalizaciones](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/formalization.yaml) y [Comparator](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/ComparatorChallenges/README.md).
- [Steinitz: introducción y enunciados](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/The-Euclidean-Steinitz-Bergstrom-theorem-September-24-2026/build/introduction.tex), [endpoint Lean](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/OAI/Analysis/Steinitz/Main.lean) y [challenge](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/ComparatorChallenges/SteinitzBergstrom.json).
- [Fourier: enunciado, modelo de cálculo y límites prácticos](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/build/sections/introduction.tex).
- [Multiplicación matricial: manuscrito fuente](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Matrix-Multiplication-Nine-Fourths-October-2-2026/build/paper.tex).
- [Local smoothing: enunciado y contexto](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Critical-local-smoothing-for-the-three-dimensional-wave-equation-September-24-2026/build/sections/00-introduction.tex).
- [Shewchuk: predicados geométricos robustos](https://www.cs.cmu.edu/~quake/robust.html), artículo y código del autor.
- [Ogita–Rump–Oishi: Accurate Sum and Dot Product](https://www.tuhh.de/ti3/paper/rump/OgRuOi05.pdf), 2005; [DOI](https://doi.org/10.1137/030601818).
- [GNU MPFR: redondeo correcto](https://www.mpfr.org/).
- [Meep: suavizado subpíxel](https://meep.readthedocs.io/en/latest/Subpixel_Smoothing/) y [descomposición modal](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/).
- [Shen et al.: circuitos nanofotónicos coherentes](https://arxiv.org/abs/1610.02365) y [Lin et al.: redes difractivas](https://arxiv.org/abs/1804.08711), antecedentes del aprendizaje óptico.

## 20. Código completo del kit de apoyo

Los bloques siguientes se extraen con `extract_support.py`; sus rutas empiezan por `agent_support/`. No contienen funciones pendientes. El kit se validó con CPython 3.12.14, NumPy 2.3.5 y SciPy 1.17.0 en Linux. Sus pruebas verifican los comportamientos declarados del kit; no ejecutan Blender, GPU, el entrenamiento del proyecto, Comparator ni la física de la red completa.

No copies el kit sobre módulos congelados para hacer coincidir pines. Úsalo como control independiente o intégralo en una versión sucesora con su protocolo y pruebas nativas. Conserva las limitaciones de cada docstring al comunicar resultados.

> **Revisión v2.** Estos once bloques se conservan sin cambios (SHA256 en §22.3). Las correcciones de los tres defectos reproducidos (§23, E5–E7) están en el kit v2 del §38, que importa estos módulos sin modificarlos.


### 20.1. extract_support.py

<!-- CODEFILE: agent_support/extract_support.py -->
```python
"""Extract the guide's complete CODEFILE blocks without overwriting other work."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import sys


PATTERN = re.compile(r"^<!-- CODEFILE: ([^\n]+) -->\s*\n```(?:python|text|json|yaml|glsl)\n(.*?)\n```", re.DOTALL | re.MULTILINE)


def extract(text: str) -> list[tuple[str, bytes]]:
    """Validate explicit support paths and return complete LF-normalized payloads."""
    blocks, seen = [], set()
    for relative, body in PATTERN.findall(text):
        relative = relative.strip()
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or ":" in relative or "\\" in relative or not relative.startswith("agent_support/"):
            raise ValueError("Every code target must be beneath agent_support/")
        if relative in seen:
            raise ValueError("Duplicate code target: "+relative)
        seen.add(relative)
        blocks.append((relative, (body.replace("\r\n", "\n")+"\n").encode("utf-8")))
    if not blocks:
        raise ValueError("No complete CODEFILE blocks were found")
    if len(re.findall(r"^<!-- CODEFILE:", text, re.MULTILINE)) != len(blocks):
        raise ValueError("An incomplete or unsupported CODEFILE block was found")
    return blocks


def materialize(blocks: list[tuple[str, bytes]], root: Path) -> list[dict]:
    """Preflight every destination, then create only missing support files."""
    root = root.resolve()
    prepared = []
    for relative, payload in blocks:
        destination = (root/relative).resolve()
        if not destination.is_relative_to(root):
            raise ValueError("A destination escapes the selected root")
        if destination.exists() and (not destination.is_file() or destination.read_bytes() != payload):
            raise ValueError("Different existing content will not be overwritten: "+relative)
        prepared.append((relative, destination, payload))
    output = []
    for relative, destination, payload in prepared:
        existed = destination.exists()
        if not existed:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as stream:
                stream.write(payload)
        output.append({"path": relative, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "created": not existed})
    return output


def main() -> int:
    """Validate a guide or extract its support kit into an explicitly chosen root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        blocks = extract(args.guide.read_text(encoding="utf-8"))
        if args.write:
            records = materialize(blocks, args.root)
            for row in records:
                print(row["path"], row["bytes"], row["sha256"])
        else:
            print("Validated complete code blocks:", len(blocks))
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### 20.2. closure_reference.py

<!-- CODEFILE: agent_support/closure_reference.py -->
```python
"""Exact represented-input geometry and rational optical interval references.

This module proves inclusion for its explicit scalar input model. It does not
certify missing paths, native Blender transforms, fabrication, or Maxwell error.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import factorial, isfinite, isqrt
from typing import Iterable, Sequence


def rational(value: int | float | str | Fraction) -> Fraction:
    """Decode a rational or an exact finite binary64 value without decimal loss."""
    if isinstance(value, bool):
        raise TypeError("Boolean coordinates are not accepted")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError("All values must be finite")
        return Fraction.from_float(value)
    if isinstance(value, str) and value.lower().lstrip("+-").startswith("0x"):
        return rational(float.fromhex(value))
    return Fraction(value)


@dataclass(frozen=True)
class Interval:
    """Closed interval with exact rational endpoints and inclusion arithmetic."""
    lo: Fraction
    hi: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "lo", rational(self.lo))
        object.__setattr__(self, "hi", rational(self.hi))
        if self.lo > self.hi:
            raise ValueError("Interval endpoints are reversed")

    @staticmethod
    def point(value: int | float | str | Fraction) -> Interval:
        v = rational(value)
        return Interval(v, v)

    def __add__(self, other: Interval | Fraction | int) -> Interval:
        b = interval(other)
        return Interval(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __neg__(self) -> Interval:
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other: Interval | Fraction | int) -> Interval:
        return self + (-interval(other))

    def __rsub__(self, other: Interval | Fraction | int) -> Interval:
        return interval(other) - self

    def __mul__(self, other: Interval | Fraction | int) -> Interval:
        b = interval(other)
        v = (self.lo*b.lo, self.lo*b.hi, self.hi*b.lo, self.hi*b.hi)
        return Interval(min(v), max(v))

    __rmul__ = __mul__

    def __truediv__(self, other: Interval | Fraction | int) -> Interval:
        b = interval(other)
        if b.lo <= 0 <= b.hi:
            raise ValueError("Division by an interval containing zero")
        return self * Interval(1/b.hi, 1/b.lo)

    def square(self) -> Interval:
        lo = Fraction(0) if self.lo <= 0 <= self.hi else min(self.lo**2, self.hi**2)
        return Interval(lo, max(self.lo**2, self.hi**2))

    def contains(self, value: int | float | str | Fraction) -> bool:
        return self.lo <= rational(value) <= self.hi

    def outward_wire(self, bits: int = 128) -> list[str]:
        """Serialize bounded-size dyadic endpoints, widening rather than truncating."""
        if not 8 <= bits <= 512:
            raise ValueError("8..512 serialization bits are required")
        scale = 1 << bits
        lower = (self.lo*scale).numerator//(self.lo*scale).denominator
        negative_upper = -self.hi*scale
        upper = -(negative_upper.numerator//negative_upper.denominator)
        return [str(Fraction(lower, scale)), str(Fraction(upper, scale))]

    @property
    def midpoint(self) -> Fraction:
        return (self.lo + self.hi)/2

    @property
    def radius(self) -> Fraction:
        return (self.hi - self.lo)/2


def interval(value: Interval | int | float | str | Fraction) -> Interval:
    """Promote an exact scalar to a singleton interval."""
    return value if isinstance(value, Interval) else Interval.point(value)


def sqrt_interval(value: Interval, bits: int = 128) -> Interval:
    """Enclose square roots with integer arithmetic on a binary rational grid."""
    if value.lo < 0 or not 8 <= bits <= 512:
        raise ValueError("Nonnegative radicand and 8..512 bits are required")
    scale = 1 << bits

    def bounds(x: Fraction) -> tuple[Fraction, Fraction]:
        k = isqrt((x.numerator * scale * scale)//x.denominator)
        lo = Fraction(k, scale)
        hi = lo if k*k*x.denominator == x.numerator*scale*scale else Fraction(k+1, scale)
        return lo, hi

    return Interval(bounds(value.lo)[0], bounds(value.hi)[1])


def segment_length(a: Sequence, b: Sequence, bits: int = 128) -> Interval:
    """Enclose a 3D segment length, including supplied coordinate intervals."""
    if len(a) != 3 or len(b) != 3:
        raise ValueError("Three coordinates per endpoint are required")
    squared = sum(((interval(x)-interval(y)).square() for x, y in zip(a, b)), Interval.point(0))
    return sqrt_interval(squared, bits)


def _atan_inverse(n: int, bits: int) -> Interval:
    """Use the alternating arctangent series and its exact next-term remainder."""
    x = Fraction(1, n)
    total, power, k = Fraction(0), x, 0
    threshold = Fraction(1, 1 << bits)
    while True:
        total += (-1 if k % 2 else 1)*power/(2*k+1)
        next_power = power*x*x
        next_term = (-1 if (k+1) % 2 else 1)*next_power/(2*k+3)
        if abs(next_term) <= threshold:
            return Interval(min(total, total+next_term), max(total, total+next_term))
        power, k = next_power, k+1


@lru_cache(maxsize=8)
def pi_interval(bits: int = 128) -> Interval:
    """Enclose pi by Machin's identity; no floating-point pi is assumed exact."""
    if not 8 <= bits <= 512:
        raise ValueError("8..512 bits are required")
    return 16*_atan_inverse(5, bits+8)-4*_atan_inverse(239, bits+8)


def phase_from_length(length: Interval, wavelength: Interval, bits: int = 128) -> Interval:
    """Reduce exact length/wavelength cycles before multiplying by enclosed pi."""
    if length.lo < 0 or wavelength.lo <= 0:
        raise ValueError("Nonnegative lengths and strictly positive wavelengths are required")
    cycles = length/wavelength
    turns = round(cycles.midpoint)
    return 2*pi_interval(bits)*(cycles-turns)


def _trig_at_rational(x: Fraction, terms: int) -> tuple[Interval, Interval]:
    """Enclose cosine and sine using real Taylor remainder bounds."""
    if not 8 <= terms <= 64 or abs(x) > 4:
        raise ValueError("Taylor reduction requires |x| <= 4 and 8..64 terms")
    cosine = sum(((-1)**k*x**(2*k)/factorial(2*k) for k in range(terms+1)), Fraction(0))
    sine = sum(((-1)**k*x**(2*k+1)/factorial(2*k+1) for k in range(terms+1)), Fraction(0))
    ec = abs(x)**(2*terms+1)/factorial(2*terms+1)
    es = abs(x)**(2*terms+2)/factorial(2*terms+2)
    return Interval(cosine-ec, cosine+ec), Interval(sine-es, sine+es)


def unit_phasor(phase: Interval, bits: int = 128, terms: int = 24) -> tuple[Interval, Interval]:
    """Enclose exp(i*phase), preserving pi uncertainty during range reduction."""
    period = 2*pi_interval(bits)
    turns = round(phase.midpoint/period.midpoint)
    reduced = phase-turns*period
    if reduced.radius >= 2 or abs(reduced.midpoint) > 4:
        return Interval(-1, 1), Interval(-1, 1)
    c, s = _trig_at_rational(reduced.midpoint, terms)
    e = reduced.radius  # Both sin and cos are globally 1-Lipschitz.
    return (Interval(max(Fraction(-1), c.lo-e), min(Fraction(1), c.hi+e)),
            Interval(max(Fraction(-1), s.lo-e), min(Fraction(1), s.hi+e)))


def complex_product(a: tuple[Interval, Interval], b: tuple[Interval, Interval]) -> tuple[Interval, Interval]:
    """Multiply rectangular complex enclosures without dropping cross terms."""
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def coherent_field(paths: Iterable[tuple[tuple[Interval, Interval], Interval]]) -> tuple[Interval, Interval]:
    """Sum every supplied complex amplitude times its enclosed phase factor."""
    real, imag = Interval.point(0), Interval.point(0)
    for amplitude, phase in paths:
        r, i = complex_product(amplitude, unit_phasor(phase))
        real, imag = real+r, imag+i
    return real, imag


def modal_power(field: tuple[Interval, Interval]) -> Interval:
    """Enclose normalized modal power; this quantity is not calibrated watts."""
    return field[0].square()+field[1].square()


def certified_argmax(powers: Sequence[Interval]) -> int | None:
    """Return a class only when its lower power exceeds every other upper power."""
    if len(powers) < 2 or any(p.lo < 0 for p in powers):
        raise ValueError("At least two nonnegative power intervals are required")
    for i, p in enumerate(powers):
        if all(p.lo > q.hi for j, q in enumerate(powers) if i != j):
            return i
    return None


def field_to_power_error(observed_abs_upper: Fraction, field_error: Fraction) -> Fraction:
    """Bound |P_true-P_observed| from a supplied upper bound on |E_observed|."""
    a, e = rational(observed_abs_upper), rational(field_error)
    if a < 0 or e < 0:
        raise ValueError("Error and magnitude bounds must be nonnegative")
    return 2*a*e+e*e


def _vector(v: Sequence) -> tuple[Fraction, Fraction, Fraction]:
    if len(v) != 3:
        raise ValueError("Three-dimensional vectors are required")
    return tuple(rational(x) for x in v)


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Fraction(0))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def exact_first_hit(origin: Sequence, direction: Sequence, triangles: Sequence[dict]) -> dict:
    """Find a first hit in exact represented coordinates; retain contacts and ties.

    Each triangle needs primitive_id, object_id, and vertices (three 3D vectors).
    Coplanar support and degenerate triangles deliberately return UNKNOWN.
    A shared triangle seam is merged only within one object and one exact plane.
    """
    o, d = _vector(origin), _vector(direction)
    if _dot(d, d) == 0:
        raise ValueError("A nonzero direction is required")
    hits, ids = [], set()
    for triangle in triangles:
        pid = str(triangle["primitive_id"])
        if pid in ids:
            raise ValueError("Primitive identifiers must be unique")
        ids.add(pid)
        vertices = triangle["vertices"]
        if len(vertices) != 3:
            raise ValueError("Three vertices per triangle are required")
        a, b, c = (_vector(x) for x in vertices)
        e1, e2 = _sub(b, a), _sub(c, a)
        normal = _cross(e1, e2)
        if _dot(normal, normal) == 0:
            return {"status": "UNKNOWN", "reason": "DEGENERATE_TRIANGLE", "primitive_id": pid}
        p = _cross(d, e2)
        determinant = _dot(e1, p)
        if determinant == 0:
            if _dot(normal, _sub(o, a)) == 0:
                return {"status": "UNKNOWN", "reason": "COPLANAR_QUERY", "primitive_id": pid}
            continue
        delta = _sub(o, a)
        u = _dot(delta, p)/determinant
        q = _cross(delta, e1)
        v = _dot(d, q)/determinant
        t = _dot(e2, q)/determinant
        if t >= 0 and u >= 0 and v >= 0 and u+v <= 1:
            hits.append((t, pid, str(triangle["object_id"]), a, normal))
    if not hits:
        return {"status": "MISS"}
    first_t = min(h[0] for h in hits)
    tied = [h for h in hits if h[0] == first_t]
    if first_t == 0:
        return {"status": "UNKNOWN", "reason": "LAUNCH_CONTACT", "primitive_ids": [h[1] for h in tied]}
    reference = tied[0]
    same_surface = all(h[2] == reference[2] and _cross(h[4], reference[4]) == (0, 0, 0)
                       and _dot(reference[4], _sub(h[3], reference[3])) == 0 for h in tied)
    if not same_surface:
        return {"status": "UNKNOWN", "reason": "DISTINCT_SURFACE_TIE", "primitive_ids": [h[1] for h in tied]}
    return {"status": "HIT", "parameter": first_t, "object_id": reference[2],
            "primitive_ids": sorted(h[1] for h in tied),
            "point": tuple(o[j]+first_t*d[j] for j in range(3))}
```

### 20.3. closure_coherent.py

<!-- CODEFILE: agent_support/closure_coherent.py -->
```python
"""Coherent reductions, exact roundoff diagnostics, and equivalent operators.

Greedy ordering is an experimental heuristic, not a constructive implementation
of the new Steinitz theorem. No routine changes optical signs or drops terms.
"""
from __future__ import annotations

import math
import struct
from fractions import Fraction
from typing import Callable, Iterable

import numpy as np


def finite_terms(values: Iterable[complex]) -> list[complex]:
    """Materialize finite complex terms so every method sees identical inputs."""
    values = [complex(v) for v in values]
    if not all(math.isfinite(v.real) and math.isfinite(v.imag) for v in values):
        raise ValueError("All complex terms must be finite")
    return values


def coherent_sum(values: Iterable[complex], method: str = "fsum") -> complex:
    """Reduce complex fields, with separate real and imaginary compensated sums."""
    terms = finite_terms(values)
    if method == "fsum":
        result = complex(math.fsum(v.real for v in terms), math.fsum(v.imag for v in terms))
    elif method == "pairwise":
        while len(terms) > 1:
            terms = [terms[i]+terms[i+1] for i in range(0, len(terms)-1, 2)] + terms[-1:]*(len(terms) % 2)
        result = terms[0] if terms else 0j
    elif method == "naive":
        result = sum(terms, 0j)
    else:
        raise ValueError("Supported methods: fsum, pairwise, naive")
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError("Reduction overflow is not a valid field")
    return result


def greedy_order(values: Iterable[complex], max_terms: int = 4096) -> list[int]:
    """Choose a diagnostic O(N^2) permutation minimizing the next prefix norm."""
    terms = finite_terms(values)
    if len(terms) > max_terms:
        raise ValueError("Greedy diagnostic exceeds its declared term budget")
    remaining, order, prefix = set(range(len(terms))), [], 0j
    while remaining:
        i = min(remaining, key=lambda j: (abs(prefix+terms[j]), j))
        remaining.remove(i)
        order.append(i)
        prefix += terms[i]
        if not math.isfinite(prefix.real) or not math.isfinite(prefix.imag):
            raise ValueError("Greedy prefix overflow exceeds the diagnostic domain")
    return order


def exact_roundoff_report(values: Iterable[complex], method: str = "fsum") -> dict:
    """Measure exact absolute reduction error for the represented binary64 terms."""
    terms = finite_terms(values)
    exact_real = sum((Fraction.from_float(v.real) for v in terms), Fraction(0))
    exact_imag = sum((Fraction.from_float(v.imag) for v in terms), Fraction(0))
    result = coherent_sum(terms, method)
    if not math.isfinite(result.real) or not math.isfinite(result.imag):
        raise ValueError("Reduction overflow is not a valid optical result")
    error = abs(Fraction.from_float(result.real)-exact_real)+abs(Fraction.from_float(result.imag)-exact_imag)
    prefix, largest = 0j, 0.0
    for term in terms:
        prefix += term
        largest = max(largest, abs(prefix))
    return {"method": method, "terms": len(terms), "field": [result.real, result.imag],
            "exact_real": str(exact_real), "exact_imag": str(exact_imag),
            "observed_reduction_error_L1_exact": str(error), "maximum_naive_prefix_norm": largest,
            "scope": "Reduction of supplied represented terms only; phase, geometry, and physical errors are excluded"}


def pack_complex64(values: Iterable[complex]) -> bytes:
    """Serialize coherent channels as little-endian binary64 real/imaginary pairs."""
    return b"".join(struct.pack("<dd", v.real, v.imag) for v in finite_terms(values))


def unpack_complex64(payload: bytes) -> list[complex]:
    """Decode a complete native channel packet and reject invalid or partial data."""
    if len(payload) % 16:
        raise ValueError("A complex binary64 packet needs a multiple of sixteen bytes")
    return finite_terms(complex(r, i) for r, i in struct.iter_unpack("<dd", payload))


def first_trace_divergence(reference: list[dict], candidate: list[dict], tolerance: float) -> dict | None:
    """Locate the first mismatched state/component in identically ordered traces."""
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("A finite nonnegative tolerance is required")
    if len(reference) != len(candidate):
        return {"reason": "TRACE_LENGTH", "reference": len(reference), "candidate": len(candidate)}
    for index, (a, b) in enumerate(zip(reference, candidate)):
        if a["state_id"] != b["state_id"]:
            return {"reason": "STATE_IDENTITY", "index": index}
        if set(a["components"]) != set(b["components"]):
            return {"reason": "COMPONENT_IDENTITY", "state_id": a["state_id"]}
        for name in sorted(a["components"]):
            x, y = complex(*a["components"][name]), complex(*b["components"][name])
            if not all(math.isfinite(v) for v in (x.real, x.imag, y.real, y.imag)):
                return {"reason": "NONFINITE_COMPONENT", "state_id": a["state_id"], "component": name}
            error = abs(x-y)
            if error > tolerance:
                return {"reason": "COMPONENT_ERROR", "state_id": a["state_id"], "component": name, "error": error}
    return None


def compile_operator(forward: Callable[[np.ndarray], np.ndarray], input_dimension: int) -> np.ndarray:
    """Compile a fixed linear geometry operator by one forward call per basis input.

    The caller must independently validate linearity, geometry/cache identity,
    source ordering, and forward completeness before using this optimization.
    """
    if input_dimension < 1:
        raise ValueError("A positive input dimension is required")
    basis = np.eye(input_dimension, dtype=np.complex128)
    columns = [np.asarray(forward(basis[i]), dtype=np.complex128) for i in range(input_dimension)]
    if any(c.ndim != 1 or not c.size or c.shape != columns[0].shape or not np.isfinite(c).all() for c in columns):
        raise ValueError("Every basis response must be a complete finite modal vector")
    return np.column_stack(columns)


def apply_operator(operator: np.ndarray, inputs: np.ndarray) -> np.ndarray:
    """Evaluate equivalent fixed-geometry modal fields with optimized matrix work."""
    u, x = np.asarray(operator, dtype=np.complex128), np.asarray(inputs, dtype=np.complex128)
    if u.ndim != 2 or x.ndim != 2 or x.shape[1] != u.shape[1] or not np.isfinite(u).all() or not np.isfinite(x).all():
        raise ValueError("Finite (modes, sources) and (samples, sources) arrays are required")
    result = x @ u.T  # The optical operator is linear, not conjugate-linear.
    if not np.isfinite(result).all():
        raise ValueError("Operator evaluation overflow is not a valid field")
    return result
```

### 20.4. closure_statistics.py

<!-- CODEFILE: agent_support/closure_statistics.py -->
```python
"""Paired inference with explicit independent-unit and overlap assumptions."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy.stats import t as student_t


def differences(candidate: Iterable[float], reference: Iterable[float]) -> np.ndarray:
    """Validate paired accuracy values and return candidate-minus-reference."""
    a, b = np.asarray(list(candidate), dtype=float), np.asarray(list(reference), dtype=float)
    if a.ndim != 1 or a.shape != b.shape or len(a) < 2:
        raise ValueError("At least two matched experimental units are required")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any((a < 0)|(a > 1)) or np.any((b < 0)|(b > 1)):
        raise ValueError("Accuracy values must be finite and in [0, 1]")
    return a-b


def paired_bootstrap(candidate, reference, *, seed: int = 0, draws: int = 10000, alpha: float = 0.05) -> dict:
    """Bootstrap paired independent units; do not pass overlapping split scores."""
    d = differences(candidate, reference)
    if draws < 1000 or not 0 < alpha < 1:
        raise ValueError("At least 1000 draws and 0 < alpha < 1 are required")
    rng = np.random.default_rng(seed)
    means = np.empty(draws)
    for begin in range(0, draws, 512):
        end = min(draws, begin+512)
        means[begin:end] = d[rng.integers(0, len(d), size=(end-begin, len(d)))].mean(axis=1)
    lo, hi = np.quantile(means, [alpha/2, 1-alpha/2])
    return {"units": len(d), "mean_difference": float(d.mean()), "interval": [float(lo), float(hi)],
            "alpha": alpha, "seed": seed, "draws": draws,
            "wins": int((d > 0).sum()), "ties": int((d == 0).sum()), "losses": int((d < 0).sum()),
            "assumption": "Paired exchangeable independent units; subjects or independent datasets, not overlapping train/test splits"}


def corrected_resampled_interval(candidate, reference, *, test_train_ratio: float, alpha: float = 0.05) -> dict:
    """Approximate overlap-corrected t interval for repeated holdout differences."""
    d = differences(candidate, reference)
    if not math.isfinite(test_train_ratio) or test_train_ratio <= 0 or not 0 < alpha < 1:
        raise ValueError("A positive finite test/train ratio and 0 < alpha < 1 are required")
    variance = float(d.var(ddof=1))
    error = math.sqrt((1/len(d)+test_train_ratio)*variance)
    radius = float(student_t.ppf(1-alpha/2, len(d)-1))*error
    mean = float(d.mean())
    return {"units": len(d), "mean_difference": mean, "interval": [mean-radius, mean+radius],
            "standard_error": error, "alpha": alpha, "test_train_ratio": test_train_ratio,
            "scope": "Nadeau-Bengio-style approximate correction; not a substitute for external independent data"}


def holm_adjust(p_values: Iterable[float]) -> list[float]:
    """Return monotone Holm-adjusted p-values in the original hypothesis order."""
    values = [float(p) for p in p_values]
    if not values or not all(math.isfinite(p) and 0 <= p <= 1 for p in values):
        raise ValueError("Finite p-values in [0, 1] are required")
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted, previous = [0.0]*len(values), 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1.0, (len(values)-rank)*values[i]))
        adjusted[i] = previous
    return adjusted


def comparison_label(interval: Iterable[float], margin: float) -> str:
    """Classify an interval with equivalence checked before directional effects."""
    values = list(interval)
    if len(values) != 2 or not all(math.isfinite(float(x)) for x in values) or values[0] > values[1] or not math.isfinite(margin) or margin <= 0:
        raise ValueError("An ordered finite interval and a positive margin are required")
    lo, hi = values
    if lo >= -margin and hi <= margin:
        return "EQUIVALENT_WITHIN_MARGIN"
    if lo > 0:
        return "POSITIVE_DIFFERENCE"
    if hi < 0:
        return "NEGATIVE_DIFFERENCE"
    return "INCONCLUSIVE"


def exact_mcnemar(candidate_correct: Iterable[bool], reference_correct: Iterable[bool]) -> dict:
    """Compute an exact paired binomial test on the same independent examples."""
    a, b = list(candidate_correct), list(reference_correct)
    if not a or len(a) != len(b) or any(type(x) is not bool for x in a+b):
        raise ValueError("Matched nonempty Boolean correctness arrays are required")
    wins = sum(x and not y for x, y in zip(a, b))
    losses = sum(y and not x for x, y in zip(a, b))
    n = wins+losses
    p = min(1.0, 2*sum(math.comb(n, k) for k in range(min(wins, losses)+1))/(1 << n)) if n else 1.0
    return {"candidate_only_correct": wins, "reference_only_correct": losses, "p_two_sided": p,
            "scope": "Independent paired examples; clustered observations require a cluster-level analysis"}
```

### 20.5. closure_wave.py

<!-- CODEFILE: agent_support/closure_wave.py -->
```python
"""Paraxial controls and complex modal projection for a declared scalar regime.

These controls support a new wave-validation protocol. They do not implement
the complete Neuro3D device or establish vector electromagnetic fidelity.
"""
from __future__ import annotations

import math
import numpy as np


def gaussian_1d(y, distance: float, wavelength: float, waist: float) -> np.ndarray:
    """Propagate a 1-transverse-dimensional Gaussian with its phase and Gouy term.

    The convention is exp(-i*omega*t), exp(+i*k*z); waist field exp(-y^2/w0^2).
    The amplitude factor is sqrt(w0/w), appropriate for one transverse dimension.
    """
    y = np.asarray(y, dtype=float)
    if not np.isfinite(y).all() or not all(math.isfinite(x) for x in (distance, wavelength, waist)) or wavelength <= 0 or waist <= 0:
        raise ValueError("Finite coordinates and positive wavelength/waist are required")
    k = 2*math.pi/wavelength
    rayleigh = math.pi*waist*waist/wavelength
    ratio = distance/rayleigh
    width = waist*math.sqrt(1+ratio*ratio)
    inverse_radius = distance/(distance*distance+rayleigh*rayleigh)
    phase = k*distance + 0.5*k*inverse_radius*y*y - 0.5*math.atan(ratio)
    return math.sqrt(waist/width)*np.exp(-(y/width)**2)*np.exp(1j*phase)


def angular_spectrum_1d(field, spacing: float, distance: float, wavelength: float) -> np.ndarray:
    """Use an FFT outgoing Helmholtz propagator on a finite periodic 1D window."""
    e = np.asarray(field, dtype=np.complex128)
    if e.ndim != 1 or len(e) < 8 or not np.isfinite(e).all() or spacing <= 0 or wavelength <= 0 or distance < 0 or not all(math.isfinite(v) for v in (spacing, distance, wavelength)):
        raise ValueError("A finite 1D field, positive spacing/wavelength, and nonnegative distance are required")
    k = 2*math.pi/wavelength
    ky = 2*math.pi*np.fft.fftfreq(len(e), d=spacing)
    kz = np.sqrt((k*k-ky*ky).astype(np.complex128))
    return np.fft.ifft(np.fft.fft(e)*np.exp(1j*kz*distance))


def modal_amplitude(field, reference_mode, spacing: float) -> complex:
    """Project onto a declared mode; retain complex phase instead of only power."""
    e, g = np.asarray(field, dtype=np.complex128), np.asarray(reference_mode, dtype=np.complex128)
    if e.ndim != 1 or e.shape != g.shape or not np.isfinite(e).all() or not np.isfinite(g).all() or spacing <= 0 or not math.isfinite(spacing):
        raise ValueError("Matched finite 1D arrays and a positive spacing are required")
    norm = float(np.vdot(g, g).real*spacing)
    if norm <= 0:
        raise ValueError("A zero reference mode has no defined modal amplitude")
    return complex(np.vdot(g, e)*spacing/norm)


def circular_phase_difference(a: complex, b: complex, dark_floor: float = 1e-12) -> float | None:
    """Return a wrapped phase difference; a dark field has undefined phase."""
    a, b = complex(a), complex(b)
    if not all(math.isfinite(v) for v in (a.real, a.imag, b.real, b.imag, dark_floor)) or dark_floor <= 0:
        raise ValueError("Finite fields and a positive dark-field floor are required")
    if abs(a) <= dark_floor or abs(b) <= dark_floor:
        return None
    return float(np.angle(a*np.conjugate(b)))


def observed_order(coarse: complex, medium: complex, fine: complex, refinement_ratio: float) -> dict:
    """Estimate convergence order for three matched observables and fixed geometry."""
    values = [complex(v) for v in (coarse, medium, fine)]
    if not all(math.isfinite(x) for v in values for x in (v.real, v.imag)) or refinement_ratio <= 1 or not math.isfinite(refinement_ratio):
        raise ValueError("Finite observables and a refinement ratio greater than one are required")
    d1, d2 = abs(values[0]-values[1]), abs(values[1]-values[2])
    if d1 == 0 or d2 == 0:
        return {"status": "INCONCLUSIVE", "reason": "ZERO_DIFFERENCE", "coarse_medium": d1, "medium_fine": d2}
    p = math.log(d1/d2)/math.log(refinement_ratio)
    return {"status": "DIAGNOSTIC", "order": p, "coarse_medium": d1, "medium_fine": d2,
            "scope": "Observed asymptotic diagnostic; neither a rigorous error bound nor proof that the asymptotic regime has been reached"}
```

### 20.6. closure_evidence.py

<!-- CODEFILE: agent_support/closure_evidence.py -->
```python
"""Read-only repository inventory, pin checking, and closure-record validation.

Integrity checks never establish scientific correctness. Objective acceptance
must also cite an independently executed verifier and its frozen raw results.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def sha256(path: Path) -> str:
    """Hash a file incrementally without loading large evidence into memory."""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def contained_file(root: Path, relative: str) -> Path:
    """Resolve a repository-relative file and reject escapes and absolute paths."""
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts or not p.parts or ":" in relative:
        raise ValueError("Only repository-relative evidence paths are accepted")
    target = (root/p).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("Evidence is missing or resolves outside the repository: "+relative)
    return target


def check_pins(root: Path, pins: dict[str, str]) -> list[dict]:
    """Check every source/evidence pin, reporting all mismatches without edits."""
    if not isinstance(pins, dict) or not pins:
        raise ValueError("A nonempty path-to-SHA256 dictionary is required")
    results = []
    for name, expected in sorted(pins.items()):
        try:
            if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
                raise ValueError("An exact lowercase SHA256 is required")
            actual = sha256(contained_file(root, name))
            results.append({"path": name, "status": "PASS" if actual == expected else "FAIL", "expected": expected, "actual": actual})
        except (ValueError, OSError) as exc:
            results.append({"path": name, "status": "BLOCKED", "reason": str(exc)})
    return results


def _git(root: Path, *arguments: str) -> str:
    """Run a bounded read-only git query with explicit arguments and no shell."""
    return subprocess.check_output(["git", "-C", str(root), *arguments], text=True, timeout=60)


def inventory(root: Path) -> dict:
    """Identify current state, missing tracked files, and import-time cwd changes."""
    root = root.resolve()
    head = _git(root, "rev-parse", "HEAD").strip()
    tracked = _git(root, "ls-files", "-z").split("\0")
    tracked = [s for s in tracked if s]
    missing, module_chdir, syntax_errors = [], [], []
    for relative in tracked:
        p = root/relative
        if not p.is_file():
            missing.append(relative)
            continue
        if p.suffix != ".py" or not relative.startswith(("Blender/", "Tools/", "Benchmarks/")):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8-sig"), filename=relative)
            for statement in tree.body:
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    fn = statement.value.func
                    if isinstance(fn, ast.Attribute) and fn.attr == "chdir":
                        module_chdir.append({"path": relative, "line": statement.lineno})
        except (SyntaxError, UnicodeError) as exc:
            syntax_errors.append({"path": relative, "reason": str(exc)})
    acceptance_path = root/"Docs/research/optic_neuro_blender_acceptance_v1.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8")) if acceptance_path.is_file() else None
    return {"schema": "neuro3d.closure.inventory.v1", "head": head,
            "tracked_files": len(tracked), "missing_tracked_files": missing,
            "module_scope_chdir": module_chdir, "python_syntax_errors": syntax_errors,
            "working_tree": _git(root, "status", "--porcelain").splitlines(),
            "canonical_priorities": acceptance["priorities"] if acceptance else None,
            "claim_policy": acceptance.get("claim_policy") if acceptance else None,
            "scope": "Static inventory only; no experiment, GPU, or proof has been executed"}


def verify_closure(root: Path, document: dict) -> dict:
    """Check that eleven fronts have honest states and verifiable evidence pins."""
    if document.get("schema") != "neuro3d.closure.manifest.v1":
        raise ValueError("Unsupported closure schema")
    objectives = document.get("objectives", [])
    if not isinstance(objectives, list) or any(not isinstance(x, dict) or type(x.get("id")) is not int for x in objectives):
        raise ValueError("Objectives must be dictionaries with integer identifiers")
    if sorted(x.get("id") for x in objectives) != list(range(1, 12)):
        raise ValueError("Exactly the eleven joint-status fronts are required")
    failures, unresolved = [], []
    states = {"PASS", "PARTIAL", "OPEN", "BLOCKED", "NOT_APPLICABLE"}
    for objective in objectives:
        oid, state = objective["id"], objective.get("state")
        if state not in states:
            failures.append({"id": oid, "reason": "INVALID_STATE"})
            continue
        if state == "NOT_APPLICABLE":
            if not objective.get("scope_reason"):
                failures.append({"id": oid, "reason": "UNEXPLAINED_SCOPE_EXCLUSION"})
            continue
        if state != "PASS":
            unresolved.append({"id": oid, "state": state, "remaining": objective.get("remaining", [])})
            continue
        if objective.get("remaining") or not objective.get("scientific_verifier_record"):
            failures.append({"id": oid, "reason": "PASS_WITHOUT_VERIFIER_OR_WITH_REMAINING_WORK"})
            continue
        checks = check_pins(root, objective.get("pins", {}))
        failures.extend({"id": oid, **x} for x in checks if x["status"] != "PASS")
        if objective["scientific_verifier_record"] not in objective.get("pins", {}):
            failures.append({"id": oid, "reason": "UNPINNED_SCIENTIFIC_VERIFIER"})
    return {"schema": "neuro3d.closure.integrity.v1", "failures": failures, "unresolved": unresolved,
            "integrity_pass": not failures, "all_selected_fronts_pass": not failures and not unresolved,
            "scope": "Manifest integrity only; verify scientific semantics, independence, and scope separately"}


def write_report(path: Path, report: dict) -> None:
    """Create a new report atomically with respect to an existing destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def main() -> int:
    """Expose static inventory and evidence checking without modifying sources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="action", required=True)
    inv = sub.add_parser("inventory")
    inv.add_argument("--out", type=Path, required=True)
    pins = sub.add_parser("check-pins")
    pins.add_argument("--profile", type=Path, required=True)
    closure = sub.add_parser("verify-closure")
    closure.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.action == "inventory":
            report = inventory(args.repo)
            write_report(args.out, report)
            print(json.dumps({"head": report["head"], "tracked_files": report["tracked_files"], "report": str(args.out)}))
            return 0
        if args.action == "check-pins":
            profile = json.loads(args.profile.read_text(encoding="utf-8"))
            checks = check_pins(args.repo, profile["pins"])
            print(json.dumps(checks, indent=2))
            return 0 if all(x["status"] == "PASS" for x in checks) else 2
        report = verify_closure(args.repo, json.loads(args.manifest.read_text(encoding="utf-8")))
        print(json.dumps(report, indent=2))
        return 0 if report["all_selected_fronts_pass"] else 2
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
```

### 20.7. support_demo.py

<!-- CODEFILE: agent_support/support_demo.py -->
```python
"""Run explicit CPU reference controls and save their complete outputs.

The examples are synthetic support-kit controls, not a Neuro3D training result,
blind task, GPU experiment, or full-device physical validation.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from closure_reference import (Interval, exact_first_hit, phase_from_length,
    coherent_field, modal_power, certified_argmax)
from closure_coherent import exact_roundoff_report, greedy_order
from closure_wave import gaussian_1d, angular_spectrum_1d, modal_amplitude
from closure_evidence import write_report


def control_result() -> dict:
    """Evaluate geometric, interference, cancellation, and free-space controls."""
    triangle = {"primitive_id": "thin-plane", "object_id": "plane",
                "vertices": [(-2, -1, F(1, 2**80)), (2, -1, F(1, 2**80)), (0, 2, F(1, 2**80))]}
    hit = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle])
    amplitude = (Interval.point(1), Interval.point(0))
    phase = phase_from_length(Interval.point(F(1, 2)), Interval.point(1))
    dark = modal_power(coherent_field([(amplitude, Interval.point(0)), (amplitude, phase)]))
    bright = modal_power(coherent_field([(amplitude, Interval.point(0)), (amplitude, Interval.point(0))]))
    terms = [1e16+1e16j, 1+2j, -1e16-1e16j]
    y = np.linspace(-20, 20, 4096, endpoint=False)
    spacing = float(y[1]-y[0])
    initial = gaussian_1d(y, 0, 0.1, 0.8)
    spectral = angular_spectrum_1d(initial, spacing, 2, 0.1)
    paraxial = gaussian_1d(y, 2, 0.1, 0.8)
    projection = modal_amplitude(spectral, paraxial, spacing)
    return {"schema": "neuro3d.closure.support_controls.v1",
            "scope": "Synthetic CPU support controls; not a claim about the complete Neuro3D device",
            "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "first_hit": {"status": hit["status"], "parameter_exact": str(hit["parameter"]), "primitive_ids": hit["primitive_ids"]},
            "interference": {"dark_power": dark.outward_wire(), "bright_power": bright.outward_wire(),
                             "wire_scope": "128-bit dyadic outward serialization; bounds may widen",
                             "certified_argmax": certified_argmax([dark, bright])},
            "reductions": [exact_roundoff_report(terms, name) for name in ("naive", "pairwise", "fsum")],
            "diagnostic_permutation": greedy_order(terms),
            "free_space_control": {"samples": len(y), "spacing": spacing, "distance": 2, "wavelength": 0.1, "waist": 0.8,
                                   "max_field_difference": float(np.max(np.abs(spectral-paraxial))),
                                   "modal_amplitude": [projection.real, projection.imag],
                                   "observable": "Normalized scalar modal overlap; not calibrated electromagnetic flux"}}


def main() -> int:
    """Create a new control receipt; never overwrite a previous run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = control_result()
    write_report(args.out, report)
    print(json.dumps({"receipt": str(args.out), "scope": report["scope"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 20.8. test_closure_support.py

<!-- CODEFILE: agent_support/test_closure_support.py -->
```python
"""Behavioral regressions for geometry, enclosures, coherence, and evidence."""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np

from closure_reference import (Interval, rational, sqrt_interval, segment_length,
    pi_interval, phase_from_length, unit_phasor, coherent_field, modal_power,
    certified_argmax, field_to_power_error, exact_first_hit)
from closure_coherent import (coherent_sum, greedy_order, exact_roundoff_report,
    pack_complex64, unpack_complex64, first_trace_divergence, compile_operator, apply_operator)
from closure_statistics import (paired_bootstrap, corrected_resampled_interval,
    holm_adjust, comparison_label, exact_mcnemar)
from closure_wave import (gaussian_1d, angular_spectrum_1d, modal_amplitude,
    circular_phase_difference, observed_order)
from closure_evidence import check_pins, verify_closure
from extract_support import extract, materialize


def triangle(z, pid="0", object_id="plane"):
    """Build a large triangle crossed by the positive-z ray through the origin."""
    return {"primitive_id": pid, "object_id": object_id,
            "vertices": [(-2, -1, z), (2, -1, z), (0, 2, z)]}


class IntervalTests(unittest.TestCase):
    def test_binary64_and_hex_decode_identically(self):
        self.assertEqual(rational(0.1), rational(0.1.hex()))
        self.assertNotEqual(rational(0.1), F(1, 10))

    def test_square_handles_zero_crossing(self):
        self.assertEqual(Interval(-2, 1).square(), Interval(0, 4))
        with self.assertRaises(ValueError):
            Interval.point(1)/Interval(-1, 1)

    def test_serialized_bounds_remain_outward_for_large_denominators(self):
        original = Interval(-F(1, 10**5000), F(1, 10**5000))
        lo, hi = map(F, original.outward_wire())
        self.assertLessEqual(lo, original.lo)
        self.assertGreaterEqual(hi, original.hi)

    def test_sqrt_uses_verified_endpoint_inequalities(self):
        b = sqrt_interval(Interval.point(2))
        self.assertLessEqual(b.lo*b.lo, 2)
        self.assertGreaterEqual(b.hi*b.hi, 2)
        self.assertEqual(sqrt_interval(Interval.point(4)), Interval.point(2))

    def test_coordinate_uncertainty_reaches_segment_length(self):
        b = segment_length((0, 0, 0), (Interval(3, F(31, 10)), 4, 0))
        self.assertTrue(b.contains(5))
        self.assertGreater(b.hi, 5)

    def test_machin_pi_with_an_independent_decimal_bracket(self):
        decimal = "3.141592653589793238462643383279502884197169399375105820974944"
        lower = F(decimal)
        upper = lower+F(1, 10**60)
        p = pi_interval(256)
        self.assertGreater(p.lo, lower)
        self.assertLess(p.hi, upper)

    def test_large_cycle_reduction_preserves_quarter_turn(self):
        phase = phase_from_length(Interval.point(F(10**30)+F(1, 4)), Interval.point(1))
        c, s = unit_phasor(phase)
        self.assertTrue(c.contains(0))
        self.assertTrue(s.contains(1))
        self.assertLess(c.radius, F(1, 10**20))

    def test_destructive_interference_is_not_a_missing_branch(self):
        amplitude = (Interval.point(1), Interval.point(0))
        field = coherent_field([(amplitude, Interval.point(0)), (amplitude, pi_interval())])
        power = modal_power(field)
        self.assertTrue(power.contains(0))
        self.assertLess(power.hi, F(1, 10**20))

    def test_overlapping_decisions_remain_unknown(self):
        self.assertIsNone(certified_argmax([Interval(0, 1), Interval(0, 1)]))
        self.assertEqual(certified_argmax([Interval(2, 3), Interval(0, 1)]), 0)
        self.assertEqual(field_to_power_error(F(2), F(1, 10)), F(41, 100))


class GeometryTests(unittest.TestCase):
    def test_ultrathin_positive_hit_is_not_skipped(self):
        gap = F(1, 2**80)
        hit = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(gap)])
        self.assertEqual(hit["status"], "HIT")
        self.assertEqual(hit["parameter"], gap)

    def test_shared_seam_keeps_both_primitive_identities(self):
        a = {"primitive_id": "a", "object_id": "square", "vertices": [(-1, -1, 1), (1, -1, 1), (1, 1, 1)]}
        b = {"primitive_id": "b", "object_id": "square", "vertices": [(-1, -1, 1), (1, 1, 1), (-1, 1, 1)]}
        hit = exact_first_hit((0, 0, 0), (0, 0, 1), [a, b])
        self.assertEqual(hit["primitive_ids"], ["a", "b"])
        self.assertEqual(hit["status"], "HIT")

    def test_distinct_tie_and_contact_remain_unknown(self):
        tie = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(1, "a", "a"), triangle(1, "b", "b")])
        self.assertEqual(tie["reason"], "DISTINCT_SURFACE_TIE")
        self.assertEqual(exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(0)])["reason"], "LAUNCH_CONTACT")

    def test_nearest_order_survives_below_float_ulp(self):
        near = F(1)+F(1, 2**80)
        far = F(1)+F(2, 2**80)
        hit = exact_first_hit((0, 0, 0), (0, 0, 1), [triangle(far, "far"), triangle(near, "near")])
        self.assertEqual(hit["primitive_ids"], ["near"])

    def test_coplanar_and_degenerate_queries_are_rejected(self):
        hit = exact_first_hit((0, 0, 1), (1, 0, 0), [triangle(1)])
        self.assertEqual(hit["reason"], "COPLANAR_QUERY")
        bad = {"primitive_id": "x", "object_id": "x", "vertices": [(0, 0, 1)]*3}
        self.assertEqual(exact_first_hit((0, 0, 0), (0, 0, 1), [bad])["reason"], "DEGENERATE_TRIANGLE")


class CoherenceTests(unittest.TestCase):
    def test_fsum_recovers_a_cancelled_small_component(self):
        terms = [complex(1e16, 1e16), 1+2j, complex(-1e16, -1e16)]
        self.assertEqual(coherent_sum(terms), 1+2j)
        self.assertEqual(exact_roundoff_report(terms)["observed_reduction_error_L1_exact"], "0")
        self.assertNotEqual(coherent_sum(terms, "naive"), 1+2j)

    def test_nonfinite_or_overflow_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            coherent_sum([complex(float("nan"), 0)])
        for method in ("naive", "pairwise"):
            with self.assertRaises(ValueError):
                coherent_sum([1e308, 1e308], method)

    def test_greedy_is_only_a_permutation(self):
        terms = [3+4j, -3-4j, 1j, -1j]
        order = greedy_order(terms)
        self.assertEqual(sorted(order), list(range(len(terms))))
        self.assertEqual(coherent_sum(terms), coherent_sum(terms[i] for i in order))

    def test_packet_roundtrip_is_bit_exact(self):
        packet = pack_complex64([complex(-0.0, 0.0), complex(0.1, -2.0)])
        self.assertEqual(pack_complex64(unpack_complex64(packet)), packet)
        with self.assertRaises(ValueError):
            unpack_complex64(packet[:-1])

    def test_trace_localizes_the_first_divergence(self):
        a = [{"state_id": 1, "components": {"local": [1, 0]}}, {"state_id": 2, "components": {"local": [2, 0]}}]
        b = [{"state_id": 1, "components": {"local": [1, 0]}}, {"state_id": 2, "components": {"local": [2.1, 0]}}]
        self.assertEqual(first_trace_divergence(a, b, 1e-11)["state_id"], 2)

    def test_compiled_operator_uses_transpose_not_adjoint(self):
        u = np.array([[1j, 2], [3, -1j]], dtype=np.complex128)
        compiled = compile_operator(lambda v: u@v, 2)
        x = np.array([[1+1j, 2-1j]], dtype=np.complex128)
        np.testing.assert_allclose(apply_operator(compiled, x), (u@x.T).T, atol=1e-14)


class StatisticsTests(unittest.TestCase):
    def test_bootstrap_is_paired_and_reproducible(self):
        a, b = [0.8, 0.9, 0.7], [0.7, 0.8, 0.6]
        self.assertEqual(paired_bootstrap(a, b, draws=1000), paired_bootstrap(a, b, draws=1000))
        self.assertAlmostEqual(paired_bootstrap(a, b, draws=1000)["mean_difference"], 0.1)

    def test_overlap_correction_increases_standard_error(self):
        a, b = [0.81, 0.92, 0.73, 0.84], [0.8]*4
        small = corrected_resampled_interval(a, b, test_train_ratio=0.01)
        large = corrected_resampled_interval(a, b, test_train_ratio=0.25)
        self.assertGreater(large["standard_error"], small["standard_error"])

    def test_multiplicity_and_equivalence(self):
        self.assertEqual(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        self.assertEqual(comparison_label([0.001, 0.009], 0.01), "EQUIVALENT_WITHIN_MARGIN")
        self.assertEqual(comparison_label([-0.1, -0.03], 0.01), "NEGATIVE_DIFFERENCE")

    def test_nonfinite_margin_and_unmatched_units_are_rejected(self):
        with self.assertRaises(ValueError):
            comparison_label([0, 1], float("nan"))
        with self.assertRaises(ValueError):
            paired_bootstrap([0.8, 0.7], [0.8])

    def test_exact_mcnemar_retains_pairing(self):
        p = exact_mcnemar([True]*10, [False]*10)["p_two_sided"]
        self.assertEqual(p, 2/1024)
        self.assertEqual(exact_mcnemar([True], [True])["p_two_sided"], 1)


class WaveTests(unittest.TestCase):
    def test_waist_control_and_paraxial_norm(self):
        y = np.linspace(-20, 20, 8192, endpoint=False)
        dy = y[1]-y[0]
        initial = gaussian_1d(y, 0, 0.1, 0.8)
        np.testing.assert_allclose(initial, np.exp(-(y/0.8)**2), atol=1e-14)
        propagated = gaussian_1d(y, 10, 0.1, 0.8)
        self.assertAlmostEqual(float(np.vdot(initial, initial).real*dy), float(np.vdot(propagated, propagated).real*dy), places=11)

    def test_spectrum_identity_and_declared_paraxial_agreement(self):
        y = np.linspace(-20, 20, 8192, endpoint=False)
        dy = y[1]-y[0]
        initial = gaussian_1d(y, 0, 0.1, 0.8)
        np.testing.assert_allclose(angular_spectrum_1d(initial, dy, 0, 0.1), initial, atol=1e-14)
        actual = angular_spectrum_1d(initial, dy, 2, 0.1)
        approximate = gaussian_1d(y, 2, 0.1, 0.8)
        self.assertLess(float(np.max(np.abs(actual-approximate))), 1e-4)

    def test_mode_projection_and_dark_phase(self):
        g = np.array([1, 2, 3], dtype=complex)
        self.assertAlmostEqual(abs(modal_amplitude((2+3j)*g, g, 0.1)-(2+3j)), 0)
        self.assertIsNone(circular_phase_difference(0, 1))
        self.assertAlmostEqual(circular_phase_difference(1j, 1), math.pi/2)

    def test_convergence_diagnostic_does_not_claim_a_proof(self):
        report = observed_order(1.04, 1.01, 1.0025, 2)
        self.assertAlmostEqual(report["order"], 2)
        self.assertEqual(observed_order(1, 1, 1, 2)["status"], "INCONCLUSIVE")


class EvidenceTests(unittest.TestCase):
    def test_changed_bytes_and_escapes_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/"receipt.json").write_bytes(b"{}")
            pins = {"receipt.json": hashlib.sha256(b"{}").hexdigest()}
            self.assertEqual(check_pins(root, pins)[0]["status"], "PASS")
            (root/"receipt.json").write_bytes(b"{ }")
            self.assertEqual(check_pins(root, pins)[0]["status"], "FAIL")
            self.assertEqual(check_pins(root, {"../secret": "0"*64})[0]["status"], "BLOCKED")

    def test_unresolved_fronts_cannot_be_complete(self):
        manifest = {"schema": "neuro3d.closure.manifest.v1", "objectives": [{"id": i, "state": "OPEN", "remaining": ["Independent evidence required"]} for i in range(1, 12)]}
        with tempfile.TemporaryDirectory() as directory:
            report = verify_closure(Path(directory), manifest)
        self.assertTrue(report["integrity_pass"])
        self.assertFalse(report["all_selected_fronts_pass"])

    def test_malformed_front_identifiers_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                verify_closure(Path(directory), {"schema": "neuro3d.closure.manifest.v1", "objectives": [{"id": None}]})

    def test_extraction_rejects_overwrite_and_path_traversal(self):
        text = '<!-- CODEFILE: agent_support/a.py -->\n```python\nprint("ready")\n```'
        blocks = extract(text)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertTrue(materialize(blocks, root)[0]["created"])
            self.assertFalse(materialize(blocks, root)[0]["created"])
            (root/"agent_support/a.py").write_text("different")
            with self.assertRaises(ValueError):
                materialize(blocks, root)
        with self.assertRaises(ValueError):
            extract(text.replace("agent_support/a.py", "../a.py"))


if __name__ == "__main__":
    unittest.main()
```

### 20.9. requirements-closure.txt

<!-- CODEFILE: agent_support/requirements-closure.txt -->
```text
# Support-kit environment verified with CPython 3.12.14 on Linux.
# This is independent of the historical Windows and Blender environments.
numpy==2.3.5
scipy==1.17.0
```

### 20.10. closure-manifest.json

<!-- CODEFILE: agent_support/closure-manifest.json -->
```json
{
  "schema": "neuro3d.closure.manifest.v1",
  "base_commit": "69db25ce7b04a98e24609bcd539c5041f269658d",
  "snapshot_date": "2026-10-12",
  "scope": "Eleven joint-status fronts; separate from the canonical ten-objective acceptance JSON",
  "objectives": [
    {
      "id": 1,
      "name": "State and provenance",
      "state": "PARTIAL",
      "remaining": [
        "Integrate post-2026-10-09 evidence; preserve historical NULL and immutable receipts"
      ]
    },
    {
      "id": 2,
      "name": "Correct graphics engine",
      "state": "PARTIAL",
      "remaining": [
        "Explain resident-field divergence; verify native outputs and tangents"
      ]
    },
    {
      "id": 3,
      "name": "Geometry and optimizations",
      "state": "PARTIAL",
      "remaining": [
        "Extend adverse geometry; prove cache invalidation and retained branches"
      ]
    },
    {
      "id": 4,
      "name": "End-to-end error and robustness",
      "state": "PARTIAL",
      "remaining": [
        "Transform/input/model preimages and all claimed gradient budgets"
      ]
    },
    {
      "id": 5,
      "name": "Learning and capacity",
      "state": "PARTIAL",
      "remaining": [
        "Broader geometry families, conditioning, and independent controls"
      ]
    },
    {
      "id": 6,
      "name": "Generalization and fair references",
      "state": "PARTIAL",
      "remaining": [
        "New reserved data; nested EEG comparators; matched tuning"
      ]
    },
    {
      "id": 7,
      "name": "Wave fidelity",
      "state": "PARTIAL",
      "remaining": [
        "Confirm diffraction prospectively; validate the declared full network"
      ]
    },
    {
      "id": 8,
      "name": "Hardware and total cost",
      "state": "PARTIAL",
      "remaining": [
        "External graphics, actual AMD, isolated energy, structural scaling"
      ]
    },
    {
      "id": 9,
      "name": "Product and recovery",
      "state": "PARTIAL",
      "remaining": [
        "Accepted GPU UI, repeated resume interruption, bounded power-loss tests"
      ]
    },
    {
      "id": 10,
      "name": "Reproduction and scientific delivery",
      "state": "PARTIAL",
      "remaining": [
        "Clean complete reproduction, human specialist critique, final manuscript"
      ]
    },
    {
      "id": 11,
      "name": "Novelty and impact",
      "state": "OPEN",
      "remaining": [
        "Closest-method comparison and demonstrated useful contribution; external identifiers only if obtained"
      ]
    }
  ]
}
```

### 20.11. scientific_closure_cpu.yml

<!-- CODEFILE: agent_support/scientific_closure_cpu.yml -->
```yaml
# Copy to .github/workflows/scientific-closure-cpu.yml after the support kit is committed.
# This job verifies the support kit. It does not certify the full project or a GPU.
name: Scientific closure support CPU
on:
  workflow_dispatch:
  pull_request:
    paths:
      - 'agent_support/**'
      - '.github/workflows/scientific-closure-cpu.yml'
permissions:
  contents: read
jobs:
  support:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install declared support dependencies
        run: python -m pip install -r agent_support/requirements-closure.txt
      - name: Run support regressions
        env:
          PYTHONNOUSERSITE: '1'
          PYTHONDONTWRITEBYTECODE: '1'
          OPENBLAS_NUM_THREADS: '1'
          OMP_NUM_THREADS: '1'
        run: python -m unittest discover -s agent_support -p 'test_*.py' -v
```

## 21. Ejecución inmediata del kit y validación de la entrega

Después de extraer todos los bloques desde esta guía, ejecuta desde la raíz del checkout:

```bash
python -m unittest discover -s agent_support -p 'test_*.py' -v
python agent_support/support_demo.py --out agent_support-control-run01.json
python agent_support/closure_evidence.py --repo . verify-closure --manifest agent_support/closure-manifest.json
```

El último comando **debe devolver 2 en el estado inicial**, porque hay frentes PARTIAL/OPEN. Ese código es una protección contra declarar el cierre, no un fallo del kit. Los cambios reales se registran en copias sucesoras del manifiesto con evidencia y verificadores; el estado inicial se conserva como snapshot.

El primer comando comprueba los 33 controles del kit. El segundo produce un recibo sintético CPU, con todas sus salidas y ámbito explícito; no es una ejecución GPU ni una nueva clasificación del proyecto. Nunca publiques ese recibo como sustituto de P1-7, de un certificado nativo o de una prueba ciega.

> **Revisión v2.** Con el kit v2 extraído, el mismo comando ejecuta 57 pruebas (33 v1 y 24 v2); §39 añade el recibo v2 y la verificación del manifiesto de frontera, que también devuelve 2 en el estado inicial.

En esta preparación se ejecutaron esas 33 regresiones en Linux. La entrega final también se comprueba extrayendo el código del propio Markdown y ejecutando sus pruebas desde la copia extraída, verificando identidades de bytes y JSON/YAML. Las pruebas completas de Neuro3D, Blender, NVIDIA/AMD, experimentos EEG, demostraciones Lean, durabilidad eléctrica y revisión humana son trabajos que el agente debe ejecutar bajo sus protocolos. La guía contiene sus instrucciones; no los presenta como ya terminados.

Para informar al propietario al terminar un hito, comunica: problema y resultado; hipótesis aceptada/refutada/inconclusa; commit; pruebas y limitaciones; enlaces a datos/código; y siguiente dependencia concreta. Evita porcentajes de proyecto completado o promesas de premio sin un denominador y evidencia verificables.

## 22. Revisión v2: método, comprobaciones ejecutadas y alcance

Esta revisión trató la guía como una hipótesis que había que poner a prueba. Se siguieron cuatro reglas:

1. **Nada se borra.** El texto original y los once bloques `CODEFILE` se conservan; el `diff` contra el original solo contiene líneas añadidas (comprobado, §39).
2. **Cada afirmación nueva tiene una comprobación ejecutada o una fuente localizada.** Lo que no pudo comprobarse figura como no comprobado.
3. **Los defectos se reproducen antes de corregirse.** Cada errata de código tiene una prueba que demuestra el defecto en v1 y la corrección en v2.
4. **Las correcciones son sucesoras, no ediciones.** El código v1 sigue intacto; las funciones corregidas viven en módulos nuevos.

### 22.1. Comprobaciones ejecutadas

| Comprobación | Resultado |
|---|---|
| Base `69db25c` en GitHub | Existe y era el HEAD de `main` el 12-oct-2026 (0 commits posteriores). 9.317 archivos rastreados, árbol de 2,5 GB, licencia MIT, sin `AGENTS.md` ni `CITATION.cff` |
| Rutas citadas por la guía | Todas las rutas con directorio existen; tres referencias sin ruta completa eran inexactas (§23, E1–E3) |
| Cifras de la tabla del §2 | Todas presentes en documentos y resultados del commit (nota v2 del §2) |
| Kit v1 en el entorno declarado | 33/33 con CPython 3.12.3, NumPy 2.3.5 y SciPy 1.17.0 (la guía cita 3.12.14; no se dispuso de esa revisión menor) |
| Kit v1 en un entorno reciente | 33/33 con CPython 3.13.16, NumPy 2.5.3 y SciPy 1.18.1 |
| Demo v1 y `verify-closure` | Recibo generado; `verify-closure` devuelve 2, como indica §21 |
| Regresiones del §6.2 | 8/8 archivos (55 pruebas) pasan en un único entorno limpio: CPython 3.12.3, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.7.2 y mpmath 1.3.0, las versiones del workflow sucesor. Sin mpmath no importa `test_state_graph_enclosure_v1`; sin scikit-learn, `test_escala_modos` |
| Lock del proyecto | `requirements-lock-20261009.txt` no es instalable como conjunto: pip no resuelve juntos `numpy==2.2.6`, `scipy==1.15.1` y `scikit-learn==1.4.0` (CPython 3.12.3, Linux) |
| Suite completa `Blender/tests` | 1.344 pruebas: 5 fallos, 241 errores, 4 omitidas (clasificación en la nota v2 del §6.1); ningún archivo rastreado modificado |
| Job CI existente `cpu-tests.yml` | No instala dependencias; en un entorno vacío equivalente: 1.259 pruebas, 5 fallos, 237 errores |
| `chdir` al importar | Dos módulos, no uno: `Blender/tests/test_validacion_onda.py:8` y `Benchmarks/eeg-motor-imagery/codigo/work/nested/predict_var.py:7` |
| Diagnóstico de difracción de P1-7 | Reproducido de forma independiente en espacio libre: solapamiento 0,973181 (espectro angular) frente a 0,973210 (fórmula paraxial) |
| `openai/math@fd4aeeb` | Existe y seguía siendo `main`; rutas, endpoints, axiomas permitidos, 372 familias y 719 manuscritos confirmados; toolchain `leanprover/lean4:v4.34.1`; licencia Apache-2.0 |
| Referencias añadidas (§37) | Cada una localizada en su editorial, arXiv, repositorio institucional o web oficial |
| Kit v2 | 57/57 pruebas (33 v1 + 24 v2) en los dos entornos anteriores; pyflakes sin avisos en todo el kit |

### 22.2. Lo que esta revisión no comprobó

Los comandos PowerShell en Windows; Blender 4.5.14 y cualquier ruta GPU; la cola `gpuq` y los perfiles NVIDIA/AMD; la compilación Lean y Comparator; los experimentos EEG; el contenido científico del PDF más allá de su número de páginas; el historial de ejecuciones de GitHub Actions (la API de GitHub no estaba disponible en esta sesión; `git` por HTTPS sí). Ninguna de esas tareas debe darse por hecha a partir de esta revisión.

### 22.3. Identidad de los bloques originales

SHA256 de cada bloque v1 tal como lo escribe `extract_support.py` (LF y salto final). Si un agente obtiene otro valor, el bloque se alteró:

| Archivo | Bytes | SHA256 |
|---|---|---|
| `agent_support/extract_support.py` | 3288 | `ca9ba0fae9e10595b0ff9556241c3ec5f1548bd95d35cab0127514b41167bfd5` |
| `agent_support/closure_reference.py` | 11980 | `569e78649fac4cf60d09735e2751a91481affe7b4668fb9bef7d1b62974d3409` |
| `agent_support/closure_coherent.py` | 6826 | `ed24a106c2e36b10c0fedc6328ed57436558defe2fac0bb3dca8086590911063` |
| `agent_support/closure_statistics.py` | 4854 | `5faa0fdbc13fc9f11c781224dbe9830665825bf5b5d607d9b2bc491f1a87ea5d` |
| `agent_support/closure_wave.py` | 4163 | `a0e362a8b01a611d1aa863921b931b617c3a6bf3e020d9a4aa9554f5938d1684` |
| `agent_support/closure_evidence.py` | 8456 | `4fc50b31899594047ce42c429455c84709f8a7db3c526b84ee4fd4033b4fc420` |
| `agent_support/support_demo.py` | 3464 | `6d1ac262218c61d5304b6a5e3b846ea92f25cb109690aa1bd957d18d582ad4be` |
| `agent_support/test_closure_support.py` | 12464 | `105ab9fcd598dd344f78603ef7ec79ddac8fe0e7701014131b2b090f945856b7` |
| `agent_support/requirements-closure.txt` | 167 | `18f47b45605e1172acf646501604bea61861af754a15da9e1865c34724a5acb2` |
| `agent_support/closure-manifest.json` | 2546 | `2e783b7a62ae2fa850be4f8a88d9825a1816d3b077920a113179df1e33eec3c0` |
| `agent_support/scientific_closure_cpu.yml` | 944 | `06f7800bffb37de1afcc0b19b61202762a6bdef8fd2d83f23124440292bed600` |

SHA256 de la guía original recibida: `28d456ed40154880dfde9d54fe979231ee0f9ad3d09f8a621a64b6cec1ad54ec` (124.814 bytes, 1.847 líneas).

## 23. Fe de erratas consolidada

| ID | Dónde | Problema | Evidencia | Acción |
|---|---|---|---|---|
| E1 | §9.1 | `surface_union_interior_v1.py` no existe | `test_surface_union_interior_v1.py` importa `Blender.benchmarks.capacity_audit.robust_multipath_v1` | Usa `robust_multipath_v1.py`; `exact_object_index_v1.py` está en el mismo directorio `Blender/benchmarks/capacity_audit/` |
| E2 | §10.3 | `outer_folds` e `inner_folds` no están en `bench.py` | Definidos en `Benchmarks/eeg-motor-imagery/codigo/work/nested/nested_bench.py`, líneas 43 y 48 | `csp_filters` y `EEGNet` sí están en `Benchmarks/eeg-motor-imagery/codigo/work/bench.py` |
| E3 | §6.1 | Hay dos `chdir` de importación, no uno | Detector `inventory` del kit sobre el árbol real | Corrige ambos; `predict_var.py` además modifica `os.environ` al importarse |
| E4 | §6.2 | La suite seleccionada necesita `mpmath` y scikit-learn | `ModuleNotFoundError` sin ellos | Instala NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.7.2 y mpmath 1.3.0 (comprobado) u otro conjunto que compruebes |
| E5 | Kit v1 | `coherent_sum(..., "fsum")` deja escapar `OverflowError` en lugar de `ValueError` | `math.fsum([1e308, 1e308])` | `coherent_sum_v2` |
| E6 | Kit v1 | `exact_first_hit` devuelve UNKNOWN por un primitivo degenerado lejano o coplanar detrás del origen | Un triángulo degenerado en t = 50 anula un impacto válido en t = 1 | `exact_first_hit_v2` |
| E7 | Kit v1 | Los extremos racionales crecen sin control | 16.399 bits en un fasor; 33.379 bits en una potencia; 64 caminos ≈ 1 s | `tighten`, `unit_phasor_v2`, `coherent_field_v2` (≤ 161 bits por extremo) |
| E8 | §10.2 y kit | `comparison_label` usa un único intervalo para equivalencia y para dirección | Definición de TOST | Intervalo 1−2α para equivalencia; `tost_paired` |
| E9 | §4.2 | El bloque Linux omite la extracción y el cambio de directorio | Lectura del bloque | Secuencia completa en la nota v2 del §4.2 |
| E10 | Repositorio | `cpu-tests.yml` ejecuta la suite sin instalar dependencias | Simulación en entorno vacío | Workflow sucesor `neuro3d_selected_cpu.yml` (§38) |
| E11 | §14.3 | Solo cita el primer teorema de dos challenges | JSON de los challenges | Comparator comprueba todos los `theorem_names` (nota v2 del §14.3) |
| E12 | §10.3 | No da la ruta de `bench.py` | Árbol del commit | Ruta en E2 |
| E13 | Kit v1 | `rational(" 0x1p-3")` falla por el espacio inicial | Reproducido | Sin cambio de código: normaliza las entradas; solo se documenta |
| E14 | §10.1 (precisión, no error del original) | Para decisiones `argmax`, las clases libre y pasiva coinciden | Multiplicar W por cualquier c > 0 no cambia la decisión | La pasividad solo pesa con ganancia o presupuesto de fotones fijos; H-A compara contra la clase cuadrática y contra la geometría |
| E15 | Repositorio | `requirements-lock-20261009.txt` no puede instalarse como conjunto | pip devuelve `ResolutionImpossible` para `numpy==2.2.6`, `scipy==1.15.1` y `scikit-learn==1.4.0` | Locks por perfil generados desde entornos reales y probados en limpio (refuerza §4.2) |

Ninguna errata invalida un resultado publicado del proyecto: afectan a instrucciones para el agente, al kit de apoyo o a la infraestructura de reproducción del repositorio (E10, E15).

## 24. Qué exige una contribución de nivel Nobel y qué significa para Neuro3D

Esta sección responde a la aspiración declarada en §1 con hechos verificables, no con promesas. Ninguna guía, agente ni cantidad de pruebas produce un premio; lo que sí puede hacerse es saber qué evidencia lo haría plausible y orientar el trabajo para generarla o para descubrir pronto que no es alcanzable.

### 24.1. Qué reconocen los premios de física cercanos a este campo

| Año | Laureados | Reconocimiento |
|---|---|---|
| 2009 | Charles K. Kao; Willard S. Boyle y George E. Smith | Transmisión de luz en fibras para comunicación óptica; invención del sensor CCD |
| 2014 | Isamu Akasaki, Hiroshi Amano y Shuji Nakamura | LED azules eficientes |
| 2018 | Arthur Ashkin; Gérard Mourou y Donna Strickland | Pinzas ópticas; amplificación de pulsos con chirp (CPA) |
| 2024 | John J. Hopfield y Geoffrey E. Hinton | Descubrimientos fundamentales que permiten el aprendizaje automático con redes neuronales artificiales |
| 2025 | John Clarke, Michel H. Devoret y John M. Martinis | Túnel cuántico macroscópico y cuantización de la energía en un circuito eléctrico |

Rasgos comunes, como hechos y no como receta: un principio físico o un método demostrado experimentalmente; una capacidad nueva o una mejora de órdenes de magnitud en algo que importa; confirmación por otros grupos; uso amplio que habilitó ciencia o tecnología posteriores; y un desfase de décadas entre el trabajo y el premio (el trabajo de Kao sobre fibras es de 1966, el CCD de 1969, la red de Hopfield de 1982 y la CPA de 1985). El premio de 2024 muestra que el comité reconoce computación conectada con la física, pero lo hizo con ideas de hace cuatro décadas adoptadas de forma masiva. No existe un Nobel de informática; en computación, el reconocimiento comparable es el Premio Turing.

### 24.2. Criterios observables para Neuro3D

| Criterio | Qué tendría que existir |
|---|---|
| C1 Principio | Una afirmación física, no solo de software; por ejemplo: «la propagación coherente en geometría 3D capturada implementa, con decisiones certificadas, una familia de funciones útil que se transfiere a un dispositivo fabricado con error acotado» |
| C2 Ventaja medida | Mejora de órdenes de magnitud en energía por inferencia, latencia o densidad de cómputo, medida extremo a extremo (fuente, moduladores, detectores, conversión y electrónica) frente a la mejor alternativa electrónica a igual exactitud |
| C3 Teoría predictiva | Leyes de escala y límites que predijeron la ventaja antes de medirla |
| C4 Réplica | Otro grupo reproduce o replica el resultado sin ayuda del proyecto |
| C5 Capacidad nueva | Algo que antes no podía hacerse, no solo hacerlo más rápido |
| C6 Adopción | Grupos independientes usan el método y lo documentan ellos mismos |

### 24.3. Situación el 12 de octubre de 2026

C1, parcial y solo como simulador: el modelo escalar está delimitado y su variante sin difracción quedó refutada en un régimen; no hay dispositivo. C2, no: toda la computación es electrónica y la ruta gráfica es más lenta que la CPU en los seis pares medidos. C3, no: no hay leyes de escala predictivas. C4, no: hay ejecución automática externa, no réplica por otro equipo. C5, por demostrar: la certificación conjunta de geometría, transporte y decisión es la candidata más clara, pero falta compararla con los métodos cercanos de §13. C6, no.

Esto describe un punto de partida, no un fracaso. Pero de ello se sigue una conclusión que el agente debe respetar: **la ruta de simulación en GPU no puede, por sí sola, satisfacer C2 ni C5 en sentido físico**, porque una GPU que simula óptica sigue siendo electrónica.

### 24.4. Decisión estratégica D0, que corresponde al propietario

- **D0-A, instrumento computacional.** Cerrar Neuro3D como simulador certificado, reproducible y publicado (pasos A–J, K, L y O–R). Alcanzable con los recursos actuales; resultado citable y útil; sin tesis física.
- **D0-B, programa de frontera.** Lo anterior más la línea física con un socio experimental (§16 deja de ser opcional; §27 y §28). Es la única vía compatible con C1–C6, y exige años, financiación y colaboración externa.

Prepara ambas opciones con coste, riesgo y dependencias, pero no elijas tú: es una decisión del propietario, tomada según su propio método de trabajo. D0-A es en cualquier caso prerrequisito de D0-B: un simulador certificado es la herramienta de diseño y el oráculo de predicción del demostrador.

### 24.5. Lo que el agente no debe hacer en nombre de esta aspiración

No afirmar novedad, superioridad ni importancia sin la evidencia del criterio correspondiente; no presentar la aspiración como objetivo cumplido; no marcar PASS en F5 ni en F9, que solo se cierran con evidencia producida por terceros; no contactar con comités, revistas ni investigadores (prepara, no envíes).

## 25. Paso K: pregunta central y teoría falsable

Formula y preregistra estas hipótesis antes de los experimentos de los pasos F y G. Para cada una: predicción numérica, criterio de refutación, comparador, datos y presupuesto.

**H-A, ¿aporta algo la geometría?** Para una codificación fija hay tres clases de decisión anidadas: F_quad (argmax de formas cuadráticas arbitrarias xᵀQ_j x), F_lin (argmax |W_j x|² con W complejo cualquiera; para decisiones `argmax` coincide con la clase pasiva, porque escalar W no cambia la decisión) y F_geom (W realizable por la geometría capturada y sus parámetros). Con entrada real, F_lin limita cada detector a rango ≤ 2 (§10.1), así que F_geom ⊆ F_lin ⊆ F_quad. La comparación informativa es doble: F_quad frente a F_lin mide el coste de la linealidad pasiva; F_lin frente a F_geom mide el coste de la geometría. La pasividad añade restricciones reales solo con ganancia de detección o presupuesto de fotones fijos; en ese régimen, compara F_lin pasiva con F_geom bajo el mismo ruido. `train_detector_classifier` (§38) entrena F_lin con ganancia fija, con o sin la proyección pasiva; F_geom es el entrenamiento propio del proyecto. Preregistra la brecha esperada por tarea y su intervalo.

**H-B, ley de cobertura de certificados.** A partir del margen de decisión y del presupuesto de error de §9.2, predice qué fracción de decisiones quedará certificada en cada nivel de perturbación. Refuta si la cobertura observada en datos nuevos cae fuera del intervalo predicho.

**H-C, transferencia simulación–realidad (solo D0-B).** Predice la matriz de transferencia y las decisiones del dispositivo con la incertidumbre propagada de §27. Refuta si la concordancia medida cae fuera de lo predicho.

**H-D, escalado de energía y latencia.** Predice la energía y la latencia por inferencia en función de modos, fuentes y precisión con el modelo de §28. Refuta con la medición extremo a extremo.

**Dimensión alcanzable.** Estima la dimensión local del conjunto de operadores U(θ) con `numerical_jacobian` y `effective_rank` en muchos θ, comunicando siempre los valores singulares y la tolerancia, nunca solo el rango. Una dimensión local muy inferior a la de F_lin explica, antes de entrenar, por qué F_geom puede quedarse corta.

## 26. Paso L: teoría fundamental y núcleo verificado formalmente

Cinco lemas pequeños sostienen todos los certificados. Conviene enunciarlos y demostrarlos en Lean 4 con Mathlib:

- **T1, certificado de decisión.** Si el límite inferior de P_i supera los superiores de todos los demás, el argmax verdadero es i para cualquier valor dentro de las cajas.
- **T2, potencia.** Con A ≥ |E_obs| y e ≥ |E_true − E_obs|, se cumple |P_true − P_obs| ≤ 2Ae + e².
- **T3, cola de Neumann.** Con una norma inducida y ‖A‖ ≤ r < 1, la cola tras K términos está acotada por r^(K+1)‖b‖/(1−r).
- **T4, rango.** Con entrada real, cada detector es una forma cuadrática de rango ≤ 2 y la diferencia de dos, de rango ≤ 4; con entrada compleja, cada detector es una forma hermítica de rango 1.
- **T5, pasividad.** Si U es una contracción, ‖Ux‖ ≤ ‖x‖ y la potencia total de salida no supera la de entrada.

Son resultados conocidos o elementales; su valor no es la novedad, sino que el núcleo de los certificados quede comprobado por máquina y libre de errores de transcripción. Fija toolchain y versión de Mathlib, compila en un proceso limpio y comprueba con `#print axioms` que solo aparecen los axiomas estándar. Esta revisión no escribió ni compiló esas demostraciones: es trabajo del agente.

Teoría con posible novedad, que debe demostrarse frente a la literatura y no suponerse: (a) caracterización de F_geom para familias de escenas (dimensión, conexidad, condicionamiento); (b) cotas de cobertura de certificados en función del margen y del ruido, que es H-B; (c) límites de energía por inferencia para redes pasivas con detección, partiendo del razonamiento de límite cuántico estándar de Hamerly et al. (2019) y de la demostración experimental de Wang et al. (2022) con menos de un fotón por multiplicación.

## 27. Paso M: demostrador físico y transferencia simulación–realidad (solo con D0-B)

**Escalera mínima**, con predicciones registradas antes de cada medida: (1) interferómetro Mach–Zehnder con visibilidad y estabilidad de fase medidas; (2) red 2×2 reconfigurable con tomografía de su matriz de transferencia; (3) una red pequeña reproducida desde una escena capturada; (4) la red 5→8 o una equivalente.

**Plataformas candidatas**, por coste y riesgo crecientes: óptica de espacio libre con componentes comerciales; fibra con acopladores y desfasadores; fotónica integrada en obleas multiproyecto con un socio. La elección corresponde al propietario y al socio.

**Métricas**: error de la matriz de transferencia medida frente a la predicha (norma de Frobenius normalizada, con incertidumbre), concordancia de decisiones, fracción de decisiones certificadas que siguen siendo correctas en el dispositivo y deriva temporal. Evalúa la incertidumbre según la GUM (JCGM 100:2008) y propágala por Monte Carlo según JCGM 101:2008.

**Entrenamiento con el dispositivo en el bucle**: compara, con el mismo presupuesto, entrenamiento solo en simulación, entrenamiento consciente de la física (Wright et al., 2022) y retropropagación in situ (Pai et al., 2023).

**Seguridad**: el trabajo con láseres sigue IEC 60825-1 y las normas del laboratorio (protección ocular, formación, responsable de seguridad láser). El agente no opera equipo físico; prepara protocolos para personas cualificadas.

## 28. Paso N: energía y latencia extremo a extremo

**Escalas de referencia**, calculadas con `closure_limits.py`; no son cotas de ningún dispositivo. Un fotón de 1.550 nm tiene 1,28·10⁻¹⁹ J. kT·ln 2 a 300 K vale 2,87·10⁻²¹ J y es una escala de borrado irreversible, no un límite óptico. Distinguir 2^b niveles adyacentes separados por k desviaciones de Poisson exige del orden de k²·4^b fotones a fondo de escala: 1.024 para b = 4 y k = 2, unos 2,6·10⁻¹⁷ J por operación con fan-in 5 y eficiencia ideal. Con fan-in 5 la escala no es pequeña: la ventaja energética de la óptica coherente, si existe, aparece con fan-in grande, que es justo lo que falta medir.

**Protocolo**: mide toda la cadena (fuente, modulación, propagación, detección, conversión analógico-digital y digital-analógica, electrónica), en frío y en caliente, a igual exactitud de tarea frente a la mejor referencia electrónica (BLAS optimizado o acelerador dedicado). Declara el punto de cruce si existe y su ausencia si no. No compares la energía de una GPU que simula con una escala fotónica teórica, ni una escala ideal con una medida real.

## 29. Paso O: análisis ciego, revisión adversarial y Registered Reports

**Etiquetas selladas.** Antes de congelar un análisis, el propietario genera una sal secreta (`new_salt`), publica en un commit solo la raíz y el recuento de `commit_labels`, y guarda sal y etiquetas fuera del alcance del agente. El agente congela protocolo y código; el propietario revela; cualquiera verifica con `verify_reveal`. Es el análisis ciego habitual en física de partículas (Klein y Roodman, 2005) aplicado a datos nuevos.

**Equipo rojo.** Un agente o una persona distinta del productor intenta refutar cada afirmación con acceso al código y a los datos, sin ver el razonamiento del productor. Su informe se archiva aunque no encuentre nada.

**Colaboración adversarial.** A través del propietario, se puede invitar a quien defienda la hipótesis contraria a acordar el diseño del experimento decisivo antes de ejecutarlo.

**Registered Reports.** Si el propietario lo decide, el protocolo se envía a una revista que acepte este formato (el Center for Open Science mantiene la lista) para obtener la aceptación en principio antes de conocer los resultados. Es la forma más fuerte de mostrar que la conclusión no se ajustó a los datos.

## 30. Paso P: control del error a nivel de programa e inferencia secuencial

Neuro3D ha ejecutado decenas de ensayos. Aunque cada uno controle su error, el programa acumula oportunidades de falso positivo. Mantén un registro de todos los ensayos, también de los abandonados, con hipótesis y decisión (`validate_experiment_record`). Distingue en cada figura lo confirmatorio de lo exploratorio. Para las afirmaciones del artículo, declara la familia de hipótesis y controla la multiplicidad sobre ella. Calcula el tamaño muestral para el efecto mínimo relevante antes de recoger datos.

Si un protocolo quiere mirar resultados conforme llegan y detenerse pronto, usa un proceso-e (`paired_sign_eprocess`): bajo H0, la probabilidad de que llegue alguna vez a 1/α es ≤ α (desigualdad de Ville; Ramdas et al., 2023), así que puede consultarse en cualquier momento sin inflar el error. Para equivalencia, TOST con intervalo 1−2α (`tost_paired`; Lakens, 2017).

## 31. Paso Q: réplica independiente y ciencia abierta

**Objetivos de evaluación de artefactos** (política de ACM, versión 1.1): *Artifacts Available*; *Artifacts Evaluated — Functional* y *— Reusable*; *Results Reproduced* (otro equipo obtiene los resultados usando en parte los artefactos de los autores) y *Results Replicated* (otro equipo los obtiene sin ellos). Los dos últimos corresponden a F5 y no los concede el proyecto.

**Archivo**: DOI por release (por ejemplo, con la integración entre GitHub y Zenodo); identificador de Software Heritage; `CITATION.cff` (no existe en `69db25c`) con autores reales y sus ORCID; licencia del código (MIT); licencia y procedencia de cada conjunto de datos; contenedor con digest fijado; dependencias exactas por perfil.

## 32. Paso R: autoría, declaración del uso de IA y ética

**Autoría**: solo personas que aceptan la responsabilidad del trabajo, con roles según la taxonomía CRediT (ANSI/NISO Z39.104-2022). Las herramientas de IA no son autoras; su uso se declara en métodos según la política de la revista elegida, y los registros de agentes (JEV, Codex, Claude u otros) se archivan como material suplementario.

**Referencias**: extrae DOIs e identificadores arXiv del manuscrito con `extract_identifiers` y compruébalos con `resolve_identifiers`; después verifica a mano que título, autores y contenido corresponden a lo citado. Que un DOI exista no prueba que la cita sea correcta.

**Ética**: cualquier dato humano nuevo (EEG u otro) requiere aprobación previa de un comité de ética, consentimiento informado y tratamiento conforme al RGPD. El agente no recoge datos humanos. Revisa licencias y condiciones de uso de los conjuntos públicos antes de redistribuir derivados.

## 33. Gobierno de agentes y evaluación entre agentes

- **Productor y verificador separados**: el verificador recibe artefactos y protocolo, no el razonamiento del productor.
- **Lista contra alucinaciones antes de cada entrega**: cada cifra enlaza un archivo y un commit; cada ruta existe en el árbol; cada referencia se resolvió y se leyó; cada afirmación de ejecución tiene comando, código de salida y salida conservados.
- **Las evaluaciones de otros agentes son asesoramiento** (nota v2 del §1). Ante un desacuerdo, decide la evidencia reproducible, sea a favor de quien sea.
- **Ningún agente borra, reescribe ni oculta trabajo de otro**; las correcciones son sucesoras con nota fechada.
- **Presupuesto**: declara antes de cada paso tiempo de CPU/GPU y criterio de parada (§18).

## 34. Riesgos, puertas de decisión y criterios de abandono

| Puerta | Condición para seguir | Si no se cumple |
|---|---|---|
| G1 Estado (A) | Matriz de afirmaciones completa y sin contradicciones | No empezar experimentos nuevos |
| G2 Reproducción (B) | Suite obligatoria limpia en dos entornos | Reparar antes de medir |
| G3 Ondas (C) | Confirmación prospectiva aceptada o refutada con régimen declarado | Limitar la tesis al régimen validado |
| G4 GPU (D) | Equivalencia completa demostrada | Declarar la CPU como referencia y retirar toda afirmación de GPU nativa residente |
| G5 Clase de funciones (K) | Resultado preregistrado de H-A | Si F_geom no aporta, orientar la contribución a certificación y reproducibilidad |
| G6 Coste (G y N) | Ventaja medida o ausencia documentada | Sin ventaja, publicar el negativo y no presentar el producto como acelerador |
| G7 Física (M, solo D0-B) | Demostrador con predicciones confirmadas | Publicar la discrepancia y revisar el modelo antes de escalar |

Riesgos principales: dependencia de una sola persona y una sola estación; datos restringidos que impiden la réplica; deriva entre documentos; ajuste de umbrales a resultados ya conocidos; herramientas externas (drivers, Blender) que cambian entre versiones.

## 35. Escalera de evidencia y comunicación

| Nivel | Evidencia | Verbos permitidos |
|---|---|---|
| L0 | Idea | «proponemos» |
| L1 | Simulación exploratoria | «observamos en una exploración» |
| L2 | Ensayo preregistrado interno | «el ensayo preregistrado muestra» |
| L3 | Reproducción automática externa | «reproducido en otro entorno» |
| L4 | Revisión por pares | «publicado» |
| L5 | Réplica por otro equipo | «replicado» |
| L6 | Demostración física con predicción confirmada | «demostrado en un dispositivo» |
| L7 | Adopción independiente | «utilizado por terceros» |

Cada afirmación del README, de la interfaz y del artículo lleva su nivel; ninguna usa un verbo de un nivel superior al de su evidencia.

## 36. Hoja de ruta orientativa

Plazos para planificar, no compromisos: pasos A y B, semanas; C–F y K, de tres a nueve meses; G–J, L y O–R, con preprint, release citable y envío, de nueve a dieciocho meses; solo con D0-B, demostrador físico con un socio, de uno a tres años; réplica y adopción por terceros, años y fuera del control del proyecto. El reconocimiento de máximo nivel, cuando llega, suele hacerlo décadas después de la réplica y la adopción (§24.1).

## 37. Referencias añadidas en la revisión v2

Todas se localizaron durante la revisión. Antes de citarlas en el artículo, léelas y comprueba que dicen lo que se les atribuye.

- Premios Nobel de Física: [2009](https://www.nobelprize.org/prizes/physics/2009/summary/), [2014](https://www.nobelprize.org/prizes/physics/2014/summary/), [2018](https://physicstoday.aip.org/news/ashkin-mourou-and-strickland-share-2018-nobel-prize-in-physics), [2024](https://sciencenews.org/article/nobel-physics-2024-machine-learning), [2025](https://www.nobelprize.org/prizes/physics/2025/press-release/).
- Hamerly et al., *Large-scale optical neural networks based on photoelectric multiplication*, Phys. Rev. X 9 (2019): [arXiv:1812.07614](https://arxiv.org/abs/1812.07614).
- Wang et al., *An optical neural network using less than 1 photon per multiplication*, Nature Communications (2022): [arXiv:2104.13467](https://arxiv.org/abs/2104.13467), [PMC8748769](https://pmc.ncbi.nlm.nih.gov/articles/PMC8748769).
- Wright et al., *Deep physical neural networks trained with backpropagation*, Nature 601 (2022): [DOI 10.1038/s41586-021-04223-6](https://doi.org/10.1038/s41586-021-04223-6).
- Pai et al., *Experimentally realized in situ backpropagation for deep learning in photonic neural networks*, Science (2023): [arXiv:2205.08501](https://arxiv.org/abs/2205.08501).
- Wetzstein et al., *Inference in artificial intelligence with deep optics and photonics*, Nature 588 (2020): [DOI 10.1038/s41586-020-2973-6](https://doi.org/10.1038/s41586-020-2973-6).
- Clements et al., *An optimal design for universal multiport interferometers*, Optica (2016): [arXiv:1603.08788](https://arxiv.org/abs/1603.08788).
- Jakob et al., *Dr.Jit: A Just-In-Time Compiler for Differentiable Rendering*, ACM TOG (2022): [arXiv:2202.01284](https://arxiv.org/abs/2202.01284).
- Woop, Benthin y Wald, *Watertight Ray/Triangle Intersection*, JCGT 2(1) (2013): [jcgt.org](https://jcgt.org/published/0002/01/05/); incorporación en Cycles: [commit rBf770bc4757a2](https://developer.blender.org/rBf770bc4757a2b471d5aaee048359096c1c79a6b2).
- *Efficient Reproducible Floating Point Summation and BLAS* (ReproBLAS), informe técnico UCB/EECS-2016-121: [Berkeley EECS](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2016/EECS-2016-121.html).
- Nadeau y Bengio, *Inference for the Generalization Error*, Machine Learning (2003): [ficha](https://mlanthology.org/mlj/2003/nadeau2003mlj-inference).
- Ramdas, Grünwald, Vovk y Shafer, *Game-Theoretic Statistics and Safe Anytime-Valid Inference*, Statistical Science 38(4) (2023): [DOI 10.1214/23-STS894](https://doi.org/10.1214/23-STS894).
- Lakens, *Equivalence Tests: A Practical Primer for t Tests, Correlations, and Meta-Analyses*, Social Psychological and Personality Science (2017): [DOI 10.1177/1948550617697177](https://doi.org/10.1177/1948550617697177).
- Klein y Roodman, *Blind analysis in nuclear and particle physics*, Annu. Rev. Nucl. Part. Sci. 55 (2005): [DOI 10.1146/annurev.ns.55.121205.200001](https://doi.org/10.1146/annurev.ns.55.121205.200001).
- JCGM 101:2008, propagación de distribuciones por Monte Carlo (suplemento 1 de la GUM): [DOI 10.59161/JCGM101-2008](https://www.bipm.org/doi/10.59161/JCGM101-2008).
- ACM, *Artifact Review and Badging*, versión 1.1: [acm.org](https://www.acm.org/publications/policies/artifact-review-and-badging-current).
- CRediT, ANSI/NISO Z39.104-2022: [niso.org](https://niso.org/publications/z39104-2022-credit).
- Center for Open Science, portal de Registered Reports: [osf.io/3wct2](https://osf.io/3wct2/wiki/home).
- API de handles de doi.org, usada por `resolve_identifiers`: `https://doi.org/api/handles/<doi>` (respuesta comprobada con `responseCode: 1` para un DOI existente).

## 38. Código completo del kit v2

Los bloques siguientes se extraen con el mismo `extract_support.py` del §20.1 y se añaden junto a los once bloques v1 sin sobrescribirlos (el extractor rechaza contenido distinto en una ruta existente y no toca las idénticas). El kit v2 importa los módulos v1 y no los modifica. Se validó con CPython 3.12.3 (NumPy 2.3.5, SciPy 1.17.0) y CPython 3.13.16 (NumPy 2.5.3, SciPy 1.18.1) en Linux. Sus pruebas verifican lo que declaran los docstrings; no ejecutan Blender, GPU, el entrenamiento del proyecto, Comparator ni la física de la red completa.

### 38.1. closure_v2.py

<!-- CODEFILE: agent_support/closure_v2.py -->
```python
"""Successor functions for defects reproduced in the v1 support kit.

The v1 modules stay byte-identical. Each function below names the v1 defect
it addresses; test_closure_v2.py reproduces the defect and the correction.
Scope is unchanged: exact represented inputs only, no native Blender, GPU,
fabrication, or Maxwell claim.
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
import sys
from typing import Iterable, Sequence

from closure_coherent import coherent_sum
from closure_evidence import check_pins
from closure_reference import (Interval, complex_product, pi_interval,
    _cross, _dot, _sub, _trig_at_rational, _vector)


def coherent_sum_v2(values: Iterable[complex], method: str = "fsum") -> complex:
    """v1 lets math.fsum raise OverflowError; v2 maps every overflow to ValueError."""
    try:
        return coherent_sum(values, method)
    except OverflowError as exc:
        raise ValueError("Reduction overflow is not a valid field") from exc


def tighten(value: Interval, bits: int = 160) -> Interval:
    """Round endpoints outward to a 2**-bits grid so rational sizes stay bounded.

    v1 keeps exact rational endpoints; through Machin pi and Taylor series their
    denominators reach tens of thousands of bits, so chained stages slow down
    super-linearly. Outward rounding preserves inclusion at a declared cost.
    """
    if not 8 <= bits <= 1024:
        raise ValueError("8..1024 grid bits are required")
    scale = 1 << bits
    lo, hi = value.lo*scale, value.hi*scale
    lower = lo.numerator//lo.denominator
    upper = -((-hi.numerator)//hi.denominator)
    return Interval(Fraction(lower, scale), Fraction(upper, scale))


def _taylor_terms(x: Fraction, bits: int) -> int:
    """Smallest v1 term count whose remainder bound is at most 2**-bits."""
    threshold, ax = Fraction(1, 1 << bits), abs(x)
    power, factorial = ax**17, Fraction(355687428096000)  # 17! for terms=8
    for terms in range(8, 65):
        if power/factorial <= threshold:
            return terms
        power *= ax*ax
        factorial *= (2*terms+2)*(2*terms+3)
    return 64


def unit_phasor_v2(phase: Interval, bits: int = 160) -> tuple[Interval, Interval]:
    """Enclose exp(i*phase) with bounded endpoint sizes and adaptive Taylor order."""
    if not 32 <= bits <= 480:
        raise ValueError("32..480 bits are required")
    period = tighten(2*pi_interval(min(512, bits+32)), bits+16)
    turns = round(phase.midpoint/period.midpoint)
    reduced = tighten(phase-turns*period, bits+16)
    if reduced.radius >= 2 or abs(reduced.midpoint) > 4:
        return Interval(-1, 1), Interval(-1, 1)
    x = reduced.midpoint
    c, s = _trig_at_rational(x, _taylor_terms(x, bits+8))
    e = reduced.radius  # sine and cosine are 1-Lipschitz.
    def clamp(v: Interval) -> Interval:
        return tighten(Interval(max(Fraction(-1), v.lo-e), min(Fraction(1), v.hi+e)), bits)
    return clamp(c), clamp(s)


def coherent_field_v2(paths: Iterable[tuple[tuple[Interval, Interval], Interval]],
                      bits: int = 160) -> tuple[Interval, Interval]:
    """Sum enclosed complex path amplitudes, tightening after every operation."""
    real, imag = Interval.point(0), Interval.point(0)
    for amplitude, phase in paths:
        r, i = complex_product(amplitude, unit_phasor_v2(phase, bits))
        real, imag = tighten(real+r, bits), tighten(imag+i, bits)
    return real, imag


def exact_first_hit_v2(origin: Sequence, direction: Sequence, triangles: Sequence[dict]) -> dict:
    """First hit where degenerate/coplanar primitives block only when they could interfere.

    v1 returns UNKNOWN as soon as it meets any degenerate or coplanar primitive,
    even one behind the origin or beyond a proven nearer hit. The ray parameter
    t(p) = (p-o).d/|d|^2 is linear on a triangle, so any hit lies inside the exact
    range of its vertex projections. A deferred primitive blocks a result only
    if that range meets [0, t_best]. Everything else follows v1 unchanged, and
    UNKNOWN results list primitive_ids (v1 used a single primitive_id).
    """
    o, d = _vector(origin), _vector(direction)
    dd = _dot(d, d)
    if dd == 0:
        raise ValueError("A nonzero direction is required")
    identifiers = [str(t["primitive_id"]) for t in triangles]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("Primitive identifiers must be unique")
    hits, deferred = [], []
    for triangle, pid in zip(triangles, identifiers):
        vertices = triangle["vertices"]
        if len(vertices) != 3:
            raise ValueError("Three vertices per triangle are required")
        a, b, c = (_vector(x) for x in vertices)
        projections = [_dot(_sub(v, o), d)/dd for v in (a, b, c)]
        e1, e2 = _sub(b, a), _sub(c, a)
        normal = _cross(e1, e2)
        if _dot(normal, normal) == 0:
            deferred.append((min(projections), max(projections), pid, "DEGENERATE_TRIANGLE"))
            continue
        p = _cross(d, e2)
        determinant = _dot(e1, p)
        if determinant == 0:
            if _dot(normal, _sub(o, a)) == 0:
                deferred.append((min(projections), max(projections), pid, "COPLANAR_QUERY"))
            continue
        delta = _sub(o, a)
        u = _dot(delta, p)/determinant
        q = _cross(delta, e1)
        v = _dot(d, q)/determinant
        t = _dot(e2, q)/determinant
        if t >= 0 and u >= 0 and v >= 0 and u+v <= 1:
            hits.append((t, pid, str(triangle["object_id"]), a, normal))
    best = min(h[0] for h in hits) if hits else None
    blocking = [x for x in deferred if x[1] >= 0 and (best is None or x[0] <= best)]
    if blocking:
        return {"status": "UNKNOWN", "reason": blocking[0][3],
                "primitive_ids": sorted(x[2] for x in blocking)}
    if not hits:
        return {"status": "MISS"}
    tied = [h for h in hits if h[0] == best]
    if best == 0:
        return {"status": "UNKNOWN", "reason": "LAUNCH_CONTACT", "primitive_ids": [h[1] for h in tied]}
    reference = tied[0]
    same_surface = all(h[2] == reference[2] and _cross(h[4], reference[4]) == (0, 0, 0)
                       and _dot(reference[4], _sub(h[3], reference[3])) == 0 for h in tied)
    if not same_surface:
        return {"status": "UNKNOWN", "reason": "DISTINCT_SURFACE_TIE", "primitive_ids": [h[1] for h in tied]}
    return {"status": "HIT", "parameter": best, "object_id": reference[2],
            "primitive_ids": sorted(h[1] for h in tied),
            "point": tuple(o[j]+best*d[j] for j in range(3))}


FRONTIER_IDS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")
EXTERNAL_ONLY = {"F5", "F9"}  # PASS needs evidence produced by people outside the project.


def verify_frontier(root, document: dict) -> dict:
    """Check the frontier manifest the same way v1 checks the eleven fronts.

    F5 (independent replication) and F9 (adoption) additionally require an
    external_evidence_record pinned in the repository: an agent cannot mark
    them PASS from its own runs.
    """
    if document.get("schema") != "neuro3d.frontier.manifest.v1":
        raise ValueError("Unsupported frontier schema")
    objectives = document.get("objectives", [])
    if not isinstance(objectives, list) or any(not isinstance(x, dict) for x in objectives):
        raise ValueError("Objectives must be dictionaries")
    if sorted(str(x.get("id")) for x in objectives) != sorted(FRONTIER_IDS):
        raise ValueError("Exactly the frontier fronts F1..F9 are required")
    states = {"PASS", "PARTIAL", "OPEN", "BLOCKED", "NOT_APPLICABLE"}
    failures, unresolved = [], []
    for objective in objectives:
        oid, state = objective["id"], objective.get("state")
        if state not in states:
            failures.append({"id": oid, "reason": "INVALID_STATE"})
            continue
        if state == "NOT_APPLICABLE":
            if not objective.get("scope_reason"):
                failures.append({"id": oid, "reason": "UNEXPLAINED_SCOPE_EXCLUSION"})
            continue
        if state != "PASS":
            unresolved.append({"id": oid, "state": state, "remaining": objective.get("remaining", [])})
            continue
        pins = objective.get("pins", {})
        needed = ["scientific_verifier_record"] + (["external_evidence_record"] if oid in EXTERNAL_ONLY else [])
        if objective.get("remaining") or any(not objective.get(k) or objective[k] not in pins for k in needed):
            failures.append({"id": oid, "reason": "PASS_WITHOUT_PINNED_VERIFIER_OR_EXTERNAL_EVIDENCE"})
            continue
        failures.extend({"id": oid, **x} for x in check_pins(root, pins) if x["status"] != "PASS")
    return {"schema": "neuro3d.frontier.integrity.v1", "failures": failures, "unresolved": unresolved,
            "integrity_pass": not failures, "all_frontier_fronts_pass": not failures and not unresolved,
            "scope": "Manifest integrity only; it never certifies scientific importance or recognition"}


def main() -> int:
    """Check the frontier manifest; exit 2 while any front is unresolved."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = verify_frontier(args.repo, json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 3
    print(json.dumps(report, indent=2))
    return 0 if report["all_frontier_fronts_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### 38.2. closure_limits.py

<!-- CODEFILE: agent_support/closure_limits.py -->
```python
"""Physical reference scales and function-class baselines for the frontier fronts.

Nothing here measures hardware. Photon budgets assume ideal Poisson detection
with a declared efficiency and are design scales, not bounds on any device.
The trainer is a digital comparator for the nested-class ablation
(free complex W, passive W, geometry-realizable W); it is not Neuro3D.
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np

PLANCK = 6.62607015e-34       # J s, exact in the 2019 SI
LIGHT_SPEED = 299792458.0     # m/s, exact in the SI
BOLTZMANN = 1.380649e-23      # J/K, exact in the 2019 SI


def photon_energy(wavelength_m: float) -> float:
    """Energy of one photon in joules."""
    if not math.isfinite(wavelength_m) or wavelength_m <= 0:
        raise ValueError("A positive finite wavelength is required")
    return PLANCK*LIGHT_SPEED/wavelength_m


def shot_noise_photons(bits: int, separation_sigmas: float = 2.0) -> float:
    """Full-scale photon count so adjacent levels sit k Poisson sigmas apart.

    With 2**bits levels spaced N/2**bits and full-scale std sqrt(N), the
    requirement N/2**bits >= k*sqrt(N) gives N >= k**2 * 4**bits. With a
    midpoint threshold the adjacent-level error is about Phi(-k/2).
    """
    if not 1 <= bits <= 24 or not math.isfinite(separation_sigmas) or separation_sigmas <= 0:
        raise ValueError("1..24 bits and a positive separation are required")
    return separation_sigmas**2*4.0**bits


def detection_energy_per_mac(bits: int, wavelength_m: float, fan_in: int,
                             efficiency: float = 1.0, separation_sigmas: float = 2.0) -> float:
    """Optical detection energy per multiply-accumulate under the stated model.

    One detected output aggregates fan_in products, so its photon budget is
    shared among them. Lasers, modulators, DAC/ADC and electronics are excluded
    and must be measured separately before any efficiency claim.
    """
    if fan_in < 1 or not 0 < efficiency <= 1:
        raise ValueError("fan_in >= 1 and 0 < efficiency <= 1 are required")
    return shot_noise_photons(bits, separation_sigmas)*photon_energy(wavelength_m)/(efficiency*fan_in)


def landauer_energy(temperature_k: float = 300.0) -> float:
    """kT ln 2: a reference scale for irreversible bit erasure, not an optical bound."""
    if not math.isfinite(temperature_k) or temperature_k <= 0:
        raise ValueError("A positive finite temperature is required")
    return BOLTZMANN*temperature_k*math.log(2)


def spectral_norm(matrix: np.ndarray) -> float:
    """Largest singular value; a passive linear optical operator has value <= 1."""
    m = np.asarray(matrix, dtype=np.complex128)
    if m.ndim != 2 or not np.isfinite(m).all():
        raise ValueError("A finite matrix is required")
    return float(np.linalg.norm(m, 2))


def is_passive(matrix: np.ndarray, tolerance: float = 1e-12) -> bool:
    """True when the represented operator cannot amplify total modal power."""
    return spectral_norm(matrix) <= 1+tolerance


def project_passive(matrix: np.ndarray) -> np.ndarray:
    """Nearest contraction in Frobenius norm: clip singular values at one."""
    m = np.asarray(matrix, dtype=np.complex128)
    if m.ndim != 2 or not np.isfinite(m).all():
        raise ValueError("A finite matrix is required")
    u, s, vh = np.linalg.svd(m, full_matrices=False)
    return (u*np.minimum(s, 1.0))@vh


def numerical_jacobian(function: Callable[[np.ndarray], np.ndarray], theta, step: float = 1e-6) -> np.ndarray:
    """Central-difference Jacobian of a complex array map, flattened as [Re, Im]."""
    x = np.asarray(theta, dtype=float)
    if x.ndim != 1 or not np.isfinite(x).all() or not 0 < step < 1:
        raise ValueError("A finite parameter vector and 0 < step < 1 are required")
    def flat(v):
        y = np.asarray(function(v), dtype=np.complex128).ravel()
        if not np.isfinite(y).all():
            raise ValueError("The map returned non-finite values")
        return np.concatenate([y.real, y.imag])
    columns = []
    for j in range(len(x)):
        e = np.zeros_like(x)
        e[j] = step
        columns.append((flat(x+e)-flat(x-e))/(2*step))
    return np.column_stack(columns)


def effective_rank(jacobian: np.ndarray, relative_tolerance: float = 1e-7) -> dict:
    """Numerical local dimension of a reachable set at one point.

    The count depends on the declared tolerance and finite-difference error;
    report the singular values, never the rank alone.
    """
    j = np.asarray(jacobian, dtype=float)
    if j.ndim != 2 or not np.isfinite(j).all() or not 0 < relative_tolerance < 1:
        raise ValueError("A finite 2D Jacobian and 0 < tolerance < 1 are required")
    s = np.linalg.svd(j, compute_uv=False)
    rank = 0 if not s.size or s[0] == 0 else int((s > relative_tolerance*s[0]).sum())
    return {"rank": rank, "singular_values": s.tolist(), "relative_tolerance": relative_tolerance}


def detector_loss(a: np.ndarray, b: np.ndarray, x: np.ndarray, y: np.ndarray, scale: float):
    """Softmax cross-entropy on scaled detector powers |(A+iB)x|^2 and its gradients."""
    e = x@(a+1j*b).T
    z = scale*np.abs(e)**2
    z -= z.max(axis=1, keepdims=True)
    p = np.exp(z)
    p /= p.sum(axis=1, keepdims=True)
    n = len(y)
    loss = float(-np.log(p[np.arange(n), y]).mean())
    g = p.copy()
    g[np.arange(n), y] -= 1.0
    g *= scale/n
    return loss, 2*(g*e.real).T@x, 2*(g*e.imag).T@x


def train_detector_classifier(x, y, modes: int, *, passive: bool = True, steps: int = 400,
                              learning_rate: float = 0.05, scale: float = 10.0, seed: int = 0) -> dict:
    """Fit argmax_j |W_j x|^2 by Adam, projecting onto contractions when passive.

    Inputs are real encodings (n, sources); labels are detector indices. This
    is the digital comparator for F1: it shows what a linear optical function
    class can do on the same encoding and data split. argmax decisions are
    invariant to positive scaling of W, so free and passive classes share
    their decision functions; passivity matters only under a fixed detection
    gain or photon budget, which `scale` models here.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y)
    if x.ndim != 2 or not np.isfinite(x).all() or y.shape != (len(x),) or modes < 2:
        raise ValueError("Finite (samples, sources) inputs, matched labels and >= 2 modes are required")
    if not np.issubdtype(y.dtype, np.integer) or y.min() < 0 or y.max() >= modes:
        raise ValueError("Labels must be integers in [0, modes)")
    if steps < 1 or not 0 < learning_rate < 1 or not math.isfinite(scale) or scale <= 0:
        raise ValueError("Positive steps, 0 < learning_rate < 1 and a positive scale are required")
    rng = np.random.default_rng(seed)
    sources = x.shape[1]
    a = rng.normal(0, 1/math.sqrt(2*sources), (modes, sources))
    b = rng.normal(0, 1/math.sqrt(2*sources), (modes, sources))
    if passive:
        w = project_passive(a+1j*b)
        a, b = w.real.copy(), w.imag.copy()
    moments = [np.zeros_like(a), np.zeros_like(b), np.zeros_like(a), np.zeros_like(b)]
    history = []
    for t in range(1, steps+1):
        loss, ga, gb = detector_loss(a, b, x, y, scale)
        history.append(loss)
        for k, (param, grad) in enumerate(((a, ga), (b, gb))):
            moments[k] = 0.9*moments[k]+0.1*grad
            moments[k+2] = 0.999*moments[k+2]+0.001*grad*grad
            mhat = moments[k]/(1-0.9**t)
            vhat = moments[k+2]/(1-0.999**t)
            param -= learning_rate*mhat/(np.sqrt(vhat)+1e-12)
        if passive:
            w = project_passive(a+1j*b)
            a, b = w.real.copy(), w.imag.copy()
    w = a+1j*b
    predictions = np.argmax(np.abs(x@w.T)**2, axis=1)
    return {"W": w, "loss_history": history, "train_accuracy": float((predictions == y).mean()),
            "spectral_norm": spectral_norm(w), "passive_constraint": passive, "seed": seed,
            "scope": "Digital comparator class; not a geometry-realizable Neuro3D network"}
```

### 38.3. closure_inference_v2.py

<!-- CODEFILE: agent_support/closure_inference_v2.py -->
```python
"""Anytime-valid and equivalence inference to complement closure_statistics.

An e-process lets a protocol look at accumulating paired results and stop
early without inflating its type-I error (Ville's inequality). TOST makes the
equivalence claim explicit with a (1-2*alpha) interval.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
from scipy.stats import t as student_t


def paired_sign_eprocess(outcomes: Iterable[int], bets: Sequence[float] = (-0.5, -0.25, 0.25, 0.5)) -> dict:
    """Mixture betting e-process for H0: each discordant pair favors either method with p=1/2.

    outcomes holds +1 when only the candidate is correct and -1 when only the
    reference is correct; ties are excluded before calling. Each fixed bet gives
    a nonnegative martingale with mean one under H0 and their average is one too,
    so P(sup_t E_t >= 1/alpha) <= alpha. Exchangeable independent pairs are assumed.
    """
    x = list(outcomes)
    if any(v not in (-1, 1) or isinstance(v, bool) for v in x):
        raise ValueError("Outcomes must be +1 or -1 discordant pairs")
    lam = np.asarray(bets, dtype=float)
    if lam.ndim != 1 or not lam.size or np.any(lam == 0) or np.any(np.abs(lam) >= 1) or not np.isfinite(lam).all():
        raise ValueError("Bets must be finite, nonzero and inside (-1, 1)")
    wealth, path = np.ones(len(lam)), []
    for v in x:
        wealth *= 1+lam*v
        path.append(float(wealth.mean()))
    return {"discordant_pairs": len(x), "e_value": path[-1] if path else 1.0,
            "max_e_value": max(path, default=1.0), "path": path, "bets": lam.tolist(),
            "assumption": "Independent exchangeable discordant pairs; clustered units need a cluster-level e-process"}


def eprocess_decision(report: dict, alpha: float) -> str:
    """Reject once the running e-process has ever reached 1/alpha."""
    if not 0 < alpha < 1:
        raise ValueError("0 < alpha < 1 is required")
    return "REJECT_H0" if report["max_e_value"] >= 1/alpha else "NOT_REJECTED"


def tost_paired(differences: Iterable[float], margin: float, alpha: float = 0.05) -> dict:
    """Two one-sided t-tests for |mean difference| < margin on independent paired units."""
    d = np.asarray(list(differences), dtype=float)
    if d.ndim != 1 or len(d) < 3 or not np.isfinite(d).all():
        raise ValueError("At least three finite paired differences are required")
    if not math.isfinite(margin) or margin <= 0 or not 0 < alpha < 0.5:
        raise ValueError("A positive margin and 0 < alpha < 0.5 are required")
    n, mean = len(d), float(d.mean())
    se = float(d.std(ddof=1))/math.sqrt(n)
    if se == 0:
        inside = abs(mean) < margin
        return {"units": n, "mean_difference": mean, "interval": [mean, mean], "p_tost": 0.0 if inside else 1.0,
                "equivalent": inside, "alpha": alpha, "margin": margin, "note": "Zero variance; decision is exact for these values"}
    crit = float(student_t.ppf(1-alpha, n-1))
    lower, upper = mean-crit*se, mean+crit*se
    p_low = float(student_t.sf((mean+margin)/se, n-1))
    p_high = float(student_t.cdf((mean-margin)/se, n-1))
    return {"units": n, "mean_difference": mean, "interval": [lower, upper],
            "interval_level": 1-2*alpha, "p_tost": max(p_low, p_high),
            "equivalent": lower > -margin and upper < margin, "alpha": alpha, "margin": margin,
            "assumption": "Independent paired units; approximately normal mean difference"}
```

### 38.4. closure_integrity.py

<!-- CODEFILE: agent_support/closure_integrity.py -->
```python
"""Blinding commitments, experiment-record checks, and citation identifier checks.

These tools make three failure modes detectable: looking at test labels
before the analysis is frozen, records that omit what section 18 requires,
and references that do not resolve. Detecting a problem is not proof of
scientific quality.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
from typing import Callable, Iterable
from urllib import error as urlerror
from urllib import request as urlrequest


def new_salt() -> bytes:
    """32 secret random bytes; keep them with the owner until the reveal."""
    return secrets.token_bytes(32)


def _item_hash(salt: bytes, index: int, label) -> str:
    payload = json.dumps(label, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(salt+index.to_bytes(8, "big")+payload.encode("utf-8")).hexdigest()


def commit_labels(labels: Iterable, salt: bytes) -> dict:
    """Commit to ordered labels: publish root and count now, reveal salt and labels later."""
    if not isinstance(salt, (bytes, bytearray)) or len(salt) < 32:
        raise ValueError("A secret salt of at least 32 bytes is required")
    items = [_item_hash(bytes(salt), i, label) for i, label in enumerate(labels)]
    if not items:
        raise ValueError("At least one label is required")
    root = hashlib.sha256(b"".join(bytes.fromhex(h) for h in items)).hexdigest()
    return {"scheme": "neuro3d.label-commitment.v1", "count": len(items), "root": root, "item_hashes": items}


def verify_reveal(labels: Iterable, salt: bytes, root: str, count: int) -> bool:
    """True only when the revealed labels and salt reproduce the published commitment."""
    try:
        c = commit_labels(labels, salt)
    except (ValueError, TypeError):
        return False
    return c["count"] == count and secrets.compare_digest(c["root"], root)


RECORD_FIELDS = ("id", "hypothesis", "alternative", "protocol_commit", "sources", "inputs", "environment",
                 "seeds", "resource_budget", "deadline", "commands", "exit_codes", "results",
                 "independent_oracle", "decision_rule", "decision", "deviations", "limitations",
                 "published_commit", "status")
RECORD_STATES = {"OPEN", "PARTIAL", "PASS", "FAIL", "BLOCKED", "UNKNOWN", "NOT_APPLICABLE"}
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?)?$")


def validate_experiment_record(record: dict) -> list[str]:
    """Return every problem found against section 18; an empty list means complete."""
    if not isinstance(record, dict):
        return ["Record must be a JSON object"]
    problems = [f"Missing field: {f}" for f in RECORD_FIELDS if f not in record]
    rid = str(record.get("id", ""))
    if rid.startswith("EXP-005-"):
        problems.append("The EXP-005-* chain is closed; new work needs a new identifier")
    if record.get("status") not in RECORD_STATES:
        problems.append("Invalid status")
    for key in ("protocol_commit", "published_commit"):
        value = record.get(key)
        if value is not None and value != "PENDING" and not _HEX40.match(str(value)):
            problems.append(f"{key} must be a 40-hex commit or PENDING")
    if record.get("status") in {"PASS", "FAIL", "UNKNOWN"} and record.get("published_commit") in (None, "PENDING"):
        problems.append("A decided record must cite its published commit")
    sources = record.get("sources", [])
    if not isinstance(sources, list) or not sources:
        problems.append("sources must be a nonempty list")
    else:
        for i, s in enumerate(sources):
            if not isinstance(s, dict) or not s.get("path") or not _HEX64.match(str(s.get("sha256", ""))):
                problems.append(f"sources[{i}] needs path and lowercase sha256")
    if "deadline" in record and not _DATE.match(str(record["deadline"])):
        problems.append("deadline must be an ISO date or datetime")
    if record.get("status") == "PASS" and not (record.get("independent_oracle") and record.get("decision_rule")):
        problems.append("PASS requires an independent oracle and a prospective decision rule")
    for i, c in enumerate(record.get("jev_consultations", []) or []):
        missing = [k for k in ("question", "answer", "date", "provenance", "confidence") if not c.get(k)]
        if missing:
            problems.append(f"jev_consultations[{i}] missing {missing}")
    return problems


_DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>\]\)]+)")
_ARXIV = re.compile(r"(?:arxiv\.org/(?:abs|pdf)/|arXiv:\s*)(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)


def extract_identifiers(text: str) -> dict:
    """Find DOIs and explicitly marked arXiv identifiers, deduplicated in order.

    A closing parenthesis ends a DOI so Markdown links parse cleanly; the rare
    DOIs that contain parentheses must be checked by hand.
    """
    dois, arxiv = [], []
    for m in _DOI.finditer(text):
        doi = m.group(1).rstrip(".,;:")
        if doi.lower().endswith(".pdf"):
            doi = doi[:-4]
        if doi not in dois:
            dois.append(doi)
    for m in _ARXIV.finditer(text):
        if m.group(1) not in arxiv:
            arxiv.append(m.group(1))
    return {"doi": dois, "arxiv": arxiv}


def _default_fetch(url: str, headers: dict) -> tuple[int, bytes]:
    req = urlrequest.Request(url, headers={"User-Agent": "neuro3d-citation-check/1", **headers})
    try:
        with urlrequest.urlopen(req, timeout=20) as response:
            return response.status, response.read(1 << 20)
    except urlerror.HTTPError as exc:
        return exc.code, b""


def resolve_identifiers(identifiers: dict, fetch: Callable[[str, dict], tuple[int, bytes]] | None = None) -> list[dict]:
    """Check that identifiers exist. Existence never proves the citation is apt.

    DOI: FOUND iff doi.org's handle API answers 200 with responseCode 1.
    arXiv: FOUND iff the abs page answers 200; NOT_FOUND on 404.
    Anything else is ERROR and needs a manual check.
    """
    fetch = fetch or _default_fetch
    out = []
    for doi in identifiers.get("doi", []):
        try:
            status, body = fetch("https://doi.org/api/handles/"+doi, {"Accept": "application/json"})
            code = json.loads(body.decode("utf-8")).get("responseCode") if status == 200 else None
            state = "FOUND" if code == 1 else "NOT_FOUND" if status == 404 else "ERROR"
            out.append({"kind": "doi", "id": doi, "status": state, "http": status})
        except (OSError, ValueError) as exc:
            out.append({"kind": "doi", "id": doi, "status": "ERROR", "detail": str(exc)})
    for aid in identifiers.get("arxiv", []):
        try:
            status, _ = fetch("https://arxiv.org/abs/"+aid, {})
            state = "FOUND" if status == 200 else "NOT_FOUND" if status == 404 else "ERROR"
            out.append({"kind": "arxiv", "id": aid, "status": state, "http": status})
        except OSError as exc:
            out.append({"kind": "arxiv", "id": aid, "status": "ERROR", "detail": str(exc)})
    return out
```

### 38.5. support_demo_v2.py

<!-- CODEFILE: agent_support/support_demo_v2.py -->
```python
"""Write a receipt of the v2 CPU controls; never overwrite an earlier receipt.

Synthetic support controls only: no Neuro3D training, GPU, blind task, or
full-device physical validation is executed here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy

from closure_evidence import write_report
from closure_limits import detection_energy_per_mac, landauer_energy, photon_energy, shot_noise_photons
from closure_reference import Interval, exact_first_hit, pi_interval
from closure_v2 import coherent_field_v2, exact_first_hit_v2
from closure_wave import angular_spectrum_1d, gaussian_1d, modal_amplitude


def control_result() -> dict:
    """Evaluate the corrected first hit, bounded enclosures, P1-7 overlap and scales."""
    near = {"primitive_id": "near", "object_id": "A", "vertices": [(-2, -1, 1), (2, -1, 1), (0, 2, 1)]}
    far = {"primitive_id": "far-degenerate", "object_id": "B", "vertices": [(0, 0, 50)]*3}
    v1, v2 = exact_first_hit((0, 0, 0), (0, 0, 1), [near, far]), exact_first_hit_v2((0, 0, 0), (0, 0, 1), [near, far])
    amp = (Interval.point(1), Interval.point(0))
    dark = coherent_field_v2([(amp, Interval.point(0)), (amp, pi_interval())])
    power = dark[0].square()+dark[1].square()
    lam, w, z = 1.0, 8.0, 95.0
    y = np.linspace(-200, 200, 8192, endpoint=False)
    dy = float(y[1]-y[0])
    g0 = gaussian_1d(y, 0, lam, w)
    overlap = abs(modal_amplitude(angular_spectrum_1d(g0, dy, z, lam), g0, dy))**2
    zeta = 2*z/((2*math.pi/lam)*w*w)
    return {"schema": "neuro3d.closure.support_controls.v2",
            "scope": "Synthetic CPU support controls; not a claim about the complete Neuro3D device",
            "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "first_hit_far_degenerate": {"v1": v1["status"], "v2": v2["status"], "v2_parameter": str(v2.get("parameter"))},
            "dark_power_upper_bound_v2": float(power.hi),
            "p17_free_space_overlap": {"waist_lambda": w, "distance_lambda": z, "angular_spectrum": overlap,
                                       "paraxial_closed_form": 1/math.sqrt(1+zeta*zeta/4),
                                       "scope": "Scalar free-space overlap only; not the FDTD device"},
            "reference_scales": {"photon_energy_1550nm_J": photon_energy(1550e-9),
                                 "landauer_300K_J": landauer_energy(300.0),
                                 "photons_full_scale_4bit_k2": shot_noise_photons(4, 2.0),
                                 "detection_energy_per_mac_4bit_fanin5_J": detection_energy_per_mac(4, 1550e-9, 5),
                                 "scope": "Ideal Poisson detection design scale; lasers, modulators and electronics excluded"}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = control_result()
    write_report(args.out, report)
    print(json.dumps({"receipt": str(args.out), "scope": report["scope"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 38.6. test_closure_v2.py

<!-- CODEFILE: agent_support/test_closure_v2.py -->
```python
"""Regressions for the v2 successors: each v1 defect is reproduced, then corrected."""
from __future__ import annotations

from fractions import Fraction as F
import json
import math
from pathlib import Path
import random
import tempfile
import unittest

import numpy as np
from scipy.stats import norm

from closure_coherent import coherent_sum
from closure_reference import Interval, exact_first_hit, phase_from_length, pi_interval, unit_phasor
from closure_wave import angular_spectrum_1d, gaussian_1d, modal_amplitude
from closure_v2 import (coherent_field_v2, coherent_sum_v2, exact_first_hit_v2, tighten,
    unit_phasor_v2, verify_frontier)
from closure_limits import (detection_energy_per_mac, detector_loss, effective_rank, is_passive,
    landauer_energy, numerical_jacobian, photon_energy, project_passive, shot_noise_photons,
    spectral_norm, train_detector_classifier)
from closure_inference_v2 import eprocess_decision, paired_sign_eprocess, tost_paired
from closure_integrity import (commit_labels, extract_identifiers, resolve_identifiers,
    validate_experiment_record, verify_reveal)

HERE = Path(__file__).resolve().parent


def triangle(z, pid="0", object_id="plane"):
    return {"primitive_id": pid, "object_id": object_id, "vertices": [(-2, -1, z), (2, -1, z), (0, 2, z)]}


class ReductionAndEnclosureV2(unittest.TestCase):
    def test_fsum_overflow_contract(self):
        with self.assertRaises(OverflowError):
            coherent_sum([1e308, 1e308], "fsum")  # v1 defect reproduced
        for method in ("fsum", "pairwise", "naive"):
            with self.assertRaises(ValueError):
                coherent_sum_v2([1e308, 1e308], method)
        self.assertEqual(coherent_sum_v2([complex(1e16, 1e16), 1+2j, complex(-1e16, -1e16)]), 1+2j)

    def test_tighten_is_outward_and_bounded(self):
        rng = random.Random(3)
        for _ in range(200):
            a = F(rng.randint(-10**40, 10**40), rng.randint(1, 10**60))
            b = a+F(rng.randint(0, 10**9), 10**rng.randint(1, 30))
            t = tighten(Interval(a, b), 96)
            self.assertLessEqual(t.lo, a)
            self.assertGreaterEqual(t.hi, b)
            self.assertLessEqual(t.lo.denominator.bit_length(), 97)
            self.assertLessEqual(t.hi-t.lo, b-a+F(2, 2**96))

    def test_v1_endpoint_growth_is_bounded_in_v2(self):
        phase = phase_from_length(Interval.point(F(10**30)+F(1, 4)), Interval.point(1))
        c1, _ = unit_phasor(phase)
        self.assertGreater(c1.lo.denominator.bit_length(), 4000)  # v1 behaviour reproduced
        c2, s2 = unit_phasor_v2(phase)
        self.assertLessEqual(c2.lo.denominator.bit_length(), 161)
        self.assertTrue(c2.contains(0) and s2.contains(1))
        self.assertLess(c2.hi-c2.lo, F(1, 2**100))
        self.assertTrue(max(c1.lo, c2.lo) <= min(c1.hi, c2.hi))

    def test_unit_phasor_v2_matches_floating_reference(self):
        rng = random.Random(11)
        for _ in range(100):
            x = rng.uniform(-1e6, 1e6)
            ph = F.from_float(x)  # exact binary64 value, so math.cos(x) refers to the same argument
            c, s = unit_phasor_v2(Interval.point(ph))
            # libm cos/sin are within a few ulp of the exact value; the enclosure must contain it.
            slack = 4e-16
            self.assertTrue(float(c.lo)-slack <= math.cos(x) <= float(c.hi)+slack)
            self.assertTrue(float(s.lo)-slack <= math.sin(x) <= float(s.hi)+slack)
            self.assertLess(c.hi-c.lo, F(1, 2**100))

    def test_dark_field_and_sixty_four_paths_stay_small(self):
        amp = (Interval.point(1), Interval.point(0))
        dark = coherent_field_v2([(amp, Interval.point(0)), (amp, pi_interval())])
        power = dark[0].square()+dark[1].square()
        self.assertTrue(power.contains(0))
        self.assertLess(power.hi, F(1, 2**100))
        field = coherent_field_v2([(amp, Interval.point(F(k, 7))) for k in range(64)])
        exact = sum(complex(math.cos(k/7), math.sin(k/7)) for k in range(64))
        self.assertLess(abs(float(field[0].midpoint)-exact.real), 1e-12)
        self.assertLess(abs(float(field[1].midpoint)-exact.imag), 1e-12)
        self.assertLessEqual(field[0].hi.denominator.bit_length(), 161)


class FirstHitV2(unittest.TestCase):
    near = triangle(1, "near", "A")
    far_degenerate = {"primitive_id": "far", "object_id": "B", "vertices": [(0, 0, 50)]*3}
    behind_coplanar = {"primitive_id": "behind", "object_id": "C", "vertices": [(0, -1, -5), (0, 1, -5), (0, 0, -6)]}
    front_coplanar = {"primitive_id": "front", "object_id": "D", "vertices": [(0, -1, F(1, 2)), (0, 1, F(1, 2)), (0, 0, F(3, 4))]}

    def test_v1_masking_reproduced_and_corrected(self):
        o, d = (0, 0, 0), (0, 0, 1)
        self.assertEqual(exact_first_hit(o, d, [self.near, self.far_degenerate])["status"], "UNKNOWN")
        self.assertEqual(exact_first_hit(o, d, [self.near, self.behind_coplanar])["status"], "UNKNOWN")
        for blocker in (self.far_degenerate, self.behind_coplanar):
            hit = exact_first_hit_v2(o, d, [self.near, blocker])
            self.assertEqual((hit["status"], hit["parameter"], hit["primitive_ids"]), ("HIT", 1, ["near"]))

    def test_possible_interference_still_blocks(self):
        o, d = (0, 0, 0), (0, 0, 1)
        hit = exact_first_hit_v2(o, d, [self.near, self.front_coplanar])
        self.assertEqual((hit["status"], hit["reason"], hit["primitive_ids"]), ("UNKNOWN", "COPLANAR_QUERY", ["front"]))
        self.assertEqual(exact_first_hit_v2(o, d, [self.far_degenerate])["status"], "UNKNOWN")
        behind_point = {"primitive_id": "p", "object_id": "E", "vertices": [(0, 0, -1)]*3}
        self.assertEqual(exact_first_hit_v2(o, d, [behind_point])["status"], "MISS")

    def test_duplicate_identifiers_rejected_anywhere(self):
        with self.assertRaises(ValueError):
            exact_first_hit_v2((0, 0, 0), (0, 0, 1), [self.far_degenerate, triangle(2, "x"), triangle(3, "x")])

    def test_v2_equals_v1_whenever_v1_met_no_deferred_primitive(self):
        rng = random.Random(2026)
        compared = 0
        for _ in range(600):
            tris = []
            for k in range(rng.randint(1, 4)):
                tris.append({"primitive_id": f"t{k}", "object_id": f"o{rng.randint(0, 1)}",
                             "vertices": [tuple(rng.randint(-3, 3) for _ in range(3)) for _ in range(3)]})
            o = tuple(rng.randint(-3, 3) for _ in range(3))
            d = tuple(rng.randint(-2, 2) for _ in range(3))
            if d == (0, 0, 0):
                continue
            v1 = exact_first_hit(o, d, tris)
            if v1.get("reason") in ("DEGENERATE_TRIANGLE", "COPLANAR_QUERY"):
                continue
            v2 = exact_first_hit_v2(o, d, tris)
            if v1["status"] in ("HIT", "MISS"):
                self.assertEqual(v1, v2)
            else:
                self.assertEqual((v1["status"], v1["reason"]), (v2["status"], v2["reason"]))
            compared += 1
        self.assertGreater(compared, 300)


class LimitsAndBaselines(unittest.TestCase):
    def test_reference_scales(self):
        self.assertAlmostEqual(photon_energy(1550e-9)/1.2816e-19, 1, places=3)
        self.assertAlmostEqual(landauer_energy(300)/2.8710e-21, 1, places=3)
        e4 = detection_energy_per_mac(4, 1550e-9, fan_in=5)
        self.assertAlmostEqual(detection_energy_per_mac(5, 1550e-9, fan_in=5)/e4, 4)
        self.assertAlmostEqual(detection_energy_per_mac(4, 1550e-9, fan_in=10)/e4, 0.5)

    def test_shot_noise_level_semantics_by_simulation(self):
        k, bits = 2.0, 4
        n_full = shot_noise_photons(bits, k)
        lower = n_full*(1-1/2**bits)
        threshold = (n_full+lower)/2
        rng = np.random.default_rng(5)
        error = float((rng.poisson(n_full, 40000) < threshold).mean())
        self.assertLess(abs(error-norm.cdf(-k/2)), 0.02)

    def test_passivity_tools(self):
        theta, phi = 0.7, 1.3
        mzi = np.array([[np.exp(1j*phi)*np.sin(theta), np.cos(theta)],
                        [np.exp(1j*phi)*np.cos(theta), -np.sin(theta)]])
        self.assertTrue(is_passive(mzi))
        self.assertAlmostEqual(spectral_norm(mzi), 1.0, places=12)
        np.testing.assert_allclose(project_passive(2*np.eye(2)), np.eye(2), atol=1e-14)
        c = 0.5*mzi
        np.testing.assert_allclose(project_passive(c), c, atol=1e-14)
        self.assertFalse(is_passive(1.01*mzi))

    def test_reachable_set_rank(self):
        mzi = lambda v: np.array([[np.exp(1j*v[1])*np.sin(v[0]), np.cos(v[0])],
                                  [np.exp(1j*v[1])*np.cos(v[0]), -np.sin(v[0])]])
        redundant = lambda v: np.array([[np.exp(1j*(v[0]+v[1])), 0], [0, 1]])
        self.assertEqual(effective_rank(numerical_jacobian(mzi, [0.7, 1.3]))["rank"], 2)
        self.assertEqual(effective_rank(numerical_jacobian(redundant, [0.7, 1.3]))["rank"], 1)

    def test_detector_gradient_matches_finite_differences(self):
        rng = np.random.default_rng(1)
        a, b = rng.normal(size=(3, 4)), rng.normal(size=(3, 4))
        x, y = rng.normal(size=(7, 4)), rng.integers(0, 3, 7)
        _, ga, gb = detector_loss(a, b, x, y, 2.0)
        h = 1e-6
        for (i, j) in ((0, 0), (1, 2), (2, 3)):
            for grad, which in ((ga, 0), (gb, 1)):
                p, m = [a.copy(), b.copy()], [a.copy(), b.copy()]
                p[which][i, j] += h
                m[which][i, j] -= h
                fd = (detector_loss(*p, x, y, 2.0)[0]-detector_loss(*m, x, y, 2.0)[0])/(2*h)
                self.assertAlmostEqual(grad[i, j], fd, places=6)

    def test_passive_trainer_recovers_a_teacher_network(self):
        rng = np.random.default_rng(4)
        q, _ = np.linalg.qr(rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3)))
        x = rng.normal(size=(300, 3))
        x /= np.linalg.norm(x, axis=1, keepdims=True)
        y = np.argmax(np.abs(x@q.T)**2, axis=1)
        result = train_detector_classifier(x, y, 3, passive=True, steps=600, scale=20.0, seed=0)
        self.assertGreaterEqual(result["train_accuracy"], 0.9)
        self.assertLessEqual(result["spectral_norm"], 1+1e-9)
        again = train_detector_classifier(x, y, 3, passive=True, steps=600, scale=20.0, seed=0)
        np.testing.assert_array_equal(result["W"], again["W"])


class InferenceV2(unittest.TestCase):
    def test_eprocess_exact_value_and_inputs(self):
        self.assertAlmostEqual(paired_sign_eprocess([1, 1], bets=[0.5])["e_value"], 2.25)
        with self.assertRaises(ValueError):
            paired_sign_eprocess([1, 0])
        with self.assertRaises(ValueError):
            paired_sign_eprocess([1], bets=[1.0])

    def test_eprocess_controls_error_and_has_power(self):
        rng = np.random.default_rng(9)
        null = rng.choice([-1, 1], size=(2000, 200))
        type1 = np.mean([eprocess_decision(paired_sign_eprocess(r), 0.05) == "REJECT_H0" for r in null])
        self.assertLessEqual(type1, 0.065)
        alt = np.where(rng.random((300, 200)) < 0.75, 1, -1)
        power = np.mean([eprocess_decision(paired_sign_eprocess(r), 0.05) == "REJECT_H0" for r in alt])
        self.assertGreaterEqual(power, 0.9)

    def test_tost(self):
        close = tost_paired([0.001, -0.002, 0.0015, 0.0, -0.001, 0.002], margin=0.01)
        self.assertTrue(close["equivalent"])
        self.assertLess(close["p_tost"], 0.05)
        far = tost_paired([0.05, 0.06, 0.04, 0.055, 0.045], margin=0.01)
        self.assertFalse(far["equivalent"])
        self.assertGreater(far["p_tost"], 0.05)


class IntegrityTools(unittest.TestCase):
    def test_commitment_round_trip_and_tampering(self):
        salt = bytes(range(32))
        labels = [0, 2, 1, 1, 3]
        c = commit_labels(labels, salt)
        self.assertTrue(verify_reveal(labels, salt, c["root"], c["count"]))
        self.assertFalse(verify_reveal([0, 2, 1, 1, 2], salt, c["root"], c["count"]))
        self.assertFalse(verify_reveal(labels, bytes(32), c["root"], c["count"]))
        with self.assertRaises(ValueError):
            commit_labels(labels, b"short")

    def _record(self):
        return {"id": "EXP-006-WAVE-CONFIRM-001", "hypothesis": "h", "alternative": "a",
                "protocol_commit": "a"*40, "sources": [{"path": "x.py", "sha256": "b"*64}], "inputs": {},
                "environment": {}, "seeds": [0], "resource_budget": {}, "deadline": "2026-11-01",
                "commands": ["python x.py"], "exit_codes": [0], "results": {}, "independent_oracle": "meep",
                "decision_rule": "E_max <= 0.02", "decision": "PASS", "deviations": [], "limitations": ["2D"],
                "published_commit": "c"*40, "status": "PASS"}

    def test_record_validation(self):
        self.assertEqual(validate_experiment_record(self._record()), [])
        bad = self._record() | {"id": "EXP-005-NEW", "independent_oracle": "", "sources": [{"path": "x", "sha256": "XYZ"}]}
        problems = " | ".join(validate_experiment_record(bad))
        for needle in ("EXP-005", "independent oracle", "sources[0]"):
            self.assertIn(needle, problems)
        self.assertIn("published commit", " ".join(validate_experiment_record(self._record() | {"published_commit": "PENDING"})))

    def test_identifier_extraction_and_resolution(self):
        text = ("See [Wright](https://doi.org/10.1038/s41586-021-04223-6), arXiv:2104.13386v1 and "
                "https://arxiv.org/abs/1812.07614. Also 10.1137/030601818.")
        ids = extract_identifiers(text)
        self.assertEqual(ids["doi"], ["10.1038/s41586-021-04223-6", "10.1137/030601818"])
        self.assertEqual(ids["arxiv"], ["2104.13386", "1812.07614"])
        def fake(url, headers):
            if "04223" in url:
                return 200, json.dumps({"responseCode": 1}).encode()
            if "030601818" in url:
                return 404, b""
            return (200, b"") if "2104.13386" in url else (503, b"")
        status = {r["id"]: r["status"] for r in resolve_identifiers(ids, fetch=fake)}
        self.assertEqual(status, {"10.1038/s41586-021-04223-6": "FOUND", "10.1137/030601818": "NOT_FOUND",
                                  "2104.13386": "FOUND", "1812.07614": "ERROR"})


class WaveCrossCheck(unittest.TestCase):
    def test_p17_free_space_overlap_is_reproduced(self):
        """P1-7 reports a 2.7 % free-diffraction loss for w = 8 lambda over ~95 lambda."""
        lam, w, z = 1.0, 8.0, 95.0
        zeta = 2*z/((2*math.pi/lam)*w*w)
        closed = 1/math.sqrt(1+zeta*zeta/4)
        y = np.linspace(-200, 200, 8192, endpoint=False)
        dy = y[1]-y[0]
        g0 = gaussian_1d(y, 0, lam, w)
        overlap = abs(modal_amplitude(angular_spectrum_1d(g0, dy, z, lam), g0, dy))**2
        self.assertLess(abs(overlap-closed), 1e-4)
        self.assertTrue(0.026 < 1-overlap < 0.028)


class FrontierManifest(unittest.TestCase):
    def test_initial_frontier_cannot_be_complete(self):
        doc = json.loads((HERE/"frontier-manifest.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            report = verify_frontier(Path(directory), doc)
        self.assertTrue(report["integrity_pass"])
        self.assertFalse(report["all_frontier_fronts_pass"])

    def test_replication_needs_external_evidence(self):
        doc = json.loads((HERE/"frontier-manifest.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/"verifier.json").write_text("{}")
            import hashlib
            pin = {"verifier.json": hashlib.sha256(b"{}").hexdigest()}
            for o in doc["objectives"]:
                if o["id"] == "F5":
                    o.update(state="PASS", remaining=[], pins=pin, scientific_verifier_record="verifier.json")
            report = verify_frontier(root, doc)
        self.assertIn("F5", [f["id"] for f in report["failures"]])
        with self.assertRaises(ValueError):
            verify_frontier(Path("."), {"schema": "neuro3d.frontier.manifest.v1", "objectives": [{"id": "F1"}]})


if __name__ == "__main__":
    unittest.main()
```

### 38.7. frontier-manifest.json

<!-- CODEFILE: agent_support/frontier-manifest.json -->
```json
{
  "schema": "neuro3d.frontier.manifest.v1",
  "base_commit": "69db25ce7b04a98e24609bcd539c5041f269658d",
  "snapshot_date": "2026-10-12",
  "scope": "Frontier fronts added by guide revision v2; separate from the eleven closure fronts and from the canonical ten-objective JSON",
  "objectives": [
    {
      "id": "F1",
      "name": "Central falsifiable hypothesis and nested function-class ablation",
      "state": "OPEN",
      "remaining": [
        "Preregister H-A to H-D; run free, passive and geometry-realizable classes on the same encoding and split"
      ]
    },
    {
      "id": "F2",
      "name": "Fundamental theory and formally checked core",
      "state": "OPEN",
      "remaining": [
        "Reachable-set dimension study; Lean statements and proofs for the certificate lemmas T1-T5"
      ]
    },
    {
      "id": "F3",
      "name": "Physical demonstrator and sim-to-real fidelity",
      "state": "OPEN",
      "remaining": [
        "Owner decision D0; partner, platform, transfer-matrix tomography and prospective predictions"
      ]
    },
    {
      "id": "F4",
      "name": "End-to-end energy and latency at matched accuracy",
      "state": "OPEN",
      "remaining": [
        "Measured optical and electronic chain against the best electronic baseline; reference limits computed"
      ]
    },
    {
      "id": "F5",
      "name": "Independent replication by another team",
      "state": "OPEN",
      "remaining": [
        "Results Reproduced or Replicated by people outside the project, with their own record"
      ]
    },
    {
      "id": "F6",
      "name": "Adversarial review, blind analysis and registered report",
      "state": "OPEN",
      "remaining": [
        "Sealed test labels, red-team report, Stage 1 submission if the owner chooses that route"
      ]
    },
    {
      "id": "F7",
      "name": "Open archive and citable release",
      "state": "OPEN",
      "remaining": [
        "Release DOI, Software Heritage identifier, CITATION.cff, container digest, data licences"
      ]
    },
    {
      "id": "F8",
      "name": "Authorship, AI-use disclosure and ethics",
      "state": "OPEN",
      "remaining": [
        "CRediT roles agreed by real authors; AI-use statement; ethics approval before any new human data"
      ]
    },
    {
      "id": "F9",
      "name": "External adoption and impact",
      "state": "OPEN",
      "remaining": [
        "Use by independent groups documented by them; cannot be produced by the project itself"
      ]
    }
  ]
}
```

### 38.8. scientific_closure_v2.yml

<!-- CODEFILE: agent_support/scientific_closure_v2.yml -->
```yaml
# Copy to .github/workflows/scientific-closure-v2.yml after the v2 kit is committed.
# Actions are pinned to commit SHAs resolved with git ls-remote on 2026-10-12
# (same major versions the repository already uses). The job checks the
# support kit only; it does not certify the project, Blender, or any GPU.
name: Scientific closure support v2
on:
  workflow_dispatch:
  pull_request:
    paths:
      - 'agent_support/**'
      - '.github/workflows/scientific-closure-v2.yml'
permissions:
  contents: read
jobs:
  support:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4.4.0
        with:
          persist-credentials: false
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5.6.0
        with:
          python-version: '3.12'
      - name: Install declared support dependencies
        run: python -m pip install -r agent_support/requirements-closure.txt
      - name: Run v1 and v2 support regressions
        env:
          PYTHONNOUSERSITE: '1'
          PYTHONDONTWRITEBYTECODE: '1'
          OPENBLAS_NUM_THREADS: '1'
          OMP_NUM_THREADS: '1'
        run: python -m unittest discover -s agent_support -p 'test_*.py' -v
```

### 38.9. neuro3d_selected_cpu.yml

<!-- CODEFILE: agent_support/neuro3d_selected_cpu.yml -->
```yaml
# Copy to .github/workflows/neuro3d-selected-cpu.yml. Successor to the manual-only
# cpu-tests.yml, which installs no dependencies. It runs the eight section 6.2
# regressions, each in a fresh process. With exactly these pins they passed at
# 69db25c on Linux with CPython 3.12.3 during guide revision v2 (55 tests); this
# GitHub job itself has not been run yet. The project lock pins scikit-learn
# 1.4.0 with numpy 2.2.6, which pip cannot resolve together, so it is not used.
name: Neuro3D selected CPU regressions
on:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  selected:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        test:
          - test_governance_consistency
          - test_coherent_state_graph_v1
          - test_state_graph_enclosure_v1
          - test_surface_union_interior_v1
          - test_robust_first_hit_exact_v1
          - test_affine_geometry_network_v1
          - test_escala_modos
          - test_verificar_hashes
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4.4.0
        with:
          persist-credentials: false
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5.6.0
        with:
          python-version: '3.12'
      - name: Install minimal dependencies
        run: python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.7.2 mpmath==1.3.0
      - name: Run one regression in a fresh process
        env:
          PYTHONNOUSERSITE: '1'
          PYTHONDONTWRITEBYTECODE: '1'
          OPENBLAS_NUM_THREADS: '1'
          OMP_NUM_THREADS: '1'
        run: python -m unittest Blender/tests/${{ matrix.test }}.py -v
```

## 39. Ejecución del kit v2 y validación de esta entrega

Tras extraer todos los bloques, desde la raíz del checkout:

```bash
python -m unittest discover -s agent_support -p 'test_*.py' -v
python agent_support/support_demo_v2.py --out agent_support-control-v2-run01.json
python agent_support/closure_v2.py --repo . --manifest agent_support/frontier-manifest.json
```

El primer comando ejecuta 57 pruebas (33 v1 y 24 v2). El segundo escribe un recibo sintético CPU con los controles v2; no es una ejecución GPU ni un resultado del proyecto. El tercero **debe devolver 2 en el estado inicial**, porque los nueve frentes de frontera están OPEN; es una protección contra declarar el cierre, no un fallo.

Validación de esta entrega, ejecutada antes de publicarla: (1) `diff` entre la guía original y esta revisión sin ninguna línea eliminada ni modificada; (2) extracción de los 20 bloques desde este mismo Markdown a un directorio vacío; (3) los once bloques v1 extraídos coinciden byte a byte con los de la guía original (tabla del §22.3); (4) los bloques v2 extraídos coinciden con los archivos probados; (5) las 57 pruebas pasan desde la copia extraída en los dos entornos; (6) los YAML se analizan sin errores.

Para informar al propietario de esta revisión basta con lo anterior y con la fe de erratas del §23. Las tareas pendientes siguen siendo las de los pasos A–J y K–R; esta revisión no ejecutó ninguna de ellas.
