# Contrato congelado: coste pareado V1

30/09/2026 03:56UTC, ANTESGPU. Preparación anterior conservada.
Runner exp005_paired_cost.py; kernels previos INMUTABLES, comprobados contra
manifests0315SHAc101286137e59... yshared0337SHAca23f606478b...

CuatroinputsK3/K4base.blend SOLOLECTURA: basis0 yTODASfuentes1 simultáneas.
24warmups(3porbackend/input),160mediciones(20paresporinput),AB/BAalternado
con10primerosA+10primerosBporcaso. Nada descartado/sinselecciónoutliers.

Cada llamada mide sourceupdate→exportevaluado→preflight/pack→transfer→
GPUdispatch/sync/readback→decoder/destruccióntemporales. Cronómetroexterno
hot_inference_ms, más dispatch_sync_readback_ms interno que NO es purokernel.
Oráculo/validación yserialización DESPUÉS cronómetro,tiempo separado visible.
Aperturascena/compileAPI incluidos como lifecycle separado,compilacióndiferida
podría entrar primerwarmup: retener TODOSwarmups. Startup externo =guardjob,
no asignar arbitrariamente a unbackend ni esconderlo como tiempoGPU.

Gates port/field/ledger/counts/longitud/balance de cada una de184llamadas,
mismos1e-4/2e-4/1e-5BU. Oráculoescenacompleta+analíticobase independientes,
CPUfuentes4/5all1 ya comprobadas. Sharedtotalcasts ypaths exactos; repeated
totalcastsSUMAportcasts, sharedtotalcastsÚNICO(no sumar copias).
Snapshotreal EXACTO esperado porllamada,12blendsSHAintactosantes/después.

Reportmediana/p95(interpolaciónlineal ordenada),20razonespareadasrepeated/
shared,16grupos métricas(4inputs×2backends×2tiempos) yTODASmuestrasreadbacks.
Ratio>1 favoreceshared SOLOen estafronteracaliente. No MLP/RT/redesajenas,
no inferencia completa de deployment/no energía/no capacidadmáxima.
Si menosqueries resulta máslento, reportarnegativo sinmodificarprotocolo.

Guard120s/host1,5GiB/device1GiB/gpuqexclusivo/RAMfloor4/VRAMtotal18/temp80/
deadline06UTC/hijo110s. Si falta tiempo/margen,guardarpartialFAIL y nuevo
contratoantesotra prueba;no bajarreservas. Carpetanueva yno editarinputs/
resultadosviejos. JEVbloqueado porsecurity,fallbacklocalsinavalremoto.
