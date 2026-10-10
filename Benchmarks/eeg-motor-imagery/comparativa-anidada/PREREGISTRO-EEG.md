# Preregistro: comparativa anidada FBCSP y EEGNet frente a la linea optica (EEG, imaginacion motora)

Fecha de fijacion: 2026-10-10, antes de ejecutar ningun modelo de esta comparativa. Repo base: 9_NEBULA_NEW, HEAD 043a205 en el momento de redactar.
Cualquier cambio posterior va en una seccion "Enmiendas" con fecha, y el informe debe dar ambas versiones.

## 0. Estado de conocimiento
- Quien redacta conoce los resultados opticos (`results_full.json`: N1 0,7009; N2 0,7274; N3 0,7128) y las bases historicas no anidadas (FBCSP 0,6526; EEGNet 0,6273 en LORO). No ha visto ningun resultado anidado de FBCSP ni de EEGNet: no existen.
- La rejilla optica (36 configuraciones) se construyo viendo los LORO historicos de estos 17 sujetos (declarado en `PREINSCRIPCION.md` de la evidencia). Las rejillas de FBCSP y EEGNet de abajo se fijan sin ejecutar nada, pero tambien conociendo el orden de magnitud de las bases. Este sesgo residual favorece a la linea optica y se declara como limite.

## 1. Pregunta
Con el mismo esquema externo y el mismo presupuesto de busqueda interna (36 configuraciones), la linea optica (rejilla `full` de la evidencia: polar, lattice32, free) tiene una exactitud externa por sujeto distinta de la de FBCSP (H1) y de la de EEGNet (H2)?

## 2. Datos y esquema externo (identico a la evidencia optica)
- Datos: `D:\PROJECTS\neuro3d-kaggle\motor-imagery\work\data\S###.npz` (17 archivos, 110 398 389 bytes), campos `Xtr` (n,8,1250), `ytr`, `run`. 17 sujetos: S001-S007, S009-S012, S014, S016-S020. El test oculto de Kaggle (`Xte`) no se usa en nada. No se descarga nada.
- Externo: leave-one-run-out (LORO) por sujeto con `outer_folds(runs)` de `nested_bench.py` (50 pliegues externos: 16 sujetos x 3 runs + S007 x 2). Mismos indices de entrenamiento y test que `raw/full/S###.npz` (`tr|r`, `te|r`).
- Interno: `inner_folds(runs, tr)` de `nested_bench.py` (LORO interno, grupo = run, entrenamiento >= 20 y validacion >= 10 epocas; 64 pliegues internos). Sin pliegue interno valido (2 pliegues de S007) se usa la configuracion por defecto de cada metodo.
- Las funciones de particion se importan de `nested_bench.py` sin copiarlas. Se comprueba que los indices coinciden con los guardados en la evidencia optica (verificacion previa, `resultados\verificacion.json`).
- La seleccion interna usa solo `ytr` de las epocas de entrenamiento externo; el run externo de test no se toca hasta puntuar la configuracion ya elegida.

## 3. Busqueda interna: 36 configuraciones por metodo
La unidad es la configuracion = una combinacion de hiperparametros y, en las redes, una instantanea de epoca. Los tres metodos tienen 36.

| Metodo | Composicion | Total |
|---|---|---:|
| Optica (ya hecha, no se reejecuta) | 3 modelos (polar, lattice32, free) x 2 features (f8w1, f12w3) x 2 decaimientos (1e-3, 1e-2) x 3 epocas (30, 60, 90); lr 2e-2 y lote 32 fijos | 36 |
| FBCSP | 4 conjuntos de bandas x 9 valores de C | 36 |
| EEGNet | 3 lr x 2 lotes x 2 decaimientos x 3 epocas (30, 60, 90) | 36 |

**FBCSP.** Extraccion de `bench.py` (`csp_filters`, 3 pares por banda, 6 filtros; Butterworth orden 4, `sosfiltfilt`, log-varianza), CSP ajustado solo con el entrenamiento del pliegue. Clasificador: regresion logistica L2 (sklearn, `lbfgs`, `max_iter=1000`, sin pesos de clase) sobre las caracteristicas estandarizadas con media y desviacion del entrenamiento. El clasificador cambia respecto a la base historica (LDA con contraccion) porque C debe existir; la base historica 0,6526 no se usa como referencia de esta comparativa.
- Conjuntos de bandas (Hz): `A` = 8-12, 12-16, 16-20, 20-24, 24-30 (historico); `B` = nueve bandas de 4 Hz entre 4 y 40 (4-8, 8-12, ..., 36-40); `C` = 8-13, 13-20, 20-30; `D` = 8-30 (una banda).
- C en {1e-4, 1e-3, 1e-2, 1e-1, 1, 1e1, 1e2, 1e3, 1e4}.
- Por defecto (N3, desempates, sin pliegue interno): `A`, C = 1.

**EEGNet.** EEGNet-8,2 de `bench.py` (F1=8, D=2, F2=16, p=0,5; entrada 8x1250 estandarizada con la desviacion del entrenamiento; AdamW; BCE con logits).
- lr en {1e-3, 3e-3, 1e-2}; lote en {16, 32}; decaimiento en {1e-3, 1e-2}. 12 entrenamientos, cada uno de 90 epocas.
- Parada temprana = instantanea: se guardan los logits tras las epocas 30, 60 y 90 de una sola trayectoria (la trayectoria es identica hasta cada epoca, igual que en la linea optica) y la validacion interna elige la epoca. No se usa ningun conjunto externo para parar.
- Por defecto: lr 3e-3, lote 32, decaimiento 1e-2, 60 epocas (ajustes de `bench.py`, con 60 en lugar de 80 para caer en la rejilla).

**Seleccion** (identica para los tres metodos): configuracion de menor log-loss (BCE) de validacion interna agrupada, ponderada por el tamano del pliegue interno; empate o ausencia de pliegue valido: configuracion por defecto. Luego se reentrena sobre todo el entrenamiento externo y se puntua en el run externo.

## 4. Semillas
- Externa: indice del pliegue externo k (0, 1, 2), como la linea optica. Interna: 100 + 10k + j (j = indice del pliegue interno), como `nested_bench.py`. Una semilla por entrenamiento; `torch.manual_seed` con esa semilla (EEGNet); FBCSP es determinista.
- Bootstrap: semilla 0 (`numpy.random.default_rng(0)`, generador nuevo para cada comparacion). Ninguna otra semilla se cambia tras ver resultados; no se anaden semillas extra.

## 5. Metrica y estimadores
- Metrica: exactitud del sujeto agrupada sobre sus epocas de test externo, media sin ponderar entre los 17 sujetos (como `analyze_nested.py`).
- **Primario (el que decide): N1**, seleccion interna por sujeto y pliegue, para los tres metodos. Optica: `estimates.N1_nested_per_subject_innerBCE` recalculado por sujeto con `analyze_nested.py` sobre `raw/full` (reproduce `results_full.json`; se comprueba 0,7009).
- Secundarios (se informan, no deciden): N1b (seleccion por exactitud interna), N2 (configuracion global elegida con los otros 16 sujetos, sin el evaluado), N3 (defecto fijo), media de las 36 configuraciones.
- Exploratorio: linea optica restringida a polar y lattice32 (24 configuraciones, sin `free`, que no es una malla unitaria realizable), solo con N2 y N3. No cuenta para las decisiones porque el numero de configuraciones difiere.

## 6. Comparacion pareada
- Para cada sujeto: d = exactitud N1 optica menos exactitud N1 del metodo base (n = 17). H1: base FBCSP. H2: base EEGNet.
- IC95: bootstrap por sujetos, 10 000 remuestreos con reemplazo, semilla 0, percentiles 2,5 y 97,5 de la media de d.
- Wilcoxon de rangos con signo, bilateral (`scipy.stats.wilcoxon`, `alternative="two-sided"`, `zero_method="wilcox"`, `method="auto"`). Se informan p crudo y p ajustado por Holm sobre las dos comparaciones primarias.
- Tambien se informa el numero de sujetos con d > 0, d = 0 y d < 0.

## 7. Reglas de decision (por hipotesis, sobre N1)
- **Superior**: limite inferior del IC95 > 0.
- **Equivalente**: IC95 entero dentro de [-0,02; +0,02].
- **No concluyente**: en cualquier otro caso. Si el IC95 queda entero por debajo de 0, se anota "inferior" como descripcion, sin cambiar las reglas.
- Si hay superior pero el p de Holm de Wilcoxon es >= 0,05, se mantiene "superior" con la nota "aviso: Wilcoxon no confirma". No hay correccion de multiplicidad para el IC95; los dos contrastes primarios se declaran como tales.
- Los secundarios usan la misma regla, etiquetados "exploratorio". No se afirma superioridad general de "la optica" salvo que se cumpla la regla en N1.

## 8. Calculo, coste y plan parcial (sin cambiar el diseno)
- CPU solamente; `torch.set_num_threads(2)`; maximo 2 procesos; sin GPU ni cola.
- Entrenamientos EEGNet: 12 x (50 + 64) = 1368, como la linea optica. FBCSP: coste de segundos por pliegue.
- Estimacion previa, NO medida: ~14 s por entrenamiento EEGNet en CPU con 2 hilos (rango 7-30 s) implica ~0,11 h por pliegue externo (27 entrenamientos), ~5,5 h en un proceso y ~2,7 h con dos procesos (rango 1,4-5,5 h). FBCSP: menos de 5 min en total. La medicion real de un pliegue por metodo se hace antes de lanzar la ejecucion.
- Regla: si el total medido con 2 procesos supera 3 h, no se lanza la ejecucion completa. Plan parcial predeclarado: sujetos completos en orden ascendente de identificador (S001, S002, ...), repartidos alternos entre los dos procesos, hasta agotar 3 h; FBCSP se ejecuta siempre con los 17. Con menos de 17 sujetos de EEGNet, H2 se evalua solo sobre los sujetos completos (la optica restringida a los mismos), se etiqueta "parcial" y no se afirma superioridad en la poblacion de 17.
- Salidas y temporales: `D:\PROJECTS\.cognition\neuro3d-audit\eeg\` (tmp en `tmp\`); resultados, `verificacion.json` y `SHA256SUMS.txt` en `comparativa-anidada\resultados\`.

## 9. Limites declarados
1. Un solo conjunto de datos, 17 sujetos, 8 canales, LORO dentro de sesion (runs de 50/50/10 epocas); sin sujetos ni sesiones nuevas ni datos ciegos. Diferencia minima detectable pareada ~0,03.
2. La rejilla optica se eligio viendo estos mismos LORO y sus resultados (sesgo a favor de la optica); las rejillas de las bases se fijan sin ejecutar pero no estan afinadas por busqueda previa. Presupuesto igual en numero de configuraciones, no en esfuerzo de diseno.
3. La seleccion interna es debil (10 epocas de validacion en 2 de 3 pliegues; 0 pliegues validos en 2 de 50): N1 puede no superar al defecto. Por eso se informan N2 y N3.
4. La rejilla optica incluye `free`, que no es una malla unitaria realizable; una victoria de "la linea optica" no demuestra que lo sea la parte fisica.
5. FBCSP usa regresion logistica en lugar de LDA con contraccion; EEGNet no tiene aumento ni normalizacion especiales. Ninguna de las dos es la mejor posible; la conclusion es sobre estas rejillas.
6. Una semilla por entrenamiento; el ruido de semilla (~0,01) es del orden de las diferencias esperables.
7. La cadena de evidencia temporal se basa en el commit de este archivo, no en sellos externos.
8. No se explica la diferencia entre las cifras de Kaggle y el LORO.

## Decisiones de diseño (consulta a JEV, 2026-10-10)
- Medir un pliegue antes de commitear: no. JEV (provenance=jev), confianza 0,84. El plan parcial cubre la incertidumbre de tiempo.
- FBCSP: regresión logística con C en 9 valores. JEV (provenance=jev), confianza 0,97.
- Rejilla de EEGNet: 36 configuraciones tal como están. JEV (provenance=jev), confianza 0,48, por debajo de 0,6. Desempate por evidencia: 36 es la única rejilla que iguala el presupuesto de búsqueda de la línea óptica; reducirla rompería la equivalencia.
- Plan si el tiempo medido supera 3 h: sujetos completos en orden ascendente hasta agotar el presupuesto, sin cambiar el diseño. FBCSP siempre con los 17 sujetos. JEV (provenance=jev), confianza 1,0.
