# Informe de ejecucion P1-5 · benchmark v1

Ejecutado el 2026-10-09 siguiendo `PREREGISTRO-P1-5.md` con su Enmienda 1. Solo CPU (un proceso, hilos BLAS = 1), sin GPU, sin Blender, sin descargas. Entorno: Python 3.13.7, numpy 2.2.6, scipy 1.15.1, scikit-learn 1.4.0. Duracion total de la ejecucion de modelos: 32 s (reloj). Resultados completos en `resultados/RESULTADOS_BENCHMARK_V1.md` y `.json`; datos por particion en `resultados/benchmark_v1_raw.json`; hashes en `resultados/SHA256SUMS.txt`.

## Que se ejecuto

- Datos: Iris (`Blender/demo_lattice_iris/iris.csv`), Wine (`Docs/data/uci-wine/wine.data`, 4 primeras columnas de atributos), Breast Cancer y Digits (`sklearn.datasets`). SHA-256 de X e y de cada conjunto en el raw y en el resultado.
- Particiones: Iris y Wine usan las de P0-4 (`splits.json`; los SHA-256 de los indices coinciden con los registrados). Breast Cancer (455/114) y Digits (1437/360): `StratifiedShuffleSplit(test_size=0.2, random_state=20261009+k)`, k = 0..9; indices ordenados y SHA-256 por particion.
- Escalado min-max ajustado solo con entrenamiento, sin recorte.
- B1 a B4 en los cuatro conjuntos; B5 y B6 (con `fit_baseline`) en Iris y Wine.
- Version multiclase generica (`multiclass_softmax.py`) verificada contra `fit_baseline` en Iris y Wine (lineal y cuadratica, 10 particiones cada una): diferencia maxima de probabilidades 0.0 (tolerancia 1e-6), antes de usarla en Breast Cancer y Digits. Las predicciones recalculadas de B5/B6 son identicas a las de P0-4 (`baselines.json`).
- Modelo optico: no se ejecuto nada nuevo. Se leyeron los resultados guardados de P0-4 y se aplico la seccion 7.

## Desviaciones y decisiones de interpretacion

1. **Iris, serie optica.** El optico de Iris no tiene las semillas 1049-1051 (esas son de Wine); su inicializacion es una sola semilla (0) con 4 reinicios. Se uso como "media por particion" la media de los 4 reinicios, que es lo que P0-4 fijo en su seccion 7 (`SENSIBILIDAD_IRIS`). El analisis primario de P0-4 (mejor reinicio) se reporta como sensibilidad: misma clasificacion.
2. **B1 igual a B5 en Iris y Wine.** B1 usa la misma codificacion que `fit_baseline` (min-max, columna constante 1, normalizacion de fila a norma 1) y el mismo objetivo, asi que reproduce B5 exactamente; el preregistro lo define asi (B1 = `fit_baseline` lineal). B2 a B4 usan solo min-max (preregistro seccion 4), sin columna constante ni normalizacion de fila.
3. **Columnas de rango cero (Digits).** La version generica escala a 0 las columnas constantes en entrenamiento (`fit_baseline` abortaria). Es una generalizacion necesaria; no afecta a Iris ni a Wine.
4. **Convergencia.** La version generica no aborta si no converge; registra la bandera. B1 convergio (gradiente maximo < 1e-5) en 10/10 particiones de los cuatro conjuntos.
5. **Importacion de P0-4.** `analisis_benchmark_v1.py` importa (sin modificarlas) las funciones `holm`, `bootstrap_ci`, `wilcoxon_p`, `classify`, `describe` de `Benchmarks/lineas-base/analisis.py` y `load` de `analisis_extension.py` para aplicar exactamente la misma regla; sus SHA-256 quedan en el resultado.
6. **Aviso de convergencia de B4.** `MLPClassifier` con `max_iter=500` emite aviso de no convergencia en 10/10 particiones de Iris, Wine y Breast Cancer, y en 1/10 de Digits. El preregistro fija max_iter=500 sin parada temprana, por lo que no se cambio.

## Resultados (exactitud de prueba, media de 10 particiones)

| Conjunto | B1 | B2 | B3 | B4 | B5 | B6 | Mejor |
|---|---|---|---|---|---|---|---|
| Iris | 0.9467 | 0.9400 | 0.9400 | 0.9500 | 0.9467 | 0.9467 | B4 |
| Wine | 0.8541 | 0.8676 | 0.8514 | 0.8622 | 0.8541 | 0.8622 | B2 |
| Breast Cancer | 0.9711 | 0.9754 | 0.9675 | 0.9816 | - | - | B4 |
| Digits | 0.9397 | 0.9886 | 0.9742 | 0.9733 | - | - | B2 |

Diferencias pareadas frente a la mejor linea base (IC95 bootstrap) y exactitud equilibrada, en el `.md` de resultados. Resumen: en Iris y Wine ninguna linea base se separa de la mejor (todos los IC contienen 0). En Breast Cancer, B1 y B3 quedan por debajo de B4 (IC excluyen 0, -0.0105 y -0.0140); B2 no. En Digits todas quedan por debajo de B2 (B1 -0.0489, B3 -0.0144, B4 -0.0153), con IC que excluyen 0.

## Claim optico (Iris y Wine, serie = media por particion, frente a B5 y B6, Holm dentro del conjunto)

- **Iris: equivalente.** Optico 0.9483; diferencia +0.0017, IC95 [-0.0092, +0.0142] frente a B5 y a B6; p Holm 1.0. Sensibilidad con el mejor reinicio: 0.9500, equivalente.
- **Wine: inferior o inconcluso.** Optico (media de 3 semillas) 0.7910; frente a B5 -0.0631, IC95 [-0.0838, -0.0414]; frente a B6 -0.0712, IC95 [-0.0910, -0.0486]; p Holm 0.0039 en ambos. El optico es peor, no equivalente. La semilla 1049 sola (0.8622) sobreestima el resultado; 1050 da 0.8270 y 1051 da 0.6838.
- Concuerda con P0-4 y su extension; el claim de P0-4 no cambia. Breast Cancer y Digits: sin claim optico (alcance del preregistro).

## Tiempo de CPU (suma de modelos y particiones, s)

Iris 3.3, Wine 3.3, Breast Cancer 6.8, Digits 17.3. Por particion en Digits: B1 0.03, B2 0.06, B3 0.53, B4 1.10. Detalle por modelo en el resultado (insumo de P1-9).

## Limitaciones

- Wine usa 4 de 13 atributos; el claim vale solo para ese codificado.
- Las particiones se solapan: los IC subestiman la incertidumbre; Wilcoxon con 10 particiones tiene poca potencia. "Equivalente" en Iris se apoya en el IC, no en Wilcoxon.
- Los hiperparametros de B2 a B4 son valores por defecto fijados antes de ejecutar; no estan afinados, por lo que B1 en Digits (0.94) y el resto describen referencias, no maximos posibles.
- Los tiempos de CPU son de una sola maquina y un solo hilo, utiles solo como orden de magnitud.
- Un resultado "no superior" del optico se reporta tal cual.

## Archivos

`multiclass_softmax.py`, `run_benchmark_v1.py`, `analisis_benchmark_v1.py`, `resultados/{benchmark_v1_raw.json, RESULTADOS_BENCHMARK_V1.json, RESULTADOS_BENCHMARK_V1.md, SHA256SUMS.txt}`, y `Blender/tests/test_benchmark_v1.py` (5 pruebas en verde: tamanos, estratificacion, coincidencia con `fit_baseline`, determinismo de hashes).
