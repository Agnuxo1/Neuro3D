# PRECISION-AXIAL-SCENE-TRANSPORT-CPU-001

Base bd787a94731e793dbaba08a2c2260c7d4bf7cd4a. Acuse DEPARTURE001 recibo
SHA167532ed212ed30813f3d399990360ba57edfd806f58921fa2b043e1236b8a7d.
Propio capacity_audit/EXP005; skills cognición extendida y feature-development
mantienen dependencias frozen y evidencia nueva separadas. JEV LOCALfallback
sin aval remoto/no retry por bloqueo de seguridad.

## Contrato

Opt-in precision-axial-scene-transport-CPU-v1, perfil exact-point NUEVO.
No reemplaza ni amplía tolerancias de conf1 ni contratos congelados.
Entrada MISMA escena racional axial de ROOT/salida y peticiones mirror explícitas
por SOURCE+SHA+orden. Original prepare_departures debe pasar antes del encoder.
Se verifica SHA frozen exp005_blender_gpu.py antes de cargarlo: import-time sólo
definiciones/stdlb, y se llama SÓLO split_double (2RN32 casts+1RN64sub por scalar).
Nunca main/dispatch/texture_data/escritor/GPU/Bpy. Su código permanece intacto.
El cargador ejecuta exactamente los bytes verificados con compile/exec, sin reread
del archivo entre SHA y ejecución. NOauth de escena/host/telemetría/GPU por ello.

Por cada coordenada de triángulo y posición/dirección de SOURCE:
q ORIGINAL racional -> RN64 Python float -> hi/lo IEEE32 -> suma CPU RN64.
Un cast64 inicial, dos casts32, una resta64 y una suma64 CPU por scalar.
Palabras uint64/uint32 y bytes hi-lo LE retenidos, ORIGINAL nunca sobrescrito.
Separar e_cast=abs(first-q), e_hilo=abs(hi+lo-first),
e_decode=abs(decoded-hi-lo); cota puntual=sumas, error observado<=cota.
Pérdida ORIGINAL->float64 se diagnostica antes del gate de pérdida hi-lo.
Se audita la geometría ORIGINAL y la reconstruida DE ESTA ESCENA cambiada
para preservar contacto/colapso, NO old sweep/fixture/productor ni barrido005006.
Decode CPU float64 aquí es MODELO de consumidor, NO aritmética shader/readback.

No se transforman IDs, orden, unidades BU ni SOURCE/material. SHA canónico literal
ORIGINAL y SHA reconstruido se mantienen SEPARADOS; representación no canónica
[2,2] puede cambiar SHA aun sin cambiar valor exacto. SHA NO autenticación.
Para emitir rutas, todos scalars deben conservar ORIGINAL exacto, ambas geometrías
deben pasar y rutas/SOURCE/primitivas/segmentos/puntos/longitud ser iguales.
Todas SOURCE verificadas antes ANY emisión. STOP conserva evidencia y emitted=[].
No tolerancia nueva positiva, no snap/bias/gauge ni sustituir origen por distancia.
Este prerequisite CPU es deliberadamente exacto, no guard universal de errores.

## Evidencia y alcance

6testsPASS sobre13escenas NUEVAS: 4 controles CPU exact-point y9STOP esperados.
228scalarencodes=456RN32casts+228RN64sub+228CPUdecodeadds+228casts64 iniciales.
Worldgap2^-56 al lado x1: original ROOT/salida conserva2^-57/2^-56;
coords originales colapsan en float64 y decoded ROOTcontacto0 STOP. Distancias
float64 positivas del oráculo original NO autorizan ese transporte de coordenadas.
F(0.1) original YAfloat64: e_cast0, hi-lo pierde punto y segmentos ->STOP.
1/10 racional: e_cast>0 separado; no puede reclamar mismo ORIGINALfloat64.
2^-160 gap ySOURCE2^-162 originalesbinary64: hi-lo underflow colapsa ->STOP.
2^-48 gap a x1 ambas direcciones sí conservado bajo suma CPU64, NOGPUproof.
DosSOURCE exactas separadas ysecondSOURCE0.1loss ->0emittedpaths aun con2diagnósticos.
SHA/request/model/originalcontact/encoderidentity fallan antes split.

No nuevos FAIL inesperados, no thresholds cambiados ni errores ocultados.
Suite stdout lossless/stderr/tiempo/comando en recibo. Oráculo independiente stdlib
sin producer import/spawn comprueba hashes, orden/cobertura scalars, RN por
intervalos exactos IEEE y ties-even (cero/subnormal incluidos), errorstresetapas,
bytesLE, geometría escalar planosx de escenas originales ydecodificadas, SOURCE,
IDs/segmentos/longitudes y atomicidad. Resta x-h exacta por Sterbenz o h0;
este modelo no certifica ftz/DAZ/reasociación/FMA de GPU ni consumidorfloat32.

CPUafinidad1/OMPBLAS1/hijo60s. GPUBlender/preflight/reservas/colas/kills/tickets
ajenos0/noGPUlibreclaim. 0337CLOSEDdeadline yconf1-v0-v4-0119-0315-nearestV2/
bounds/caps/guards/runners/shaders/FAILs/ajenos intactos. Sharedboards/checkpoint
localesSINstage, versionar sólo propios. Sin SDKDrJit/Kaggle/pushmerge/replay.
Todos flags nativepromotion-GPU-nativecoverage-physicalauth-mirrormaterial-
lengthreferencephase-fullfield false. HOSTsplit escalar NOwholegeometry ABI
layout/textures/endiannessGPU/readback/Bpyfloat32/RT/óptica física/inferencia completa.
Longitud reducida racional2segmentos NOlongitudóptica ni Lref/fase/field.
Costes completos UNMEASURED_NOT_ZERO; tiempos tests NOeficiencia/ganador.

Petición Claude ACK ID+SHA recibo; SOLO artifacts EXISTENTES backend/guard/candidates/
readback/ABI SOURCE y contrato MISMO ORIGINAL-decoder-ABI-gauges-trabajo-output-
costes completos ID/path/SHA/bytes, no cargas relleno. Siguiente consumidor nativo
verificado y cotas/material/lambda-Lref-phase antes promoción y jobGPUguardreservado.

Suite rc0/0.8894018999999389s/199562bytes stdoutSHA
0196e7d60ff62d5cdac50a3101dd81ff29200b63ab90986cff6f416ba97c874f.
