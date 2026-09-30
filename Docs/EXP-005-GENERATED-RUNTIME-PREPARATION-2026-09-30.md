# EXP-005: piloto privado de exportación e historias generadas

## Contrato previo, implementación opt-in todavía sin ejecutar en Blender

`exp005_history_generated_runtime.py` prepara tres escenas privadas del MZI
base/switch/referencia. Reutiliza el constructor y exportador congelados;
guarda/reabre archivos NUEVOS, lee geometría evaluada y propiedades de escena,
genera las historias desde ese readback y calcula campos de referencia CPU.
No recibe rutas previas ni U/GEMM; no renderiza ni ejecuta propagación GPU.

La fase de MA es una propiedad óptica ideal, no un desplazamiento de espejo.
El contrato conserva exactamente los tres casos, igualdad de snapshots,
coherencia explícita, perfil 64 registros/profundidad32 y campo <=1e-13
de la preparación anterior. No subir bounds/conf1 ni relajar gates.

La CLI exige hijo privado, carpeta nueva, archivo inicial no abierto y
deadline UTC NUEVO, futuro y a <=120s. Comprueba el MISMO deadline antes de
importar bpy, entre pasos y antes/después de escribir el report, sin reiniciarlo.
Los checks UTC NO sustituyen watchdog monotónico ni preflight de recursos.
El flag de hijo tampoco sustituye autorización/reserva/telemetría.

## Prueba CPU del flujo

Ejecución 30/09/2026 14:14:34 UTC, tres tests PASS en 0,119s, un hilo/hijo<=60s.
Retenidos tres casos simulados: tres saves/tres reopens/catorce checkpoints
de deadline; 13 registros por caso y error máximo de campo 2,220446049250313e-16.
Dos negativos simulados (fase cambiada al reabrir y error al guardar) detienen
el flujo sin devolver resultado de éxito ni iniciar el siguiente caso.
Tests de deadline aceptan110s y rechazan vencido/pasado/121s/sin zona UTC.

Report local:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_runtime_cpu_20260930_1414.json`
SHA `b49a22bb0afae6907117eb720f96a29161281837f642193e55455f572a30df8c`.
Diecisiete code SHA verificados; dieciséis pins de1358 siguen iguales.

Se usaron mocks de builder/operaciones de archivo y doubles de readback:
NO se creó ningún `.blend`, ni se ejecutó bpy, ni se probó el cierre del proceso.
El hash de bytes sintéticos NO es evidencia de un archivo Blender real.
`bpy_execution_certified=False` sigue explícito en las comprobaciones internas;
el auditor externo deberá establecer la procedencia con artefactos reales.

## Requisitos de ejecución real futura

- RT-CAP-006 sigue turno de Claude, GPU ocupada por otro proyecto; no reservar
  encima, cancelar tickets, matar procesos ajenos ni ejecutar escritores peer.
- Preparar primero job propio con contrato/commit, todos los pins previos y
  manifiesto/folder nuevos. El runner está listo como candidato, NO el wrapper
  operacional completo ni un piloto con aceptación real ya conseguido.
- Adquirir gpuq exclusivo; refrescar procesos/RAM/VRAM/temperatura dentrojob.
  Presupuesto inicial RAM2GiB, piso4GiB libre DESPUÉS del presupuesto;
  geometría>=1024B/celda más márgenes fijos/temporales. Si ese presupuesto no
  cubre la carga real, aumentarlo o abortar, nunca reducir piso/márgenes.
  Presupuesto VRAM2GiB, total<=18GiB, temperatura<=80C.
- Guard fail-closed externo, hijo<=110s y deadline nuevo porjob<=120s con
  margen. Compartir ese deadline con el runner; nada del cierre nocturno06UTC.
  No cargas cercanas al límite/MLP32768 tras el reinicio0x9F.
- Aceptación conjunta: rc0 + envelopeOK + childfinalizado + report/readback/
  campos/historias PASS + recomputar tresSHAblend yreport. Report existente
  o marcador stdout solos NO éxito operacional. Preservar todaslasfallas.

Este piloto comprobaría vínculo a escena y persistencia, NO red íntegra GPU,
RT, fase nativa/hi-lo, solape físico, generalidad ni velocidad frente a otras
redes. La propagación nativa tendrá su contrato separado; no pasarle rutasCPU.
JEV bloqueado por seguridad: fallback local sin aval remoto. No instalación,
Kaggle, publicación/push/merge. No nueva guardreview solicitada a Claude.
