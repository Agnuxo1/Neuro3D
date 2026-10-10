# Resultados P2-10 (escala a 64 modos)

Generado por `analisis.py` a partir de `resultados_raw.json`. CPU, sin GPU.

## H3 (digits, N = 64)

| Modelo | Exactitud media | DE |
|---|---|---|
| Malla N=64 | 0.9492 | 0.0124 |
| Logistica (L2=0,001) | 0.9394 | 0.0113 |
| MLP 48 | 0.9736 | 0.0091 |

- Malla - logistica: +0.0097, IC95 bootstrap [+0.0053, +0.0147], Wilcoxon p = 0.0059.
- **Decision H3: soportado** (criterio: diferencia >= -0,01 e IC95 inferior >= -0,03).
- Control malla - MLP (sin criterio): -0.0244, IC95 [-0.0300, -0.0181], Wilcoxon p = 0.0020.

## H2 (escala)

| N | t por entrada (us) | t en lote, por entrada (us) | bytes coeficientes | bytes matriz densa |
|---|---|---|---|---|
| 8 | 57.39 | 0.59 | 1792 | 1024 |
| 16 | 114.10 | 2.44 | 7680 | 4096 |
| 32 | 230.19 | 11.70 | 31744 | 16384 |
| 64 | 488.79 | 102.38 | 129024 | 65536 |

- Pendiente log-log (tiempo por entrada, evaluacion individual): 1.028, IC95 [0.962, 1.095] (t, 2 gl). p en [1,8; 2,2]: False; IC95 dentro: False.
- Exploratorio (lote de 1000, tiempo por entrada): 2.459, IC95 [1.700, 3.218].
- Memoria de coeficientes: pendiente 2.056 IC95 [2.003, 2.108]; matriz densa: 2.000.

## CPU de entrenamiento (malla N=64, 2000 pasos)

- 30 entrenamientos; mediana 710.2 s, min 474.7 s, max 1440.9 s, total 23955 s.
