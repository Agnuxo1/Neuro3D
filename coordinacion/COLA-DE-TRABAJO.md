# Cola única de trabajo de Neuro3D

Estado al 2026-09-28 20:55 UTC. Antes de iniciar una tarea, comprobar aquí que
no haya otra ejecución del mismo trabajo.

| ID | Prioridad | Estado | Responsable | Modelo o ruta | Esfuerzo | Recursos reservados | Dependencias | Entregable | Criterio de aceptación |
|---|---|---|---|---|---|---|---|---|---|
| OPS-001 | P0 | Completada | Codex | Agente principal y JEV | Medio | Lecturas CPU ligeras; GPU ninguna | Repositorio existente | `coordinacion/INFORME-INICIAL.md` y documentos de coordinación | Estado previo preservado, recursos sondeados y prioridad JEV registrada. |
| OPT-001 | P0 | Entregada; referencias clave contrastadas por Codex | Claude | Sonnet, revisión independiente | Medio | Solo lectura; red y CPU ligera; GPU ninguna | Circuito óptico actual | `coordinacion/respuestas/OPT-001.json` | Ecuaciones, riesgos y prueba falsable de dos caminos con evidencia verificable. |
| OPT-002 | P0 | Referencia de fase corregida y regresiones CPU pasan; solape/coherencia pendientes | Codex | Agente principal, JEV supervisa | Alto | CPU ligera; GPU ninguna | DEC-006/008; contrato EXP-001 aún borrador | `Blender/core/mz_scene.py`, regresiones no rectangular/cuadrada, siguiente control de solape y coherencia | No promocionar sin controles de solape/coherencia, contrato cerrado y validación Blender autorizada. |
| OPT-006 | P1 | Oráculo provisional entregado; 14 autocomprobaciones pasan | Claude | Referencia analítica separada | Medio | CPU ligera; GPU ninguna | OPT-001 | `Blender/oracle/` | Coincidencia con motor independiente en controles acordados; limitaciones explícitas. |
| OPT-008 | P1 | Entregada; fallo principal reproducido por Codex | Claude | Auditoría cruzada de solo lectura | Medio | Lectura; GPU ninguna | Primer prototipo OPT-002 | `coordinacion/respuestas/OPT-008.json` | Hallazgos verificables sobre energía, geometría y contrato Blender; Codex decide correcciones. |
| OPT-009 | P1 | Entregada; referencia CPU reproducida por Codex | Claude | Referencia geométrica independiente | Medio | CPU ligera; GPU ninguna | DEC-006 | `coordinacion/respuestas/OPT-009.json`, oráculo separado | Ecuación de frente de onda y caso falsable, categorías de pérdida sin duplicar el motor. |
| OPT-003 | P1 | Bloqueada por DEC-006 y recursos | Codex | Blender background CPU | Medio | Ninguno ahora; GPU ninguna | Corrección OPT-002, contrato cerrado y margen de RAM | Smoke real de dos caminos en `.blend` | Guardar/reabrir y modificar un camino cambia la salida medida. |
| OPT-004 | P2 | En cola | Codex | Revisión manual | Bajo | Recursos interactivos cuando el PC esté libre | Ninguna | Comprobación del panel addon | Botones funcionan y no despachan GPU. |
| OPT-005 | Pausada | Bloqueada por recursos | Sin asignar | Pendiente de JEV | Pendiente | GPU local reservada por trabajo ajeno | GPU libre y autorización posterior | Investigación de aceleración GPU | Paridad con baseline CPU y presupuesto acordado. |

Una propuesta de Claude no cambia el estado de la cola hasta que Codex la
compruebe y registre la decisión.
