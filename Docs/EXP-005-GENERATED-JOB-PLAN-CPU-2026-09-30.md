# EXP-005: manifiesto preparatorio del piloto privado

## Unidad CPU, sin reserva ni lanzamiento

`exp005_history_job_plan.py` prepara el comando privado del runner95358ee,
deadline UTC nuevo y presupuesto, pero SIEMPRE marca `admitted_for_launch=False`.
No llama a subprocess, gpuq, bpy, render ni telemetría. Las muestras suministradas
NO se autentican: deberán refrescarse dentro de un job exclusivo futuro.

Comprueba SHA del report1414 y sus diecisiete dependencias congeladas, más el
SHA de guarded_job.py. Solo reutiliza su función PURA `violations` con deadline
explícito; NO invoca su launcher nocturno ni modifica el cierre histórico06UTC.
Cambiar el runner o report rechaza la preparación. Fichero .exe explícito/hash,
carpeta directa nueva y comando sin shell; hijo110s, deadline115–120s desde el
check, margen restante>=5s. No reiniciar el mismo deadline al lanzar.

Presupuesto candidato RAM2GiB de arranque/temporales +3*1024bytes por celda;
piso4GiB DESPUÉS del presupuesto. VRAM2GiB,total18GiB,temp80C. Son reservas
iniciales, NO picos certificados ni garantía de seguridad del PC; aumentar o
abortar si la carga requiere más, nunca bajar piso ni márgenes.

## Evidencia retenida

Ejecución real del auditor14:37:28 UTC (1438 es etiqueta del archivo).
Dos tests CPU PASS0,022s; un hilo/hijo<=60s. Catorce negativos rechazan:
deadline histórico/corto/largo/sinUTC, ruta relativa/fuera del parent/carpeta
existente, RAM baja/VRAM alta/temperatura alta/telemetría ausente/NaN,
report cambiado y runner cambiado. Control con hashes REALES de dependencias,
pero ejecutable simulado, muestras y reloj sintéticos. Solo carpeta temporal
en D:, sin .exe/.blend/export creado ni proceso iniciado.

Report local1438:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_job_plan_cpu_20260930_1438.json`
SHA `68b215a431734a8511ea3412de42b95a71dbb782017e03c133689d03a7ecddf7`.
Veintiún codeSHA (18 dependencies+3 preparación) verificados. Report1436
anterior conservado; nuevo resultado tras mover carpeta temporal a D:.

Fallo inicial propio retenido en `exp005_history_job_plan_initial_fail_20260930_1433.json`:
TypeError por usar argumentos posicionales ante API keyword-only; se corrigió
SOLO el caller y nombres de telemetría. No cambió política/gates/guard congelado.
La etiqueta1433 no pretende ser reloj exacto del fallo; trace completo en chat.

## Siguiente paso operacional, NO conseguido por este manifiesto

Un wrapper NUEVO debe adquirir/verificar reserva real, procesos y recursos,
revalidar pins y .exe antes de lanzar, vigilar tiempo monotónico y deadline UTC
común, rechazar salida tardía y conservar envelope obligatorio/errores/limpieza
de hijos propios. Aceptación real: rc0 + envelopeOK + procesos finalizados +
readbacks/árboles/campos válidos + recomputar SHA de tres blends y report.
No ejecutar el viejo guard nocturno ni usar este JSON como permiso de lanzamiento.

14:36: holderexterno41932/37728 y ticket006Claude26480 vivos, RAM1,434GiB
disponible; sin respuesta006. No carga propia, nueva reserva ni cancelación.
006 sigue única petición Claude; no nueva guardreview o repetición de renders.
Mientras se libera, completar wrapper propio CPU acotado o auditar006retenido.

Esto NO es avance de inferencia GPU/RT, prueba Bpy real, precisión nativa/hi-lo,
conf1, óptica física ni ventaja de velocidad. Referencia CPU desde escena sigue
explícita; no suministrar sus rutas al backend nativo. Fixtures/shaders previos
intactos. JEV bloqueado: fallback local sin aval remoto. Skills de desarrollo y
continuidad guiaron pruebas focalizadas y separación de preparación/evidencia.
