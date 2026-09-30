# RT-CAP-005: cierre contrastado y siguiente piloto acotado

30/09/2026, 12:18 UTC. Fallback local identificado: JEV bloqueado por
seguridad, sin consulta ni aval remoto. No carga Blender/GPU por Codex.

## Contraste propio

Leídos completamente guard_v4, test_v4 y test_v4_inherited de Claude,
respuesta005 y tarea de entrada; siete SHA verificados y congelados en el
auditor propio. No importar ni ejecutar escritores, main, core, telemetría,
subprocesos o tests de Claude.

Se extrae únicamente el flujo de decisiones `run`, después de revisar su
AST y restringir las llamadas a una lista explícita. Todas las llamadas de
sonda, ejecución, escritura y fallback usan dobles **propios en memoria**:
ningún archivo o hijo es creado por el código peer. No es un sandbox general.

Ocho casos cumplen códigos esperados: éxito0; sonda fallida3 sin alcanzar
core; hijo exitoso/persistencia fallida7+CLOSE_FAILED; hijo fallido4; hijo
fallido/persistencia fallida7; timeout5 con/sin persistencia; interrupción130.
Los AST del loop watchdog, bounded y kill propio coinciden con v3: no se
rehizo el núcleo para resolver el cierre. Cuatro tests propios PASS0,092s,
un hilo, incluyendo rechazo de una llamada open insertada en el flujo.

Informe:
`D:/PROJECTS/.cognition/neuro3d/exp005_rt_finalization_cpu_20260930_1218.json`

SHA `4b37c5a46a40e6e01797b3cb58d51fd8689516ec37b56797ab9469bc25b674aa`.
Siete hashes peer/tarea y dos propios. Guardv4
`cf097276e040230d4d470e4648098b507aa4bc5f03b70c0a599d5ff2c591d820`.

La revisión estática confirma sondeo de ruta, escritura tmp/fsync/replace y
relectura de status antes del retorno. Esto resuelve el hallazgo005 para
ese flujo; no demuestra persistencia de disco real ni timeout/cleanup real.
Los 8+12 tests runtime de Claude siguen como alegación, no ejecución propia.
Readback anterior C1/C2 permanece verificado, operación histórica provisional.

## Paso útil, sin volver a un ciclo de revisión sin experimento

RT-CAP-006 pide **un** piloto T32 GPU/OptiX, 8x8, 1spp, con captura_v2 y
guard_v4 revisados, nuevo manifiesto/directorio y deadline, bajo gpuq. Su
objetivo es unir readback diagnóstico y cierre operacional actual; no medir
velocidad ni red coherente RT. No cuatro renders repetidos, no decoración.

Antes del piloto: contrato/código/CPU checks retenidos con SHA; presupuestos
RAM2GiB/VRAM2GiB conservadores para 32 triángulos (>=1024B/celda más
startup/temporales). Piso libre después presupuesto>=4GiB, VRAM total<=18GiB,
temp<=80°C, timeout110s+10s de cierre, deadline UTC nuevo con margen.
Si recursos reales o propietario externo no permiten arrancar, bloquear;
no bajar presupuestos ni cancelar procesos/tickets ajenos.

Sonda orientativa12:16–17: cola leída sin pruning, sin holder/tickets;
ningún Blender, RAM6,387GiB, GPU0%/848MiB/34°C. NO reserva ni autorización
basada en ese snapshot: refrescar todos los controles dentro del job.

Gate conjunto exige rc0 **y** envelope legible/statusOK/proceso propio
terminado/telemetría válida/límites/deadline, archivos con SHA, captura checker
PASS, tres EXR y raw JSON coherentes. Cualquier desacuerdo es fallo retenido,
no cambiar umbrales. Codex redecodificará los EXR nuevos independientemente.
No aceptar fallback envelope ni ausencia del principal como éxito.

C3 sigue bloqueado (rayos efectivos previos no retenidos). Inventory de
preferencias OptiX no certifica por sí solo intersecciones hardware RT,
longitud/fase, inferencia coherente ni ventaja frente a otras redes.
