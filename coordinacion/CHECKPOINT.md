# Checkpoint factual de Neuro3D

Actualizado: 2026-09-28 22:19 UTC.

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
- 18 pruebas Python CPU/estáticas superadas en la línea base EXP-000 original.
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
- El prototipo inicial no tenía controles de solape/coherencia; el estado
  actual de OPT-002 con esos controles se resume más abajo. Si dos modos no
  pasan sus compuertas de geometría, su potencia queda `unresolved`.
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
- Claude entregó `Blender/oracle/overlap_cases.py` y
  `expected_overlap_coherence.json` como referencia preliminar separada para
  el paso siguiente. Codex verificó en CPU ligera que el JSON coincide con el
  generador; cuatro casos de anchura cierran potencia, nueve casos
  incoherentes son independientes de la fase y una fórmula cerrada separada
  reproduce los cuatro puertos/solapes con error máximo 0. Los archivos del
  oráculo se conservan separados del motor y se incluyen como referencia, no
  como validación física.
- OPT-002 solape/coherencia (21:34 UTC): el motor admite anchura de haz
  constante opcional y coherencia mutua declarada. Calcula separación
  transversal entre modos de salida y solape gaussiano, mezcla puertos
  coherentes/incoherentes conservando energía y exige que ambos rayos alcancen
  cada detector; si no, deja la potencia sin resolver. El adaptador expone las
  propiedades, pero no se ejecutó en Blender. Pasan 41/41 pruebas CPU/estáticas
  y 26/26 del oráculo. Los casos nuevos cubren tres anchuras, nueve escenas
  incoherentes, g=0,4, puertos asimétricos, parámetros inválidos y compuertas.
  JEV remoto `provenance=jev` aprobó el alcance y mantuvo el bloqueo físico.
  Claude informó un barrido independiente de 3000 escenas sobre una versión
  anterior al nuevo control de detectores; pidió contrastar puertos asimétricos
  y Codex añadió esa regresión. Informe para re-revisión en
  `coordinacion/INFORME-OPT-002-SOLAPE-CPU.md`.
- DEC-009: Codex revisó los scripts y la propuesta de preinscripción de
  Claude; JEV remoto `provenance=jev` recomendó aceptarla con ajustes. El
  contrato vigente es `coordinacion/experimentos/EXP-001-PREINSCRIPCION.md`:
  A/B-geo/B-mat/C/D primarios, E/F secundarios, umbrales CPU 1e-12 y
  Blender 1e-9 congelados antes de medir. La exploración CPU previa no cuenta
  como prueba confirmatoria. No se ejecutó Blender.
- Claude entregó OPT-010 con atribuciones falsas de detectores y un
  contraejemplo para la compuerta fija 0,02 BU. Codex ejecutó el script y
  reprodujo los casos; observó que el ejemplo original de «oclusión» también
  encierra el origen BS2, y añadió una variante que aísla la oclusión.
  DEC-010, supervisada por JEV remoto, exige la primera esfera de detector
  positiva y rechaza origen encerrado/empates; con anchura positiva usa
  `mode_overlap≥0,01`, conservando el umbral 0,02 BU solo en modo ideal.
  Pasan 47/47 CPU/estáticas, 26/26 oráculo y 3000/3000 casos asimétricos
  contra el oráculo de Claude (error máximo 6,495e-14). La geometría del
  empty padre del adaptador pasa un test simulado, no Blender real. Informe
  `INFORME-OPT-010-GATE-CPU.md` y reauditoría OPT-011 solicitada a Claude.
  El contrato EXP-001 se enmendó antes de Blender sin cambiar umbrales.
- Claude entregó OPT-011: aceptó la corrección del motor dentro del alcance
  CPU (barrido propio de 20.000 escenas sin atribución falsa), pero halló que
  el adaptador no construía `NonRectMZ(60)` ni existía runner MZ de Blender.
  Codex añadió `create_mz_circuit(..., layout="nonrect60")` con geometría
  cerrada independiente del oráculo, frecuencia 100, anchura 0,2 y detectores
  bajo el grupo. La nueva prueba estática compara posiciones y normales con
  `NonRectMZ(60,2,2)`; pasan 49/49 pruebas CPU/estáticas. No se abrió Blender.
  Queda pendiente revisión independiente de Claude del constructor y crear
  un runner A–D de guardar/reabrir; no confundir esto con validación runtime.
- Claude revisó después `nonrect60` con bpy simulado y la referencia
  `NonRectMZ`: diferencias de posiciones/normales 0,0; una escena reconstruida
  da A: B=1 y B-geo: A=1. Entregó los desplazamientos B-geo del grupo
  `(0,2799038106, 0,1616025404, 0) BU` y de M1
  `(0,1866025404, 0, 0) BU`. Codex leyó su script y añadió el plan puro
  `Blender/tests/mz_exp001_plan.py` con A, B-geo, B-mat, tres controles C y D;
  una prueba independiente verifica el desplazamiento contra `NonRectMZ`.
  Pasan 51/51 pruebas CPU/estáticas. El README ya no afirma que el error
  antiguo de fase siga presente. Aún NO existe runner runtime MZ.
- Claude detectó una ambigüedad del giro D: +10° sobre +Z da
  `missed_bs2`, −10° da `missed_bs2_aperture`, con iguales potencias. JEV
  remoto (`provenance=jev`) eligió fijar +10° alrededor del Z mundial antes
  de Blender (DEC-011). El contrato y el plan lo explicitan; la nueva prueba
  CPU confirma status y potencias. 52/52 pruebas ligeras; no Blender/GPU.

## Recursos y procesos

- GPU ocupada según el usuario; no iniciar ninguna tarea GPU.
- Sondeo de CPU/RAM/disco en `coordinacion/RECURSOS.md`.
- Ningún proceso Blender quedó tras el smoke anterior; no se ha iniciado
  ninguno en esta sesión de coordinación.
- Una invocación acotada de Claude Sonnet para OPT-001 agotó 60 s sin salida;
  fue interrumpida. Otros procesos Claude preexistentes no se tocaron.
- Archivo local no rastreado `Docs/assets/nebula-santo-grial-hero.png`:
  preservar y no añadir al repositorio público por accidente.
- El vigilante de este hilo se actualizó para avanzar en cada ciclo seguro
  y entregar a Claude un informe/petición concreta en el tablón; ya no espera
  solo cambios nuevos. Evita duplicar trabajo y no usa GPU/Blender.

## Trabajo activo y siguiente paso

- `OPT-001` ya está entregada. `DEC-005` registra la revisión de Codex/JEV.
- `OPT-002` tiene fase, solape/coherencia y primer detector implementados en
  CPU; OPT-011 acepta acotadamente el motor. El adaptador sigue sin verificarse
  en Blender. Las comprobaciones actuales son exploratorias.
- `OPT-003` queda bloqueada. DEC-009 cerró el contrato pre-Blender y DEC-010
  lo enmendó antes de ejecutar. Constructor revisado solo con bpy simulado;
  falta runner MZ A–D, verificación runtime del empty padre y margen de
  RAM/autorización del usuario.
  No se permite Blender/GPU.

Leer al reanudar, en este orden: este archivo, `COLA-DE-TRABAJO.md`,
`TABLON.md`, `DECISIONES.md`, la tarea activa y el último informe técnico.
