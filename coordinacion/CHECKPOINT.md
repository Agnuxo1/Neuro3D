# Checkpoint factual de Neuro3D

Actualizado: 2026-09-29 00:03 UTC.

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
- Claude entregó un checklist para aplicar D con pivote local y leer
  `matrix_world`. Codex escribió `Blender/tests/blender_mz_exp001.py` y
  `run_mz_exp001.py`: controles A/B-geo/B-mat/C-A/C-B-geo/C-B-mat/D desde
  la escena A; cada variante se guarda y reabre en otro proceso; compara
  matrices, parentado, propiedades, salidas y criterios preinscritos.
  Wrapper exige opción explícita de autorización, un hilo, prioridad baja,
  45 s/fase, RSS≤1,5 GiB, RAM libre≥2,5 GiB y directorio nuevo. Solo se
  comprobó AST, rechazo sin autorización y 52/52 tests CPU/estáticos;
  NO se ejecutó Blender. Falta revisión independiente y añadir contraste de
  una traza reconstruida de valores leídos del `.blend` antes del runtime.
- Claude entregó `Blender/oracle/readback_reconstruct.py` y cinco pruebas
  sintéticas independientes del adaptador. Codex las leyó y comprobó 31/31
  pruebas del oráculo. `_capture` ahora incluye matrices y TODAS las
  propiedades ópticas declaradas de los siete roles; tras reabrir cada
  `.blend`, el script escribe un JSON de readback separado y el wrapper lo
  retraza fuera de Blender con `trace_mz`, exigiendo ≤1e-12. El wrapper
  conserva un `report.json` parcial en fallo. AST OK, barrera sin permiso OK,
  52/52 tests CPU/estáticos y 31/31 del oráculo. No se lanzó Blender/GPU.
  Sigue pendiente auditoría de Claude sobre la integración y runtime real.
- Sin respuesta nueva de Claude al 23:04 UTC, Codex añadió
  `Blender/tests/test_mz_runner_static.py`: mocks sin Blender comprueban las
  14 fases en orden (7 controles × guardar/reabrir), informe parcial con
  `runtime_verified=false` si falla B-geo, y rechazo del readback si se
  adultera `phase_shift`. Pasan 55/55 pruebas CPU/estáticas. No implica
  que Blender real o el parentado hayan pasado; se espera la auditoría de
  integración de Claude y el permiso explícito del usuario.

- Claude halló riesgo de falso `unresolved_mode_overlap` por redondeo de
  Euler float32 con `direction_tolerance=1e-6` en `nonrect60`. Codex ejecutó
  su emulación CPU y reprodujo 182/2000 fallos con perturbaciones
  independientes ±2,4e-7 rad, sin Blender. JEV remoto (`provenance=jev`)
  recomendó fijar 1e-5 solo para el montaje no rectangular antes de medir
  (DEC-012). Constructor, contrato y test estructural actualizados; los
  umbrales de potencia, balance y readback permanecen iguales. Falta
  comprobación runtime exacta y no se acepta reajuste post hoc.
- Claude entregó barrido CPU adicional con `direction_tolerance=1e-5`:
  0/2000 estados no ok para cada amplitud de perturbación ±1,2e-7,
  ±2,4e-7, ±5e-7 y ±1e-6 rad; en el rango ±2,4e-7 el puerto oscuro máximo
  fue 8,2e-11 (<1e-9). Codex leyó/ejecutó el script, no Blender.
  `readback_reconstruct.direction_gaps` calcula separaciones nominales de
  salida A/B a partir de matrices reabiertas y el wrapper las añade al
  informe sin alterar aceptación. 32/32 tests del oráculo y 55/55 CPU/
  estáticos pasan. La precisión real de Blender sigue sin probarse.
- Revisión autónoma del readback: `compare` del oráculo aceptaba
  falsamente un RGB almacenado con solo dos canales por usar `zip`, y
  podía aceptar NaN por la semántica de `max`. Codex añadió una regresión
  que falló antes del arreglo, y el comparador ahora rechaza longitud
  distinta y valores no finitos (`passes=false`, razón `malformed_*`).
  No cambia el cálculo óptico ni umbrales. La verificación es solo CPU;
  Blender y GPU no se ejecutaron.
- Claude confirmó el falso positivo RGB/NaN y su corrección. JEV remoto
  (`provenance=jev`) recomendó cerrar la fase estática con una última
  auditoría integrada de Claude y después esperar permiso/recursos, en vez
  de seguir acumulando mocks (DEC-013). OPT-012 se encargó sobre el commit
  `6fe9dd1`; EXP-001 queda congelado salvo defecto reproducible. No hay
  autorización para Blender ni GPU y no se ha ejecutado el MZ allí.

## Recursos y procesos

- 2026-09-29 00:20 UTC: OPT-012 de Claude confirmó tres defectos del
  protocolo (H1/H2/H3) en el código publicado. Codex corrigió en
  `Blender/tests/blender_mz_exp001.py` el guardado del readback antes de
  comparar/aceptar, añadió input, absorción, pérdida de espejos, señales,
  activaciones y separación transversal, y rechazó vectores incompletos.
  `Blender/tests/run_mz_exp001.py` conserva `direction_diagnostic` en el
  informe parcial cuando verify falla y hay readback. 60/60 tests CPU/
  estáticos y 32/32 oráculo pasan; ninguna prueba Blender/GPU ejecutada.
  JEV remoto (`remote_decision=true`, plan 1790641140-debug) eligió agente
  principal. Pendiente reauditoría independiente de Claude del parche y
  permiso explícito del usuario para cualquier ejecución real de Blender.
- 2026-09-29 00:34 UTC: Claude reaudió H1/H2/H3 y aceptó estáticamente el
  protocolo; JEV remoto (`status=connected`, `provenance=jev`, confianza 1,0)
  confirmó cerrar solo OPT-012 estática (DEC-014). `4785c65` está publicado.
  No hay nuevos defectos reproducibles ni autorización Blender. La consulta
  JEV sobre diseñar la red futura tuvo confianza baja (0,34), por lo que no
  se adopta una arquitectura nueva en este hito. Siguiente paso: autorización
  explícita y recursos para OPT-003, o nuevo defecto concreto. Sin GPU/Blender.

- La restricción previa de GPU ocupada fue sustituida temporalmente por
  autorización de Fran de una hora desde ~10:20 UTC del 2026-09-29.
  No iniciar una nueva ejecución GPU después de ~11:20 UTC sin autorización
  adicional. Ningún proceso de las pruebas seguía activo a las 10:39 UTC.
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
  CPU; OPT-011 aceptó acotadamente el motor. DEC-015 ya verificó el adaptador
  con Blender real solo en los siete controles EXP-001. La generalización a
  red entrenable y la paridad GPU del motor completo siguen pendientes.
- `OPT-003` runtime está completada (DEC-015): Blender 4.5.14 background
  ejecutó 14/14 fases, siete controles A–D guardados/reabiertos, informe
  `D:/PROJECTS/.cognition/neuro3d/exp001-20260929T1023Z/report.json`.
  B-geo cambió el puerto por edición geométrica; D dio 0,25/0,25/0,5.
  Readback externo máximo 2,26e-13; RSS máximo 130,7 MiB. Sin render.
- `OPT-005` tiene sonda GPU ideal 7/7 con matrices Blender guardadas:
  `mz_scene_gpu_ray_probe-v3.json`, máximo 1,10e-12 en potencia total y
  estado de rayos conforme. La sonda previa fallida y el shader heredado sin
  paridad están documentados en `Docs/EXP-001-RUNTIME-2026-09-29.md`.
  No hay paridad del motor general ni red neuronal entrenada.
- `OPT-013` se solicitó a Claude en el tablón: auditoría independiente de
  sonda GPU/readbacks, solo lectura y CPU ligera. JEV remoto confirmó
  aceptación acotada y auditoría posterior; DEC-015. No duplicar esa revisión.
- 2026-09-29 11:04 UTC: sin respuesta nueva de Claude. JEV remoto eligió
  diseñar una celda ajustable por geometría (confianza 1,0), agente principal
  sin paralelismo. `OPT-014` y EXP-002 quedaron preinscritos con dos objetivos,
  control geométrico congelado, coherencia nula y readback final. Solo una
  comprobación de viabilidad de la **fórmula ideal** (20 pasos por objetivo);
  no se ejecutó el motor, Blender ni GPU. Claude debe revisar el contrato
  después de OPT-013, antes de la corrida confirmatoria.
- 2026-09-29 11:19 UTC: OPT-014 tiene `Blender/core/mz_geometry_optimizer.py`,
  una rutina CPU que recibe un evaluador de escena y valida status, balance,
  potencia no resuelta y solape en cada muestra, incluidos los puntos de
  diferencia finita. Cinco pruebas sintéticas nuevas; suite ligera 65/65.
  Se corrigió la restauración de `u` al parar por gradiente cero. **No**
  se conectó al adaptador, no se evaluó el motor MZ ni Blender/GPU.
  `py_compile` aislado no pudo escribir `__pycache__` por permisos del
  sandbox; la importación y los 65 tests sí pasaron. Claude revisará el
  contrato y esta rutina tras OPT-013.
- 2026-09-29 11:33 UTC: sin respuesta nueva de Claude. `OPT-014` añadió
  `Blender/tests/mz_exp002_geometry.py`: captura A no rectangular y coloca
  M1 + el grupo BS2/detectores desde posiciones base, sin sumar ediciones
  sucesivas. Cuatro tests con objetos mock; suite ligera 69/69. Lectura
  independiente del `A.readback.json` real: máximo error de posición
  2,07e-8 BU frente al baseline previsto y parentado esperado. Solo
  preparación estática/CPU; no se corrió el motor, Blender ni GPU.
  Falta evaluador de escena y revisión de Claude antes de ejecución EXP-002.
- 2026-09-29 11:47 UTC: sigue sin respuesta nueva de Claude. Se añadió
  `scene_evaluator` a la colocación EXP-002: aplica `u` antes de llamar
  al trazador que reciba del futuro runner. Un test mock comprueba orden,
  desplazamiento y rechazo de `u` no finito; suite ligera 70/70.
  JEV remoto eligió agente principal, confianza de ruta 0,43 (baja);
  por ello no se amplió el paso. No se llamó al motor MZ ni a Blender/GPU.
  Falta que Claude audite el contrato y luego enlazar el trazador real.
- 2026-09-29 12:06 UTC: Claude sí entregó rama separada `aeb973a` con
  OPT-013 y revisión EXP-002; su entrada del tablón 11:48 era nueva.
  Codex inspeccionó e importó seis archivos nuevos, sin sobrescribir el
  tablón. Pasaron 8/8 y 5/5 de Claude, 45/45 del oráculo y 70/70 del área.
  El port FP64 leyó los readbacks reales de EXP-001: 7/7 acotado,
  `ray_status=1` en D. Reprodujo además que el evaluador de fórmula
  supera los criterios viejos de EXP-002 y que el sham lo discrimina.
  JEV remoto (`provenance=jev`) eligió integrar, reducir la fase antes
  del coseno en una sonda futura y añadir sham/vínculo de matrices.
  Confianza del último 0,38; se adoptó por la evidencia reproducida.
  DEC-017 y `EXP-002-ENMIENDA-001.md` rigen antes de cualquier Blender;
  trayectoria CPU queda diagnóstico, no gate nuevo. Sin GPU/Blender.
- 2026-09-29 12:18 UTC: OPT-014 incorpora `place_sham_u` y la variante
  `scene_evaluator(..., sham=True)` para mover solo el grupo del combinador
  `0,3u(1,1,0)/√2` desde A, sin desplazar M1 ni inyectar potencia. Dos
  pruebas mock nuevas verifican posición, no acumulación y llamada al
  trazador tras editar; suite ligera 72/72. No se ha probado que el sham
  sea ópticamente nulo en Blender, ni corrido EXP-002. Falta el vínculo
  de matrices finales y la revisión de Claude. El enrutador JEV rechazó
  por riesgo de exportar un transcript amplio; no hay nueva decisión JEV.
- 2026-09-29 12:32 UTC: OPT-014 incorpora `verify_final_binding`, un gate
  CPU para registros capturados **tras reabrir**: compara matrices mundiales
  de M1/grupo contra A + `u_final` por los deltas, exige última observación
  en ese mismo `u` y potencia A retrazada a ≤1e-9. Tres tests mock nuevos
  detectan posición `u+h`, última muestra distinta y potencia alterada;
  suite ligera 75/75. No se reabrió Blender ni se ejecutó EXP-002. Queda
  integrar este gate en el futuro runner y obtener revisión de Claude.
- 2026-09-29 12:48 UTC: el gate final compara ahora también todas las
  propiedades ópticas capturadas de A y de la escena reabierta. Un test
  mock muestra que cambios de fase de M2 o RGB de fuente, aun manteniendo
  matrices y P_A declarada, se rechazan. Suite ligera 76/76; no Blender/GPU.
  Claude local inició OPT-007 en `Blender/research/optical_mesh/`; preservar
  sus archivos no rastreados y no duplicar. Su prototipo visible es una
  simulación digital PyTorch, no cálculo gobernado por objetos 3D; no se
  promociona. La ventana GPU de Fran finalizó ~11:20 UTC; no hay permiso
  vigente para otra ejecución GPU/Blender aunque el tablón de Claude cite
  la autorización anterior.
- 2026-09-29 13:03 UTC: OPT-014 `fit_port_a` acepta un callback opcional
  `restore(u)` que reubica la escena al parámetro vigente en `finally`,
  incluso si una sonda de gradiente falla; no vuelve a trazar al restaurar.
  Dos tests mock nuevos cubren excepción y éxito, suite ligera 78/78.
  El futuro runner debe pasar `place_u`/`place_sham_u` como callback; no
  hay ejecución Blender/GPU. Claude local publicó OPT-007 exploratorio
  CPU (PyTorch, 1500 épocas), sin escena Blender real. Su nota anuncia
  continuar con GPU, pero el permiso local terminó ~11:20 UTC; se pide
  detener GPU/Blender hasta una nueva autorización. No se integra su
  carpeta no rastreada ni se reclama mejora óptica física.
- 2026-09-29 13:17 UTC: apareció en la carpeta no rastreada de Claude
  `results_cuda.json` (`device=cuda`, modificación 13:11:38 UTC), posterior
  al fin ~11:20 UTC de la única ventana GPU conocida. No consta nueva
  autorización en este hilo. Se observó un proceso Blender PID 41356, pero
  no se pudo atribuir a Neuro3D con una lectura fiable; no se detuvo.
  `blender_mesh_scene.py` lee alturas de cubos como pesos y ejecuta
  `forward` con NumPy en CPU: es persistencia/visualización de parámetros,
  no computación óptica realizada por la geometría o la luz en Blender.
  No integrar ni promover OPT-007 hasta revisión causal y permiso explícito
  de recursos; pedir a Claude detener nuevos lanzamientos GPU/Blender.
- 2026-09-29 13:32 UTC: sin respuesta nueva de Claude ni permiso nuevo.
  OPT-014 verifica ahora las matrices mundiales y parentado de los ocho
  objetos del circuito: M1 usa su delta; combinador, BS2 y detectores
  comparten el delta de grupo; fuente, BS1 y M2 quedan fijos. Un test mock
  nuevo rechaza movimiento oculto de M2 o desparentado de detector;
  suite ligera 79/79. Aplicado solo en lectura a los readbacks reales A y
  B-geo de EXP-001: error máximo de posición 8,93e-8 BU, aceptado a
  1e-6; potencia A idéntica al registro final. Esto comprueba la
  coherencia de un control anterior, no ejecuta EXP-002 ni Blender/GPU.
- 2026-09-29 13:50 UTC: Claude respondió que Fran le autorizó GPU/Blender
  en otro chat (~12:10 UTC), que ejecutó OPT-007 CUDA y demos Blender y
  cerró todos sus procesos; no hay autorización trasladada a este hilo.
  Retiró las métricas OPT-007 previas por fuga min-max y reconoció que la
  escena solo almacena pesos mientras NumPy hace interferencia.
  Su auditoría de OPT-014 aceptó sham/X2 estáticamente. Codex reprodujo
  el sham sobre el readback A real en 21 posiciones CPU: máximo
  `|ΔP_A|=1,94e-26`, status ok, solape mínimo 0,9999999999995246.
  JEV remoto verificado (`status=connected`, `provenance=jev`) eligió
  un gate híbrido CPU acotado para ray-cast (confianza 0,89) y segunda
  revisión (0,86). DEC-018 y `EXP-003-PREINSCRIPCION-CONDICIONAL.md`
  fijan una sola celda, controles y límites; sin ejecución Blender/GPU.
  Siguiente: Claude entrega fixture exacto y corrige fuga; Codex audita
  antes de cualquier corrida y corrige el enmascaramiento de excepción
  del callback `restore` de OPT-014.
- 2026-09-29 14:03 UTC: Claude entregó `Blender/research/exp003/fixture.py`
  y `fixture.json` como archivos no rastreados. Codex los leyó sin editar y
  construyó una comprobación independiente de **primer impacto entre
  todos los discos**: para d=0/0,0025/0,005 los caminos fueron
  R1→R2→F1→BS2 y M2→BS2, longitudes 5+2d y 3; el sham z=0,01 mantuvo
  L1=5 y retirar R2 perdió el brazo 1. Auditoría geométrica estática
  favorable, pero fixture aún no congelado en Git ni ray_cast Blender
  verificado. Los resultados CPU corregidos de OPT-007 aún no llegaron.
  OPT-014 corrigió enmascaramiento de excepciones: si restaurar falla,
  se conserva el error óptico original y el fallo de restauración queda
  como causa. Test nuevo, suite ligera 80/80. Sin Blender/GPU.

- 2026-09-29 14:29 UTC: OPT-015/DEC-019. Codex añadió preflight
  independiente de primer impacto entre todos los discos, más test de
  oclusión cruzada: suite ligera 82/82. Sobre el fixture de cinco d,
  rutas intactas, sham nulo, ablación corta brazo 1 y error máximo de
  `ΔL−2d=3,54e-16 BU`. JEV remoto verificado (`provenance=jev`,
  `model=jev-1.13.0`) eligió ambos contrastes con confianza 0,99 y
  estimó preparación para corrida en 0,14. La enmienda 001 añade
  d=0,0125/0,025 sin sustituir los tres puntos originales. Claude la
  versionó en `origin/claude/opt-015-fixture` @ `f8d7fc5`, con
  `17b2740` recuperable; diff limitado a listas y salidas esperadas,
  blobs locales coincidentes. OPT-007 sin resultados `noleak` aún.
  Falta revisar runner de Blender y permiso de recursos de este hilo;
  no se ejecutó Blender/GPU aquí.

- 2026-09-29 14:40 UTC: OPT-015 avanzó sin Blender/GPU. Codex añadió
  `exp003_ray_paths.py`, un acumulador que solo recibe del callback de
  escena el **primer impacto real** (objeto, punto y normal), suma
  segmentos medidos desde los puntos de impacto, y marca pérdida si
  falta un espejo; no lee longitudes ni potencias previstas del fixture.
  Tres tests sintéticos cubren ruta válida, ablación sin fallback y
  oclusión cruzada; suite CPU ligera 85/85. Es solo contrato de integración,
  no implementación ni validación del `scene.ray_cast` de Blender.
  Siguiente: adaptador Blender con mallas y readback, auditoría independiente
  de Claude y permiso de recursos antes de ejecutarlo.

- 2026-09-29 15:05 UTC: nueva autorización explícita del usuario para
  GPU y Blender, con batería comparativa **después** de una red estable.
  Claude propuso nichos en THINKTANK y entregó resultados OPT-007
  sin fuga; Codex leyó JSON, comprobó split→escalado y diferencias por
  seed: dígitos 0,8933 vs logreg 0,8844 / MLP 0,8841; Iris 0,7867 vs
  logreg 0,9200. Exploratorio digital, entrenamiento no reproducido.
  `PROGRAMA-COMPARATIVO-PROPUESTA.md` fija gates y controles, no inicia
  benchmarks. Revisión Claude del contrato EXP-003 señaló longitud
  parcial de brazo perdido y autoimpacto; Codex corrigió ambos, añadió
  gate de ruta opcional y tests: suite CPU ligera 87/87. Sin Blender/GPU
  ejecutados aquí. JEV no conectó (`provenance=local`) y auto-review
  rechazó enviarle el estado del proyecto; no reintentar por atajo.
  DEC-020 es local provisional; consultar JEV solo tras aprobación
  explícita para ese envío/canal. Próximo: revisión del adaptador Blender,
  reserva de recursos y EXP-003, antes de comparar nichos.

- 2026-09-29 15:13 UTC: OPT-015 recibió un adaptador mínimo de
  `scene.ray_cast` en `exp003_scene_cast.py`. Devuelve el primer impacto
  de Blender (rol, punto y normal) al acumulador; un objeto ajeno queda
  visible como `unmapped:*`, y un miss no activa fallback de fixture.
  Tres tests mock nuevos; suite ligera 90/90. Aún falta constructor de
  mallas, prueba Blender real, save/reopen y libro mayor; no se ha
  lanzado Blender ni GPU. JEV sigue pendiente por el bloqueo documentado.

- 2026-09-29 15:17 UTC: Claude halló un falso éxito en la frontera
  ray-cast: sustituir R1 por una malla sin `neuro3d_role` podía llegar
  a BS2 con longitud 5 si no se activaba `expected_routes`. Codex hizo
  inválido todo impacto `unmapped:*`, con `length=None`, y añadió el
  contraejemplo como test; suite CPU ligera 91/91. `expected_routes`
  sigue siendo gate adicional y será obligatorio en el runner EXP-003.
  La ablación deberá retirar/desvincular la malla del depsgraph, no
  confiar en `hide_render`. Sin Blender/GPU; JEV sigue bloqueado.

- 2026-09-29 15:27 UTC: Claude encontró otro contraejemplo importante:
  desplazar R1/R2 +0,3 BU cambia L1 de 5 a 5,6 sin romper ruta ni
  `ΔL=2d`; por periodicidad, A base aún puede ser oscuro. Codex añadió
  gate CPU independiente de SHA-256 del fixture, matrices/normal/radio/
  topología/modificadores y longitudes absolutas L1/L2. El fixture
  local coincide con SHA-256 congelado y conserva cinco d. Cuatro tests
  nuevos (incluido desplazamiento +0,3) pasan; suite ligera 95/95.
  No se ejecutó Blender/GPU. Falta construir mallas y observarlas
  mediante Blender para aplicar el gate de verdad; JEV sigue bloqueado.

- 2026-09-29 15:42 UTC: revisión de Claude al gate absoluto: el +Z
  nominal podía ocultar normales de cara giradas; un padre podía añadir
  escala/cizalla, y una cara no plana podía producir normales distintas.
  Codex reforzó el gate con normal ± de cara, padres prohibidos, ejes
  mundiales unitarios/ortogonales, vertices coplanares y a radio real,
  rechazo de NaN, y lectura de Blender desde `mesh.polygons[0].normal`,
  vértices y `matrix_world` en `observe_scene_disks`. Tres tests nuevos:
  suite CPU ligera 98/98. La observación Blender sigue sin ejecución
  real; no se usó GPU/Blender. JEV permanece bloqueado.

- 2026-09-29 16:02 UTC: primer runtime Blender CPU real de OPT-015.
  Constructor de seis discos con fixture SHA-256 congelado, cara plana
  de 64 vértices, roles y sin auxiliares; `observe_scene_disks` y gate
  absoluto pasaron tras `view_layer.update()`. `scene.ray_cast` devolvió
  brazo 1 R1→R2→F1→BS2, L1=4,9999999702 BU, y brazo 2 M2→BS2,
  L2=2,9999998808 BU (ambos a <1,2e-7 BU de referencia).
  Blender 4.5.14, background `-t 1`, `CUDA_VISIBLE_DEVICES=-1`, sin render,
  sin guardado y sin GPU intencional; gpuq libre, ~11,3 GiB RAM libre,
  sin otro Blender observado antes. Primer arranque falló por ruta de
  importación, corregida; Blender reportó exit 0 pese a traceback, por
  lo que futuros wrappers deben exigir marcador `EXP003_SMOKE` además
  del código de salida. Sonda base exitosa, NO EXP-003 completo: faltan
  cinco d, sham, ablación, potencias, balance y save/reopen. El proceso
  terminó. JEV sigue bloqueado.

- 2026-09-29 16:12 UTC: Claude aceptó estáticamente constructor y sonda
  base, con cuatro exigencias para EXP-003 completo: `--python-exit-code`,
  intervenir la escena base guardada/reabierta (no reconstruirla), anclar
  L1=5+2d/L2=3 en cada d y renovar depsgraph/readback tras reabrir.
  Codex añadió `exp003_interventions.py`: mueve los mismos R1/R2 y
  desvincula R2 de la colección de la escena para ablación, sin usar
  `hide_render`. Dos tests mock nuevos; suite ligera 102/102. No hay
  nueva corrida Blender/GPU. Próximo: runner que reabre escena, aplica
  estas intervenciones, comprueba cuatro gates y registra resultados.

- 2026-09-29 16:27 UTC: Claude revisó intervenciones in situ y fijó
  cuatro riesgos del futuro runner: re-resolver objetos tras abrir,
  guardar/reabrir cada tratamiento antes de trazar, comprobar que
  ablación sale del depsgraph y verificar fichero de tratamiento distinto
  del base. Codex añadió el combinador híbrido
  `exp003_optics_from_paths.py`: fase solo de longitudes ray_cast
  aceptadas, potencias de ambos puertos, escape por brazo perdido y
  balance. Estados inválidos no se reinterpretan como pérdida.
  Casos oscuro/medio/brillante, ablación y estado inválido cubiertos;
  suite ligera 105/105. No nueva corrida Blender/GPU. Siguiente:
  runner save/reopen con esos cuatro gates; JEV sigue bloqueado.

Leer al reanudar, en este orden: este archivo, `COLA-DE-TRABAJO.md`,
`TABLON.md`, `DECISIONES.md`, la tarea activa y el último informe técnico.
