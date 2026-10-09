# Resultados P1-8

Decision: **sin limite practico demostrado**

| Conjunto | n | acc Q | acc O | media Q-O | IC95 bootstrap | Wilcoxon p | tareas Q-O>0,02 |
|---|---|---|---|---|---|---|---|
| Cuadratica | 40 | 0.9441 | 0.9351 | 0.0090 | [0.0055, 0.0126] | 0.00010473741586718425 | 8 |
| Lineal (control) | 40 | 0.9264 | 0.9239 | 0.0025 | [-0.0006, 0.0057] | 0.14051483460740122 | 3 |

Control de cordura (media Q-O lineal < 0,01): cumplido. H1 (IC95 inf > 0,02 en cuadratica): no cumplida.

Verificacion de rango: max rango de P_k = 2 (teoria <= 2); max rango de Q_i-Q_j en O = 4 (teoria <= 4); QDA con los 3 pares de rango 5 en 40/40 tareas cuadraticas (120/120 pares).

Gradiente analitico vs diferencias finitas (max error relativo): {'T=1': np.float64(5.607376491563125e-09), 'T=0.05': np.float64(2.006607595691879e-09)}.

Python 3.13.7, numpy 2.2.6, scipy 1.15.1; CPU. Tiempo total 144.4 s.
