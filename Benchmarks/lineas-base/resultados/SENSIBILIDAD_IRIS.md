# Sensibilidad de Iris: optico = media de los 4 reinicios

Preregistro seccion 7: para el optico se usa la media de reinicios por particion; el analisis primario uso el mejor reinicio por perdida de train. El mejor reinicio reproduce el original (diferencia maxima de parametros 0.0e+00).

| Modelo | media | desv. | min | max |
|---|---|---|---|---|
| optico_media_reinicios | 0.9483 | 0.0346 | 0.9000 | 1.0000 |
| linear | 0.9467 | 0.0450 | 0.8667 | 1.0000 |
| quadratic | 0.9467 | 0.0450 | 0.8667 | 1.0000 |

| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |
|---|---|---|---|---|---|
| linear | +0.0017 | [-0.0092, +0.0142] | 0.7188 | 1.0000 | equivalente |
| quadratic | +0.0017 | [-0.0092, +0.0142] | 0.7188 | 1.0000 | equivalente |

Clasificacion del conjunto: **equivalente** (primaria: equivalente; cambia: False)
