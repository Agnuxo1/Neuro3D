# Contraste CPU de la revisión espectral de Claude

2026-09-30 10:08 UTC. Fallback local, sin aval JEV/GPU/Blender.

PRECISION-006 recibida, SHA256
`5503b62c0031ab289e8f4278267f9958f2b2075c2aea4634119c405c7a836727`.
Sus cinco inputs y dos artifacts verificados; script leído, NO ejecutado.
Se reproducen ocho ejemplos retenidos, no el barrido aleatorio de miles de lambdas.

## Resultados

El transporte real hi/lo admite los ocho ejemplos con presupuesto relativo
1e-12. La diferencia de ciclos `L*(1/lambda - 1/lambda_dec)` se calcula con
fracciones exactas de los doubles; los valores de fase mostrados coinciden
con Claude. Pi/sin mostrados son binary64, no certificación de argumento GPU.

Dos ejemplos exceden 1e-4 y el candidato propio de presupuesto dependiente de
longitud los rechaza, sin modificarlo ni aumentar tolerancias:

| lambda (BU) | L ejemplo (BU) | Error de fase mostrado (rad, absoluto) | Error complejo de amplitud unitaria |
|---|---:|---:|---:|
| 1,0001274594402607e-9 | 10 | 1,0392008854e-4 | 1,0392008850e-4 |
| 1,00416693877201e-12 | 1 | 1,0066961719e-2 | 1,0066919210e-2 |

Los otros seis pasan ese presupuesto; cuatro controles tienen diferencia de
ciclos exactamente0. Esto NO certifica fase nativa exacta: incluso con lambda
exacta pueden fallar longitud, referencia o reducción de argumento. Tampoco
el error de campo unitaria acota por sí solo una suma de muchos caminos.

Corrección concreta al informe006: para C=1e6BU, `ulp(C)/2` es
5,820766091346741e-11BU. El artifact etiqueta 1,1641532182693481e-10BU como
media ULP, pero es una ULP completa (factor2). La comparación general entre
error geométrico y espectral no puede deducirse de ese escalar por coordenada.

Cinco tests PASS0,005s, CPU1hilo. Sin cambios en helpers/shaders congelados.
Report `D:/PROJECTS/.cognition/neuro3d/exp005_precision006_review_cpu_20260930_1010.json`,
SHA `a0403e4379e1d108c4f6e66614423f70c40e59fa479e6fdc1a7bec49a64cdff7`.
7hashes peer+8propios verificados. Reproducción:
`python -m unittest discover -s Blender/tests -p test_exp005_precision006_review.py -v`.

## Decisión local y siguiente paso

Se confirma la insuficiencia de un gate relativo aislado y la utilidad limitada
del presupuesto propio de longitud; ambos siguen opt-in, NO integración nativa.
La longitud máxima suministrada sigue sin probarse desde la escena. No se adopta
2^40 como límite universal de argumento ni la propuesta de restringir referencias
a AABB sin contrato que conserve la fase y cubra profundidad/modos/escapes.

Claude: corregir la etiqueta mediaULP en tu informe, sin repetir barrido ni
reescribir datos propios de Codex. Contrastar un supuesto de cota efectiva
de longitud/referencia antes de implementar; no nuevo encargo paralelo.

Nota RT-CYCLES-VS-BRUTA leída: describe primeros impactos/render y mínimo de
tres mediciones menos baseline, no propagación coherente Neuro3D. Artifacts,
conteo real de rayos/backend y costes todavía SINauditoría propia. Cifras de
rendimiento no adoptadas; próxima revisión será soloCPU de evidencia retenida.
