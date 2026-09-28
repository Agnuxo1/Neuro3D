# Checkpoint factual de Neuro3D

Actualizado: 2026-09-28 20:55 UTC.

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
  geométricos, dos brazos, campos complejos y balance por canal. La suite
  inicial sumó 28 pruebas CPU/estáticas en 0,026 s. Coincide
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
- DEC-006 bloquea promoción y prueba confirmatoria MZ en Blender. JEV remoto
  confirmó el bloqueo y la secuencia de corrección. El motor sigue siendo
  experimental; el circuito monocamino previamente verificado no se invalida.
- OPT-009 entregó una referencia geométrica independiente. Sus 26 pruebas
  ligeras pasan; Codex reprodujo un MZ no rectangular de siete objetos con
  impactos coincidentes que cambia de B=1 a A=1 al mover M1 y el grupo del
  combinador. Un barrido de siete puntos coincide con el oráculo dentro de
  6,11e-15. No se ha probado en Blender ni corrige el error de fase para
  impactos distintos. DEC-007 permite añadirlo como regresión CPU previa
  a la corrección, sin levantar el bloqueo DEC-006.
- Claude añadió un diseño preliminar de malla OPT-007. Codex reprodujo solo
  sus comprobaciones aritméticas CPU (celda unitaria, 6 MZI/16 fases para 4×4,
  desplazamiento lateral 0,1616 BU); no hay malla ni entrenamiento ejecutados.
  La expansión queda en espera del MZ corregido. Un enlace detector→emisor
  sería optoelectrónico, no una capa puramente óptica.
- DEC-008: Codex añadió dos regresiones CPU. La no rectangular pasa y la
  cuadrada de impactos separados falló antes de la corrección: A≈0 cuando el
  oráculo independiente predice A=1. Tras transportar la fase a un punto
  común del plano de BS2, la cuadrada da A=1 y B≈3e-26; mover la referencia
  sobre ese plano no cambia el resultado. Se corrigió además la omisión de
  un brazo de potencia diminuta. Pasan 32 pruebas CPU/estáticas del área
  Blender y 26 del oráculo, ejecutadas por separado. Claude informó una
  revisión CPU adicional en el tablón a las 20:53 UTC. No se usó Blender.
- Dos consultas JEV remotas con `provenance=jev` aceptaron la reparación como
  diagnóstico CPU y mantuvieron el bloqueo físico/Blender: el umbral de
  solape todavía representa una aproximación de ondas planas, sin anchura de
  haz ni control incoherente. EXP-001 permanece borrador.

## Recursos y procesos

- GPU ocupada según el usuario; no iniciar ninguna tarea GPU.
- Sondeo de CPU/RAM/disco en `coordinacion/RECURSOS.md`.
- Ningún proceso Blender quedó tras el smoke anterior; no se ha iniciado
  ninguno en esta sesión de coordinación.
- Una invocación acotada de Claude Sonnet para OPT-001 agotó 60 s sin salida;
  fue interrumpida. Otros procesos Claude preexistentes no se tocaron.
- Archivo local no rastreado `Docs/assets/nebula-santo-grial-hero.png`:
  preservar y no añadir al repositorio público por accidente.
- El vigilante de este hilo estaba configurado solo para cambios nuevos; por
  eso no retomó OPT-002 aunque figuraba P0. Se corrigió su instrucción para
  continuar un paso CPU ligero cuando quede una tarea P0 concreta y el hilo
  esté inactivo; sigue evitando trabajo duplicado y GPU/Blender.

## Trabajo activo y siguiente paso

- `OPT-001` ya está entregada. `DEC-005` registra la revisión de Codex/JEV.
- `OPT-002` corrigió su subfase de referencia de fase en CPU. El adaptador
  sigue sin verificarse en Blender y `EXP-001-BORRADOR.md` debe cerrarse antes
  de pruebas confirmatorias. Las comprobaciones actuales son exploratorias.
- `OPT-003` queda bloqueada hasta especificar y probar solape espacial y
  coherencia/incoherencia, cerrar los controles CPU y disponer de recursos.
  Siguiente trabajo de Codex: control explícito de anchura de haz/solape y
  control incoherente, con balance de energía y criterios numéricos. Claude
  conserva el oráculo separado.

Leer al reanudar, en este orden: este archivo, `COLA-DE-TRABAJO.md`,
`TABLON.md`, `DECISIONES.md`, la tarea activa y el último informe técnico.
