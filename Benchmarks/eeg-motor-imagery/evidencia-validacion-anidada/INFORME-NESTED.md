# Motor Imagery sin sesgo de seleccion: inventario, protocolo anidado, ideas, coste y humo

Fecha: 2026-09-30 ~04:15 UTC. Autor: subagente Claude (tarea "nested"). Carpeta: `D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/`.
No se ha modificado `bench.py`, `predict.py`, `lattice_torch.py` ni `prep.py`. No se ha usado GPU ni Blender; no se ha enviado nada a Kaggle.
HECHO = reproducido con el comando indicado. INFERENCIA/PROPUESTA = marcado. Lo que no pude comprobar esta en la seccion 8.

## 1. Inventario de decisiones tomadas mirando el LORO (o el CV interno)

| # | Decision | Que se miro | Configs comparadas | Fuente |
|---|---|---|---|---|
| D1 | Pasar de CV aleatorio 5x3 estratificado a LORO | 5x3: fbcsp 0,733; optic 0,736; free 0,764; polar 0,760 frente a LORO 0,653/0,669/0,697/0,682 (el CV aleatorio mezcla epocas de un mismo run: inflado ~0,06-0,08) | 1 (metodologica, correcta) | `bench_run1.log`, `bench_loro.log` |
| D2 | Familia de modelo | 8 modelos en 5x3 (fbcsp, optic, free, eegnet, optic16r8, optic16r16, opticsvd, polar) y luego 9 en LORO (fbcsp, optic, polar, free, eegnet, lattice, spectral, lattice32 en f8w1; polar y lattice32 en f12w3) | ~10 pares (modelo, features) puntuados en LORO, 9 con datos por sujeto | `bench_*.json` |
| D3 | `polar` (descomposicion polar) creado tras ver optic/free; `lattice`->`lattice32` (+16 enlaces) tras ver lattice 0,663 y spectral 0,588 | LORO/5x3 | 2 disenos nuevos guiados por resultado | `bench_lattice_*_loro.json` |
| D4 | Features: 8 bandas/1 ventana -> 12 bandas (6..35 Hz)/3 ventanas | LORO polar 0,682 -> 0,713 y lattice32 0,677 -> 0,687 | 1 cambio conjunto (bandas y ventanas a la vez, sin separarlos), solo para polar y lattice32 (no para free/optic) | `bench_f12w3.log` |
| D5 | Hiperparametros: 60 epocas, lr 2e-2, wd 1e-3, batch 32, ncyc 5, paso 5 | Sin rastro de ajuste en los registros (fijos desde el primer `bench.py`) | 0 documentadas (INFERENCIA: pudo haber pruebas no registradas) | `bench.py:train_torch` |
| D6 | Que enviar a Kaggle | LORO y ademas la tabla publica: libre f8w1 0,77; polar f8w1 0,72; polar f12w3 0,74; lattice32 f12w3 0,72 | 4 envios (canal de seleccion adicional: la tabla publica) | CHECKPOINT-CLAUDE, Cierre sesion 2 |
| D7 | `predict.py`: 5 semillas y entrenamiento con los 3 runs | No ajustado. Nota: el LORO usa 1 semilla y 2 de 3 runs; los envios usan 5 semillas y 3 runs | 0 | `predict.py` |

Recuento: unos 10 pares (modelo, features) vistos en LORO, ~8 en 5x3, 4 envios evaluados en la tabla publica y 2 disenos nuevos guiados por resultado.
Los registros no muestran otras variantes de FREQS/WIN, pero los JSON se sobrescriben con el mismo nombre si se relanza sin `TAGX`; no puedo excluir pruebas sin registrar.

Nota de la estructura de runs (HECHO, `np.load('data/S###.npz')['run']`): 3 runs de 50/50/10 epocas; los runs 1 y 2 estan equilibrados 25/25, el run 3
tiene solo 2-8 'move' de 10 (desequilibrado; su prior cambia). S006: 25/50/10. S007: solo runs 1 y 3 (50/10). El test oculto son 40 epocas por sujeto.
Esto tiene tres consecuencias: (i) el LORO externo tiene 50/50/10 epocas de test por sujeto; (ii) el bucle interno de 2 de cada 3 folds valida en solo 10 epocas;
(iii) S007 no tiene bucle interno posible.

### 1.1 Cuanto de 0,713 frente a 0,687 es distinguible del ruido
HECHO (`python bias_inventory.py`; `bias_inventory.json`; bootstrap por sujetos 20 000 remuestreos, permutacion de signos, semilla 20260930), n = 17 sujetos:

| Contraste (emparejado por sujeto) | Diferencia | EE | IC95% | p sign-flip / Wilcoxon | victorias/empates/derrotas |
|---|---|---|---|---|---|
| polar f12w3 - lattice32 f12w3 (0,7128 - 0,6872) | +0,0256 | 0,0115 | [+0,003, +0,046] | 0,044 / 0,055 | 13/0/4 |
| polar f12w3 - polar f8w1 (0,7128 - 0,6822) | +0,0306 | 0,0101 | [+0,012, +0,050] | 0,007 / 0,011 | 12/2/3 |
| lattice32 f12w3 - lattice32 f8w1 | +0,0101 | 0,0135 | [-0,015, +0,036] | 0,47 / 0,66 | 9/1/7 |
| polar f12w3 - free f8w1 (0,6968) | +0,0160 | 0,0111 | [-0,005, +0,037] | 0,18 / 0,19 | 11/3/3 |
| polar f8w1 - free f8w1 | -0,0146 | 0,0066 | [-0,027, -0,002] | 0,045 / 0,038 | 5/2/10 |
| polar f12w3 - fbcsp | +0,0602 | 0,0182 | [+0,026, +0,095] | 0,004 / 0,008 | 13/2/2 |
| polar f12w3 - eegnet | +0,0855 | 0,0288 | [+0,031, +0,141] | 0,010 / 0,011 | 12/1/4 |

Errores estandar de una media LORO entre sujetos: 0,019-0,027 (polar f12w3 0,026; lattice32 f12w3 0,019). EE binomial de una exactitud agrupada sobre 1795 epocas (p=0,7): 0,011.

Lectura (marcada como INFERENCIA salvo las cifras de arriba):
- La mejora de features en polar (+0,031) es la unica diferencia solida: IC95% lejos de 0, 12 de 17 sujetos mejoran y sobrevive incluso a una correccion de 2-3 comparaciones (p~0,007 x 3 = 0,02).
- La diferencia polar - lattice32 (+0,026) es marginal: IC95% [+0,003, +0,046], p~0,05. No sobrevive a Bonferroni si ademas se cuentan las otras comparaciones entre familias (aqui al menos 3-4). No es distinguible del ruido con esta muestra; solo se puede decir "polar >= lattice32 probablemente, tamano entre 0 y 0,046".
- Diferencia minima detectable con 17 sujetos y EE emparejado ~0,011-0,015: ~2,8 x EE = 0,03-0,04 (80% de potencia, alfa 0,05). Diferencias < 0,03 entre variantes no se pueden resolver con estos datos, ni con 17 sujetos en LORO en general.
- Free f8w1 (0,697) no es peor que polar f12w3 (+0,016, IC95% que incluye 0), y free nunca se probo con f12w3. En la tabla publica free f8w1 (0,77) supero a polar f12w3 (0,74): coherente con que la ventaja de polar sobre free no esta establecida.
- Maldicion del ganador por bootstrap de sujetos (elegir el mejor de K candidatos en los sujetos in-bag y medirlo en los OOB; `bias_inventory.py`): optimismo medio +0,002 (K=9) a +0,004 (K=6), con p5..p95 de -0,09 a +0,10. Es HECHO como calculo, pero su lectura es limitada: como polar f12w3 gana en casi todos los remuestreos (91-100%), no mide el sesgo de que la rejilla ya estaba informada por estos mismos sujetos ni el ruido de semilla/epocas. Conclusion: el sesgo por elegir el mejor de ~9 candidatos ya vistos no es detectable con estos datos; su cota realista es 0-0,03 (INFERENCIA: 0,5-1 EE del contraste entre el ganador y sus rivales cercanos, ~0,006-0,015, mas el ruido de semilla no medido). Lo mide directamente MAX_LORO - N2 de la validacion anidada.

## 2. Diseno de la validacion anidada (preinscrita en `PREINSCRIPCION.md`, 2026-09-30 04:05 UTC, antes de cualquier ejecucion `full`)

- Externo: LORO por sujeto (identico a `bench.py`, semilla = indice de fold). Interno: LORO interno con grupo = `run` dentro del entrenamiento externo; fold interno valido si train >= 20 y val >= 10 epocas. Resultado con la estructura real: 1 fold interno cuando el run externo es el 1 o el 2 (entrenar con el otro run grande, validar en el run 3), 2 cuando es el 3, 0 en S007 (usa el defecto). En total 64 folds internos y 2 de 50 folds externos sin bucle interno (HECHO: `test_nested_groups.py`).
- Rejilla declarada (36 configs = 12 entrenamientos x 3 instantaneas de epoca): modelo {polar, lattice32, free} x features {f8w1, f12w3} x wd {1e-3, 1e-2} x epocas {30, 60, 90}. Las epocas son gratis: la trayectoria (AdamW, lr constante, semilla fija) es identica hasta cada epoca (HECHO: `fit_snapshots` == `bench.train_torch` a 3 y 6 epocas, y las instantaneas 3/6 == entrenar 3 y 6 por separado).
- Estimadores (todos en `analyze_nested.py` sobre logits crudos, asi la eleccion no puede ver el test externo):
  - N1 (primario): por sujeto y fold externo, la config con menor BCE interna; reentrenar con todo el entrenamiento externo y puntuar en el run externo.
  - N1b: igual con exactitud interna. N2 (primario): la config con mayor LORO medio en los otros 16 sujetos (leave-one-subject-out; no depende del ruido de validar en 10 epocas).
  - N3: referencia fija `polar|f12w3|1e-3|60` (la actual; su cifra esta contaminada, no es "a priori limpio"; el sustituto limpio es N2).
  - Sesgadas de referencia: MAX_LORO (mejor config por LORO medio), MEAN_over_grid, ORACLE por sujeto. Optimismo = MAX_LORO - N2 y MAX_LORO - N1.
  - Contrastes emparejados por sujeto con IC95% bootstrap: N1-N3, N2-N3, N1-N2, N1-MEAN, N3-MEAN. Efectos marginales por dimension. Diagnostico: Spearman medio (BCE interna vs exactitud externa) por fold. Frecuencia de eleccion por config y por nivel.
  - Exploratorios (sin reentrenar): E1/E2 conjuntos de logits; T1 umbral en la mediana.
- Criterio de decision: "seleccion interna util" solo si N1-N3 > 0 con IC95% que excluya 0 y Spearman medio < 0. Un cambio para Kaggle debe salir de N2 (o N1 si es significativa), no de MAX_LORO.
- Sesgo residual declarado: la rejilla contiene f12w3, que se eligio despues de ver LORO. La anidacion quita el sesgo de elegir dentro de la rejilla, no el de haber definido la rejilla. El control limpio es el test oculto.
- Limitacion estructural (HECHO en la estructura de runs): con 10 epocas de validacion en 2 de cada 3 folds, N1 tendra poca potencia. Se espera que N1 se parezca a "una config aleatoria de la rejilla ponderada por un poco de senal"; por eso N2 es el estimador principal para decidir la config global, y N1 es la respuesta a "vale la pena personalizar por sujeto".

## 3. Scripts (todos en `nested/`)
- `bias_inventory.py` (+ `bias_inventory.json`): inventario numerico, IC pareados, maldicion del ganador. Segundos en CPU.
- `nested_bench.py`: entrena y guarda logits externos/internos por sujeto en `raw/<tag>/S###.npz` (reanudable: omite sujetos ya hechos). Opciones: `--grid {full,smoke}`, `--dev cpu|cuda`, `--subjects all|S001,S002`, `--shard i/n`, `--no-inner`, `--seeds n` (promedio de logits externo), `--norm train|run`, `--force`.
- `analyze_nested.py --tag <tag>`: estimadores, contrastes, frecuencias, marginales, E1/E2, T1 -> `results_<tag>.json/.txt`.
- `test_nested_groups.py [tag]`: pruebas de particion (datos reales, 300 layouts aleatorios, test negativo, indices guardados) y fidelidad frente a `bench.train_torch`.
- `time_cpu_probe.py`: tiempo de un entrenamiento de 90 epocas por (modelo, features) en CPU.
- `PREINSCRIPCION.md`: rejilla y estimadores con fecha.

## 4. Ideas de mejora baratas, respetando los modelos opticos y sin el test oculto
Todas se puntuan con el mismo LORO externo y contrastes emparejados por sujeto; ninguna toca el test de Kaggle. "Coste" en unidades de "un LORO externo de una config" = 3 entrenamientos por sujeto.

| Idea | Hipotesis | Refutacion (resultado que la mata) | Coste / estado |
|---|---|---|---|
| I1 Promedio de 5 semillas | El ruido de la inicializacion aleatoria (theta/phi/A y readout) es parte notable del error por sujeto; promediar logits sube la exactitud +0,005-0,02. INFERENCIA relacionada: `predict.py` ya usa 5 semillas y los 3 runs, el LORO usa 1 semilla y 2 runs; eso puede explicar parte de que la tabla publica (0,72-0,77) quede por encima del LORO (0,68-0,71). | LORO con `--seeds 5` menos LORO con 1 semilla: IC95% incluye 0, o < +0,005. | 5x un LORO externo por config; implementado (`--seeds`). |
| I2 Regularizacion: wd | Mas decaimiento de pesos generaliza mejor entre runs. | Efecto marginal wd 1e-2 - 1e-3 con IC95% que incluye 0 (en la rejilla). | Dentro de la rejilla `full`. |
| I2b Dropout de bandas / ruido de fase | Descartar bandas enteras o perturbar las fases de la malla en entrenamiento hace el modelo robusto a la deriva de fase/amplitud entre runs. | Diferencia LORO emparejada frente a la base con IC95% que incluye 0 en las 2-3 intensidades preinscritas. | NO implementado (requiere subclase de `Optic/LatticeNet` con `forward` propio); ~1 LORO externo por intensidad. Preinscribir antes. |
| I3 Early stopping por validacion interna | El numero optimo de epocas depende del sujeto/run; elegirlo con validacion interna supera fijar 60. | Frecuencia de eleccion de epocas ~uniforme y N1 - N3 <= 0; o efecto marginal de epocas plano. | Dentro de la rejilla (epocas 30/60/90 gratis). |
| I4 Calibracion por sujeto (prior/umbral) | El error tiene un componente de desplazamiento de prior (runs 1-2 equilibrados 25/25 pero run 3 desequilibrado; las predicciones 'move' del test oculto van de 0,28 a 0,85 por sujeto en `predict_*.log`). Si el test oculto esta equilibrado, umbral en la mediana de logits mejora. | En folds externos exactamente equilibrados, exactitud con umbral mediana - exactitud con umbral 0: IC95% que incluye 0 o negativa. El equilibrio del test oculto NO se puede comprobar sin etiquetas (solo un envio lo revelaria). | T1 en `analyze_nested.py`, sin reentrenar; barato. |
| I5 Normalizacion por sujeto/sesion | La amplitud del EEG deriva entre runs; escalar cada run con su propia std (sin etiquetas, transductivo) reduce el fallo de generalizacion entre runs. | LORO(`--norm run`) - LORO(`--norm train`): IC95% que incluye 0 o < 0. Hay que comprobar que el test oculto es una sesion unica para aplicar lo mismo. | Implementado (`--norm run`, humo ejecutado sin errores); 1 LORO externo de 1-3 configs. |
| I6 Conjunto polar + lattice32 (ambos fisicos) | Los errores de polar y lattice32 no estan totalmente correlados; la media de logits >= mejor de los dos. | E1 - N3: IC95% incluye 0 o E1 < N3. INFERENCIA: lattice32 es un subconjunto restringido de la malla unitaria, asi que sus errores pueden ser muy parecidos y la ganancia, pequena. | E1/E2 de `analyze_nested.py` sin reentrenar (config por defecto). |
| I7 Seleccion de bandas por validacion interna | Algunas de las 12 bandas (p. ej. 6 y 35 Hz) son ruido; quitarlas o penalizar (L1 por grupo en los pesos del lector) mejora. | LORO con subconjunto/penalizacion - f12w3: IC95% que incluye 0. La rejilla ya lo mide de forma gruesa (f8w1 frente a f12w3). | NO implementado; L1 por banda en `out.weight` es un cambio de una linea en una subclase; preinscribir. |
| I8 Incluir `free` con f12w3 | `free` (matriz compleja) rinde >= polar cuando tambien tiene 12 bandas y 3 ventanas (free f8w1 ya rendia 0,697 frente a 0,682). | free f12w3 - polar f12w3: IC95% en negativo. | Dentro de la rejilla `full`. |

Orden recomendado (mayor valor esperado / menor coste): I1 -> I8 -> I4 -> I5 -> I6 -> I3 -> I2/I7.

## 5. Coste y plan escalonado
Base de medida (HECHO): `bench_f12w3.log`: LORO completo polar + lattice32 en GPU, 17 sujetos, 335 s = 100 entrenamientos de 60 epocas (3,35 s/entrenamiento). Mi sonda CPU (4 hilos, `time_cpu_probe.py`, 90 epocas, 100 epocas de entrenamiento): polar 7,3 s, free 4,7 s, lattice32 11,5 s (f8w1/f12w3 similares, `time_cpu_probe.json`). Para un LORO polar + lattice32 f12w3 equivalente la CPU necesita ~9,3 s por fold frente a 6,7 s de la GPU, es decir la GPU es solo ~1,4x mas rapida que 4 hilos de CPU (INFERENCIA de dos mediciones; el trabajo es de lanzamientos pequenos, no de calculo).

Extrapolacion (INFERENCIA, no medida en GPU):
- Por sujeto (3 folds, tamanos de entrenamiento externo 60/60/100): externo 36 entrenamientos ≈ 207 s CPU; interno 24-28 entrenamientos con tamanos 50/50/100 ≈ 188 s CPU. S007: 56 s externo, 0 interno.
- Total rejilla completa (externo + interno, 17 sujetos): ≈ 6 400 s CPU-4-hilos ≈ 1,8 h; en GPU secuencial ≈ 4 500 s ≈ 1,3 h. En 4 procesos GPU en paralelo (`--shard i/4`, cada proceso ~1 nucleo y < 2 GB de VRAM): ≈ 20-30 min de reloj si hay >= 4 nucleos libres (el escalado en paralelo NO esta medido; el PC lo comparte Codex).
- Solo externo (`--no-inner`, 600 entrenamientos): ≈ 3 400 s CPU; ≈ 2 400 s GPU secuencial; ≈ 10-12 min con 4 shards.
- Version escalonada:
  1. Etapa 1 (opcional): `--no-inner` con los 17 -> N2, N3, MAX, marginales, tabla de 36 configs, T1, E1/E2. ~10-12 min con 4 shards.
  2. Etapa 2: rejilla completa con bucle interno en S001-S005 (fijados por identificador, sin mirar rendimiento): ≈ 2 000 s GPU secuencial, ≈ 7-10 min con shards. Da el primer N1, el coste real y el diagnostico de Spearman.
  3. Etapa 3: los 12 sujetos restantes (≈ 15-20 min con 4 shards).
  4. Etapa 4 (ideas): I1 (5 semillas, 3 configs finalistas, ~15 LORO externos ≈ 20 min con shards), I5 (1-3 configs).
- Comandos (los lanza Claude principal; NO los he ejecutado). `--vram 2 --ram 6` por shard como valor prudente (INFERENCIA, no medido en GPU):
  ```
  python D:/PROJECTS/.cognition/gpu_queue/gpuq.py status
  # Etapa 2 (5 sujetos, 4 shards)
  for i in 0 1 2 3; do python D:/PROJECTS/.cognition/gpu_queue/gpuq.py run --name "neuro3d:mi-nested-A$i" --vram 2 --ram 6 -- python D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/nested_bench.py --grid full --tag full --dev cuda --subjects S001,S002,S003,S004,S005 --shard $i/4 ; done
  # Etapa 3 (todos; omite los ya hechos)
  for i in 0 1 2 3; do python D:/PROJECTS/.cognition/gpu_queue/gpuq.py run --name "neuro3d:mi-nested-B$i" --vram 2 --ram 6 -- python D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/nested_bench.py --grid full --tag full --dev cuda --subjects all --shard $i/4 ; done
  python D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/analyze_nested.py --tag full
  python D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/test_nested_groups.py full
  ```
  (cada `run` con `run_in_background`; la cola solo arranca con GPU/VRAM/RAM libres.) Nota: con `--shard i/4` sobre 5 sujetos un shard se queda sin trabajo; en la Etapa 3 el reparto es por indice del listado completo.

## 6. Prueba de humo (HECHA, CPU 4 hilos, sin GPU)
Comandos exactos (desde `nested/`, `TORCH_THREADS=4 OMP_NUM_THREADS=4 PYTHONIOENCODING=utf-8`):
```
python nested_bench.py --grid smoke --tag smoke --dev cpu --subjects S001,S007 --force
python analyze_nested.py --tag smoke
python test_nested_groups.py smoke
python time_cpu_probe.py
```
Resultados (logs en `smoke_logs/`, salida en `raw/smoke/`, `results_smoke.json/.txt`):
- Corre de extremo a extremo: 2 sujetos, rejilla minima de 6 triples (polar, free, lattice32 x f8w1, f12w3; wd 1e-3; instantaneas de 2 y 4 epocas), 54 entrenamientos en 14 s; S001 con folds internos [1, 1, 2], S007 sin folds internos (usa el defecto).
- `test_nested_groups.py smoke` -> "TODOS LOS TESTS OK": (a) 17 sujetos reales: en ningun fold interno un run se comparte entre train y val, el run externo de test nunca aparece en el bucle interno, el val interno es un run completo y el interno cubre exactamente el entrenamiento externo (64 folds internos; S007 y solo S007 tiene 0); (b) 300 disposiciones aleatorias de 1-6 runs con epocas entrelazadas: idem; (c) test negativo: una validacion que mezcla runs se detecta; (d) los 4 folds internos guardados en `raw/smoke` cumplen lo mismo; (e) fidelidad: `fit_snapshots` reproduce `bench.train_torch` exactamente en CPU y las instantaneas de epoca coinciden con entrenar esas epocas por separado.
- Las exactitudes del humo (~0,49-0,52, N1 = N2 = N3 = 0,4917) NO significan nada: 2-4 epocas y 2 sujetos. Solo demuestran que el codigo corre.
- `--norm run` se ejecuto en S002 sin errores (el resultado no se conserva ni se interpreta).
- No probado: ejecucion en GPU (`--dev cuda`), ni el escalado con varios procesos, ni `--seeds 5`. `analyze_nested.py` con n = 1 sujeto da NaN en N2 (esperado, no es un caso de uso).

## 7. Que hacer con Kaggle (PROPUESTA, sin enviar nada)
- Hasta tener N2/N1, no cambiar de modelo con diferencias menores de ~0,03 en LORO. Los envios de hoy (2) ya estan usados.
- Manana: si la Etapa 1-3 confirma que `polar|f12w3` (o el que salga en N2) es la config global, reentrenar con 5 semillas y los 3 runs (como `predict.py`) y enviar 1 modelo optico (polar) y 1 alternativo (`free f12w3` si N2/I8 lo favorece) informando antes a Fran.
- I4 (umbral en la mediana) solo tiene sentido si T1 sale positivo; un envio unico lo pondria a prueba en el test oculto (INFERENCIA: si el test esta equilibrado).

## 8. Lo que no pude comprobar
- Que no hubo otras variantes de FREQS/WIN o hiperparametros lanzadas sin registro (JSON sobrescritos).
- El tiempo real en GPU y el escalado con varios procesos (tengo prohibida la GPU); la razon GPU/CPU ~1,4x sale de dos mediciones distintas.
- Si el test oculto de Kaggle esta equilibrado o es una sola sesion (las ideas I4 e I5 dependen de ello).
- La cifra N1/N2 real: la validacion anidada esta preparada y probada, pero no ejecutada en su escala (no autorizado a usar GPU ni trabajos >5 min).
- La rejilla se define conociendo los LORO previos (seccion 2, sesgo residual).
