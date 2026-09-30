# Próximo paso: costes pareados y todas las fuentes simultáneas

Preparación03:43UTC, **no congelada, no ejecutada**. No cambiar kernels ni
umbrales tras medir. Esta comparación es entre dos backends ALU propios,
no contra MLP, no RT y no equivalencia neuronas/canales.

Cuatro entradas de escenasbase0315 SOLOLECTURA:K3basis0,K3todas1,
K4basis0,K4todas1. Las dos últimas entradasdensas prueban simultáneamente
4/5fuentes; bounds CPU ya conocidos58/128caminos y184/415casts,46ledgermax.
No suministrar al GPU caminos calculadosCPU. Mantener readbackreal porprobe.

Propuesta antes de congelar:compilar ambos kernels en el mismo proceso
Blender,3warmups porbackend/entrada;20pares porentrada con orden AB/BA
alternado predefinido. Rechazar cada resultado que no pase gates de campo,
ledger,conteos y balance frente a oráculo independiente/mismo1e-4/2e-4.
El coste de oráculo se registra separado y no se resta del tiempo medido.

Registrar separadamente: exportaciónreal+pack/preflight+transfer+dispatch+
sync/readback+decoder (tiempo de inferencia caliente completo); tiempoGPU
dispatch/readback existente; apertura/reapertura/compilación/startup como
costes de lifecycle explícitos, nunca escondidos en otrobackend. Mediana/p95
y razones pareadas, todaslasmuestras/counters/orden retenidos;sinselección.
Verificar counterscompartidos/copias y hashesinputs a salida.

No concluir mejora si se reduce trabajo pero aumenta tiempo por menor
paralelismo. Inferencia caliente no es despliegue completo ni entrenamiento.
Si no cabe en120s, conservarpartial/FAIL y replantear nuevo protocolo ANTES
otra corrida, sin bajarreserva ni retocarumbrales trasmedir. RAM1,5/device1,
gpuq porjob/floor4/VRAM18/temp80/deadline06UTC. Claude: críticaindependiente
yOptiX pendiente; no tocar sucarpeta. JEVbloqueado/fallbacklocal.
