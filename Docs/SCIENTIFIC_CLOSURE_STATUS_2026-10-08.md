# Neuro3D: control de los 26 cierres solicitados

Fecha de inicio: 2026-10-08. Cada cierre requiere evidencia verificable y publicación en GitHub. La referencia al Nobel expresa una exigencia de rigor; no constituye un criterio medible de aceptación ni una predicción de reconocimiento.

| Punto | Trabajo | Estado verificable |
|---|---|---|
| 1 | Entrada first-hit: `pinned packet` | CERRADO; commit 2522b4b; 21 pruebas CPU PASS; entradas originales intactas |
| 2 | 20 consultas first-hit GPU | CERRADO; native18 20/20, supervisor PASS y auditor independiente PASS |
| 3 | Contactos, huecos, empates, bordes y retornos en multicamino | ABIERTO |
| 4 | Presupuesto completo geometría → intensidad | ABIERTO |
| 5 | Justificación de fusión/reducción/descarte | ABIERTO |
| 6 | Red entrenada completa en GPU nativa | ABIERTO |
| 7 | RT coherente y Unreal compilado/readback | ABIERTO; decidir continuidad con evidencia |
| 8 | Supervisión y ramas defensivas restantes | ABIERTO |
| 9 | Reproducción integral desde checkout limpio | ABIERTO |
| 10 | Flujos interactivos y reconciliación documental | ABIERTO |
| 11 | Contribución central falsable | ABIERTO; obligatorio antes de escalado/fabricación |
| 12 | Revisión sistemática y novedad | ABIERTO |
| 13 | Expresividad, no linealidad, estabilidad y límites | ABIERTO |
| 14 | Generalización con incertidumbre | ABIERTO |
| 15 | Baselines de tarea/precisión/salidas/presupuesto equivalentes | ABIERTO |
| 16 | Tiempo, memoria y energía completos | ABIERTO |
| 17 | Escalado funcional y separación de capacidades | ABIERTO |
| 18 | Ablaciones | ABIERTO |
| 19 | Plataforma física fabricable y régimen válido | ABIERTO |
| 20 | Ruido, pérdidas, deriva, tolerancias y precisión | ABIERTO; requiere mediciones para afirmación física |
| 21 | Experimento físico discriminante mínimo | ABIERTO; diseño/simulación no equivalen a construcción |
| 22 | Cálculo/aprendizaje en plataforma física | ABIERTO; requiere experimento |
| 23 | Sílice: convergencia, modos, acopladores y parámetros medidos | ABIERTO; checkout separado con trabajo concurrente |
| 24 | Reproducción por terceros/laboratorio | ABIERTO; requiere acción independiente |
| 25 | Artículo, crítica especializada y revisión por pares | ABIERTO; preparación/envío/aceptación son estados distintos |
| 26 | Consecuencia científica importante y duradera | ABIERTO; exige evidencia e impacto posteriores |

Punto 1: [corrección y recibo](FIRST_HIT_ADMISSION_FIX_2026-10-08.md). Publicación de progreso: [PR #6](https://github.com/Agnuxo1/Neuro3D/pull/6), en borrador, branch `codex/neuro3d-scientific-closure-20261008`. Incluye la consolidación local anterior; no se ha fusionado automáticamente con main.

Regla de ejecución: no elevar un resultado CPU a GPU, una simulación a medición física ni una publicación propia a reproducción independiente. Conservar intentos negativos y criterios preregistrados. Si un punto no satisface sus criterios, permanece abierto y se resuelve antes de declarar el siguiente cerrado.
