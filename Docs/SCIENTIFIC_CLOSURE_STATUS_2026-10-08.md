# Neuro3D: control de los 26 cierres solicitados

Fecha de inicio: 2026-10-08. Cada cierre requiere evidencia verificable y publicación en GitHub. La referencia al Nobel expresa una exigencia de rigor; no constituye un criterio medible de aceptación ni una predicción de reconocimiento.

Actualización de alcance 2026-10-08 por decisión expresa del propietario: Blender es la plataforma principal; Unreal deja de ser requisito y queda como referencia histórica. El punto 7 sigue abierto para propagación RT coherente en Blender. [Plan de pruebas y criterios de los 26 puntos](BLENDER_SCIENTIFIC_ROADMAP_2026-10-08.md).

| Punto | Trabajo | Estado verificable |
|---|---|---|
| 1 | Entrada first-hit: `pinned packet` | CERRADO; commit 2522b4b; 21 pruebas CPU PASS; entradas originales intactas |
| 2 | 20 consultas first-hit GPU | CERRADO; native18 20/20, supervisor PASS y auditor independiente PASS |
| 3 | Contactos, huecos, empates, bordes y retornos en multicamino | CERRADO en referencia CPU de óptica escalar; 17 pruebas, 41 estímulos analíticos y 8 ejecuciones JSON; integración nativa de geometrías adversas pendiente en punto 7 |
| 4 | Presupuesto completo geometría → intensidad | CERRADO en modelo CPU escalar y cajas certificables; 14 pruebas/41 certificados/9 ejecuciones JSON; certificado integral de aritmética nativa y física requieren evidencia adicional |
| 5 | Justificación de fusión/reducción/descarte | CERRADO para operaciones activas; prueba matemática y 8 testigos PASS; reducción coherente en DAG canónico justificada en punto 6, sin poda heurística |
| 6 | Red entrenada completa en GPU nativa | CERRADO para circuito canónico Iris completo; commit 68d9b7d; 450/450 decisiones y todas las salidas coinciden con referencia; puente geométrico CPU exacto. No recorrido de triángulos GPU ni captura Blender float32 |
| 7 | RT coherente en Blender; Unreal retirado | ABIERTO para transporte coherente y recorrido nativo de triángulos en Blender con salidas completas/auditoría; Unreal NO APLICA por decisión expresa del propietario. Retirar Unreal no acredita RT |
| 8 | Supervisión y ramas defensivas restantes | ABIERTO |
| 9 | Reproducción integral desde checkout limpio | ABIERTO |
| 10 | Flujos interactivos y reconciliación documental | ABIERTO |
| 11 | Contribución central falsable | CERRADO como formulación de pregunta/H1, utilidad y refutación; [contrato](CONTRIBUTION_AND_FALSIFICATION_2026-10-08.md). Hipótesis y novedad sin confirmar |
| 12 | Revisión sistemática y novedad | ABIERTO; [búsqueda y revisión seleccionada](LITERATURE_AND_NOVELTY_AUDIT_2026-10-08.md):194registros/175únicos,30entradas extraídas; cobertura no exhaustiva y novedad no demostrada |
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

Punto 6: [resultados, alcance y recibos](IRIS_NATIVE_CIRCUIT_RESULTS_2026-10-08.md). GPU nativa evalúa scaler/normalización, 16 celdas, ocho modos, fases/conexiones, campos/potencias/logits/argmax de la red congelada. Primer ensayo numérico fallido conservado; segundo PASS sin cambiar umbrales. El test histórico 29/30 no acredita generalización nueva ni el coste completo del punto 16.

Análisis retrospectivo posterior: [cotas racionales de los readbacks](IRIS_RETROSPECTIVE_RATIONAL_CERTIFICATE_2026-10-08.md) para el modelo algebraico canónico; campo ≤1.282e-13 y 450 decisiones certificadas en `native02`. El control `native01` también conserva las decisiones, pero una cota inferior prueba el incumplimiento de precisión. No es nueva ejecución GPU ni certificado de captura/recorrido de triángulos, y no cierra la novedad.

Punto 7: [preparación Unreal histórica preservada](UNREAL_RT_READINESS_2026-10-08.md) y [nuevos ensayos RT en Blender](BLENDER_SCIENTIFIC_ROADMAP_2026-10-08.md). El propietario retiró expresamente Unreal del alcance; la consulta sobre ubicación del motor ya no es necesaria. Se preservan recibos y fuentes; el transporte RT coherente sigue abierto.

Regla de ejecución: no elevar un resultado CPU a GPU, una simulación a medición física ni una publicación propia a reproducción independiente. Conservar intentos negativos y criterios preregistrados. Si un punto no satisface sus criterios, permanece abierto. El propietario ha solicitado ahora [una nueva secuencia](SEQUENTIAL_RESEARCH_PROGRESS_2026-10-08.md): formulación, antecedentes y después trazador Blender; esa instrucción sustituye el orden anterior.
