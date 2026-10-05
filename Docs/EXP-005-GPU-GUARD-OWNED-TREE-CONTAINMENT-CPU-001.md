# EXP-005: contención de procesos propios, verificada sólo con controles CPU

ID: GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001. Codex, capacity_audit/EXP005.
Base local: 70179200ca3ad446ba913c84f0f972576f8ea7e1.
JEV bloqueado por seguridad; fallback local sin aval remoto.

## Resultado y límite

Nueva pieza opt-in: windows_job_tree_control_CPU_v1.py y su worker CPU fijado
por SHA. Diez tests pasan; 22 registros, diez raíces creadas suspendidas,
siete reanudadas. Incluidos nieto sobreviviente al padre, supervisor anidado
que sale mediante os._exit(19), timeout, interrupción, rc0/rc7 y errores antes
de reanudar. Un error de limpieza inyectado permanece CLEANUP_UNCONFIRMED,
no se convierte en éxito.

Es una implementación real de contención Windows comprobada con procesos CPU;
NO es el guard GPU completo ni un backend nativo. No acepta comandos arbitrarios:
sólo cinco perfiles del worker propio. No CLI GPU, telemetríaGPU, reserva gpuq,
Blender, RT, consulta geométrica ni inferencia desde escena. Todos los indicadores
de admisión/certificación GPU, precisión nativa y reserva autenticada son false.
No se modificaron ni ejecutaron los runners congelados.

El hueco estaba declarado en EXP-005-PILOT-WATCHDOG-CPU-2026-09-30.md:
la limpieza por PID+create_time de procesos observados no certifica el árbol
que se escapa a la observación. Ese supervisor y guarded_job.py siguen intactos;
no se reabre el deadline histórico.

## Contrato nuevo de control CPU

Antes de crear un proceso: modelo/perfil exactos, SHA del worker y Python,
deadline UTC explícito nuevo (horizonte máximo60s), timeout0.05..5s y margen
de cierre de tres segundos; RAM disponible menos presupuesto256MiB >=4GiB.
El presupuesto es para estos controles CPU, NO estimación GPU/celda.

Job Object sin nombre, handle no heredable: KILL_ON_JOB_CLOSE, memoria de commit
del job192MiB, máximo4 miembros, afinidad máscara1 y sin flags breakaway.
Creación suspendida; AssignProcessToJobObject antes de ResumeThread.
DETACHED_PROCESS evita consola/conhost en estos controles; no es breakaway.
Python -I -S -B, variables de cómputo1hilo y código CPU fijo. Se vuelve a verificar
reloj antes de reanudar y antes de aceptar la salida; timeout monotónico también
cuenta preparación. No garantía sobre procesos de sistema/driver ni otros caminos
de creación, como servicios/WMI: no se generaliza a un renderer.

Cierre: TerminateJobObject por handle privado, consultar active_processes hasta0
dentro de dos segundos, comprobar raíz y cerrar handles. Fallo de asignación
finaliza sólo el proceso propio todavía suspendido, por su handle de creación,
nunca por búsqueda de PID. El cierre del último handle añade una segunda barrera
del kernel; un error de limpieza sigue sin confirmar aunque se cierre el handle.
Interrupciones no se suprimen; cierre repetido no vuelve a tocar procesos.

En el caso huérfano hay dos miembros: padre sale con0, nieto sigue activo1;
el cierre deja0. En el caso anidado hay tres: supervisor/worker/nieto. El supervisor
comprueba el nieto y sale sin finally/destructor; el job exterior ya observa0 antes
de su propia terminación explícita. Esto contrasta cierre automático del job
interior, sin enumerar nietos por PID.

## Evidencia retenida y fallo corregido

Suite final: rc0, 1.1841870000062045s de QA, stdout19144bytes,
SHA97c7c25c6401c608bb6f916b4cec8e09464abafce1706fdf27e13dab687a0324.
Diez tests / 22 registros; 13 procesos Python por flujo y contabilidad del job,
incluidas tres raíces suspendidas no ejecutadas y tres descendientes.
No afirmar que todos los procesos internos del sistema tienen un hilo; afinidad
del job y variables fijan el cómputo de los controles a un procesador/hilo.

La revisión detectó además una interrupción justo después de CreateProcessW:
el buffer de handles ahora vive en el llamador desde antes de la llamada nativa.
La regresión inyecta KeyboardInterrupt tras la creación real, antes de asignar
o reanudar: conserva handles, finaliza sólo esa raíz suspendida y propaga la
interrupción. No se ejecutó una versión antigua dejando un proceso huérfano.
La suite previa de9tests y su verificador también se conservan en el recibo;
el rerun responde a este cambio de código, no a relleno ni ajuste de criterios.

Verificador separado: lee la captura guardada sin repetir la suite y consulta
los límites al kernel con sus propias estructuras ctypes. Un control CPU adicional,
rc0/0.1250642000231892s, stdout1619bytes,
SHA053e58d1fc8ec541992dc5211e7b6b45d09c9fc917c82f86b9f00b8792c00bd9.
Flags8728=0x2218, afinidad1, miembrosmáximo4, commit201326592bytes; breakaway false.
Confirma cierre0 del proceso de consulta. No prueba universal ni ensayo GPU.
Tiempos son QA, NO benchmark/eficiencia/costes completos.

Primera suite rc1/1.404639499989571s, stdout15733bytes,
SHAdb82b8ab754df2b1c2aa943e75e1f6dad4584c1d8ea57e90bf71a9be4b32f557:
dos FAIL de construcción del control, esperado2 miembros observado4; supervisor
salió82, no19. CREATE_NO_WINDOW generaba un conhost.exe por consola.
Diagnóstico acotado lee sólo miembros del job propio: primero Python; después
Python+conhost. Capturas SHA620bb6c6b99331691322c819c4ac90cd9c4d403d3339ffebdbad398b399934a9
y030f93e0d912e95677ed2cbf4274940739b5c208ef899341b2b2b14f292c916f.
No procesos ajenos terminados ni aumento del máximo4 para obtener PASS.
Corrección: DETACHED_PROCESS en la raíz y hoja y aislamiento -S; pin del worker
actualizado por cambio revisado. Conservados código inicial y captura completa
(stdout+stderr), con los límites/asserts originales. La consulta pyvenv.cfg
inexistente y el diagnóstico de sitecustomize no son fallos de GPU; no hubo SDK
ni modificación de instalación. El recibo conserva evidencia de construcción.

## Antes de GPU

Falta integrar admisión real: reserva exclusiva por job/Claude, lectura fresca
gpuq/procesos/RAM/VRAM/temperatura, guard de recursos fail-closed durante el trabajo,
deadline nuevo verificable y logs/resultados/envelope retenidos, backend/ABI
de escena e inferencia y costes completos. Este control no admite esos comandos.
No tomar la contención CPU como permiso de lanzamiento o precisión física.

Mantener >=1024bytes/celda más márgenes/temporales, RAM>=4GiB tras presupuesto,
VRAMtotal<=18GiB, temperatura<=80C, pilotos<=120s y otros<=600s; noMLP32768 ni
cargas próximas al límite tras0x9F. Sin SDK/DrJit/Kaggle/push/publicación/merge.
Fixtures conf1/v0/v4/0119/0315/nearestV2, bounds, umbrales y fallos previos intactos.
U/GEMM CPU no sustituye inferencia desde escena; RT16Mvs1M y salidas diferentes
no comparación equivalente. Claude conserva capacity/nebulatrace/research/RT.
Sharedboards/checkpoint locales SINstage; sólo estos archivos propios a commit.

Referencias de semántica Win32:
[flags de creación](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
y [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects).
La evidencia operacional es el test local, no sólo la documentación.
