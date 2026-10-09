# Entrenamiento propio desde la geometría capturada: protocolo fijado

Este perfil posterior usa la autorización humana de continuidad GitHub.
El registro externo/IPFS sigue pendiente. Se publican protocolo, entradas y
fuentes antes de recoger el resultado. El piloto original y sus límites no cambian.

Los 32 bindings de coordenadas X de los espejos r1/r2 forman 16 parejas
entrenables. El compilador obtiene las derivadas afines del origen, hit y
longitud de cada segmento mediante las ecuaciones de intersección con los
planos capturados. Las normales permanecen constantes. Cada fusión del grafo
exige que todas las derivadas del origen coincidan exactamente; una familia
que rompe esta condición se rechaza. No se consume el modelo analítico
`model_U`, los pesos `theta` históricos ni una matriz neuronal aprendida.

**Se borran los retardos previamente entrenados** antes del ensayo: cada
pareja se sitúa en `X capturada de bs1 + 2 BU`, más una perturbación aleatoria
fijada de ±0,0125 BU. La referencia óptica tiene amplitud fija 1. La pérdida
y sus gradientes se calculan directamente sobre todos los arcos coherentes
del grafo. La salida conserva los detectores R0/R1/R2 y su argmax.

Iris se divide mediante índices publicados: 120 filas de entrenamiento y 30
reservadas, estratificadas 40/10 por especie. Min/max se ajustan sólo con las
120 filas. Se normaliza explícitamente la potencia de entrada a 1; no se
renormalizan detectores ni se recortan las filas reservadas. La temperatura
0,05 afecta sólo a la pérdida. El proyecto ya ha utilizado Iris: este ensayo
es una validación de entrenamiento con separación de filas, no un descubrimiento
confirmatorio sobre un conjunto nuevo o ciego.

Se fijan 60 actualizaciones Adam, paso 0,001 BU, límites ±0,035 BU respecto
a la geometría sin retardo y proyección a las coordenadas nativas float32 de
Blender. Los 61 estados (inicial y posteriores) se auditan independientemente
para primeros hits, ramas y vecindades interiores. No se escoge un checkpoint
según las filas reservadas: se evalúa el último estado prefijado.

Las diferencias centrales de los 16 gradientes de entrenamiento deben tener
error absoluto ≤ `10^-4`, con paso `10^-6 BU`. La reconstrucción geométrica
final desde cero debe dar error de campo ≤ `10^-11`. El criterio de entrenamiento
es una reducción de pérdida ≥ 0,02. Se informa también el acierto de ambas
particiones, sin fijar una exigencia de acierto después de ver el resultado.

El perfil tiene límites nuevos y separados: 900 s, un núcleo CPU, RAM libre
antes ≥ 4.000 MiB, suelo 2.500 MiB, RSS propia ≤ 1.500 MiB y evidencia ≤ 64 MiB.
La GPU, guardar/reabrir Blender y recapturar la escena se validarán en ensayos
posteriores propios. No hay afirmación de fabricación o fidelidad Maxwell.

Cinco controles del compilador comparan campos con reconstrucciones geométricas
nuevas, gradientes de campos/potencias/pérdida con diferencias centrales,
descenso de pérdida y rechazo de fusiones incompatibles y entradas no válidas.
La primera ejecución de esos controles rechazó la fixture histórica con floats:
se corrigió su serialización a racionales exactos; el compilador estricto se
conservó. Pasan los cinco controles y dos de protocolo/registro.

[Perfil y valores exactos fijados](research/captured_geometry_training_profile_2026-10-09.json),
[recibo de autorización](research/captured_geometry_training_registration_2026-10-09.json),
[motor y gradientes propios](../Blender/blender_lab/affine_geometry_network_v1.py).

## Resultado del ensayo fijado

El perfil se publicó en `7d09d009a1f2bf72e0d57afb8bcaded6115f7854` antes
de ejecutarse. Los 18 archivos fijados coincidían con los bytes publicados.
El [recibo y las preimágenes](validation/captured-geometry-training-2026-10-09/attempt01/evidence_index.json)
conservan `VALID_FROZEN_TRAINING_PROFILE_RESULT`, métrica 1, sin interrupción.

| Criterio o resultado | Valor observado |
|---|---:|
| Pérdida inicial → final | 6,25544 → 0,309707 |
| Diferencia máxima de los 16 gradientes | 1,475×10⁻⁶, límite 10⁻⁴ |
| Campo frente a reconstrucción geométrica final | 4,620×10⁻¹⁶, límite 10⁻¹¹ |
| Estados geométricos auditados | 61/61 |
| Acierto de entrenamiento | 110/120, 91,67 % |
| Acierto en filas reservadas | 27/30, 90 % |
| Tiempo supervisado del worker | 369,43 s |
| RSS propia máxima observada | 59,32 MiB |

Los 369,43 s incluyen preparación, diferencias centrales, entrenamiento,
auditorías y reconstrucción final. La pérdida/gradientes de las 61 evaluaciones
consumieron 1,17 s; las auditorías geométricas, 349,67 s; la reconstrucción
final, 17,33 s; y el compilador afín, 0,063 s. No debe compararse sólo el tiempo
de gradientes con el coste completo de otra solución.

![Pérdida propia y errores en las filas reservadas](assets/captured-own-geometry-training-2026-10-09.png)

Esto demuestra entrenamiento propio de las coordenadas de la geometría
representada, con gradientes útiles y readout fijo. El tamaño reservado es
pequeño y el proyecto ya había examinado Iris. Las comparaciones equivalentes,
otros conjuntos, estabilidad, cotas de las nuevas salidas y reproducción
externa siguen abiertas. Guardar/reabrir la escena nativa se comprueba aparte.
