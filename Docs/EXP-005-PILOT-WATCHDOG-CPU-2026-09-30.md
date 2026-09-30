# EXP-005: supervisor propio con deadline nuevo, contraste CPU

## Interfaz opt-in y alcance

`pilot_watchdog_v1.py` implementa el núcleo pendiente de supervisión del hijo:
envelope exclusivo antes del lanzamiento, admisión rechazada por defecto,
preflight antes y segunda comprobación de admisión inmediatamente antes de
Popen. Conserva un deadline UTC nuevo (<=120s), timeout monotónico<=110s,
margen de cierre>=7s y política congelada RAM/VRAM/temperatura. La función
pura de guarded_job recibe este deadline; su launcher06UTC NO se usa ni cambia.

Cada ciclo verifica recursos/tiempos TAMBIÉN cuando el hijo ya devuelve rc0.
El cierre vuelve a comprobar UTC y tiempo monotónico: salida tardía NOéxito.
Errores de admisión/telemetría/proceso se registran por tipo, sin diagnósticos
crudos ni secretos. El finally finaliza una vez el envelope. NaN/telemetría
inválida no entra en JSON. Envelopes existentes no se sobrescriben.

Registra identidades PID+create_time de procesos propios observados y solo
mata esas identidades al abortar/cerrar. NO es contención Windows Job Object:
un descendiente fugaz huérfano no observado sigue fuera de la certificación.
`full_tree_containment_certified=False` siempre. Fallo de cierre no es PASS.
No enumera/procede contra otros proyectos ni cancela/pruna tickets.

## Prueba retenida

Auditor ejecutado14:49:27 UTC (1454 es etiqueta del archivo), tres tests
PASS1,197s, un hilo/hijo<=60s. Doce casos: seis procesos Python CPU privados
reales y seis rechazos antes de lanzar; además envelope existente rechazado
sin Popen/sin sobrescribir bytes. Los seis PID terminaron; cuatro abortos
post-launch cubren timeout, fallo de telemetría, deadline y finalización tardía.
Dos controles cubren rc0 y rc3. NaN/política inválida/pérdida de segunda
admisión se conservan como errores, no éxito ni JSON inválido.

Admisión/recursos/reloj adversario son sintéticos; hijos reales solo duermen
brevemente/salen. NO Blender/GPU/gpuq/telemetríaGPU ni prueba operacional de la
red. El auditor guarda los mismos casos usados en los tests, sin segundo barrido.

Report `D:/PROJECTS/.cognition/neuro3d/exp005_watchdog_cpu_20260930_1454.json`
SHA `782a93ee31a2e56133464541626a634afa8813ee4e5f4ce2a8db6639043d6f62`.
Cuatro codeSHA verificados; veintiún pins del plan1438 siguen intactos.

## Pendiente antes de ejecutar Blender

No existe CLI de GPU ni adaptador real de admisión en este núcleo. Integrar
en el piloto propio verificación del holder/identidad/procesos, pins y .exe,
logs retenidos, telemetría fresca, envelope y gates/readbacks/SHA. Resolver o
acotar explícitamente la contención de helpers; no certificarla por estos tests.
No tomar el status completed como aprobación de artefactos o permiso GPU.

14:50 GPU de otro proyecto y006Claude pendiente/RAM1,307GiB; no carga propia
Blender/GPU, nueva reserva ni escritores de Claude. 006 sigue única petición,
sin nueva guardreview/renders. No tocar fixtures/runners/shaders congelados ni
promover conf1. Siguiente integración propia CPU o audit006 si llega retenido.
JEV bloqueado: fallback local sin aval. Skills de desarrollo/continuidad
mantuvieron pruebas focalizadas y separación entre núcleo probado y piloto real.
