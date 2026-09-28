# Agenda de trabajo de Neuro3D

Propuesta de Claude, 2026-09-28 18:45 UTC. Complementa la cola de Codex
(`COLA-DE-TRABAJO.md`, que sigue siendo la fuente de verdad del estado):
aquí se planifican orden, horas estimadas y recursos. Codex ajusta y JEV
decide las prioridades sustanciales. Horas = trabajo efectivo del agente,
sin esperas.

## Recursos vigentes

- GPU: ocupada. Ninguna tarea GPU, render ni CUDA.
- CPU: permitida para tareas pequeñas y un proceso a la vez, sin colapsar el
  PC. Antes de Blender, sondear RAM (mínimo 2,5 GiB libres, como EXP-000).

## Plan por fases

| Orden | ID | Tarea | Responsable | Horas est. | Recursos | Depende de | Entregable | Estado |
|---|---|---|---|---:|---|---|---|---|
| 1 | OPT-001 | Auditoría óptica de solo lectura | Claude | 1 | Lectura | — | `respuestas/OPT-001.json` | Entregada; pendiente de validar por Codex |
| 2 | DEC-005 | Resolver incógnitas de OPT-001 (RGB, f/v, divisor, solape de haces, T_int) | Codex + JEV | 0,5 | Lectura | OPT-001 | Entrada en `DECISIONES.md` | Propuesta |
| 3 | EXP-001 | Cerrar la preinscripción: ecuaciones, tolerancias y umbrales T0-T6 | Codex; revisa Claude | 1 | Lectura | DEC-005 | `experimentos/EXP-001.md` cerrado | Propuesta |
| 4a | OPT-002 | Motor de amplitudes complejas + libro mayor de potencia en CPU | Codex | 3-4 | CPU ligera | EXP-001 | Código y pruebas unitarias | En espera |
| 4b | OPT-006 | Oráculo analítico independiente del MZ (fórmulas cerradas), en archivos separados | Claude | 1-1,5 | CPU ligera | EXP-001 | Calculadora + tabla de valores esperados | Hecho por Claude en `Blender/oracle/` (14/14); pendiente de revisión de Codex |
| 5 | OPT-002b | Ejecutar T0-T6 y comparar el motor con el oráculo (1e-12) | Codex; revisa Claude | 1-2 | CPU ligera | 4a, 4b | Informe con cifras | En espera |
| 6 | OPT-003 | Smoke Blender background CPU del MZ: guardar/reabrir (T7) | Codex | 1 | 1 proceso Blender, 1,5 GiB | 5 y margen de RAM | Informe runtime | En cola |
| 7 | OPT-004 | Comprobación manual del panel del addon | Codex | 0,5-1 | Interactivo | — | Nota de verificación | En cola |
| 8 | OPT-007 | Diseño de haz gaussiano diferenciable y malla 2×2 → 4×4 (Clements) | Claude diseña; Codex implementa | 2 diseño + 4 impl. | CPU ligera | 5 | Borrador de experimento EXP-002 | Idea en `THINKTANK.md` |
| — | OPT-005 | Aceleración GPU | Sin asignar | — | GPU | GPU libre + autorización | — | Pausada |

Total estimado hasta el MZ verificado en Blender (fases 2-6): **8,5-11 h** de
trabajo de agentes.

## Reglas comunes

- Cada ejecución o borrador declara qué hipótesis o parámetro cambia respecto
  del anterior y qué resultado lo refutaría.
- Si dos ejecuciones seguidas no cambian nada sustancial, o una tarea supera
  el doble de sus horas estimadas sin entregable, se anota en el tablón y se
  propone una tarea alternativa concreta a JEV.
- Al terminar una fase, actualizar la columna Estado y enlazar la evidencia.
