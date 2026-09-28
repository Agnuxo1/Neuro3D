# Cola única de trabajo de Neuro3D

Estado al 2026-09-28 22:50 UTC. Antes de iniciar una tarea, comprobar aquí que
no haya otra ejecución del mismo trabajo.

| ID | Prioridad | Estado | Responsable | Modelo o ruta | Esfuerzo | Recursos reservados | Dependencias | Entregable | Criterio de aceptación |
|---|---|---|---|---|---|---|---|---|---|
| OPS-001 | P0 | Completada | Codex | Agente principal y JEV | Medio | Lecturas CPU ligeras; GPU ninguna | Repositorio existente | `coordinacion/INFORME-INICIAL.md` y documentos de coordinación | Estado previo preservado, recursos sondeados y prioridad JEV registrada. |
| OPT-001 | P0 | Entregada; referencias clave contrastadas por Codex | Claude | Sonnet, revisión independiente | Medio | Solo lectura; red y CPU ligera; GPU ninguna | Circuito óptico actual | `coordinacion/respuestas/OPT-001.json` | Ecuaciones, riesgos y prueba falsable de dos caminos con evidencia verificable. |
| OPT-002 | P0 | Fase y solape/coherencia implementados en CPU; revisión del último parche solicitada a Claude | Codex | Agente principal, JEV supervisa | Alto | CPU ligera; GPU ninguna | DEC-006/008; contrato EXP-001 aún borrador | Motor/adaptador, 41 pruebas CPU/estáticas e informe de revisión | No promocionar sin revisión independiente del parche final, contrato cerrado y validación Blender autorizada. |
| OPT-006 | P1 | Oráculo provisional entregado; 14 autocomprobaciones pasan | Claude | Referencia analítica separada | Medio | CPU ligera; GPU ninguna | OPT-001 | `Blender/oracle/` | Coincidencia con motor independiente en controles acordados; limitaciones explícitas. |
| OPT-008 | P1 | Entregada; fallo principal reproducido por Codex | Claude | Auditoría cruzada de solo lectura | Medio | Lectura; GPU ninguna | Primer prototipo OPT-002 | `coordinacion/respuestas/OPT-008.json` | Hallazgos verificables sobre energía, geometría y contrato Blender; Codex decide correcciones. |
| OPT-009 | P1 | Entregada; referencia CPU reproducida por Codex | Claude | Referencia geométrica independiente | Medio | CPU ligera; GPU ninguna | DEC-006 | `coordinacion/respuestas/OPT-009.json`, oráculo separado | Ecuación de frente de onda y caso falsable, categorías de pérdida sin duplicar el motor. |
| OPT-010 | P1 | Entregada; casos reproducidos y corregidos por Codex en CPU | Claude | Oráculo y crítica independientes | Medio | CPU ligera; GPU ninguna | OPT-002, DEC-009 | `coordinacion/respuestas/OPT-010.json` y tablón | Revisión de atribución de detectores y compuerta de anchura; DEC-010 conserva limitaciones. |
| OPT-011 | P1 | Entregada; hallazgo de constructor no rectangular reproducido y constructor añadido por Codex | Claude | Oráculo y crítica independientes | Medio | CPU ligera; GPU ninguna | Parche actual, DEC-010 | `coordinacion/respuestas/OPT-011.json` | Revisión del constructor nuevo solicitada; motor aceptado solo en CPU. |
| OPT-003 | P1 | Runner/readback integrados, solo revisión CPU/estática; prueba real bloqueada | Codex | Agente principal; Blender background CPU solo tras autorización | Alto | CPU ligera ahora; GPU ninguna | DEC-009/010/011, revisión final Claude del runner, parentado real, margen de RAM y permiso | Smoke real de dos caminos en `.blend` | Guardar/reabrir objetos y comprobar A–D con umbrales congelados. |
| OPT-004 | P2 | En cola | Codex | Revisión manual | Bajo | Recursos interactivos cuando el PC esté libre | Ninguna | Comprobación del panel addon | Botones funcionan y no despachan GPU. |
| OPT-005 | Pausada | Bloqueada por recursos | Sin asignar | Pendiente de JEV | Pendiente | GPU local reservada por trabajo ajeno | GPU libre y autorización posterior | Investigación de aceleración GPU | Paridad con baseline CPU y presupuesto acordado. |

Una propuesta de Claude no cambia el estado de la cola hasta que Codex la
compruebe y registre la decisión.
