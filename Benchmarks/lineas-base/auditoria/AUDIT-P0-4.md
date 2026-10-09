# AUDIT-P0-4 - verificacion independiente (2026-10-09)

Alcance: solo lectura sobre `D:\PROJECTS\9_NEBULA_NEW` y `D:\PROJECTS\.cognition`. Sin GPU, sin Blender, sin Kaggle. Verificado: ningun archivo del repositorio modificado (`find -newermt 18:08` sin resultados). Scripts mios en el scratchpad de la sesion: `verify.py` (recalculo completo; salida en `verify_out.txt`), `iris_restarts.py`, y una reejecucion de Wine con `Tools/train_wine_comparison_v1.py` escribiendo fuera del repo.

Rutas base: `B = D:\PROJECTS\9_NEBULA_NEW\Benchmarks\lineas-base`, `R = B\resultados`.

## Veredicto resumido

- Las cifras publicadas (primario Iris/Wine y extension) se reproducen exactamente: diferencias de exactitud 0,0 (tolerancia 1e-9), IC95 identicos, p de Wilcoxon y Holm identicos.
- La clasificacion del primario sigue la regla de la seccion 2 del preregistro.
- La extension esta etiquetada como exploratoria post hoc en el JSON, el MD y los JSON individuales; el primario no la contiene.
- Hay 3 desviaciones/omisiones no documentadas en INFORME-EJECUCION.md (todas menores, ninguna cambia una clasificacion) y varios riesgos no cubiertos por los criterios (seccion 5 y 7).

## 1. Particiones - PASA

Comando: `verify.py` (carga `R\splits.json`, `wine.data`, `iris.csv`).

| Comprobacion | Wine (10 x 141/37) | Iris (10 x 120/30) |
|---|---|---|
| train y test disjuntos | True en k=0..9 | True en k=0..9 |
| `sorted(train+test) == range(N)` (N=178 / 150) | True | True |
| tamanos | 141/37 | 120/30 |
| conteos test por clase | [12,15,10] en las 10 | [10,10,10] en las 10 |
| conteos train por clase | [47,56,38] | [40,40,40] |
| `test_class_counts` de splits.json | coincide | coincide |
| SHA-256 de indices recalculado (`sha256(json.dumps({"train":tr,"test":te}))`) vs `sha256_indices` | 10/10 coinciden | 10/10 coinciden |
| Regenerado desde cero (`default_rng(seed).permutation` por clase, test fijo por clase) | 10/10 identico a splits.json | 10/10 identico |
| Particiones distintas entre si | 10 | 10 |

Datos: SHA-256 de `wine.data` = `6be6b120...aea659` (igual que preregistro seccion 3 y `splits.json`); `iris.csv` = `9cc1c345...e8e355` (igual que splits.json). Wine: 178 filas, clases [59,71,48]. Iris: 150 filas, [50,50,50].

Las semillas coinciden con la seccion 4 (Wine 20261009+k; Iris k).

Observacion: la convencion de hash (`json.dumps` por defecto, listas ordenadas) no esta descrita en el preregistro; solo en `run_lineas_base.py:make_splits`. Reproducible, pero hay que citar la convencion.

Observacion relevante para la redaccion del informe: el punto 5 de "Desviaciones" dice que la asignacion fija por clase "coincide con la particion congelada del perfil". Eso es cierto solo para los CONTEOS por clase (los exige el `need()` del worker, `train_wine_comparison_v1.py:34`). Los INDICES son otros: la particion historica del perfil `Docs/research/wine_comparison_profile_2026-10-09.json` tiene 0 indices de prueba en comun con k=0 (solape con k=1..9: 7, 9, 6, 6, 9, 9, 9, 4, 5 de 37). Ver riesgo 7.2.

## 2. Exactitud - PASA

| Cantidad | Metodo de recalculo | Diferencia maxima con RESULTADOS.json |
|---|---|---|
| Iris lineal y cuadratico (10 particiones) | reajuste propio (softmax L2=1e-3, L-BFGS-B maxiter 2000, gtol 1e-8, ftol 1e-12, escalado min-max con train, codificacion 5 fuentes) y comparacion con `test_predictions` guardadas | 0 (y 0 predicciones distintas) |
| Wine lineal y cuadratico | idem | 0 (0 predicciones distintas) |
| Iris optico | reevaluacion de los 18 parametros guardados (`params`) en `iris_numeric.loss_acc` con escalado propio train-only; ademas reentrenamiento completo de `train()` (4 reinicios, 500 pasos) en las 10 particiones | exactitud 0; parametros reentrenados vs guardados: diferencia maxima 0,0 en 10/10 |
| Wine optico, semilla 1049 | exactitud recalculada desde las 178 predicciones de `wine_trabajo\k*\result.json` en los indices de prueba de splits.json | 0 |
| Wine optico, k=1 semilla 1049 | reejecucion del worker en el scratchpad (376 s CPU) | exactitud 0,8918918918918919 = guardada; perdida final 0,49027394862995577 = guardada (identica) |

Medias recalculadas: Iris optico 0,950000, lineal y cuadratico 0,946667; Wine optico 0,862162, lineal 0,854054, cuadratico 0,862162. Descriptivos (media, desv. con ddof=1, min, max): diferencia 0 con RESULTADOS.json.

Nota: el optico de Wine en las particiones k=1..9 y los 30 entrenamientos solo se reprodujeron parcialmente (k=1 reentrenado; el resto, recomputado a partir de las predicciones guardadas). El reentrenamiento de los otros 8 entrenamientos primarios y de las 18 ejecuciones de extension queda NO COMPROBADO (coste 6 min de CPU cada uno).

Tambien: los `code_version.files` de todos los JSON crudos (baselines, optical_iris, optical_wine_k*, extension) coinciden con los hashes actuales de los 12 archivos (0 discrepancias; `combined_sha256` coherente y unico `131c8842...` en los 10 primarios).

## 3. Estadistica - PASA

Implementacion propia en `verify.py` (rng `default_rng(0)`, `integers(0,n,(10000,n))`, percentiles 2,5 y 97,5; `scipy 1.15.1`, `numpy 2.2.6`).

Primario (diferencia = optico menos linea base, 10 particiones):

| Conjunto | vs | media dif. | IC95 mio | IC95 publicado | p Wilcoxon | p Holm | Clasificacion |
|---|---|---|---|---|---|---|---|
| Iris | lineal | +0,003333 | [-0,006667, +0,013333] | idem | 1,0 | 1,0 | equivalente |
| Iris | cuadratico | +0,003333 | [-0,006667, +0,013333] | idem | 1,0 | 1,0 | equivalente |
| Wine | lineal | +0,008108 | [-0,005405, +0,024324] | idem | 0,5625 | 1,0 | inferior_o_inconcluso |
| Wine | cuadratico | 0,000000 | [-0,010811, +0,010811] | idem | 1,0 | 1,0 | equivalente |

Extension (Wine, media de 3 semillas por particion):

| vs | media dif. | IC95 | p Wilcoxon | p Holm | Clasificacion |
|---|---|---|---|---|---|
| lineal | -0,063063 | [-0,083784, -0,041441] | 0,001953 | 0,003906 | inferior_o_inconcluso |
| cuadratico | -0,071171 | [-0,090991, -0,048649] | 0,001953 | 0,003906 | inferior_o_inconcluso |

Diferencias pareadas por particion: diferencia maxima 0 con RESULTADOS.json y RESULTADOS_EXTENSION.json. Medias por particion de la extension y desviacion entre semillas (0,09552) identicas. Por semilla (1049/1050/1051): medias 0,8622/0,8270/0,6838, y conteos gana/empata/pierde frente al lineal 4/4/2, 1/3/6, 0/0/10: identicos a lo publicado.

Holm: mi implementacion propia (paso a paso, monotona) coincide con la de `analisis.py:holm`.

Sensibilidad al generador aleatorio del bootstrap (pedida en la tarea): con `RandomState(0).randint` en vez de `default_rng(0)` el unico valor que cambia es el limite inferior del IC de Wine-lineal primario: -0,008108 frente a -0,005405. Los IC son rejillas discretas (paso 0,0027), y con 20 semillas distintas de `default_rng` el limite inferior oscila entre -0,0081 y -0,0054 (desv. tipica 0,00099), es decir, la diferencia es del orden de un paso de rejilla y del error de Monte Carlo (no mayor). No afecta a la clasificacion: el limite superior (+0,0243) esta fuera de +-0,02 en cualquier caso y el limite inferior sigue sin superar 0. En los otros IC la dispersion de Monte Carlo es 0 o <0,0005 y las conclusiones no cambian.

Sensibilidad del Wilcoxon (la eleccion no esta especificada en el preregistro): `analisis.py:wilcoxon_p` usa los valores por defecto de scipy (zero_method="wilcox", method="auto"; el JSON lo declara). Alternativas: Iris con `method="exact"` p=0,75; con `zero_method="pratt"` p=0,564. Wine-lineal 0,5625 con exact y 0,423 con pratt aproximado. Wine-extension con pratt aproximado p=0,0051 (Holm ~0,010). Ninguna alternativa cambia ninguna clasificacion.

## 4. Fugas - PASA (con una comprobacion no ejecutable)

- Escalado min-max ajustado solo con train:
  - `Blender/blender_lab/classifier_comparison_v1.py:14` `low,high=raw[train].min(axis=0),raw[train].max(axis=0)`; linea 16 aplica `(raw-low)/(high-low)` a todas las filas sin recorte (`test_clipping:False`, linea 21). Lo usan las lineas base (`run_lineas_base.py:90`) y el worker de Wine (`Tools/train_wine_comparison_v1.py:32`).
  - Iris optico: `run_lineas_base.py:131-132` `lo, hi = x[tr].min(0), x[tr].max(0); xs = (x - lo) / (hi - lo)`.
- El conjunto de prueba no se usa para elegir nada:
  - `fit_baseline` recibe solo `x[tr], y[tr]` (`run_lineas_base.py:93`; worker linea 35). No hay validacion ni hiperparametros que elegir.
  - Iris: `IN.train(xs[tr], y[tr], ...)` (`run_lineas_base.py:134`); dentro de `train()` el mejor reinicio se escoge por perdida de TRAIN (`neuro3d_iris_demo.py:189` docstring y `:202` `if best is None or L < best[0]`). La prueba se evalua despues (`run_lineas_base.py:137`). Reentrenamiento mio: el mejor reinicio por perdida de train reproduce los parametros guardados con diferencia 0 en las 10 particiones.
  - Wine: el gradiente y la perdida usan `x[train],y[train]` (worker lineas 42, 46-47, 54); el comentario de la linea 63 y el calculo de `heldout` (linea 76) ocurren despues de las 60 actualizaciones; el `detectors` y el criterio PASS dependen solo de la caida de perdida de train.
  - Las semillas se fijaron en el preregistro; no hay seleccion de semilla por resultado. La semilla primaria (1049) es la primera de la lista.
  - Los entrenamientos de Wine del primario siguen procesos con `heldout` solo informativo; los `iris_numeric.py` extraen del demo por AST solo funciones y constantes (sin variables dependientes de datos).
- No comprobable: si los hiperparametros del perfil (60 pasos, tasa 0,001, temperatura 0,05) se fijaron sin mirar ningun holdout historico. Hay una ejecucion congelada previa en `Docs/validation/wine-comparison-2026-10-09/attempt01` (con registro previo), pero no he auditado su historial; ver riesgo 7.2.

## 5. Desviaciones respecto al preregistro NO documentadas en INFORME-EJECUCION.md

(Las documentadas son: plan de respaldo Wine 1 semilla, cifra 0,309707, `trained_lattice.json`, semilla 0 de Iris, estratificacion por conteos fijos, codificacion de las lineas base de Iris. No las repito.)

1. Hash de los resultados (seccion 8: "se registran ... el hash de los resultados"). `analisis.py:148` lo imprime por pantalla pero no se guarda en ningun archivo (grep en .py, .md y RESULTADOS.json: sin coincidencias). Ademas, el hash impreso se calcula sobre el texto con `\n`, y en Windows `write_text` escribe CRLF: hash del archivo actual `798cbfb2d31f142051ceff313528685cb821ade72c69e4dc2b03623fbbe1be50`; hash que habria impreso (normalizando CRLF) `aa660f627710b4fb1ab3873b60302e42d567ea7f5b84312479c6581296a0eb0e`. Son distintos, asi que ni siquiera se puede rehacer a partir del archivo sin saberlo. No altera cifras.
2. Seccion 7: "Para el optico, la media de sus semillas o reinicios dentro de cada particion". En Iris el analisis usa el modelo del MEJOR reinicio (por perdida de train, como hace `train()`), no la media de los 4 reinicios. Es coherente con la seccion 5 (usa `train()`), pero no esta anotado como interpretacion. Sensibilidad que he calculado (reentrenando cada reinicio por separado): media de reinicios por particion media 0,9483 (frente a 0,9500 publicado); optico menos lineal +0,0017, IC95 [-0,0092, +0,0142], Wilcoxon p=0,72: misma clasificacion (equivalente).
3. El informe, en "Desviaciones" punto 5, dice que la asignacion de Wine "coincide con la particion congelada del perfil". Solo coincide en conteos por clase (141/37 y [12,15,10]), no en indices (solape 0 con k=0). Ver seccion 1. Es una redaccion enganosa mas que una desviacion del protocolo.
4. Los archivos `analisis.py` y `analisis_extension.py` no entran en `code_version` (el preregistro habla de "hash de los archivos usados"); tampoco se guarda el hash de entrada de cada resultado agregado. Menor.

Verificado como NO desviacion (coincide con el preregistro): hiperparametros del perfil copiados sin cambios salvo `train_indices`, `test_indices` e `initializations` (todos los perfiles de `perfiles/` y `extension/perfiles/` comparados con el original: solo esas tres claves difieren, las inicializaciones son identicas a las del original); `baseline_optimizer` = {l2 0,001, maxiter 2000, gtol 1e-8, ftol 1e-12}; cuadratico con 15 monomios unicos (45 coeficientes nominales); IC bootstrap por particion con 10 000 remuestreos y semilla 0; Wilcoxon bilateral; Holm sobre las dos lineas base por conjunto; equivalencia numerica de `iris_numeric.py` con el demo (informe: diferencia 0; `iris_numeric_check.json`: `equivalent_below_1e-12: true`).

## 6. Regla de decision y etiquetado

- Regla seccion 2 en `analisis.py:classify` (lineas 60-66): superior si IC inferior > 0 y p Holm < 0,05; equivalente si IC dentro de [-0,02, +0,02]; otro caso inferior_o_inconcluso. Coincide con el texto. La clasificacion del conjunto exige la condicion frente a las dos lineas base (`superior` y `equivalente`); el preregistro lo dice explicitamente para "superior" pero no para "equivalente": la lectura del codigo es la mas conservadora y esta anotada en el JSON (`dataset_classification_note`). Con la lectura alternativa (equivalente si lo es frente a alguna) Wine seria "equivalente" frente al cuadratico y "inconcluso" frente al lineal; el informe lo muestra por linea base, asi que no hay ocultamiento.
- Resultado primario: Iris equivalente frente a ambas (IC dentro de +-0,02); Wine lineal inconcluso (limite superior +0,0243); Wine cuadratico equivalente (IC +-0,0108); conjunto Wine inconcluso; no se declara superioridad en ningun caso (p Holm 1,0).
- Extension: `RESULTADOS_EXTENSION.json` clave `etiqueta` = "EXPLORATORIO post hoc (decisión JEV 2026-10-09)" y `nota` ("decidido tras observar el split k=0; no sustituye al primario"); el `.md` repite la etiqueta en el titulo y en el primer parrafo (2 apariciones); cada JSON de `extension\` lleva la marca "exploratorio post hoc". `RESULTADOS.json` y `RESULTADOS.md` del primario no contienen la extension ni el termino exploratorio. La conclusion del informe sobre la extension ("no iguala de forma robusta a la semilla") se apoya en cifras que reproducen; hay que recordar que es post hoc.

## 7. Riesgos no cubiertos por los criterios

1. Plan de respaldo con trigger marginal. El preregistro dice "si medir un entrenamiento ... supera 6 minutos de CPU". Medicion previa en k=0: entrenamiento por semilla 358,2 s (<360), 374,5 s, 376,9 s; proceso completo 1112,6 s (370,9 s por semilla). Es decir, una de tres mediciones por semilla no supera 360 s. Luego los entrenamientos 1-semilla de k=1..9 tardaron 353-371 s (proceso 354-373 s): la mitad queda por debajo de 6 min. El informe lo documenta como "marginal"; la decision es defendible pero discutible, y su efecto es grande (primario con 1 semilla frente a 3). Ademas, se aplico tras haber ya ejecutado y visto las 3 semillas de k=0 (0,892, 0,838, 0,676).
2. Posible influencia indirecta del holdout historico. La particion congelada del perfil original se uso en una ejecucion previa con resultados observados (attempt01, registro previo). Los hiperparametros de P0-4 (60 pasos, tasa, temperatura) son los de ese perfil. No he comprobado si se ajustaron mirando ese holdout. Los 37 de prueba historicos se solapan en 4-9 ejemplos con las pruebas de k=1..9 (0 con k=0). Riesgo bajo, pero la afirmacion "no se usa el conjunto de prueba para elegir nada" cubre solo P0-4.
3. Dependencia de la semilla de Wine. Con las tres semillas el optico es inferior (-0,063 y -0,071, p Holm 0,0039). El resultado primario "equivalente al cuadratico" depende de que 1049 sea la mejor semilla de las tres. La desviacion tipica entre semillas por particion (media 0,0955) es mucho mayor que la diferencia entre lineas base. El informe lo senala; hay que mantener la redaccion publica en esta linea.
4. Potencia y solapamiento. Wilcoxon exacto con n=10 tiene p minimo 0,00195; las particiones comparten datos (no independientes), asi que los p y los IC por particion subestiman la incertidumbre. En Iris lineal y cuadratico dan la misma exactitud en las 10 particiones (observacion del informe, no investigada); eso reduce a una sola comparacion efectiva y el Holm se vuelve trivial (p Holm = p). No cambia el veredicto.
5. Wine con 4 de 13 caracteristicas y geometria del perfil sin recapturar por particion (preregistro seccion 9). Iris: el optico usa su propia codificacion y las lineas base la de 5 fuentes coherentes (documentado).
6. Reproducibilidad numerica entre maquinas. `trained_lattice.json` (guardado en Blender) no coincide con `train(seed=0)` en esta maquina (documentado en el informe); la reproducibilidad exacta que yo observo (diferencia 0) es en la misma maquina y versiones de numpy 2.2.6 / scipy 1.15.1; en otra build de BLAS podria haber diferencias de ULPs en el optimizador de las lineas base y en Adam (no en esta ejecucion).
7. Extension: las 18 ejecuciones se hicieron con hasta 3 procesos en paralelo (CPU 380-403 s por proceso frente a 353-373 s en serie). Los resultados numericos no deberian depender de ello (un solo hilo, determinista), y el reentrenamiento en serie de k=1 semilla 1049 reproduce el valor guardado, pero no he reejecutado ninguna de las 18.

## Resumen por criterio

| Criterio | Estado | Evidencia |
|---|---|---|
| Particiones disjuntas, completas, 141/37 y 120/30, conteos por clase | PASA | `verify.py`: 20/20 particiones OK |
| Hash SHA-256 de indices | PASA | 20/20 coinciden con `splits.json`; regenerado de cero identico |
| Exactitudes de prueba (optico y lineas base) | PASA | diferencia maxima 0 (tol. 1e-9) vs RESULTADOS.json; reentreno de Iris (10/10) y de Wine k=1 reproduce |
| Diferencias pareadas, IC95 bootstrap, Wilcoxon, Holm | PASA | identicos a RESULTADOS.json y RESULTADOS_EXTENSION.json; sensibilidad al RNG de un paso de rejilla (Monte Carlo) |
| Sin fugas | PASA | `classifier_comparison_v1.py:14,16`; `run_lineas_base.py:131-134`; `neuro3d_iris_demo.py:202`; worker lineas 32-54, 63, 76 |
| Reentrenamiento de los otros 8 entrenamientos primarios de Wine y 18 de extension | NO COMPROBABLE (no ejecutado) | coste de 6 min de CPU cada uno; solo k=1 reproducido |
| Desviaciones no documentadas | 4 menores (seccion 5) | hash de resultados no guardado; media de reinicios; frase "coincide con la particion congelada"; analisis fuera de `code_version` |
| Clasificacion primaria segun seccion 2 | PASA | `analisis.py:60-66` y tablas de la seccion 3 |
| Extension etiquetada como exploratoria | PASA | `RESULTADOS_EXTENSION.json` clave `etiqueta`/`nota`; `.md` titulo y primer parrafo |
