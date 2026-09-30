# Integración de job escalar V1 (opt-in)

Invocación únicamente como hijo directo de una reserva gpuq ya concedida.
No adquiere ni cancela tickets. Recibe executableBlender absoluto existente,
jobdirectory privado nuevo dentro del proyecto y nombre exacto de reserva.

Verifica pins congelados del child/report, SHA executable y PID/birth del
supervisor/queue. Escribe initial/final propios exclusivos incluso ante
rechazo de recursos después de establecer owner. La falta de reserva
rechaza antes de crear cualquier carpeta o lanzar un hijo.

Prelaunch exige RAMlibre>=6GiB (2 de presupuesto + piso4), VRAMactual+.25GiB
<=18GiB y <=80C. Solo escalares; no geometría ni escalado de conf1.
Genera deadlineUTC=ahora+90s DESPUÉS del turno adquirido, hash y preflight;
no acepta plazo externo ni reutiliza06UTC. Hijo60s/margen20 según supervisor
frozen, con comprobación repetida de reserva/telemetría. No ocupa GPU cuando
falta RAM ni altera márgenes. Programa command privado del child frozen.

Recipe y binding guardan SHA de executable/entrypoint y PID/birth reales;
se revisan nuevamente antes del supervisor. Tras retorno exige envelope
completed, gates y re-decoder raw por bundleV1, sidecar del PID propio y
SHA recipe/binding/entrypoint iguales, deadline absoluto aún vivo y pins
intactos. Nunca modifica capturas ni shaders congelados. Final propio liga
estas evidencias; rc0 indica SOLO consistencia escalar, NO autenticaciónGPU.

Pruebas CPU: ancestry/resources/supervisor MOCK, executable ficticio no
ejecutado y raw generado CPU. Rechazos reserva, RAM, telemetría, rc17,
sidecar alterado, executable cambiado, paths/overwrite. No GPU/Blender
real, RT, scene-inference, conf1, driver, velocidad o avalJEV.

Comprobación adicional acotada: importar el child congelado con el Python
bundled de Blender4.5.14 en CPU, sin ejecutar blender.exe/importar bpy/gpu.
No instala dependencias ni prueba cierre GUI, driver o shader. Primer
intento de comando mal escapado falló en Python del supervisor antes de
lanzar ese intérprete; conservar el fallo de invocación separado del import.
El psutil observado procede del user-site existente de Python311 en C:.
No se escribió allí. El Python embedded de blender.exe podría excluir ese
user-site: import exitoso del intérprete standalone NO certifica ese entorno.
Si el piloto revela falta de dependencia, fallar cerrado y retener rc/stderr;
no instalar ni habilitar rutas/env silenciosamente.

Pendiente real: admitir un piloto SOLO cuando llegue turno y recursos;
retener raw, backend, PID/birth, rc/envelope/cierre; evaluar evidencia antes
de cualquier promoción. Flags auth/operational/promote/scene siguenFalse.
JEV bloqueado, fallback local sin atribuir aval remoto.
