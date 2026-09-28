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
