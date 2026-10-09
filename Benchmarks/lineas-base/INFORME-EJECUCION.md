# Informe de ejecucion P0-4 (2026-10-09)

Ejecucion del protocolo de `PREREGISTRO-P0-4.md` (no editado). Solo CPU, sin Blender, sin bpy real, sin GPU, sin git. Resultados en `resultados/`; tabla completa en `resultados/RESULTADOS.md` y `RESULTADOS.json`.

## Que se ejecuto

- `iris_numeric.py`: modulo numerico de Iris que extrae por AST `lattice_xy, modes, model_U, encode, loss_acc, train` del demo (sin copia manual).
- `iris_numeric_check.py`: importa el demo ORIGINAL con `bpy` y `mathutils` falsos (el stub bastó) y compara. Particion historica (`default_rng(0).permutation(150)`, 120/30, escalado min-max con train): perdida original = numerica = 0,043710367060916036, diferencia 0, parametros diferencia maxima 0 (umbral 1e-12 cumplido).
- `run_lineas_base.py`: particiones (`resultados/splits.json`, hash SHA-256 de indices por particion), lineas base lineal y cuadratica (`fit_baseline` importado sin modificar; el modulo NO arrastra bpy), optico Iris y optico Wine (worker `Tools/train_wine_comparison_v1.py` sin modificar, vía `wine_worker_runner.py`; perfil copiado a `resultados/perfiles/` cambiando solo `train_indices`, `test_indices` y la lista de inicializaciones).
- `analisis.py`: seccion 7 del preregistro. `Blender/tests/test_lineas_base.py`: 8 pruebas en verde.

## Tiempos de CPU medidos

- Iris optico: 34,2-34,9 s por particion (4 reinicios x 500 pasos), 345,5 s en total.
- Wine optico, medicion previa en k=0 con 3 semillas: entrenamiento por semilla 358,2 / 374,5 / 376,9 s; proceso completo 1112,6 s (371 s por semilla de media). Despues, 1 semilla por particion: 354-373 s por proceso.
- Lineas base: segundos por particion (en `baselines.json`).

## Desviaciones del preregistro

1. **Plan de respaldo de Wine aplicado**: 10 particiones x 1 semilla (1049). El entrenamiento supero 6 minutos de CPU de forma marginal (media de 3 semillas 371 s de proceso; 2 de 3 semillas por encima de 360 s, la primera con 358 s). Se aplico la regla fijada con la medicion del proceso completo. En k=0 quedaron ya ejecutadas las semillas 1050 y 1051 (accuracy 0,838 y 0,676); el analisis usa solo la 1049 y las otras dos figuran como dato extra en `RESULTADOS.json`.
2. **Cifra 0,309707 no comparable**: esa perdida pertenece al protocolo de geometria capturada (60 actualizaciones, 61 auditorias), no a `train()` del demo de Iris. No existe cifra de perdida publicada de `train()` con la que contrastar; se verifico la equivalencia frente al original ejecutado (diferencia 0).
3. `trained_lattice.json` (producido en Blender con su numpy) no coincide con la salida de `train(seed=0)` en esta maquina: misma particion y escalado, perdida del guardado 0,04306 frente a 0,04371 y parametros distintos (maximo 6,45, minimos locales/fase equivalentes); exactitud guardada 0,975 train / 0,9667 prueba frente a 0,975 / 1,000 aqui. No afecta a la comprobacion de equivalencia del modulo numerico.
4. Semilla de `train()` de Iris: `seed=0` en todas las particiones (reinicios `0..3`), pues el preregistro fija `seed + r` sin indicar valor para el argumento.
5. Estratificacion: asignacion fija por clase de prueba (Wine [12,15,10], Iris [10,10,10]) mediante `default_rng(seed).permutation` dentro de cada clase. Coincide con la particion congelada del perfil SOLO en los conteos (141/37 y [12,15,10] por clase, exigidos por el `need()` del worker), no en los indices.
6. **Iris: mejor reinicio, no media.** El preregistro (seccion 7) resume el optico con la media de los reinicios por particion; el analisis primario uso el mejor reinicio por perdida de train (lo que devuelve `train()`). Sensibilidad con la media de reinicios en `resultados/SENSIBILIDAD_IRIS.md`: optico 0,9483, diferencia +0,0017 frente a ambas lineas base (IC95 [-0,0092, +0,0142], p_Holm = 1,0), clasificacion equivalente: la clasificacion primaria NO cambia. El mejor reinicio se reprodujo con diferencia 0.
7. Las lineas base de Iris usan la codificacion de 5 fuentes coherentes (constante 1) de `encode_real_features`; el optico de Iris usa su propio codificado (referencia entrenable). Wine: las predicciones de las lineas base propias son identicas a las del worker en las 10 particiones.

## Resultados

| Conjunto | Optico | Lineal | Cuadratico | Optico-lineal (IC95) | Optico-cuadratico (IC95) | Clasificacion |
|---|---|---|---|---|---|---|
| Iris (10x30) | 0,9500 | 0,9467 | 0,9467 | +0,0033 [-0,0067, +0,0133] | +0,0033 [-0,0067, +0,0133] | equivalente frente a ambas |
| Wine (10x37) | 0,8622 | 0,8541 | 0,8622 | +0,0081 [-0,0054, +0,0243] | 0,0000 [-0,0108, +0,0108] | frente a lineal inferior/inconcluso (IC sale de +-0,02), frente a cuadratico equivalente; conjunto: inferior o inconcluso |

Wilcoxon (con Holm) p = 1,0 en Iris y p_Holm = 1,0 en Wine: ninguna superioridad. No se declara superioridad optica en ninguno de los dos conjuntos. Todas las ejecuciones de Wine terminaron con estado PASS.

## Limitaciones

- Wilcoxon con 10 particiones tiene poca potencia; "equivalente" significa solo IC95 dentro de +-0,02, con IC amplios por tener 30-37 ejemplos de prueba.
- Wine: 4 de 13 caracteristicas; una sola semilla de inicializacion (plan de respaldo); geometria del perfil no recapturada por particion. Iris: 150 ejemplos.
- En Iris, lineal y cuadratico dan la misma exactitud en las 10 particiones (con convergencia distinta: iteraciones diferentes); coincidencia observada, no investigada.
- Las 10 particiones comparten datos entre si (solapamiento), por lo que las diferencias pareadas no son independientes.

## Extension post hoc (EXPLORATORIO, decision JEV 2026-10-09)

**Motivo.** El encargo pedia mas semillas de inicializacion y el plan de respaldo redujo el analisis primario de Wine a una sola semilla (1049). El coordinador autorizo (JEV, confianza 1,0) ejecutar tambien 1050 y 1051 en las 10 particiones. El analisis primario (`RESULTADOS.json/.md`, `analisis.py`, `optical_wine_k*.json`) NO se modifica.

**Advertencia.** Esta extension se decidio despues de observar el resultado de la particion k=0 (semillas 1050 y 1051 ya conocidas: 0,838 y 0,676). Es un analisis post hoc: no es confirmatorio y no sustituye al preregistrado.

**Ejecucion.** k=0 reutilizado (mismo proceso que la ejecucion primaria; verificados hash de particion, copia del perfil y hash de Wine). k=1..9 x semillas 1050 y 1051: 18 ejecuciones, hasta 3 procesos en paralelo, todas en PASS. Coste de CPU por proceso: 380-403 s (media 389 s; algo mas que en serie por la ejecucion en paralelo). Resultados en `resultados/extension/optical_wine_ext_k{k}_s{seed}.json`; analisis en `analisis_extension.py` -> `resultados/RESULTADOS_EXTENSION.json/.md`.

**Cifras** (media de 3 semillas por particion, 10 particiones):

| Modelo | media |
|---|---|
| Optico | 0,7910 |
| Lineal | 0,8541 |
| Cuadratico | 0,8622 |

- Optico menos lineal: -0,0631, IC95 [-0,0838, -0,0414], p_Holm = 0,0039. Optico menos cuadratico: -0,0712, IC95 [-0,0910, -0,0486], p_Holm = 0,0039. Clasificacion: inferior o inconcluso frente a ambas (aqui con evidencia de inferioridad).
- Por semilla: 1049 media 0,8622 (supera a lineal en 4 de 10 particiones, 4 empates); 1050 media 0,8270 (1 de 10); 1051 media 0,6838 (0 de 10).
- Desviacion tipica entre semillas por particion: media 0,096 (rango 0,016 a 0,133), mucho mayor que la desviacion entre particiones de las lineas base.

**Lectura.** El resultado primario (semilla 1049: equivalente al cuadratico, inconcluso frente al lineal) depende de la inicializacion: la semilla 1049 es la mejor de las tres y las otras dos son peores. Con las tres semillas promediadas, el optico queda por debajo de ambas lineas base. La conclusion honesta es que el optico de Wine no iguala a las lineas base de forma robusta a la semilla. Nunca se seleccionaron semillas por el resultado de prueba; la primaria se fijo antes (preregistro).

## Limitaciones anadidas tras la auditoria

- Los hiperparametros del perfil de Wine (pasos, tasa, temperatura, recorte) se fijaron con resultados observados en un intento previo sobre la particion original (attempt01); este conjunto de datos no es un holdout virgen para esos hiperparametros.
- Reproducibilidad: la comprobacion exacta (diferencia 0) es en esta maquina, con numpy 2.2.6 y scipy 1.15.1. Con otras versiones o BLAS pueden aparecer diferencias numericas (ya se vio con `trained_lattice.json` producido con el numpy de Blender).

## Auditoria independiente

`AUDIT-P0-4.md` reproduce las cifras primarias y de la extension con diferencia 0 (tolerancia 1e-9); los IC95 y los p coinciden. Sin fugas: el escalado min-max se ajusta solo con train y el mejor reinicio de Iris se elige por perdida de train, nunca por prueba. Hashes de los resultados en `resultados/SHA256SUMS.txt` (`verificar_hashes.py`; `--check` para verificar).
