# Informe de ejecucion P2-10 (escala a 64 modos)

Ejecucion 2026-10-09/10 sobre CPU, sin GPU, Blender ni cola GPU. Versiones: Python 3.13.7, numpy 2.2.6, scipy 1.15.1, scikit-learn 1.4.0. Preregistro (`PREREGISTRO-P2-10.md`) sin editar.

## Que se ejecuto

- `malla.py`: malla de Clements por capas (N capas, N(N-1)/2 MZI, dos fases cada uno; N=64: 2016 MZI, 4032 fases) y matriz densa de referencia (ruta independiente: embebe cada 2x2 y multiplica).
- `gradiente.py`: perdida softmax sobre P/T y gradiente analitico por retropropagacion de Wirtinger (version rapida, contrastada con una version de referencia mas simple).
- `datos.py`, `ejecutar.py`, `analisis.py`, `sumas.py`: particiones, entrenamiento, lineas base, escala, analisis, sumas SHA-256.
- 10 particiones estratificadas 80/20 (semillas 20261009+k; 1437/360), 3 semillas de fases (0,1,2) = 30 entrenamientos de la malla N=64, Adam 2000 pasos, lr 0,01, T=0,05, lote completo. Semilla elegida por perdida de entrenamiento.
- Logistica multinomial y MLP(48) por particion; escala N=8,16,32,64.
- `Blender/tests/test_escala_modos.py`: 6 pruebas rapidas (pasan).

## Verificacion V (implementacion)

Capas frente a densa, N=2..8, 5 semillas cada una: diferencia maxima 5,0e-15 (< 1e-12). Unitariedad: error maximo 3,1e-15. Recuento de MZI = N(N-1)/2 correcto. `resultados/verificacion.json`.

## Gradiente

Frente a diferencias finitas centrales (h=1e-6), error relativo en norma: N=8 con 8 detectores 1,2e-9; N=8 con 4 detectores 7,1e-10; N=4 9,7e-10; N=64 (60 fases al azar) 1,6e-8. Criterio < 1e-6: cumplido. Version rapida frente a referencia: diferencia maxima < 1e-15. `resultados/verificacion_gradiente.json`. N=8 usa 8 detectores (no caben 10 en 8 modos).

## H3 (digits, N=64)

| Modelo | Exactitud media de prueba | DE |
|---|---|---|
| Malla N=64 | 0,9492 | 0,0124 |
| Logistica | 0,9394 | 0,0113 |
| MLP 48 | 0,9736 | 0,0091 |

Malla - logistica: +0,0097, IC95 bootstrap [+0,0053, +0,0147]; Wilcoxon bilateral p = 0,0059 (exacto con rangos medios, hay empates en |d|; aproximacion normal p = 0,0078). Criterio (diferencia >= -0,01 e IC95 inferior >= -0,03): **H3 soportado como no inferioridad frente a la logistica con la regularizacion original; no como superioridad.** La malla gana en 9 de 10 particiones, pero las 10 particiones 80/20 se solapan y el bootstrap y el Wilcoxon las tratan como independientes. Con la correccion de Nadeau-Bengio (varianza x (1/10 + 360/1437)): IC95 [-0,001; +0,020], p = 0,07 (`sensibilidad/nadeau_bengio.py`, `sensibilidad/resultados_nadeau_bengio.json`). La no inferioridad se mantiene (-0,001 >= -0,03); la superioridad no esta establecida. H3 ademas depende de la regularizacion de la logistica (siguiente seccion). Control malla - MLP (sin criterio): -0,0244, IC95 [-0,0300, -0,0181], Wilcoxon p = 0,0020. La malla queda por debajo del MLP. Exactitud de entrenamiento media de la malla elegida: 0,964 (no sobreajusta mucho, pero tampoco converge del todo: la perdida sigue bajando a los 2000 pasos).

## Sensibilidad a la regularizacion de la logistica

Resumen de `sensibilidad/resultados_sensibilidad.md` (mismas exactitudes de la malla; solo cambia la logistica; no preregistrado):

| Variante | Logistica | Dif. malla - logistica | IC95 | Wilcoxon p | H3 |
|---|---|---|---|---|---|
| Original (L2 = 0,001, C ~ 0,696) | 0,9394 | +0,0097 | [+0,0053, +0,0147] | 0,0059 | soportado |
| (a) C = 1,0 | 0,9458 | +0,0033 | [+0,0000, +0,0067] | 0,1367 | soportado |
| (b) C por validacion interna (5 pliegues) | 0,9703 | -0,0211 | [-0,0286, -0,0128] | 0,0078 | no soportado |

En (b) la logistica gana en 8 de 10 particiones y empata en 2 (la malla no gana ninguna). **Conclusion: H3 depende de la regularizacion de la logistica.** La ventaja de la malla desaparece con C = 1 y se invierte con C elegido por validacion (C = 100 en 9 particiones, 10 en una). La logistica original estaba sobrerregularizada.

## H2 (escala)

Tiempo por entrada (mediana de 7 repeticiones de 1000 evaluaciones individuales tras 100 de calentamiento, particion 0, fases al azar):

| N | tiempo (us) | memoria coeficientes (B) | matriz densa (B) |
|---|---|---|---|
| 8 | 57,4 | 1792 | 1024 |
| 16 | 114,1 | 7680 | 4096 |
| 32 | 230,2 | 31744 | 16384 |
| 64 | 488,8 | 129024 | 65536 |

- Pendiente log-log del tiempo por entrada: **1,03**, IC95 [0,96; 1,09] (t con 2 gl, R2 0,9995). Fuera de [1,8; 2,2]: **H2 no se cumple tal como esta preregistrada** para la evaluacion individual. Interpretacion (hipotesis, **causa no establecida**): el t/N casi constante (7,2; 7,1; 7,2; 7,6 us por capa) es compatible con un sobrecoste fijo de Python/numpy por capa (N llamadas por entrada, que crece como N), pero no lo demuestra. Diagnostico (`sensibilidad/diagnostico_capas.py`, N=64, mismas llamadas con 1 MZI por capa en vez de 32): coste fijo por capa de 35 a 94 % segun la ejecucion y la carga de la maquina; no concluyente como causa unica. Tres ejecuciones mias en la maquina cargada dieron 35-60 % (16 s cada una) y una medicion del auditor dio 94 % (588 us frente a 624 us); la dispersion es ruido de carga, no una medida estable.
- Exploratorio (no preregistrado): tiempo por entrada en lote de 1000 entradas: pendiente 2,46, IC95 [1,70; 3,22]. Que la aritmetica domine o que haya efectos de cache en el salto N=32 a 64 (11,7 a 102 us) no esta medido; el lote copia el array en cada capa, luego puede estar limitado por memoria. No es una confirmacion limpia de N^2.
- Coste frente a la matriz densa: la evaluacion por capas es unas 180 veces mas lenta que la matriz densa (N=64: matvec denso 2,7 us frente a 489 us por capas) y los coeficientes ocupan el doble de memoria (129 024 B frente a 65 536 B). La representacion por capas no ahorra tiempo ni memoria en evaluacion. H2 es mixta: el tiempo no sigue N^2, el almacenamiento si. En mi reejecucion el factor fue ~230-350 (maquina cargada; comprobacion del auditor).
- Memoria: coeficientes pendiente 2,06 (IC95 [2,00; 2,11]) y matriz densa 2,00. El almacenamiento si crece como N^2.
- El IC con 4 puntos y 2 grados de libertad es amplio y supone residuos normales.

## Tiempos de CPU por entrenamiento (para P1-9)

30 entrenamientos de la malla N=64 (2000 pasos, 1437 muestras, lote completo): CPU minima 475 s, mediana 710 s, media 798 s, maxima 1441 s, total 23 955 s. La dispersion viene de la carga de la maquina compartida (3 trabajadores en paralelo y otros procesos); el tiempo depende de la franja horaria, no de la semilla (tercetos de 475 s a las 22:41 y de 1439 s a las 00:26). El minimo observado, 475 s (0,24 s/it), ya incluye 3 trabajadores. Logistica y MLP: segundos por particion (en `resultados_raw.json`).

## Lineas base y avisos

- Logistica: 650 parametros, lbfgs, 93-105 iteraciones, sin avisos. "L2 = 0,001" se interpreto como objetivo CE media + (0,001/2)||W||^2, es decir C = 1/(0,001 n_train) en sklearn.
- MLP: 3610 parametros. **Las 10 particiones alcanzan max_iter=500 y emiten aviso de no convergencia** (registrado). Se reporta tal cual. Con max_iter = 5000 el MLP converge y su exactitud no cambia (0,9733); malla - MLP pasa de -0,0244 a -0,0242 (comprobacion del auditor, no guardada en el repo).

## Desviaciones y limites

- Interpretaciones propias donde el preregistro no concreta: lote completo en Adam; L2 de la logistica como arriba; inicializacion de fases uniforme en [0, 2pi); sin recorte de la prueba tras min-max; MZI = B diag(e^{i theta},1) B diag(e^{i phi},1); decision H3 con la media de las 10 diferencias como "diferencia de intervalo".
- Decisiones no declaradas en el preregistro (anadidas tras la auditoria): (1) Adam con beta1 0,9, beta2 0,999, eps 1e-8; (2) umbral de gradiente 1e-6 (fijado por el ejecutor antes de entrenar; la puerta "pasa" evalua solo N=8, N=64 es informativo con 60 de 4032 fases); (3) logistica lbfgs con max_iter 5000 y tol 1e-8; (4) MLP con valores por defecto de sklearn (relu, Adam, lr 1e-3, lote 200, alpha 1e-4, tol 1e-4); (5) tiempo H2 como mediana de 7 repeticiones con calentamiento de 100, en lugar del "promedio de 1000 evaluaciones" preregistrado, con reloj de pared en maquina compartida; (6) PCA(random_state=0) y normalizacion unitaria posterior para N < 64; (7) sin pantalla de fases de salida; (8) paridad de capas (la capa 0 empieza en el modo 0); (9) bootstrap con numpy default_rng(0) (el preregistro dice solo "semilla 0").
- Verificacion V: comparte la geometria de capas entre ambas rutas; prueba capas = densa, no que la topologia sea la universal de Clements.
- La malla no converge a 2000 pasos (perdida 2,38 a 0,247); H3 vale para este presupuesto de entrenamiento.
- `sumas.py` usa rglob: si se reejecuta incluira `sensibilidad/` y cambiara SHA256SUMS.txt.
- Se uso paralelismo de 3 procesos de entrenamiento (3 hilos en total, BLAS a 1 hilo) en lugar de un proceso unico; los tiempos de CPU de entrenamiento estan inflados por contencion.
- Tiempo H2 medido con fases aleatorias y entradas de la particion 0 (el tiempo no depende de los valores); para N<64 no se entrena ni clasifica (N=8 < 10 detectores).
- Numpy puro; no se uso numba ni torch.
- Limite del preregistro: dígitos con 10 detectores; nada se afirma sobre la geometria de Neuro3D ni hardware fotonico; N=64 es escalado numerico, no una malla fabricable.
- `resultados/parciales/` guarda cada entrenamiento (curva de perdida cada 100 pasos). Las fases entrenadas no se guardaron; son reproducibles por semilla.
