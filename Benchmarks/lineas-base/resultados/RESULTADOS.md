# Resultados P0-4 (lineas base con igual numero de parametros)

Generado por `analisis.py` segun la seccion 7 del preregistro. Exactitud de prueba; diferencia = optico menos linea base; IC95 bootstrap por particion (10000 remuestreos, semilla 0); Wilcoxon bilateral con Holm sobre las dos lineas base.

## Iris (10 particiones)

| Modelo | media | desv. | min | max |
|---|---|---|---|---|
| optico | 0.9500 | 0.0393 | 0.9000 | 1.0000 |
| linear | 0.9467 | 0.0450 | 0.8667 | 1.0000 |
| quadratic | 0.9467 | 0.0450 | 0.8667 | 1.0000 |

| Optico vs | diferencia media | IC95 | p Wilcoxon | p Holm | clasificacion |
|---|---|---|---|---|---|
| linear | +0.0033 | [-0.0067, +0.0133] | 1.0000 | 1.0000 | equivalente |
| quadratic | +0.0033 | [-0.0067, +0.0133] | 1.0000 | 1.0000 | equivalente |

Clasificacion del conjunto: **equivalente**

## Wine (10 particiones)

| Modelo | media | desv. | min | max |
|---|---|---|---|---|
| optico | 0.8622 | 0.0450 | 0.7838 | 0.9189 |
| linear | 0.8541 | 0.0463 | 0.7838 | 0.9189 |
| quadratic | 0.8622 | 0.0484 | 0.7838 | 0.9189 |

| Optico vs | diferencia media | IC95 | p Wilcoxon | p Holm | clasificacion |
|---|---|---|---|---|---|
| linear | +0.0081 | [-0.0054, +0.0243] | 0.5625 | 1.0000 | inferior_o_inconcluso |
| quadratic | +0.0000 | [-0.0108, +0.0108] | 1.0000 | 1.0000 | equivalente |

Clasificacion del conjunto: **inferior_o_inconcluso**

Wilcoxon con 10 particiones tiene poca potencia: ausencia de diferencia no prueba equivalencia (preregistro, seccion 9).
