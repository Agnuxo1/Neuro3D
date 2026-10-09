# Auditoria independiente: validacion anidada de Motor Imagery (Neuro3D)

Fecha de la auditoria: 2026-10-09. Carpeta auditada (solo lectura): `D:\PROJECTS\neuro3d-kaggle\motor-imagery\work\nested`.
Hora local de los ficheros = UTC+2 (la preinscripcion declara 04:05 UTC = 06:05 local).
Nada se modifico en la carpeta origen ni en `D:\PROJECTS\9_NEBULA_NEW` (comprobado con `find -newermt` tras las pruebas: 0 ficheros nuevos).
Mis scripts y copias de trabajo estan en el scratchpad de la sesion, no en la carpeta origen.
Reproduccion: una sola ejecucion, CPU, un sujeto (S001), 12 s de reloj (muy por debajo del tope de 10 min). Sin GPU. No lei ningun fichero de configuracion de Kaggle.

## Resumen de criterios

| Criterio | Estado | Evidencia corta |
|---|---|---|
| Preinscripcion anterior a los resultados, con rejilla, metricas, anidacion, semillas y criterios | PASA (con huecos menores) | mtime 06:09 frente a primer resultado 06:32 |
| ADDENDUM-SEEDS5: motivado por resultados previos, declarado post hoc | PASA como transparencia; es enmienda post hoc | "finalistas elegidas por el resultado anterior" |
| El codigo actual reproduce results_full.json | PASA PARCIAL (1 config, 1 sujeto) | dlogit <= 4,7e-5, 0 cambios de signo |
| Sin fugas en la validacion anidada | PASA | lineas citadas en seccion 4 |
| Cifras del informe frente a JSON | PASA para las cifras historicas; el informe no contiene N1/N2 | recalculo identico |
| Rutas absolutas | FALLA (portabilidad) en predict_var.py y 2 .sh | seccion 6 |
| Veredicto: modelo optico mejor que FBCSP/EEGNet con la significacion reportada | NO COMPROBABLE con la validacion anidada tal cual; direccion del efecto robusta, significacion y magnitud no validadas | seccion 7 |

## 1. Cronologia: la preinscripcion fija todo ANTES de results_full.json

Marcas de tiempo (`ls --time-style=full-iso`; no hay git en la carpeta, luego mtime es la unica prueba y es modificable):

| Hora local | Evento | Fuente |
|---|---|---|
| 06:03:50 | creacion de nested_bench.py | CreationTime |
| 06:05:33 | creacion de PREINSCRIPCION.md | CreationTime |
| 06:06-06:08 | humo en CPU (raw/smoke) | smoke_logs |
| 06:08:02 | analyze_nested.py (creado y no modificado despues) | mtime |
| 06:09:14 | PREINSCRIPCION.md, ultima modificacion (Enmienda 1) | mtime |
| 06:10:46 | INFORME-NESTED.md | mtime |
| 06:27:05 | se encola el primer trabajo `full` | logs/full_shard0.log |
| 06:32:27 | primer resultado real (raw/full/S001.npz) | mtime |
| 07:05:23 | primera creacion de results_full.json (con 9 sujetos) | CreationTime |
| 07:46:39 | results_full.json definitivo (17 sujetos) | mtime |

Contenido de la preinscripcion (PREINSCRIPCION.md):
- Rejilla: seccion 2 (lineas 27-33), 36 configuraciones = 3 modelos x 2 features x 2 wd x 3 instantaneas de epoca; lr 2e-2 y batch 32 fijos.
- Metrica: linea 36, exactitud agrupada por sujeto sobre sus epocas de test externo, media sin ponderar entre 17 sujetos.
- Diseno anidado: lineas 14-25 (LORO externo y LORO interno con grupo = `run`; fold interno valido con >= 20 train y >= 10 val; sin fold valido se usa el defecto).
- Semillas: linea 17 y 33 (semilla externa = indice de fold; `--seeds` con `k+1000*s` en linea 70).
- Criterios de decision: lineas 59-64. Estimadores N1, N1b, N2, N3 y contrastes con umbral Bonferroni p < 0,01: lineas 35-58.
- Declara honestamente (linea 7-13) que la rejilla se construyo conociendo los LORO historicos.

Verificacion adicional: los 17 `raw/full/*.npz` tienen metadatos identicos (rejilla de 12 tripletas, epocas 30/60/90, defecto polar|f12w3|0.001|60, norm=train, seeds=1, inner=True); la rejilla no cambio durante la ejecucion. Se ejecuto en cuda.

Discrepancias entre la preinscripcion y el codigo o la ejecucion real:
1. Etapas de ejecucion (preinscripcion lineas 66-72): Etapa 1 (`--no-inner` primero) y Etapa 2 (primero S001-S005) no se siguieron. Se lanzo directamente la rejilla completa con bucle interno para los 17 sujetos, repartida en `--shard 0/2` (el shard 1 nunca corrio: `logs/full_shard1.log` solo tiene lineas de cola) y luego un trabajo por sujeto (`run_per_subject.sh`). Efecto sobre la inferencia: ninguno, pues la rejilla y los estimadores son los preinscritos.
2. Un analisis parcial: `results_full.json` nacio a las 07:05:23, cuando solo existian 9 sujetos (shard 0). Alguien miro resultados parciales. La rejilla ya estaba fija y no cambio despues, pero el hecho no esta documentado.
3. Convencion de signo del Spearman: la preinscripcion (linea 61) exige "Spearman medio < 0 (BCE baja <-> exactitud alta)", pero `analyze_nested.py:68` calcula el rango de BCE frente al rango de (-exactitud), de modo que rho > 0 significa que la seleccion interna informa (nota del propio fichero, linea 99). Los criterios quedan con signos opuestos entre texto y codigo. No cambia la decision: N1-N3 = -0,0119 (IC95 incluye 0) ya impide "seleccion interna util"; rho = +0,033 (convencion del codigo) es esencialmente cero.
4. Semillas internas no preinscritas: el codigo usa `seed=100+10*k+j` (`nested_bench.py:122`); la preinscripcion solo fija la semilla externa. Hueco menor.
5. `analyze_nested.py` se creo a las 06:08, tres minutos DESPUES del texto de la preinscripcion que lo describe (06:05). No hay prueba independiente de que el script implemente lo preinscrito mas alla de leerlo (lo hice, ver seccion 4: coincide).
6. Contrastes frente a FBCSP/EEGNet: la preinscripcion no los contiene. La rejilla anidada solo cubre modelos opticos.
7. Seleccion del umbral de significacion: la preinscripcion pide IC95 que excluya 0 y a la vez p < 0,01 (Bonferroni). N2-N3 (+0,0146) tiene IC95 [+0,0012, +0,0283] (excluye 0) pero p_signflip = 0,065 (no cumple 0,01). La preinscripcion no dice cual de las dos reglas manda.
8. El INFORME (06:10) se escribio antes de los resultados y no se actualizo: `INFORME-NESTED.md:66` anuncia `--grid {full,smoke}` (ya existe `finalists`) y la linea 126 dice "No probado: --seeds 5" (se uso despues sin prueba previa de ese camino). Ningun documento interpreta results_full.json ni results_seeds5.json.

## 2. ADDENDUM-SEEDS5.md (08:40, posterior a results_full de 07:46)

- Motivado por resultados previos: SI. Linea 4-5: "las tres configuraciones finalistas elegidas por el resultado anterior (12 bandas x 3 ventanas, decaimiento 1e-2, 90 epocas)"; linea 6-8: valores de una semilla 0,7188; 0,6953; 0,7285. Los he comprobado contra la matriz por sujeto de results_full: polar|f12w3|0.01|90 = 0,7188, lattice32 = 0,6953, free = 0,7285. Es decir, son la MEJOR configuracion de cada modelo por LORO de 1 semilla (maximo de 12 por modelo), no una eleccion a priori.
- Declara que es posterior: SI. Titulo "Anexo POST-HOC", "Estatus: exploratorio", y linea 10-11 advierte del sesgo de seleccion.
- Cambia criterios de decision: NO. Anade dos hipotesis propias (H1: 5 semillas mejora >= 0,005 por finalista; H2: el conjunto de 3 no supera al mejor individual) y redefine el "defecto" de la rejilla `finalists` como `polar|f12w3|1e-2|90` (`nested_bench.py:31`). No toca N1/N2/N3 de la rejilla `full`.
- Defectos de procedimiento:
  - La preinscripcion (linea 4-5) exige que los cambios vayan en su seccion "Enmiendas" y que los resultados informen de ambas versiones; el addendum es un fichero aparte y PREINSCRIPCION.md (06:09) no lo referencia.
  - Hora declarada "~06:45 UTC" (= 08:45 local) frente a la hora real de fichero 08:40:08 local = 06:40 UTC; el trabajo se encolo a las 08:40:09 (`logs/seeds5.log`) y S001 termino a las 08:43. La hora escrita es posterior al lanzamiento; la diferencia es de 5 minutos y el "~" la excusa, pero no es una marca fiable.
  - No hay ningun fichero que evalue H1 y H2. `results_seeds5.txt` es la salida generica de `analyze_nested.py`, que en una rejilla de 3 configuraciones sin bucle interno es degenerada: N1 = N3 por construccion (0/17/0), N2 elige `free` (es el maximo), "MAX - N2 = 0", y Spearman no existe. Esas lineas no deben citarse como evidencia.
- Resultado de H1 y H2 (calculo propio sobre raw/seeds5 y la matriz de results_full; bootstrap por sujetos 20 000 remuestreos):
  - H1 polar: 0,7188 -> 0,7113, diferencia -0,0074 IC95 [-0,018, +0,003]. Refutada (y en sentido contrario).
  - H1 lattice32: 0,6953 -> 0,7047, +0,0094 IC95 [-0,003, +0,022]. Refutada por la regla del propio addendum (IC95 incluye 0), aunque el punto estimado supera 0,005.
  - H1 free: 0,7285 -> 0,7299, +0,0015 IC95 [-0,008, +0,011]. Refutada.
  - H2: conjunto polar+lattice32+free 0,7184 frente a free 0,7299, diferencia -0,0115 IC95 [-0,027, +0,003]. No se puede decir que el conjunto supere al mejor individual (coherente con H2).
- Efecto en la interpretacion: la bajada de polar al promediar semillas (0,7188 -> 0,7113, que cae a 0,7128 del defecto preinscrito) es la firma de la "maldicion del ganador": el valor de 1 semilla del mejor de 12 estaba inflado. Promediando los tres finalistas el cambio es +0,0012, de modo que el sesgo medio es pequeno pero el ruido de semilla por configuracion (+-0,01) es del tamano de las diferencias entre configuraciones. Todo lo que el addendum produce (y cualquier cifra "5 semillas") es exploratorio y no un estimador limpio del test oculto.

## 3. Cambios en nested_bench.py (08:40) y reproducibilidad de results_full.json

Que cambio: no se puede demostrar con un diff, porque no hay git ni copia previa (busque `nested_bench*` en neuro3d-kaggle, 9_NEBULA_NEW y .cognition: solo existe la version actual). Evidencia indirecta:
- El unico elemento con huella evidente del addendum es `GRIDS["finalists"]` con el comentario "ADDENDUM-SEEDS5.md (post-hoc, declarado antes de ejecutar)" en `nested_bench.py:30-31`. Como `--grid` usa `choices=list(GRIDS)` (linea 131), anadir la entrada no exige otro cambio.
- Los metadatos que escribe el codigo actual (linea 102-104: sid, triples, epochs, default, norm, seeds, runs, min_train, min_val, inner, dev) tienen exactamente las mismas claves que los guardados a las 06:32 en raw/full. No hay clave nueva.
- No se puede descartar un cambio en otra linea (por ejemplo en `--seeds`, que el informe dice que no se habia probado). La copia en `9_NEBULA_NEW\Benchmarks\eeg-motor-imagery\evidencia-validacion-anidada` (preparada en el indice de git, sin commit) NO contiene el codigo: ni nested_bench.py, ni analyze_nested.py, ni test_nested_groups.py, ni predict_var.py. Solo tiene documentos, JSON, logs y hashes. Su MANIFEST-SHA256 coincide con los ficheros de origen para PREINSCRIPCION, ADDENDUM y los dos results (comprobado, 4/4), pero la fecha de ese manifiesto es 2026-10-09, no es un sello de tiempo de 2026-09-30.

Comprobacion ejecutada (un sujeto, una configuracion, CPU, 12 s): S001, `polar|f12w3|wd 1e-3`, instantaneas 30/60/90, 3 folds externos, y el fold interno (outer=1, val=3). Se usaron las funciones actuales `outer_folds`, `inner_folds`, `make_scaled` y `fit_snapshots` de nested_bench.py con las semillas del codigo (`k` y `100+10*k+j`), y se compararon con los logits guardados en `raw/full/S001.npz` (generados en GPU):
```
OUTER run=1 ep=30/60/90: max|dlogit| 9,5e-06 / 1,8e-05 / 2,5e-05  acc_ref=acc_new=0,74/0,70/0,76  signos distintos 0
OUTER run=2 ep=30/60/90: 2,5e-05 / 2,7e-05 / 4,0e-05               acc=0,58/0,66/0,68 identicas       0
OUTER run=3 ep=30/60/90: 2,0e-05 / 2,8e-05 / 4,6e-05               acc=0,70/0,70/0,70 identicas       0
INNER outer=1 val=3 ep=30/60/90: 1,0e-05 / 2,1e-05 / 4,7e-05                                          0
```
Los indices de entrenamiento/validacion/test recalculados son identicos a los guardados (`assert np.array_equal`). Resultado: el codigo actual reproduce los logits del run `full` hasta el error numerico CPU/GPU (< 5e-5) y las exactitudes coinciden exactamente. PASA para esa ruta.

NO COMPROBABLE: las ramas `lattice32` y `free`, `wd = 1e-2`, el resto de sujetos, `--seeds 5` y `--grid finalists`. El tope de una ejecucion de un solo sujeto me impedia ampliar. Evidencia indirecta en su favor: las cinco cifras LORO historicas del informe (polar f8w1 0,6822; polar f12w3 0,7128; lattice32 f8w1 0,6771; lattice32 f12w3 0,6872; free f8w1 0,6968) salen identicas, a 4 decimales, en `loro_by_config` de results_full.json (que vienen de un entrenamiento independiente hecho dias antes con `bench.py`). Esto valida la rama `free` y `lattice32` con wd = 1e-3 y 60 epocas a nivel agregado.

Ademas, `analyze_nested.py` reproduce exactamente los dos JSON: copie `analyze_nested.py` y `raw/full`, `raw/seeds5` al scratchpad, lo ejecute y obtuve `results_full.json` y `results_seeds5.json` identicos (comparacion de JSON `True`, `diff` de los txt solo difiere en el salto de linea final).

## 4. Fugas de datos

Veredicto: no hay fuga en la ruta con `--norm train` (la que se uso en los 34 ficheros raw).

Evidencia por linea:
- Normalizacion: `nested_bench.py:62-65` (`norm == "train"`): la desviacion tipica se calcula con `Z[tr]` y se aplica a `Z[e]`. En el bucle externo `tr` es el entrenamiento externo (linea 114); en el interno `it` (linea 121). El bloque `norm == "run"` (lineas 66-72) normaliza cada run con sus propias estadisticas, incluido el run de test, sin etiquetas (transductivo); no se uso: `meta["norm"]` es "train" en los 17 ficheros de `full` y los 17 de `seeds5`.
- Particion externa: `nested_bench.py:43-45`: `np.where(runs != r)` entrena, `np.where(runs == r)` prueba; cada sujeto tiene su propio fichero y su propio modelo (linea 99), luego no hay mezcla entre sujetos. Es "por sujeto y por run" (sujeto-dependiente, LORO).
- Particion interna: `nested_bench.py:48-57`; las aserciones de las lineas 55, 110 y 111 impiden run compartido entre train/val interno, impiden que el run externo aparezca en el bucle interno y exigen que el interno este contenido en el entrenamiento externo.
- Verificacion independiente de los indices guardados (sin entrenar), sobre los 34 ficheros raw: 50 folds externos, 64 folds internos (full) y 0 (seeds5, sin bucle interno), 0 violaciones; el test externo de cada sujeto es una particion exacta de sus epocas. Coincide con el informe (64 internos; 2 de 50 externos sin interno, S007).
- Seleccion de hiperparametros: N1 usa solo logits internos: `analyze_nested.py:50-56` (BCE y exactitud del fold interno `i|...`), `63-65` (eleccion por menor BCE interna; empate al defecto) y `69` (se puntua con el logit externo `c_f[j1]` de la configuracion elegida). N2 excluye al sujeto evaluado: `analyze_nested.py:73` (`np.delete(np.arange(n), si)`). Los N1/N2 no ven el test del sujeto. N2 independiente reproducido por mi cuenta: 0,7274 (igual que el JSON); elige `free|f12w3|0.01|90` en 16 de 17 sujetos.
- Preprocesado: `prep.py:22-24` filtra cada fichero de run completo (50 Hz y 1-100 Hz, zero-phase) y quita la media por canal de ese fichero; no usa estadisticas entre runs. `bench.cwt` (lineas 24-33) es por epoca.
- Fugas que NO elimina la anidacion (declaradas por el autor en la preinscripcion, lineas 7-13): el contenido de la rejilla (f12w3, polar, lattice32) se eligio mirando el LORO historico de estos mismos 17 sujetos. Un punto no mencionado: `analyze_nested.py:128-130` (exploratorio T1) selecciona los folds "equilibrados" con la etiqueta del test (`abs(y.mean()-0.5)`) y la ganancia de umbral en la mediana (0,7106 -> 0,7358 en full; 0,7112 -> 0,7555 en seeds5) solo vale si el test oculto esta equilibrado; no es evidencia de validacion.
- Aviso sobre `predict_var.py`: su docstring dice "configuracion elegida por la validacion anidada", pero polar y lattice32 con wd 1e-2/90 epocas son el maximo LORO de 1 semilla de cada modelo (seccion 2), no una salida de N1/N2; solo `free` coincide con N2. El `submit_20261001.sh` anota "LORO 0.7188" y "0.7285", cifras de 1 semilla de la configuracion maxima (sesgadas al alza).

## 5. Cifras del informe frente a los JSON

Recalculo propio desde los logits crudos (sin usar `analyze_nested.py`) y con `analyze_nested.py` en una copia: coinciden.

Media por modelo (media sobre las 12 configuraciones de cada modelo en la rejilla de 36; exactitud agrupada por sujeto, media de 17):

| Modelo | Media de sus 12 configs | Mejor config | Config por defecto (60 ep, wd 1e-3, f12w3) |
|---|---|---|---|
| free (matriz compleja libre) | 0,7041 | 0,7285 (f12w3, wd 1e-2, 90 ep) | 0,7249 |
| polar | 0,6907 | 0,7188 (f12w3, wd 1e-2, 90 ep) | 0,7128 |
| lattice32 | 0,6787 | 0,6953 (f12w3, wd 1e-2, 90 ep) | 0,6872 |

Estimadores de results_full.json (recalculados): N1 0,7009; N1b 0,6967; N2 0,7274; N3 0,7128; MAX_LORO 0,7285; MEAN_over_grid 0,6912; ORACLE 0,7540. Efectos marginales (pareados por sujeto): free - polar -0,0134 (polar peor, IC95 [-0,018, -0,008], p = 0,0015, 15 de 17 sujetos); lattice32 frente a free -0,0254 (p = 0,006); f8w1 frente a f12w3 -0,0249 (p = 0,006); wd 1e-2 frente a 1e-3 +0,0006 (nulo); 60 y 90 epocas frente a 30: +0,018 (p < 0,002), 60 = 90.
results_seeds5.json (recalculado): polar 0,7113; lattice32 0,7047; free 0,7299; conjuntos E1 0,7132 y E2 0,7184.

Comparacion con INFORME-NESTED.md: el informe se escribio a las 06:10, antes de cualquier resultado, y no contiene N1/N2/N3, el Spearman ni ninguna cifra de results_*.json. Sus cifras (inventario historico, tabla 1.1) son las de `bias_inventory.json`. Comparacion de las que SI se pueden contrastar:
- Cifras historicas LORO (0,7128; 0,6822; 0,6872; 0,6771; 0,6968): idénticas a `loro_by_config` de results_full.json. Sin diferencias.
- Frases del informe que los resultados contradicen o dejan sin soporte: "se espera que N1 se parezca a una config aleatoria con un poco de senal" -> N1 (0,7009) esta por debajo de N3 (0,7128) y de N2 (0,7274), con Spearman medio +0,033 (ruido). "N2 es el estimador principal... un cambio para Kaggle debe salir de N2" -> N2 elige `free|f12w3`, que el informe trataba como no probado (linea 85, "free nunca se probo con f12w3"; ahora es la mejor configuracion de la rejilla). "polar f12w3 es el candidato global" (informe linea 130) queda sustituido por `free f12w3` en N2.
- Informe y addendum: valores de una semilla del addendum (0,7188; 0,6953; 0,7285) y "optimismo MAX-N2 = +0,001" coinciden con los JSON (0,00107).
- No recalculado: el "1795 epocas" del EE binomial del informe.
- Contrastes de INFORME 1.1 frente a FBCSP/EEGNet: recalculados con mi propio bootstrap (semilla distinta): polar f12w3 - FBCSP +0,0602 IC95 [+0,0255, +0,0947] p = 0,0048; - EEGNet +0,0855 [+0,0314, +0,1406] p = 0,0093. Coinciden con el informe (0,004 y 0,010).

## 6. Rutas absolutas con D:\ o D:/

| Fichero:linea | Contenido | Efecto |
|---|---|---|
| `predict_var.py:7` | `WORK = "D:/PROJECTS/neuro3d-kaggle/motor-imagery/work"` (ademas hace `os.chdir(WORK)`) | falla en otra maquina o ruta |
| `run_per_subject.sh:3` | `cd /d/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested` (ruta MSYS de D:) | idem |
| `run_per_subject.sh:5` | `python D:/PROJECTS/.cognition/gpu_queue/gpuq.py ... python D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/nested_bench.py` | gpuq.py y nested_bench.py fijos |
| `run_seeds5.sh:2` | `cd /d/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested` | idem |
| `run_seeds5.sh:4` | idem linea 5 de run_per_subject.sh (con `--grid finalists --tag seeds5 --seeds 5 --no-inner`) | idem |
| (fuera de lo pedido) `../lattice_torch.py:45` | `sys.path.insert(0, "D:/PROJECTS/.cognition/neuro3d/exp004")` | solo dentro de `if __name__ == "__main__"`, no afecta a nested |
| (fuera de lo pedido) `../submit_20261001.sh:5` | `cd /d/PROJECTS/...` | idem |

`nested_bench.py`, `analyze_nested.py`, `test_nested_groups.py` y `bias_inventory.py` no tienen rutas D: (usan `os.path.dirname(__file__)`); `bias_inventory.py:8` y `nested_bench.py:18` asumen la estructura `work/nested` con `work/` como directorio padre.

Que cambiar para ejecutar desde otra carpeta:
1. `predict_var.py:7`: `WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` (la misma idea que `nested_bench.py:18`); sustituir `os.chdir(WORK)` por no cambiar de directorio o hacerlo relativo.
2. Los dos `.sh`: `cd "$(dirname "$0")"`; `NESTED="$(pwd)"`; `mkdir -p logs`; reemplazar la ruta de `nested_bench.py` por `"$NESTED/nested_bench.py"` y la de `gpuq.py` por una variable (`GPUQ="${GPUQ:-<ruta>}"`) o llamar a `python` directo si no hay cola; usar `python -B` si se quiere evitar `__pycache__`.
3. Condicion que persiste: la carpeta `nested/` debe seguir colgando de un `work/` que contenga `bench.py`, `lattice_torch.py` y `data/S###.npz` (generados por `prep.py` desde el zip de la competicion, que no esta en la copia de evidencia). Sin esos `data/`, solo se puede ejecutar `analyze_nested.py` y `bias_inventory.py` (necesitan `raw/` y los `bench_*.json`); lo confirme ejecutando `analyze_nested.py` desde otra carpeta con solo `raw/`.
4. La copia de evidencia en `9_NEBULA_NEW` carece del codigo; para que sea reproducible hay que anadir `nested_bench.py`, `analyze_nested.py`, `test_nested_groups.py`, `predict_var.py`, los `.sh` y sus hashes.

## 7. Veredicto

Afirmacion a evaluar: el modelo optico (malla polar, matriz libre) supera a FBCSP y EEGNet con la significacion reportada.

Lo que la validacion anidada SI respalda (PASA):
- Dentro de la familia optica, el procedimiento anidado esta bien construido (sin fugas externas ni internas, indices verificados, analisis reproducible bit a bit desde los logits). Los estimadores honestos de "elegir una configuracion de la rejilla con otros sujetos" valen N2 = 0,7274 (IC95 del error por sujeto: ee 0,025) y la media de una configuracion cualquiera de la rejilla vale 0,6912. La seleccion por sujeto (N1 = 0,7009) no ayuda: N1 - N3 = -0,0119, IC95 [-0,028, +0,004], p = 0,19.
- El optimismo por elegir DENTRO de la rejilla es pequeno (MAX - N2 = +0,001), aunque esa medida esta limitada: una configuracion domina en 16 de 17 pliegues de dejar un sujeto fuera, luego N2 casi coincide con MAX por construccion.
- Direccion del efecto frente a las bases: robusta. Con mi propio calculo pareado por sujeto, 17 sujetos, contra FBCSP (0,6526) y EEGNet (0,6273):

| Estimador optico | media | - FBCSP (IC95; p) | - EEGNet (IC95; p) |
|---|---|---|---|
| polar f12w3 wd1e-3 60 ep (defecto, elegido tras ver LORO) | 0,7128 | +0,060 [+0,026, +0,095]; 0,005 | +0,086 [+0,031, +0,141]; 0,009 |
| polar, LOSO dentro de las 12 configs polar (anidado) | 0,7188 | +0,066 [+0,034, +0,099]; 0,001 | +0,091 [+0,035, +0,149]; 0,008 |
| N2 global (free f12w3 wd1e-2 90 ep, LOSO) | 0,7274 | +0,075 [+0,042, +0,109]; 0,0006 | +0,100 [+0,045, +0,157]; 0,003 |
| media de las 36 configs de la rejilla (cota prudente, sin seleccion) | 0,6912 | +0,039 [+0,012, +0,066]; 0,016 | +0,064 [+0,010, +0,119]; 0,041 |
| polar 5 semillas wd1e-2 90 ep (post hoc) | 0,7113 | +0,059 [+0,026, +0,090]; 0,004 | +0,084 [+0,028, +0,140]; 0,013 |
| FBCSP - EEGNet | | +0,025 [-0,043, +0,093]; 0,49 | |

Lo que NO se puede afirmar:
1. Que la validacion anidada confirme la superioridad sobre FBCSP/EEGNet. La rejilla anidada y el analisis solo contienen modelos opticos; FBCSP y EEGNet no pasaron por ningun bucle anidado ni por una rejilla comparable (FBCSP: 5 bandas de 8-30 Hz, 3 pares CSP, LDA con contraccion, sin ventanas temporales; EEGNet: 80 epocas, lr 3e-3, wd 1e-2 fijos, sin busqueda). Los contrastes con p = 0,004 y 0,010 salen de `bias_inventory.py`, que son LORO historicos NO anidados, NO preinscritos (no aparecen en PREINSCRIPCION.md) y que usan una configuracion optica elegida mirando ese mismo LORO. Entre los 10 contrastes de `bias_inventory.py` sin correccion, polar - EEGNet (p = 0,010) no pasa un Bonferroni 0,05/10 = 0,005 y polar - FBCSP (p = 0,004-0,005) queda en el borde.
2. Asimetria de afinado: el modelo optico recibio un cambio de features (8 bandas/1 ventana -> 12 bandas/3 ventanas), 36 configuraciones y 5 variantes de arquitectura vistas en LORO; las bases, ninguna. Parte de la ventaja puede ser afinado y de una representacion con ventanas temporales que las bases no tienen. La media de la rejilla (+0,039 frente a FBCSP) acota el efecto sin seleccion, pero sigue sin igualar el esfuerzo de afinado de las bases. EEGNet con 80 epocas en un solo run de 8 canales y 100-160 epocas de entrenamiento esta probablemente sub-entrenado; no se ha explorado.
3. Que "polar" sea el modelo optico ganador o que la restriccion fisica (malla unitaria) sea gratuita. En la propia rejilla preinscrita la matriz libre rinde mas que la polar: -0,0134 (polar peor, p = 0,0015, 15/17 sujetos); con 5 semillas (exploratorio) +0,0186 a favor de free, IC95 [+0,004, +0,034], p = 0,03. `free` no es una malla unitaria realizable (lo dice el propio `submit_20261001.sh`). lattice32 (la rejilla fisica) es la peor: 0,7047 con 5 semillas. La etiqueta "modelo optico supera" debe especificar cual; polar y lattice32 no se diferencian entre si (+0,007, IC95 [-0,019, +0,031]).
4. Una significacion de las diferencias entre configuraciones del orden de 0,01-0,02. Con 17 sujetos, la diferencia minima detectable pareada es ~0,03; el ruido de semilla por configuracion es ~0,01 (cambios entre 1 y 5 semillas: -0,0074, +0,0094, +0,0015); y 60 frente a 90 epocas es nulo.
5. Que el resultado generalice al test oculto de Kaggle ni a otros sujetos/sesiones. Es un LORO dentro de sesion (tres runs consecutivos por sujeto, run 3 de solo 10 epocas desequilibradas), 17 sujetos, 8 canales. El control limpio es el test oculto, que no se usa. Las cifras de Kaggle (0,72-0,77) quedan por encima del LORO (0,69-0,73) y no se pueden explicar ni validar con estos datos.
6. Que el bucle interno sea informativo: la validacion interna usa 10 epocas en 2 de 3 folds externos, 1 fold interno valido cuando el test externo es el run 1 o 2, 2 cuando es el run 3 y 0 en S007 (2 de 50 folds externos); N1 tiene poca potencia por diseno. Que N1 no ayude no demuestra que la seleccion por sujeto sea inutil.

Riesgos no cubiertos por los criterios:
- Cadena de evidencia debil: no hay git ni sello externo; la prueba de que la preinscripcion precede a los resultados es el mtime. El paquete de evidencia propuesto en 9_NEBULA_NEW no incluye el codigo y se creo el 2026-10-09 (manifiesto de hashes sin fecha de origen).
- Inflacion por multiplicidad: contrastes preinscritos (5), marginales (10), bias_inventory (10), seeds5 (5) y H1/H2 (4) bajo p < 0,05 sin correccion global. De los preinscritos solo N1-N2 cumple el umbral p < 0,01.
- `results_seeds5` degenerado (N1 = N3 por construccion); citarlo como validacion anidada seria incorrecto.
- Dependencia silenciosa de `bench.WIN` global: `fit_snapshots` hace `B.WIN = win` (linea 77) en cada entrenamiento; correcto en procesos secuenciales, pero cualquier uso en hilos o en paralelo dentro de un proceso lo romperia. Para `bench.FREQS`, solo lo usa `LatticeNet(spectral=True)`.
- GPU frente a CPU: diferencias de 5e-5 en logits; en configuraciones con logits cercanos a 0 puede cambiar alguna prediccion (no ocurrio en la comprobacion realizada, 0 cambios de signo en 360 logits comparados).

## Resumen de lo ejecutado
- Lectura completa de PREINSCRIPCION.md, ADDENDUM-SEEDS5.md, INFORME-NESTED.md, nested_bench.py, analyze_nested.py, test_nested_groups.py, bias_inventory.py, predict_var.py, run_*.sh, time_cpu_probe.json, results_*.txt/json, logs y `bench.py`, `prep.py`.
- Ejecuciones: (a) `analyze_nested.py --tag full` y `--tag seeds5` sobre una copia en el scratchpad (segundos, CPU); (b) calculo propio de medias por modelo, N2, H1/H2 y contrastes con las bases (segundos); (c) verificacion de particiones sobre los 34 ficheros raw (segundos); (d) reproduccion de S001, polar f12w3 wd 1e-3, 3 folds externos y 1 interno (12 s, CPU). No se lanzo `test_nested_groups.py` (cumplido el tope de una ejecucion); su cobertura la sustituye la verificacion (c).
- Fuera de lo ejecutado: GPU (no se uso), Kaggle (no se leyo ninguna configuracion), entrenamientos largos (ninguno).
