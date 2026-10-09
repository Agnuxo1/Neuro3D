# Comparación prospectiva con Wine: alcance y protocolo

La evaluación termina correctamente: las tres inicializaciones aciertan **33/37, 30/37 y 28/37** filas reservadas, frente a **32/37** de ambos baselines. No demuestra superioridad óptica y muestra sensibilidad a la inicialización. Pasan los 183 estados geométricos auditados, gradientes y reconstrucciones finales.

El [perfil](research/wine_comparison_profile_2026-10-09.json), [recibo humano GitHub](research/wine_comparison_registration_2026-10-09.json) y 22 archivos de entrada/código se publicaron **antes de ejecutar**, en `0e2e7c1e84f26d621de499ef0669037d655fef99`. Perfil `af7bd4fd-2d1f-48c6-91ce-94ab31cd4fa6`, SHA256 `623623be2f0be6acccddfa432a94526fafeb484bf2d05d50b8822319c7b0c81c`. La autorización humana de continuidad está verificada por el operador; no se ha emitido registro externo ni CID IPFS. El [supervisor y archivo completo](validation/wine-comparison-2026-10-09/attempt01/supervisor.json) conservan fuentes exactas y controles; [resultado](validation/wine-comparison-2026-10-09/attempt01/worker/result.json), [índice](validation/wine-comparison-2026-10-09/attempt01/evidence_index.json).

Wine tiene 178 ejemplos y 13 variables. Se conservan los archivos originales y su atribución a Stefan Aeberhard y M. Forina, DOI [10.24432/C5PC7J](https://doi.org/10.24432/C5PC7J), licencia CC BY 4.0 según [UCI](https://archive.ics.uci.edu/dataset/109/wine). Los datos, direcciones y hashes están en [provenance.json](data/uci-wine/provenance.json). La descarga no constituye evaluación ni registro prospectivo externo.

Las primeras cuatro variables del archivo —alcohol, ácido málico, ceniza y alcalinidad de la ceniza— se fijan antes de entrenar, adaptadas a cuatro fuentes más referencia coherente. Escalado min/max ajustado exclusivamente en las 141 filas de entrenamiento; no se recorta la evaluación. Los cinco campos reales se normalizan conjuntamente a potencia de entrada unitaria y comparten referencia de fase. La normalización también se aplica a todos los baselines. Partición estratificada fijada: entrenamiento 47/56/38 y evaluación 12/15/10, semilla 20261009. Las etiquetas se cargan para comprobar la estratificación; no participan en actualizaciones ni selección de modelos fuera del entrenamiento.

La misma geometría capturada suministra 16 pares de traslaciones de espejos. Se eliminan los antiguos retardos entrenados, situando cada par en la coordenada de su divisor más 2 BU y perturbación uniforme ±0,0125 BU. Se fijan tres inicializaciones, semillas 1049/1050/1051, todas publicadas. Cada una ejecuta exactamente 60 actualizaciones Adam, paso 0,001 BU, temperatura 0,05, límite ±0,035 BU alrededor del centro sin entrenar. Cada estado cuantizado a coordenadas nativas float32 se audita de manera independiente: vecino más próximo, ramas, reflexión y vecindad interior. Se verifica cada gradiente inicial mediante diferencias finitas y se reconstruye la geometría final desde cero para comparar los 178 campos.

Baselines: mayoría determinada por entrenamiento; softmax lineal sin intercepto adicional sobre las cinco entradas normalizadas, 15 parámetros nominales / 10 diferencias identificables; softmax cuadrático sobre los 15 monomios únicos, 45 nominales / 30 diferencias identificables. Ambos modelos optimizan una pérdida convexa con L2=0,001, L-BFGS-B, máximo 2.000 iteraciones, criterios fijados y control final del gradiente. Sus restricciones algebraicas difieren de una red óptica pasiva; comparar acierto con los mismos datos no establece equivalencia física ni de capacidad.

Se publicarán las tres semillas completas, costes, matrices de confusión, intervalos descriptivos Wilson del 95% y comparaciones pareadas exploratorias. Ningún resultado de evaluación seleccionará semilla, variables, pasos o hiperparámetros. Las tres semillas comparten 37 filas: no se agrupan como 111 observaciones independientes. McNemar exacto se informa sin corrección múltiple y sin afirmación confirmatoria de superioridad. El criterio de ejecución correcta es descenso de pérdida de entrenamiento ≥0,02 y controles de geometría/gradientes/reconstrucción; **el acierto alto no es condición para publicar**.

La representación equivalente también limita las afirmaciones de capacidad. Para entrada real y campo lineal coherente `E=u·x`, la potencia es `xᵀQx`, con `Q=aaᵀ+bbᵀ`, `u=a+ib`: matriz real positiva semidefinida de rango ≤2 por detector y diferencias de rango ≤4. La matriz hermítica compleja tiene rango ≤1. El control numérico recompone todos los puertos mediante los campos de las cinco bases y esas matrices. Esto no introduce una no linealidad óptica intermedia ni prueba universalidad.

El ensayo mide generalización dentro de un nuevo conjunto público, tras reentrenar desde pesos eliminados. No mide transferencia sin entrenamiento, evaluación externa ciega, fidelidad de Maxwell, fabricación, reproducción por otra persona, ni novedad excepcional. El presupuesto propio es 1.800 s, un núcleo CPU, 4.000 MiB RAM libre previa / 2.500 MiB mínima, RSS ≤1.500 MiB y evidencia ≤64 MiB. Las fracciones exactas y auditorías corren en CPU; la validación real de NVIDIA tiene su protocolo y coste separado.

## Resultados y límites observados

| Modelo | Parámetros nominales | Entrenamiento | Evaluación | Wilson 95%, evaluación |
|---|---:|---:|---:|---:|
| Geometría, semilla 1049 | 16 | 117/141 | 33/37 (89,2%) | 75,3–95,7% |
| Geometría, semilla 1050 | 16 | 108/141 | 30/37 (81,1%) | 65,8–90,5% |
| Geometría, semilla 1051 | 16 | 105/141 | 28/37 (75,7%) | 59,9–86,6% |
| Softmax lineal | 15 | 120/141 | 32/37 (86,5%) | 72,0–94,1% |
| Softmax cuadrático | 45 | 121/141 | 32/37 (86,5%) | 72,0–94,1% |
| Mayoría de entrenamiento | 0 | 56/141 | 15/37 (40,5%) | 26,3–56,5% |

![Resultados de las tres semillas y baselines](assets/wine-geometry-and-baselines-2026-10-09.png)

Las pérdidas de entrenamiento bajaron respectivamente `2,07045→0,49122`, `2,49522→0,54176` y `2,52629→0,76914`. El último modelo de cada ejecución se evalúa sin elegir el mejor. Comparación pareada con cada baseline: diferencias +1, −2 y −4 aciertos; McNemar exacto exploratorio p=1, 0,5 y 0,125. Las incertidumbres amplias y la única partición compartida impiden presentar una mejora estadística o estabilidad universal.

Error máximo de diferencias finitas entre las tres ejecuciones: `5,473×10⁻⁶ <10⁻⁴`. Reconstrucción desde la geometría final trazada de nuevo: error máximo de campo `5,882×10⁻¹⁶ <10⁻¹¹`. La representación densa/cuadrática reproduce todos los 178 ejemplos y ocho puertos con diferencias ≤`5,237×10⁻¹⁶` en campo y ≤`6,662×10⁻¹⁶` en potencia. Se observa rango real 2 en las matrices de cada detector con umbral `10⁻¹⁰`; valores propios negativos mínimos del orden de `10⁻¹⁶` son redondeo numérico. La restricción algebraica de rango ≤2 procede de la fórmula, no del umbral numérico. Estos controles no son certificados de aritmética ni mediciones físicas.

El supervisor midió **1.114,174 s** y RSS máximo **107,781 MiB**, sin interrupciones. Coste de las tres ejecuciones: auditorías geométricas 1.054,492 s; evaluación propia de pérdida/gradientes 3,675 s; reconstrucciones finales 52,255 s. El total incluye preparación, controles iniciales y baselines. Los optimizadores clásicos tardaron 5,58 ms y 4,71 ms, 38 iteraciones cada uno; esos tiempos excluyen la importación de SciPy, incluida en el total del worker. Evaluar 178 ejemplos con los baselines tardó 0,108 y 0,098 ms. No se equipara el coste de certificar geometría a entrenar logits ni se reivindica eficiencia fotónica a partir de estos tiempos digitales.

Este hito proporciona un resultado reproducible de aprendizaje y comparación, con variabilidad y limitaciones explícitas. Siguen pendientes otras particiones, tareas más amplias, perturbaciones acotadas, geometrías distintas, fidelidad física del conjunto, ejecución AMD y reproducción por un equipo externo.
