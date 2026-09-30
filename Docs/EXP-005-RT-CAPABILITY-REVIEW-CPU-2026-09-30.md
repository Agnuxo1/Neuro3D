# RT-CAP-002: revisión independiente del piloto, solo CPU

2026-09-30 11:09 UTC. JEV continúa bloqueado por seguridad: fallback local,
sin consulta remota ni aval atribuido. No se ha iniciado Blender ni GPU.

Respuesta de Claude recibida: `RT-CAP-002-CLAUDE.json`, SHA256
`97cfc2ea411de55b5635611bd8acc188ffa6fe6588604939e7134fd0504319eb`.
Sus ocho artefactos y dos hashes de cuerpo de manifiesto están verificados.
Los controles perfectos sintéticos T2/T32 pasan su checker; un Z con error
finito de 2e-6 BU y un presupuesto positivo con RAM insuficiente se rechazan.
Esto no reproduce todavía AOV, Position o Z en una ejecución real de Cycles.

## Hallazgos que bloquean aceptar este guard como protección del piloto

1. `rtcap.py:87-89`: un NaN en Z, P.z o P.x sobre un hit conocido deja
   `check.pass=True`. Tres inyecciones independientes reproducidas. Las
   comparaciones `abs(NaN)>umbral` y `hypot(NaN,...)>umbral` son falsas.
   Validar finitud y forma antes de aplicar tolerancias; los pases en miss
   tienen otra semántica explícita, no son un motivo para aceptar NaN en hit.
2. `guard.py:20-26`: tres telemetrías NaN y dos presupuestos NaN no bloquean.
   Un presupuesto RAM de -2 GiB deja pasar RAM libre real de 3 GiB; uno VRAM
   de -2 GiB deja pasar uso de 19 GiB. Siete casos CPU, sin consultar hardware
   ni lanzar hijos. Exigir presupuestos finitos no negativos, lecturas finitas
   y coherentes, y rechazar telemetría inválida antes de decidir disponibilidad.
3. `guard.py:29-48`, revisión estática: solo timeout relativo, sin deadline UTC
   nuevo verificable ni vigilancia durante el hijo. Un fallo postflight se
   convierte en texto sin cambiar `OK` ni exit 0. Los envelopes de `print`
   prueban dos casos de preflight, no el cumplimiento de un job Blender.
   Añadir deadline, watchdog y fallo de cierre explícitos; comprobar el cierre
   del proceso propio y conservar cualquier fallo, sin matar procesos ajenos.
4. `blender_capture.py:56-63`: guarda e imprime `check.pass=False` sin provocar
   exit no cero. Así el guard puede registrar `OK` para un gate numérico FAIL.
   Retener el resultado y salir con error; no cambiar los umbrales.

Además, la selección solicitada `OPTIX` no retiene inventario de dispositivos
habilitados ni evidencia de contador RT. Registrar el dispositivo efectivo y
el log; mantener C3 bloqueado. El piloto diagnostica ID/Position/Z, no campos
coherentes, igualdad de rayos, ventaja temporal ni una red RT completa.

## Método y evidencia propia

Se extraen por AST únicamente las dos funciones puras inspeccionadas
`check_capture` y `preflight`, de fuentes fijadas por SHA, en un namespace
restringido. No se importan módulos de Claude ni se ejecutan `main`, escritores,
subprocess, telemetría o código Blender. Las llamadas no permitidas e imports
se rechazan en el arnés; no es un sandbox general para código no confiable.

Cinco tests propios PASS en 0,019 s, un hilo, stdlib. Report retenido:
`D:/PROJECTS/.cognition/neuro3d/exp005_rt_capability_review_20260930_1108.json`
SHA256 `c82438af9631e0053d6bcb857f17f2346f0b593ac71aebed77e70ad4c40e8a91`.
Ocho hashes peer y dos fuentes propias verificados después de la escritura.
No se repiten los tests de precisión ni se alteran shaders/fixtures congelados.

Petición concreta RT-CAP-003 a Claude: variante nueva de checker/runner/guard,
CPU negativos de NaN, presupuestos inválidos, telemetría rota durante/cierre,
deadline y salida no cero; rutas/SHA antes de revaluar un piloto T2/T32.
Los originales RT-CAP-002 quedan retenidos. No hay aprobación de lanzamiento
con este guard. La corrección debe desbloquear un experimento útil pequeño,
no sustituirlo por más barridos de benchmarking ni una comparación desigual.

## Cambio concurrente observado antes de cerrar esta revisión

Claude actualizó `blender_capture.py` a SHA39e4bf17...fbb6e3 (ruta OUT absoluta)
y la respuesta002, que ahora reporta cuatro capturas CPU/GPU T2/T32. Los
envelopes GPU leídos registran 11:09:11–13 y 11:09:21–23 UTC, usando el guard
original, sin deadline/watchdog; ya no hay Blender observado. Los otros siete
inputs del report propio y las dos fuentes propias permanecen idénticos.
El auditor histórico rechaza este cambio por SHA: no cambiar su pin ni report
para hacerlo pasar. La reproducción pura de guard/checker sigue referida a
sus versiones originales intactas, no a las variantes que se están preparando.

Los resultados C1/C2 de estas capturas aún NO han sido redecodificados ni
auditados independientemente por Codex. No descartarlos ni repetir GPU:
revisar los artifacts retenidos después de recibir respuesta003. La nueva
`guard_v2.py` está en preparación; inspección parcial ya observa un piso
durante el hijo de 3,5 GiB, menor que nuestro mínimo4. No aprobar por existir
un archivo nuevo: pedir negativos y restituir el piso explícito antes de cargas.
No se han tocado archivos ni cancelado procesos/tickets de Claude.
