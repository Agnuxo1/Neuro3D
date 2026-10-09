# Resultados P1-5 · benchmark v1

Generado por `analisis_benchmark_v1.py` segun `PREREGISTRO-P1-5.md` (con Enmienda 1). Exactitud de prueba; 10 particiones por conjunto; IC95 bootstrap por particion (10000 remuestreos, semilla 0). Los resultados se publican tal cual.

Entorno: python 3.13.7, numpy 2.2.6, scipy 1.15.1, scikit-learn 1.4.0

Verificacion de la version multiclase frente a `fit_baseline` (max. diferencia absoluta de probabilidades, tolerancia 1e-6): iris_linear=0.0e+00, iris_quadratic=0.0e+00, wine_linear=0.0e+00, wine_quadratic=0.0e+00

## Iris (4 atributos, 3 clases, train/test 120/30)

| Modelo | exactitud media | desv. | min | max | exact. equilibrada media | CPU s/particion | dif. vs mejor | IC95 dif. |
|---|---|---|---|---|---|---|---|---|
| B1 softmax lineal L2=0.001 | 0.9467 | 0.0450 | 0.8667 | 1.0000 | 0.9467 | 0.008 | -0.0033 | [-0.0300, +0.0167] |
| B2 SVM RBF C=1 gamma=scale | 0.9400 | 0.0540 | 0.8667 | 1.0000 | 0.9400 | 0.000 | -0.0100 | [-0.0367, +0.0133] |
| B3 random forest 200 arboles | 0.9400 | 0.0410 | 0.8667 | 1.0000 | 0.9400 | 0.198 | -0.0100 | [-0.0333, +0.0133] |
| B4 MLP (32,) (mejor) | 0.9500 | 0.0360 | 0.9000 | 1.0000 | 0.9500 | 0.122 | - | - |
| B5 softmax lineal P0-4 | 0.9467 | 0.0450 | 0.8667 | 1.0000 | 0.9467 | 0.005 | -0.0033 | [-0.0300, +0.0167] |
| B6 softmax cuadratico P0-4 | 0.9467 | 0.0450 | 0.8667 | 1.0000 | 0.9467 | 0.002 | -0.0033 | [-0.0300, +0.0167] |

Mejor linea base por exactitud media: **B4**. B1 convergio en 10/10 particiones (gradiente maximo peor 4.1e-07); B4 con aviso de convergencia en 10/10.

### Claim optico en Iris (serie: reinicios (media por particion))

Optico: media 0.9483, desv. 0.0346, min 0.9000, max 1.0000.

| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |
|---|---|---|---|---|---|
| B5 | +0.0017 | [-0.0092, +0.0142] | 0.7188 | 1.0000 | equivalente |
| B6 | +0.0017 | [-0.0092, +0.0142] | 0.7188 | 1.0000 | equivalente |

Clasificacion del conjunto: **equivalente**.
Sensibilidad (analisis primario de P0-4, mejor reinicio por perdida de entrenamiento): media 0.9500, clasificacion equivalente.
Diferencia descriptiva del optico frente a B1-B4 (no es criterio de decision): B1 +0.0017 [-0.0092, +0.0142]; B2 +0.0083 [-0.0067, +0.0233]; B3 +0.0083 [-0.0042, +0.0225]; B4 -0.0017 [-0.0217, +0.0158].

## Wine (4 atributos, 3 clases, train/test 141/37)

| Modelo | exactitud media | desv. | min | max | exact. equilibrada media | CPU s/particion | dif. vs mejor | IC95 dif. |
|---|---|---|---|---|---|---|---|---|
| B1 softmax lineal L2=0.001 | 0.8541 | 0.0463 | 0.7838 | 0.9189 | 0.8478 | 0.005 | -0.0135 | [-0.0378, +0.0135] |
| B2 SVM RBF C=1 gamma=scale (mejor) | 0.8676 | 0.0517 | 0.7838 | 0.9459 | 0.8589 | 0.003 | - | - |
| B3 random forest 200 arboles | 0.8514 | 0.0464 | 0.7568 | 0.8919 | 0.8450 | 0.191 | -0.0162 | [-0.0486, +0.0108] |
| B4 MLP (32,) | 0.8622 | 0.0630 | 0.7568 | 0.9459 | 0.8511 | 0.122 | -0.0054 | [-0.0270, +0.0216] |
| B5 softmax lineal P0-4 | 0.8541 | 0.0463 | 0.7838 | 0.9189 | 0.8478 | 0.005 | -0.0135 | [-0.0378, +0.0135] |
| B6 softmax cuadratico P0-4 | 0.8622 | 0.0484 | 0.7838 | 0.9189 | 0.8567 | 0.003 | -0.0054 | [-0.0243, +0.0163] |

Mejor linea base por exactitud media: **B2**. B1 convergio en 10/10 particiones (gradiente maximo peor 1.9e-07); B4 con aviso de convergencia en 10/10.

### Claim optico en Wine (serie: semillas 1049,1050,1051 (media por particion))

Optico: media 0.7910, desv. 0.0409, min 0.7207, max 0.8559.

| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |
|---|---|---|---|---|---|
| B5 | -0.0631 | [-0.0838, -0.0414] | 0.0020 | 0.0039 | inferior_o_inconcluso |
| B6 | -0.0712 | [-0.0910, -0.0486] | 0.0020 | 0.0039 | inferior_o_inconcluso |

Clasificacion del conjunto: **inferior_o_inconcluso**.
Exactitud media por semilla: 1049=0.8622, 1050=0.8270, 1051=0.6838.
Diferencia descriptiva del optico frente a B1-B4 (no es criterio de decision): B1 -0.0631 [-0.0838, -0.0414]; B2 -0.0766 [-0.1009, -0.0495]; B3 -0.0604 [-0.0739, -0.0450]; B4 -0.0712 [-0.1000, -0.0405].

## Breast Cancer (30 atributos, 2 clases, train/test 455/114)

| Modelo | exactitud media | desv. | min | max | exact. equilibrada media | CPU s/particion | dif. vs mejor | IC95 dif. |
|---|---|---|---|---|---|---|---|---|
| B1 softmax lineal L2=0.001 | 0.9711 | 0.0131 | 0.9474 | 0.9912 | 0.9652 | 0.008 | -0.0105 | [-0.0184, -0.0026] |
| B2 SVM RBF C=1 gamma=scale | 0.9754 | 0.0100 | 0.9561 | 0.9912 | 0.9711 | 0.002 | -0.0061 | [-0.0132, +0.0009] |
| B3 random forest 200 arboles | 0.9675 | 0.0160 | 0.9386 | 0.9912 | 0.9644 | 0.320 | -0.0140 | [-0.0272, -0.0026] |
| B4 MLP (32,) (mejor) | 0.9816 | 0.0105 | 0.9649 | 0.9912 | 0.9785 | 0.345 | - | - |

Mejor linea base por exactitud media: **B4**. B1 convergio en 10/10 particiones (gradiente maximo peor 1.8e-07); B4 con aviso de convergencia en 10/10.

## Digits (64 atributos, 10 clases, train/test 1437/360)

| Modelo | exactitud media | desv. | min | max | exact. equilibrada media | CPU s/particion | dif. vs mejor | IC95 dif. |
|---|---|---|---|---|---|---|---|---|
| B1 softmax lineal L2=0.001 | 0.9397 | 0.0106 | 0.9250 | 0.9556 | 0.9396 | 0.034 | -0.0489 | [-0.0561, -0.0419] |
| B2 SVM RBF C=1 gamma=scale (mejor) | 0.9886 | 0.0046 | 0.9833 | 0.9972 | 0.9885 | 0.058 | - | - |
| B3 random forest 200 arboles | 0.9742 | 0.0078 | 0.9611 | 0.9861 | 0.9740 | 0.534 | -0.0144 | [-0.0192, -0.0097] |
| B4 MLP (32,) | 0.9733 | 0.0085 | 0.9611 | 0.9833 | 0.9732 | 1.102 | -0.0153 | [-0.0206, -0.0100] |

Mejor linea base por exactitud media: **B2**. B1 convergio en 10/10 particiones (gradiente maximo peor 7.8e-08); B4 con aviso de convergencia en 1/10.

## Notas

- Breast Cancer y Digits: sin modelo optico (alcance del preregistro, seccion 2).
- Las particiones se solapan: los IC subestiman la incertidumbre. Con 10 particiones Wilcoxon tiene poca potencia.
- Iris y Wine ya se ejecutaron en P0-4; las predicciones de B5/B6 recalculadas son identicas a las de P0-4: True.
- Tiempo de CPU total (s, suma de modelos y particiones): Iris 3.3, Wine 3.3, Breast Cancer 6.8, Digits 17.3.
