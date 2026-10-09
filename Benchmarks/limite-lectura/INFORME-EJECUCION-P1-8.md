# Informe de ejecucion P1-8

Preregistro seguido sin cambios (PREREGISTRO-P1-8.md). CPU, numpy 2.2.6, scipy 1.15.1, Python 3.13.7, un proceso. Sin GPU, Blender ni bpy.

## Que se ejecuto
1. Verificacion de gradiente analitico frente a diferencias finitas centrales (h=1e-6): error relativo maximo 5,6e-9 (T=1) y 2,0e-9 (T=0,05).
2. `generadores.py`: 40 tareas de frontera cuadratica (semillas 0-39) y 40 de control lineal (semillas 100-139); 3 clases en R^4, N=600 (400/200, estratificado: 133/133/134 entrenamiento).
3. `modelos.py`: QDA con MLE (con priors empiricos de entrenamiento) y modelo optico O (3 detectores |a_k^T x~|^2, T=0,05, Adam lr 0,01, 3000 pasos, 5 semillas de inicializacion, elegida la de menor perdida de entrenamiento; escalado min-max ajustado con entrenamiento).
4. `analisis.py`: diferencia Q-O por tarea, IC95 bootstrap (10 000, semilla 0), Wilcoxon bilateral, control de cordura, rangos, hashes. Tiempo total 144 s.
5. `Blender/tests/test_limite_lectura.py`: 5 pruebas, todas pasan (0,5 s).

## Resultados
| Conjunto | acc Q | acc O | media Q-O | IC95 | Wilcoxon p | tareas con Q-O>0,02 |
|---|---|---|---|---|---|---|
| Cuadratica (40) | 0,9441 | 0,9351 | 0,0090 | [0,0055; 0,0126] | 1,0e-4 | 8 |
| Lineal control (40) | 0,9264 | 0,9239 | 0,0025 | [-0,0006; 0,0057] | 0,14 | 3 |

Verificacion de rango: rango maximo de cada P_k = 2; rango maximo de Q_i-Q_j en O = 4 (teoria <= 4 cumplida en las 80 tareas); QDA tiene rango 5 en los 3 pares de las 40 tareas cuadraticas (120/120).

## Decision (seccion 6)
Control de cordura cumplido (0,0025 < 0,01). H1 no cumplida: el IC95 inferior (0,0055) no supera 0,02. **Sin limite practico demostrado.** Hay una brecha pequena pero estadisticamente distinguible de cero (Q mejor en media 0,9 puntos, p=1e-4), por debajo del umbral 0,02 preregistrado; no se presenta como limite demostrado. La teoria de rango (O no puede representar todas las fronteras de rango 5) se cumple numericamente, pero en estas tareas no se traduce en una perdida de exactitud mayor que 0,02.

## Desviaciones y decisiones no fijadas por el preregistro
- Ninguna desviacion respecto al preregistro. Elecciones de detalle fijadas antes de ejecutar y no ajustadas: medias ~ N(0,1,5^2 I); covarianza S = A A^T/4 + 0,25 I; inicializacion de U,V ~ N(0,0,5^2); perdida = entropia cruzada media; QDA incluye priors empiricos; rango numerico con tolerancia relativa 1e-9; el control se evalua como media Q-O < 0,01.
- Una sola ejecucion; sin ajuste de parametros tras ver resultados.
- Limitaciones del preregistro: solo tareas sinteticas gaussianas; el resultado no dice nada sobre Iris, Wine ni otros reales.
- Al ejecutar pytest hubo que usar PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 por un conflicto del plugin ajeno `nengo` en el entorno (no afecta al codigo).

## Archivos
Benchmarks\limite-lectura\{generadores.py, modelos.py, analisis.py}; resultados\{resultados_raw.json, RESULTADOS_LIMITE.json, RESULTADOS_LIMITE.md, SHA256SUMS.txt}.
