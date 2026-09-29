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

## DEC-009 · 2026-09-28 · Contrato EXP-001 cerrado antes de Blender

- **Evidencia revisada:** Claude propuso
  `experimentos/EXP-001-PROPUESTA-CLAUDE.md` con controles A–F y una
  estimación float32; Codex leyó sus scripts de exploración CPU. No son
  resultados de Blender ni validación física. La implementación actual de
  solape/coherencia pasa 41 pruebas ligeras y el oráculo separado 26.
- **JEV:** consulta v2 con `exit_code=0`, `status=connected`,
  `provenance=jev`; recibo
  `jev/exp-001-prereg-review-20260928-result.json`. Recomendó aceptar la
  propuesta con ajustes y congelar umbrales antes de medir.
- **Decisión:** `experimentos/EXP-001-PREINSCRIPCION.md` es el contrato
  vigente para una futura prueba MZ en Blender. A, B-geo, B-mat, C y D son
  primarios; E (visibilidad CPU) y F (baseline monocamino) son secundarios.
  B-geo son dos ediciones de escena coordinadas: M1 y el empty padre de BS2
  y detectores; no se llama edición de un único objeto. Se exige lectura
  tras guardar/reabrir, modos resueltos en A/B/C y tolerancias fijas CPU
  1e-12 / Blender 1e-9 para puertos. La estimación float32 no sustituye a
  Blender. No retocar criterios tras conocer resultados.
- **Gate:** sin Blender mientras el PC esté ocupado; hace falta implementar
  y verificar el empty padre del adaptador, revisión final del contrato y
  margen de recursos/autorización del usuario. Aunque pasase, EXP-001 solo
  demostraría cálculo escalar dependiente de objetos de escena, no física
  electromagnética real ni entrenamiento de una red completa.

## DEC-010 · 2026-09-28 · Primer detector y solape dependiente del haz

- **OPT-010:** Claude entregó contraejemplos CPU. Codex leyó y ejecutó el
  script: se acreditaba potencia al puerto A con un detector detrás de BS2
  que encerraba el origen, con dos detectores que lo encerraban y cuando el
  rayo A atravesaba antes la esfera B. En el ejemplo original de oclusión,
  B también encerraba BS2 (distancia 0,49497 < radio 0,5); una variante con
  B=(2,4;2,4), radio 0,5 aísla la oclusión real.
- **JEV:** consulta v2 `exit_code=0`, `status=connected`,
  `provenance=jev`; recibo `jev/opt-010-triage-20260928-result.json`.
- **Corrección:** añadir regresiones rojo-verde y exigir primera intersección
  positiva entre ambas esferas de detector. Origen encerrado, empate,
  detector equivocado primero o modo faltante quedan sin atribución falsa,
  con estados `unresolved` y balance conservado. Para `beam_waist` positiva,
  usar solape gaussiano mínimo `O≥0,01` y mantener dirección/aperturas/
  detectores; `overlap_tolerance=0,02 BU` queda para el modo ideal heredado.
  Este corte es fenomenológico, no validación física de haces.
- **Evidencia:** 47/47 pruebas CPU/estáticas del área Blender, 26/26 del
  oráculo y 3000/3000 escenas asimétricas del script de Claude con error
  máximo 6,495e-14. El empty padre del adaptador pasa una prueba estructural
  sin Blender. Informe `INFORME-OPT-010-GATE-CPU.md` enviado para nueva
  revisión de Claude (OPT-011).
- **Contrato y gate:** `EXP-001-PREINSCRIPCION.md` se enmendó antes de
  ejecutar Blender, sin tocar tolerancias de aceptación. OPT-003 permanece
  bloqueada por revisión independiente del nuevo parche, verificación real
  del adaptador/parentado y recursos/permiso del usuario.

## DEC-011 · 2026-09-28 · Orientación reproducible del control D

- **Hallazgo de Claude:** en `nonrect60`, girar la normal de M2 +10° y −10°
  en el plano da las mismas potencias (A/B=0,25/0,25; escape=0,5), pero
  `status=missed_bs2` y `missed_bs2_aperture`, respectivamente. El contrato
  anterior no fijaba el signo ni el eje pese a exigir la primera etiqueta.
- **JEV remoto:** consulta v2 con `exit_code=0`, `status=connected`,
  `provenance=jev`, eligió `fix_plus_world_z` (confianza 0,95). La primera
  consulta tenía criterios mal estructurados y devolvió una clave ambigua;
  se corrigió el esquema y solo se tomó como decisión la segunda respuesta.
- **Decisión:** antes de cualquier Blender, D queda definido como giro de la
  **normal de M2 +10° sobre +Z mundial, antihorario visto desde +Z**, sin
  mover el espejo. No cambia los umbrales ni las potencias esperadas.
- **Evidencia:** prueba CPU nueva con la geometría `NonRectMZ(60,2,2)`:
  `missed_bs2`, A=0,25, B=0,25, escape=0,5, balance <1e-12; suite 52/52.
  No se ha ejecutado Blender; OPT-003 sigue bloqueada.

## DEC-012 · 2026-09-28 · Compuerta direccional ante precisión float32

- **Hallazgo de Claude:** emulación CPU de errores independientes de Euler
  en `nonrect60`, sin Blender: ±1,2e-7 rad por ángulo produjo 0/2000
  fallos de status; ±2,4e-7, 182/2000; ±5e-7, 1056/2000. Codex ejecutó
  el script y reprodujo las cifras. El puerto oscuro de casos resueltos
  quedó por debajo de 1e-9. No es la ruta exacta de matrices de Blender.
- **JEV remoto:** `exit_code=0`, `status=connected`, `provenance=jev`;
  recomendó `set_1e5_nonrect_only` (confianza 0,8). Recibo en
  `jev/opt-003-angle-20260928-result.json`.
- **Decisión anterior a Blender:** fijar `direction_tolerance=1e-5` solo
  en el constructor `nonrect60`. El montaje cuadrado y el motor general
  conservan 1e-6. No cambian criterios A–D de puertos, energía, persistencia
  ni readback. Si el runtime falla, se registra sin reajuste post hoc.
- **Gate:** sigue faltando verificación Blender, margen de recursos y
  autorización explícita del usuario.

## DEC-013 · 2026-09-29 · Cierre de la fase estática OPT-003

- **Estado:** el runner/readback MZ está implementado, pero nunca ejecutado
  en Blender. Pasan 56 pruebas ligeras del área y 32 del oráculo. Claude
  confirmó el arreglo del falso positivo RGB; no ha emitido una auditoría
  final integrada sobre todos los parches posteriores.
- **JEV remoto:** consulta v2 `exit_code=0`, `status=connected`,
  `provenance=jev`; eligió `final_audit_then_wait` con confianza 0,99.
  Recibo `jev/opt-003-next-20260929-result.json`.
- **Decisión:** congelar cambios de alcance EXP-001 salvo defecto reproducible;
  encargar a Claude OPT-012, auditoría integrada de solo lectura del commit
  publicado. Tras su respuesta, no acumular pruebas simuladas sin hipótesis
  nueva. La ejecución real espera recursos y autorización explícita de Fran.
  Esta decisión no abre la GPU ni promociona el prototipo.

## DEC-014 · 2026-09-29 · Cierre estático de OPT-012, no de EXP-001

- **Evidencia:** Claude reaudió el parche H1/H2/H3 y dio aceptación estática
  acotada en `TABLON.md` (00:21 UTC). Codex publicó `4785c65`; el último
  ajuste adelanta también la validación del estado y RGB persistidos hasta
  después de escribir el readback. Pasan 60 pruebas ligeras y 32 del oráculo.
- **JEV remoto:** consulta v2 con `exit_code=0`, `status=connected` y
  `provenance=jev` eligió `close_opt012_static_only` (confianza 1,0). Una
  consulta más amplia sobre el siguiente trabajo de red dio confianza 0,34;
  no se usa para autorizar una arquitectura nueva.
- **Decisión:** OPT-012 queda cerrada **solo en inspección estática**. OPT-003
  sigue bloqueada hasta autorización expresa de Fran y recursos suficientes
  para Blender CPU. No se ha ejecutado el MZ en Blender ni demostrado una red
  neuronal o cómputo físico de luz. No añadir más mocks sin defecto concreto.

## DEC-015 · 2026-09-29 · EXP-001 runtime y GPU ideal, aceptación acotada

- **Autorización:** Fran abrió una ventana de una hora para pruebas GPU desde
  aproximadamente las 10:20 UTC. Se usó Blender CPU y una sonda OpenGL GPU
  durante esa ventana; todos los procesos terminaron antes del límite.
- **Blender:** 14/14 fases de guardar/reabrir los siete controles pasaron;
  `runtime_verified=true`, `failure=null`, readback reconstruido con
  diferencia máxima 2,26e-13. Evidencia en
  `D:/PROJECTS/.cognition/neuro3d/exp001-20260929T1023Z/report.json`.
- **GPU:** el shader heredado no tiene paridad con el motor de grafo. Una
  primera sonda de caminos entre centros falló D. La sonda posterior de
  rayos/discos/fase sobre matrices Blender reabiertas pasó potencias y estados
  7/7 con diferencia máxima de potencia total 1,10e-12; informe
  `mz_scene_gpu_ray_probe-v3.json`. Se conservan los informes fallidos.
- **JEV remoto:** `exit_code=0`, `status=connected`,
  `provenance=jev`; eligió `accept_bounded_then_audit` con confianza 1,0.
- **Decisión:** aceptar EXP-001 como verificación runtime del cálculo escalar
  CPU gobernado por escena y la sonda GPU como paridad **solo del MZ ideal
  preinscrito**. Encargar OPT-013 a Claude para auditoría independiente. No
  declarar paridad del motor general, ventaja de velocidad, red entrenada ni
  cómputo fotónico físico. Para otra ejecución GPU se necesita autorización
  nueva tras esta ventana.

## DEC-016 · 2026-09-29 · Próximo gate: celda geométrica ajustable

- **Contexto:** DEC-015 demuestra control geométrico de una celda MZ, pero
  no aprendizaje. Claude audita por separado la sonda GPU (OPT-013).
- **JEV remoto:** el plan de diseño eligió agente principal sin paralelismo
  (`remote_decision=true`); la consulta tipada devolvió
  `status=connected`, `provenance=jev` y
  `geometry_parameter` con confianza 1,0.
- **Decisión:** preinscribir EXP-002/OPT-014, ajuste de dos objetivos de
  potencia mediante la edición coordinada de M1 y el grupo BS2/detectores.
  Control congelado, coherencia nula, balance, alineación y persistencia
  son gates obligatorios. La fórmula ideal solo comprobó viabilidad de los
  parámetros antes de ejecutar; no es resultado del motor.
- **Límite:** no ejecutar ahora Blender ni GPU; Claude criticará el
  contrato después de OPT-013. Un ajuste exitoso de una celda es calibración,
  no red neuronal ni generalización. El experimento puede fallar sin
  reajustar después los umbrales.

## DEC-017 · 2026-09-29 · Auditoría OPT-013 y enmienda pre-run EXP-002

- **Procedencia:** Claude entregó `aeb973a` en una rama separada. Codex
  inspeccionó e integró solo cuatro archivos de oráculo y dos JSON, sin
  reemplazar el tablón compartido; repitió 8/8 y 5/5 pruebas individuales,
  45/45 del oráculo y 70/70 ligeras. El port FP64 sobre los readbacks
  **reales** de EXP-001 mantuvo 7/7 y confirmó en D `ray_status=1`.
- **Hallazgos aceptados:** B-geo cerca de −π hace frágil la guarda de fase
  bajo jitter float32; D calcula la clasificación del brazo, pero sus
  potencias son constantes; C con coherencia cero no demuestra fase
  geométrica. EXP-002 admite un atajo de fórmula que cumple todos los
  criterios anteriores, reproducido por Codex en el motor CPU.
- **JEV remoto:** `status=connected`, `provenance=jev`; eligió reducción
  de fase prospectiva antes del coseno (confianza 1,0), integrar los
  archivos revisados (0,9) y control sham más vínculo de matrices finales
  como gate mínimo EXP-002 (0,38, confianza baja). El último se adopta por
  el contraejemplo de fuga y la prueba CPU discriminante, no por autoridad
  de una respuesta poco confiada.
- **Decisión:** OPT-013 queda revisada y aceptada **acotadamente**. El
  informe GPU v3 y sus umbrales históricos no cambian. Antes de reutilizar
  la sonda, reducir fase y exigir en D el brazo perdido correcto; no se
  puede volver a probar en GPU sin nueva autorización. EXP-002 adopta
  `EXP-002-ENMIENDA-001.md` antes de cualquier corrida Blender: sham,
  geometría reabierta ligada a `u_final` y trayectoria registrada como
  diagnóstico. No declarar paridad general ni aprendizaje de red.

## DEC-018 · 2026-09-29 · OPT-014 auditado; EXP-003 híbrido como gate condicional

- **OPT-014:** Claude revisó sham, matrices y restauración; Codex contrastó
  el sham de forma independiente sobre el readback A real, 21 posiciones:
  `max |ΔP_A|=1,94e-26`, status `ok`, solape mínimo 0,9999999999995246.
  Esto acepta el control solo en el motor CPU, no en una corrida EXP-002.
  El aviso de Claude sobre enmascaramiento de una excepción por `restore`
  queda abierto para una corrección menor.
- **Permisos:** Claude declara que Fran le autorizó GPU/Blender en **otro**
  chat a las ~12:10 UTC y prioridad a las ~12:40; dice que cerró sus
  procesos. Esa información explica la aparente discrepancia con la
  ventana de este hilo. No es autorización transferible a Codex ni prueba
  por sí sola del resultado científico. No repetir GPU/Blender aquí.
- **JEV remoto:** consulta de estado técnico mínimo, sin historial ni datos
  privados: `exit_code=0`, `status=connected`, `provenance=jev`, modelo
  `jev-1.13.0`. Eligió `preregister_bounded_hybrid_cpu` con confianza
  0,89 y necesidad de revisión independiente 0,86.
- **Decisión:** crear `EXP-003-PREINSCRIPCION-CONDICIONAL.md` para una sola
  celda cuyo camino derive de intersecciones con mallas Blender. No adoptar
  aún la exactitud de OPT-007 como evidencia de computación hecha por la
  escena: hoy la escena guarda pesos y NumPy hace la interferencia. La
  fase CPU ray-cast debe tener fixture y revisión antes de ejecución; GPU
  o multicelda serían fases separadas, no autorizadas por esta decisión.
