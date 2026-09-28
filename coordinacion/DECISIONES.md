# Decisiones de Neuro3D

## DEC-001 · 2026-09-28 · Trabajo conjunto

- **Decisión:** Codex coordina, implementa y verifica; Claude aporta una
  revisión independiente por archivos; JEV aconseja las decisiones sustanciales.
- **Evidencia:** petición explícita del usuario y resultados actuales en
  `Docs/BLENDER_RUNTIME_REPORT.md`.
- **Responsable:** Codex.
- **Reversión:** cambiar el reparto solo si una vía falla o duplica trabajo;
  registrar el cambio y la causa aquí.

## DEC-002 · 2026-09-28 · Prioridad técnica y asignación

- **JEV:** consulta v2 con `exit_code=0`, `status=connected`,
  `provenance=jev`, modelo `jev-1.13.0`.
- **Decisiones:** primero acumulación coherente de varios caminos en CPU
  gobernada por la escena (confianza 1.0); Claude audita ecuaciones,
  conservación de energía, coherencia y prueba de dos caminos en solo lectura
  (1.0); Sonnet para esa auditoría (0.98).
- **Ruta JEV adicional:** `router.py plan` `1790615203-design`, ejecutor
  principal Codex, esfuerzo alto, sin división paralela automática.
- **Evidencia:** `coordinacion/jev/inicio-20260928-state.json` y
  `coordinacion/jev/inicio-20260928-questions.json`, con recibo compacto en
  `coordinacion/jev/inicio-20260928-result.json`; respuesta v2 verificada
  por Codex. JEV aconseja, no sustituye las pruebas.
- **Responsable:** Codex; Claude para `OPT-001`.
- **Reversión:** si la revisión identifica un error de modelo o una prueba
  falsable imposible con la representación actual, volver a diseño antes de
  programar o promocionar resultados.

## DEC-003 · 2026-09-28 · Recursos

- **Decisión:** ninguna prueba GPU local mientras el usuario indique que está
  ocupada; CPU solo para tareas pequeñas y con límites.
- **Evidencia:** instrucción explícita del usuario; sondeo no invasivo de RAM,
  CPU y disco registrado en `coordinacion/RECURSOS.md`.
- **Responsable:** Codex.
- **Reversión:** autorización posterior y medición de recursos disponibles.

## DEC-004 · 2026-09-28 · Recuperación tras timeout de Claude

- **JEV:** consulta v2 con `exit_code=0`, `status=connected` y
  `provenance=jev`; recibo en
  `coordinacion/jev/claude-timeout-20260928-result.json`.
- **Decisión:** Codex redacta únicamente el contrato falsable provisional de
  EXP-001 y las métricas baseline; no fija aún las ecuaciones controvertidas
  ni ejecuta el experimento (confianza 1.0). OPT-001 queda en el buzón y se
  usa el arranque manual de Claude en una siguiente sesión, sin otro intento
  CLI automático ahora (confianza 1.0).
- **Evidencia:** un intento de Claude Sonnet de solo lectura no produjo salida
  en 60 s y fue interrumpido; no existe respuesta JSON.
- **Responsable:** Codex.
- **Reversión:** al recibir una respuesta Claude verificable, reevaluar el
  contrato y fijar umbrales antes de cualquier experimento.

## DEC-005 · 2026-09-28 · Primera arquitectura multirrayo

- **Revisión:** Claude entregó `respuestas/OPT-001.json`. Codex comprobó su
  estructura, contrastó las observaciones principales con `scene_optics.py` y
  ejecutó las 14 autocomprobaciones CPU del oráculo (0,009 s). La respuesta
  contiene propuestas, no un resultado experimental de Blender.
- **JEV:** consulta v2 remota con `exit_code=0`, `status=connected` y
  `provenance=jev`, modelo `jev-1.13.0`; recibo en
  `jev/revision-opt-001-20260928-result.json`.
- **Decisión:** prototipo Mach–Zehnder de dos salidas, objetos explícitos,
  campos escalares complejos y balance de potencia por canal. RGB son canales
  de potencia etiquetados con una frecuencia común, no longitudes de onda
  físicas. Separar el control por `phase_shift` del control por geometría; no
  reclamar interferencia geométrica si los modos no llegan solapados al
  combinador. El oráculo de Claude es referencia provisional hasta compararlo
  con un motor independiente gobernado por la escena.
- **Caveats:** el oráculo usa `t_arm=0` tanto para pérdida como para camino
  roto; el motor debe distinguir pérdida material de potencia escapada. Las
  autocomprobaciones y la coincidencia analítica no prueban aún Blender ni
  propagación electromagnética real.
- **Responsable:** Codex. **Reversión:** corregir el modelo si la prueba real
  de objetos Blender o un control externo refuta estos supuestos.

## DEC-006 · 2026-09-28 · Bloqueo de promoción tras OPT-008

- **Evidencia:** Claude entregó `respuestas/OPT-008.json`. Codex reprodujo
  con `D:\PROJECTS\.cognition\neuro3d\opt-008\phaseref.py` que, para tres
  longitudes de onda, el motor calcula una diferencia de camino de una
  longitud de onda entre impactos distintos en BS2, mientras la fase llevada
  a un frente de onda común da media longitud de onda. `edge.py` reprodujo
  un residuo de 1,67e-10 por canal cuando se omite un brazo no nulo pequeño,
  y la igualdad de caminos del montaje cuadrado. No se ejecutó Blender.
- **JEV:** consulta v2 con `exit_code=0`, `status=connected` y
  `provenance=jev`; recibo `jev/opt-008-triage-20260928-result.json`.
- **Decisión:** bloquear la promoción de EXP-001, la prueba confirmatoria MZ
  en Blender y cualquier afirmación de interferencia geométrica hasta corregir
  la referencia de fase y el solape. Conservar el baseline monocamino. Codex
  hará primero una regresión CPU falsable de frente de onda, luego la
  corrección y la comparación CPU entre geometría no rectangular y línea de
  retardo. Claude prepara una referencia geométrica separada (`OPT-009`).
- **Alcance:** las pruebas previas de fase por propiedad y balance en escenas
  ideales siguen siendo diagnósticas, no prueban la geometría a fase. Las
  observaciones de Blender en OPT-008 son inferencias aún sin ejecución.

## DEC-007 · 2026-09-28 · Regresión no rectangular antes de corregir fase

- **Evidencia:** Claude entregó `respuestas/OPT-009.json` y un oráculo
  geométrico separado. Codex ejecutó sus 26 pruebas CPU (0,010 s) y reprodujo
  `minimal_edit.py`: un MZ no rectangular de siete objetos cambia de B=1 a
  A=1 al mover M1 y el grupo combinador/detectores, manteniendo los impactos
  coincidentes; residuo 1,1e-16. Un barrido de siete posiciones coincidió con
  el oráculo dentro de 6,11e-15. No se ejecutó Blender.
- **JEV:** consulta v2 con `exit_code=0`, `status=connected` y
  `provenance=jev`; recibo `jev/opt-009-review-20260928-result.json`.
- **Decisión:** añadir este caso como regresión diagnóstica CPU, junto con el
  contraejemplo cuadrado que debe fallar hasta corregir la referencia de fase.
  Después corregir fase y solape. El MZ no rectangular es el primer candidato
  para una futura prueba confirmatoria de geometría; la línea de retardo queda
  como control cruzado posterior. OPT-009 es referencia provisional de ondas
  planas, no validación de Blender ni de física electromagnética completa.
- **Gate inalterado:** DEC-006 sigue bloqueando promoción y prueba MZ en
  Blender hasta que los dos controles pasen, el contrato esté cerrado y haya
  margen de recursos. Codex implementa y verifica el motor.

## DEC-008 · 2026-09-28 · Fase corregida en CPU; promoción aún bloqueada

- **Regresiones:** se añadió el MZ no rectangular de siete objetos, que pasa
  antes y después del cambio, y el contraejemplo cuadrado con impactos
  separados. Este último falló antes de la corrección: A≈0 frente a A=1
  predicho por el oráculo. Después, el motor transporta cada fase desde su
  impacto hasta un punto común del plano de BS2; el caso da A=1 y B≈3e-26.
  Deslizar el punto de referencia sobre el mismo plano deja las salidas
  invariantes. También se contabiliza un brazo no nulo de potencia diminuta.
- **Verificación:** 32 pruebas CPU/estáticas del área Blender y 26 del oráculo
  pasan por separado. Claude informó una revisión CPU independiente en el
  tablón a las 20:53 UTC; la suite propia de Codex y el caso rojo-verde son
  evidencia separada. No se ejecutó Blender, render ni GPU.
- **JEV:** dos consultas v2 con `exit_code=0`, `status=connected` y
  `provenance=jev`; recibos `jev/opt-002-phase-20260928-result.json` y
  `jev/opt-002-next-gate-20260928-result.json`.
- **Decisión:** la subfase de referencia de fase de OPT-002 queda corregida
  como diagnóstico CPU. `overlap_tolerance` continúa siendo una compuerta
  idealizada de ondas planas, no una medida de solape espacial de haces.
  DEC-006 sigue bloqueando promoción, afirmaciones físicas y prueba MZ en
  Blender. Próximo paso: especificar y probar control de anchura/solape y
  coherencia frente a incoherencia, con balance de energía; cerrar EXP-001
  antes de cualquier ejecución confirmatoria en Blender.
