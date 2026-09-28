# Checkpoint factual de Neuro3D

Actualizado: 2026-09-28 17:16 UTC.

## Objetivo

Desarrollar una red neuronal cuyo cálculo dependa de geometría y propiedades
ópticas en una escena 3D, primero en Blender y conservando las versiones
históricas de Unreal. Neuro3D es el nombre público; el nombre interno previo
no se usa como marca.

## Resultado confirmado

- Baseline de código publicado en `Agnuxo1/Neuro3D`, rama `main`, commit
  `732e908`. Para el estado publicado más reciente, consultar `git log`.
- Circuito de tres objetos verificado en Blender 4.5.14 LTS background CPU:
  intensidad 0,7053474966, activación 0,3657724623, cambios por geometría,
  reflectancia y frecuencia, persistencia en `.blend`.
- 18 pruebas Python CPU/estáticas superadas en la última ejecución registrada.
- Informe y límites en `Docs/BLENDER_RUNTIME_REPORT.md` y
  `Docs/BLENDER_ARCHITECTURE.md`.
- No existe aún acumulación coherente multirrayo ni red óptica completa.

## Recursos y procesos

- GPU ocupada según el usuario; no iniciar ninguna tarea GPU.
- Sondeo de CPU/RAM/disco en `coordinacion/RECURSOS.md`.
- Ningún proceso Blender quedó tras el smoke anterior; no se ha iniciado
  ninguno en esta sesión de coordinación.
- Una invocación acotada de Claude Sonnet para OPT-001 agotó 60 s sin salida;
  fue interrumpida. Otros procesos Claude preexistentes no se tocaron.
- Archivo local no rastreado `Docs/assets/nebula-santo-grial-hero.png`:
  preservar y no añadir al repositorio público por accidente.

## Trabajo activo y siguiente paso

- `OPT-001`: revisión de óptica por Claude, de solo lectura y con una única
  respuesta estructurada. Pendiente: la CLI no respondió; el arranque manual
  está en `CLAUDE_BOOTSTRAP.md`.
- JEV indicó preparar un contrato falsable sin fijar aún ecuaciones disputadas.
  Codex creó `experimentos/EXP-001-BORRADOR.md`; la implementación de
  `OPT-002` espera la auditoría OPT-001 y una decisión documentada.
- `OPT-003` prueba real Blender solo cuando el modelo CPU tenga controles
  constructivo, destructivo e incoherente y el PC disponga de margen.

Leer al reanudar, en este orden: este archivo, `COLA-DE-TRABAJO.md`,
`TABLON.md`, `DECISIONES.md`, la tarea activa y el último informe técnico.
