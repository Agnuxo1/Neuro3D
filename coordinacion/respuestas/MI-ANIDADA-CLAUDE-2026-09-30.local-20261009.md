# Motor Imagery sin sesgo de selección: validación anidada de los modelos ópticos (Claude, sesión 99ac67, 30/09)

Código y datos: `D:/PROJECTS/neuro3d-kaggle/motor-imagery/work/nested/` (`PREINSCRIPCION.md` fechada 04:05 UTC antes de ejecutar; `nested_bench.py`, `analyze_nested.py`, `results_full.json/.txt`, `INFORME-NESTED.md`). Todo por gpuq. No se ha enviado nada a Kaggle. Etiquetas: HECHO / INFERENCIA / PROPUESTA.

## 1. Diseño (HECHO, preinscrito)

17 sujetos, validación externa *leave-one-run-out* (50 folds), bucle interno también por runs (nunca se comparte un run entre entrenamiento y validación: `test_nested_groups.py full` pasa, 300 disposiciones aleatorias más un test negativo). Rejilla declarada de **36 configuraciones**: modelo {polar, lattice32 (rejilla física de 32 retardos), free (matriz compleja libre)} × características {8 bandas 1 ventana, 12 bandas 3 ventanas} × decaimiento {1e-3, 1e-2} × épocas {30, 60, 90}. 1368 entrenamientos, 4118 s de entrenamiento en la RTX 3090.

Estimadores (todos sobre logits crudos, sin ver el test externo al elegir): **N1** = elegir por sujeto con el bucle interno; **N2** = elegir la configuración global con los otros 16 sujetos (*leave-one-subject-out*); **N3** = la configuración fija actual (polar, 12 bandas × 3 ventanas, 1e-3, 60 épocas); **MAX_LORO** = mejor configuración por LORO medio (sesgado, referencia).

## 2. Resultados (exactitud media por sujeto en el run externo; EE entre sujetos ≈ 0,025)

| Estimador | Exactitud | Lectura |
|---|---:|---|
| N3 defecto (polar f12w3, 1e-3, 60 ép.) | **0,7128** | es exactamente la cifra que ya se informaba (0,713) |
| N1 selección interna por sujeto | 0,7009 | no mejora: N1 − N3 = −0,012 [−0,028; +0,004] |
| N2 configuración global elegida con los otros sujetos | 0,7274 | N2 − N3 = +0,015 [+0,001; +0,028], p = 0,065 (marginal) |
| MAX_LORO (sesgado) | 0,7285 | optimismo MAX − N2 = **+0,001**; MAX − N1 = +0,028 |
| Media de la rejilla | 0,6912 | |

- HECHO: **no se detecta inflado por selección** en las cifras previas de polar (0,713). La configuración global elegida con leave-one-subject-out es la misma en 16 de 17 folds (`free|f12w3|1e-2|90`), lo que indica una elección estable.
- HECHO: **la selección interna por sujeto no ayuda** (Spearman medio entre BCE interna y exactitud externa 0,033; solo el 46 % de los folds positivos): la validación interna dispone de un run de 10 épocas en 2 de 3 folds y es demasiado ruidosa.

## 2b. Métodos estadísticos (para reauditar los 50 folds)
- Datos retenidos: logits crudos externos e internos por sujeto en `work/nested/raw/full/S###.npz`; `python analyze_nested.py --tag full` reproduce `results_full.json/.txt` en segundos; `test_nested_groups.py full` verifica los 64 folds internos guardados (ningún run compartido entre entrenamiento y validación ni con el run externo).
- IC95: bootstrap percentil sobre **sujetos** (17), 20 000 remuestreos con reemplazo, sobre la diferencia **emparejada por sujeto** (media sobre sus folds de la exactitud A − B). Función `boot_ci`, `analyze_nested.py` línea 22.
- p (N2 − N3 = +0,0146, p = 0,065; N1 − N3, p = 0,185): prueba de cambio de signo **Monte Carlo** (20 000 asignaciones aleatorias de signo a las 17 diferencias por sujeto; proporción con \|media\| ≥ la observada); dos colas; no exacta. Wilcoxon emparejado en `bias_inventory.py`. No se ha aplicado corrección por comparaciones múltiples; se leen como descriptivos.
- N2: para cada sujeto se elige la configuración con mayor exactitud LORO media de los OTROS 16 sujetos y se puntúa en el sujeto retenido. N1: por sujeto y fold externo, la configuración de menor BCE en el bucle interno (2 de 50 folds sin bucle válido usan la configuración por defecto). N3: configuración fija actual.

## 3. Qué importa de verdad (efectos marginales, medias sobre toda la rejilla; diferencias pareadas por sujeto)

| Factor | Efecto | IC95 | Sujetos a favor / en contra |
|---|---:|---|---|
| 12 bandas × 3 ventanas frente a 8 bandas × 1 ventana | **+0,025** | [+0,010; +0,041] | 13 / 4 |
| 60 épocas frente a 30 | **+0,018** | [+0,010; +0,026] | 16 / 1 |
| 90 épocas frente a 30 | +0,018 | [+0,010; +0,026] | 15 / 2 (60 ≈ 90) |
| Decaimiento 1e-2 frente a 1e-3 | +0,0006 | [−0,0007; +0,0020] | sin efecto |
| Familia: free frente a polar | +0,013 | [+0,008; +0,018] | 15 / 2 |
| Familia: free frente a lattice32 | +0,025 | [+0,010; +0,040] | 14 / 3 |

Mejor configuración por familia (LORO, todas con 12 bandas × 3 ventanas, 1e-2, 90 épocas): **free 0,7285**, **polar 0,7188**, **lattice32 0,6953**. Anterior: polar 0,7128 (60 ép.) y lattice32 0,687.

## 4. Lectura honesta

- Hay dos mejoras reales y sencillas: más bandas y ventanas, y no parar antes de 60 épocas. Todo lo demás (decaimiento, selección por sujeto) es ruido con 17 sujetos.
- Entre modelos, la matriz compleja libre supera a la malla unitaria (polar) en ~0,013 y a la rejilla física de 32 retardos en ~0,025. **INFERENCIA:** la restricción física (unitariedad; solo 32 retardos) cuesta 1 a 2,5 puntos de exactitud en esta tarea; no es un hallazgo sobre óptica real (`free` no es realizable sin pérdidas con una malla pasiva sencilla).
- Diferencia mínima detectable con 17 sujetos ≈ 0,03: comparaciones menores no se resuelven con estos datos.
- Puntuación pública de referencia (Kaggle): libre 0,77, polar f12w3 0,74, rejilla32 f12w3 0,72. La pública es sistemáticamente mayor que LORO (entrena con los 3 runs y 5 semillas); no son comparables en valor absoluto.

## 5. Exploratorio (sin reentrenar, no usado para decidir)

- Conjunto por promedio de logits: polar + lattice32 0,7101; + free 0,7227 (no mejora al mejor modelo individual).
- Umbral en la mediana del logit en folds equilibrados: 0,7358 frente a 0,7106 con umbral 0. Es **transductivo** (usa la distribución de los logits del propio conjunto evaluado); antes de aplicarlo al test de Kaggle habría que comprobar si las reglas de la competición lo permiten y si el test está equilibrado. No se aplica.

## 6. Propuesta para Kaggle (decide Fran; no se envía nada sin aviso; próximo cupo ≥ 01/10 00:00 UTC)

Los ficheros de predicción con la configuración elegida se están generando por gpuq (`work/submission_<modelo>_f12w3_e90_wd0.01.csv`, 5 semillas, entrenamiento con los 3 runs):
1. **polar 12 bandas × 3 ventanas, 90 épocas, 1e-2** (malla unitaria física, LORO 0,7188; +0,006 sobre la actual: dentro del ruido).
2. **rejilla de 32 retardos, mismo ajuste** (física y construible en Blender, LORO 0,6953).
3. Alternativa no física: matriz libre con el mismo ajuste (LORO 0,7285), la mejor por LORO y la más cercana a la mejor pública (0,77 con 8 bandas).
Si el objetivo es puntuar más, la 3; si es demostrar modelos ópticos físicos, la 1 (y la 2, ya verificada en escena de Blender). Con 2 envíos al día, propongo 1 y 3, o 1 y 2 si se quiere solo óptica física.

## 7. Anexo POST-HOC (declarado antes de ejecutar en `work/nested/ADDENDUM-SEEDS5.md`): promedio de 5 semillas de los tres finalistas
LORO externo (17 sujetos, 50 folds) con logits promediados sobre 5 semillas, configuración 12 bandas × 3 ventanas, 1e-2, 90 épocas (tag `seeds5`, `results_seeds5.json`):
| Finalista | 1 semilla | 5 semillas | Diferencia |
|---|---:|---:|---:|
| polar | 0,7188 | 0,7113 | −0,0074 |
| rejilla de 32 retardos | 0,6953 | 0,7047 | +0,0094 |
| matriz libre | 0,7285 | 0,7299 | +0,0015 |
- H1 (promediar mejora ≥ 0,005 a cada finalista): **refutada** para polar y libre; rejilla +0,0094, dentro del ruido (diferencia mínima detectable ≈ 0,03).
- H2 (el conjunto de logits no supera al mejor individual): **confirmada**: polar+rejilla 0,7132; polar+rejilla+libre 0,7184, frente a libre sola 0,7299.
- Con 5 semillas, polar (0,7113) y rejilla física (0,7047) no se distinguen; la matriz libre sigue siendo la mejor (+0,019 sobre polar, IC95 [+0,004; +0,033], p = 0,030 por cambio de signo Monte Carlo).
- Exploratorio y transductivo (no aplicado): umbral en la mediana de los logits del propio fold, 0,7555 frente a 0,7112 con umbral 0.
Advertencia: los tres finalistas se eligieron mirando el LORO de 1 semilla, así que estas cifras no son una estimación limpia del test oculto.
