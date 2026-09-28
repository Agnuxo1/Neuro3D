# Cola única de trabajo de Neuro3D

Estado al 2026-09-28 17:16 UTC. Antes de iniciar una tarea, comprobar aquí que
no haya otra ejecución del mismo trabajo.

| ID | Prioridad | Estado | Responsable | Modelo o ruta | Esfuerzo | Recursos reservados | Dependencias | Entregable | Criterio de aceptación |
|---|---|---|---|---|---|---|---|---|---|
| OPS-001 | P0 | Completada | Codex | Agente principal y JEV | Medio | Lecturas CPU ligeras; GPU ninguna | Repositorio existente | `coordinacion/INFORME-INICIAL.md` y documentos de coordinación | Estado previo preservado, recursos sondeados y prioridad JEV registrada. |
| OPT-001 | P0 | Pendiente de respuesta; CLI agotó 60 s | Claude | Sonnet, revisión independiente | Medio | Solo lectura; red y CPU ligera; GPU ninguna | Circuito óptico actual | `coordinacion/respuestas/OPT-001.json` | Ecuaciones, riesgos y prueba falsable de dos caminos con evidencia verificable. |
| OPT-002 | P0 | Borrador experimental creado; implementación en espera de OPT-001 | Codex | Agente principal, JEV supervisa | Alto | CPU ligera; GPU ninguna | Revisión OPT-001 y decisión JEV | `coordinacion/experimentos/EXP-001-BORRADOR.md`, después prototipo multirrayo | Escena determina amplitud/fase; controles constructivo, destructivo e incoherente; conservación y pruebas reproducibles. |
| OPT-003 | P1 | En cola | Codex | Blender background CPU | Medio | Un proceso limitado; GPU ninguna | OPT-002 | Smoke real de dos caminos en `.blend` | Guardar/reabrir y modificar un camino cambia la salida medida. |
| OPT-004 | P2 | En cola | Codex | Revisión manual | Bajo | Recursos interactivos cuando el PC esté libre | Ninguna | Comprobación del panel addon | Botones funcionan y no despachan GPU. |
| OPT-005 | Pausada | Bloqueada por recursos | Sin asignar | Pendiente de JEV | Pendiente | GPU local reservada por trabajo ajeno | GPU libre y autorización posterior | Investigación de aceleración GPU | Paridad con baseline CPU y presupuesto acordado. |

Una propuesta de Claude no cambia el estado de la cola hasta que Codex la
compruebe y registre la decisión.
