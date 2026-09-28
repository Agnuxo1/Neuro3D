# Checkpoint factual de Neuro3D

Actualizado: 2026-09-28 19:01 UTC.

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
- La línea base publicada `732e908` no contiene acumulación coherente
  multirrayo ni una red óptica completa; el prototipo local nuevo se describe
  por separado a continuación.

## Avance nuevo aún no promocionado

- Claude entregó `respuestas/OPT-001.json`; Codex comprobó las referencias
  principales. JEV confirmó el Mach–Zehnder de dos puertos como siguiente
  prototipo, con RGB como canales etiquetados y un control de solape obligatorio.
- `Blender/core/mz_scene.py` implementa un primer motor CPU de siete objetos
  geométricos, dos brazos, campos complejos y balance por canal. Diez pruebas
  nuevas pasan; la suite CPU completa suma 28 pruebas en 0,026 s. Coincide
  numéricamente con el oráculo independiente de Claude en 144 combinaciones
  (error máximo 4,72e-15). Coincidencia entre modelos, no prueba física.
- `Blender/addon/neuro3d/mz_scene_adapter.py` crea/lee objetos Blender y
  escribe resultados, pero solo se ha importado estáticamente; no se ha
  ejecutado dentro de Blender ni comprobado guardar/reabrir.
- El control de interferencia por geometría y el incoherente aún faltan. Si
  dos modos no se solapan en el combinador, el prototipo marca su potencia como
  `unresolved` y no afirma interferencia.
- `OPT-008` ya entregó nueve hallazgos. Codex reprodujo el fallo alto de
  referencia de fase al combinar impactos distintos y el residuo de un brazo
  diminuto omitido. En el montaje cuadrado, mover el vértice común manteniendo
  impactos coincidentes no cambia la diferencia de caminos.
- DEC-006 bloquea promoción, prueba confirmatoria MZ en Blender y afirmación
  de interferencia geométrica. JEV remoto confirmó el bloqueo y la secuencia
  de corrección. El motor publicado sigue siendo experimental; el circuito
  monocamino previamente verificado no se invalida.

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

- `OPT-001` ya está entregada. `DEC-005` registra la revisión de Codex/JEV.
- `OPT-002` tiene un primer motor CPU y adaptador no verificado en Blender.
  `EXP-001-BORRADOR.md` debe cerrarse antes de las pruebas confirmatorias;
  las comprobaciones CPU realizadas hasta ahora son exploratorias.
- `OPT-003` queda bloqueada hasta corregir fase/solape, cerrar los controles
  CPU y disponer de margen de recursos. `OPT-009` pide a Claude una referencia
  geométrica independiente; Codex conserva la implementación del motor.

Leer al reanudar, en este orden: este archivo, `COLA-DE-TRABAJO.md`,
`TABLON.md`, `DECISIONES.md`, la tarea activa y el último informe técnico.
