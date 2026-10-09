# Resultados de la extension - Wine, 3 semillas (EXPLORATORIO post hoc (decisión JEV 2026-10-09))

**EXPLORATORIO post hoc (decisión JEV 2026-10-09).** Decidido despues de observar el split k=0. El analisis primario (semilla 1049, `RESULTADOS.md`) no cambia.

Promedio de las semillas 1049, 1050 y 1051 por particion; IC95 bootstrap por particion (10000, semilla 0); Wilcoxon bilateral; Holm sobre las dos lineas base.

| Modelo | media | desv. | min | max |
|---|---|---|---|---|
| optico (media 3 semillas) | 0.7910 | 0.0409 | 0.7207 | 0.8559 |
| lineal | 0.8541 | 0.0463 | 0.7838 | 0.9189 |
| cuadratico | 0.8622 | 0.0484 | 0.7838 | 0.9189 |

| Optico vs | dif. media | IC95 | p Wilcoxon | p Holm | clasificacion |
|---|---|---|---|---|---|
| linear | -0.0631 | [-0.0838, -0.0414] | 0.0020 | 0.0039 | inferior_o_inconcluso |
| quadratic | -0.0712 | [-0.0910, -0.0486] | 0.0020 | 0.0039 | inferior_o_inconcluso |

Clasificacion del conjunto: **inferior_o_inconcluso**

## Por semilla

| Semilla | exactitud media | dif. vs lineal | particiones que superan a lineal (empatan/pierden) | dif. vs cuadratico | superan a cuadratico |
|---|---|---|---|---|---|
| 1049 | 0.8622 | +0.0081 | 4 (4/2) | +0.0000 | 2 |
| 1050 | 0.8270 | -0.0270 | 1 (3/6) | -0.0351 | 1 |
| 1051 | 0.6838 | -0.1703 | 0 (0/10) | -0.1784 | 0 |

Desviacion tipica entre semillas por particion: 0.113, 0.102, 0.016, 0.095, 0.102, 0.128, 0.041, 0.133, 0.128, 0.097 (media 0.0955).
