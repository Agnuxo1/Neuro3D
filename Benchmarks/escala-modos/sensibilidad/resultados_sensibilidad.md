# Sensibilidad de H3 a la regularizacion de la logistica (P2-10)

Malla N=64: exactitudes guardadas. Diferencia = malla - logistica. IC95 bootstrap (10000, semilla 0). Wilcoxon bilateral.

| Variante | Logistica media | Malla media | Dif. media | IC95 | Wilcoxon p | Victorias malla | H3 |
|---|---|---|---|---|---|---|---|
| Original (L2=0,001, C~0,696) | 0.9394 | 0.9492 | +0.0097 | [+0.0053, +0.0147] | 0.0059 | 9/10 (empates 0) | soportado |
| (a) C=1,0 | 0.9458 | 0.9492 | +0.0033 | [+0.0000, +0.0067] | 0.1367 | 6/10 (empates 1) | soportado |
| (b) C por validacion interna | 0.9703 | 0.9492 | -0.0211 | [-0.0286, -0.0128] | 0.0078 | 0/10 (empates 2) | no soportado |

C elegido por particion (b): 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 10.0, 100.0

Metodo: validacion cruzada interna de 5 pliegues sobre el entrenamiento, codificacion reajustada por pliegue, empate -> menor C; prueba no interviene. max_iter=5000, tol=1e-8 en todas.
