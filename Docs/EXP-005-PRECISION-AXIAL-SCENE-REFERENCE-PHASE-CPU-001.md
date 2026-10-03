# PRECISION-AXIAL-SCENE-REFERENCE-PHASE-CPU-001

Base ba540ea013232a870ffb408219424f5efa0b333c; acuse TRANSPORT001 recibo
SHA42298df01944d403c52ebc47edb9988ca812683ba1c9b387eb2b10894cfe1fcc.
Propio capacity_audit/EXP005, opt-in precision-axial-scene-reference-phase-CPU-v1.
Skills cognición extendida+feature-development reutilizan evidencia pinneada SIN
recalcular escenas/productores anteriores. JEV LOCALfallback/sin aval/no retry.

## Contrato adicional explícito, NO óptica implícita

Se lee sólo recibo anterior pinneado y30dependencias, salida lossless validada
con límite1MiB cerrado. No producer/importtracer/replay, geometría nueva0.
Rechazos de transporte anteriores se propagan, nunca resucitan.

Cada SOURCE de un caso CPU exact-point tiene petición cerrada en MISMO orden:
original_scene_sha256/source_id/branch_id, plano referenciax racionalBU,
normalx exacta±1, wavelength racionalBU>0, phase_budget racionalrad>=0,
units BU/rad. Tipos bool rechazados, racionales2048bits/abs<=1e6.
SHA nuevo gauge/contrato incluye parent/case/model yTODASpeticiones/orden/caps.
Estos parámetros fueron AÑADIDOS explícitamente por este modelo: NO estaban
en la escena geométrica previa, no son materiales/lambda físicos certificados.
No defaults, gauge silencioso ni declaración de experimento equivalente.

Plano de referencia axial x=R, normalσ. Lref=σ*(D-R), Dendpoint de ruta retenida.
L=sumados2segmentos exactos del caso ORIGINAL. CiclosORIGINAL=(L-Lref)/lambda.
Se encodan R/lambda mediante split_double frozen+CPUdecode64 de bytes SHAverificados,
sin reread; no main/GPU/Bpy/dispatch. Exact-point loss parámetros STOP antes
ANYsum/path. Refλ, SOURCE ybranches todos válidos antescuentas yANYemisión.
No lambda modificada/relajada para hacer pasar un caso. ParamexactoONLY opt-in.

Grafo CPU64 sin FMA/reasociación: suma2segmentos ya convertidos y RETENIDOS;
endpointfloat64 cast exacto; proyección D-R/signflip; resta Lfp-Lref_fp; divisiónλ.
Cada palabra uint64 y cada error racional retenidos:
bL=castserrorRETENIDO+sumaRN64error,
bR=error referencia proyectada,
bResidual=bL+bR+restaRN64error,
bCycles=bResidual/lambda+divisiónRN64error.
Comparar cocienteFP64 con cocienteORIGINAL racional; observar<=bCycles.
Cota error fase de propagación SINenvolver: bPhase=8*bCycles porque2pi<8.
Se usa <= inclusive incluso cuando error0. No cálculo pi/trig/selector/modulo,
material mirror/energy/fullfield; NOfase absoluta del campo óptico certificado.
El factor8 es envolvente matemática conservadora NUEVA, NOthreshold de conf1.
Presupuesto NUEVOdeclared, parte SHA; no retoca caps frozen ni Lref para obtener PASS.

TODAS SOURCE calculadas antes ANYemitted; un excedente deja0emitted.
STOP conserva parámetros, graph/error yflags falsos. Diferencias de presupuesto
producen gaugeSHA distinto: NO comparar como mejora equivalente.
Aceptación significa SÓLO cota RN64 bajo este contrato adicional y puntoCPU exacto.

## Verificación y límites

7tests/19peticiones NUEVAS sobre rutas retenidas:4CPUparciales/15STOP esperados,
7SOURCEgraphs+cotas,20paramscalarencodes=40RN32casts+20RN64sub+20decodeadd+
20inputcasts64; 7endpointcasts64/7sumasL/7restasRef/7restasResidual/7divisiones.
Operacionesgeometry-oldcasts NOejecutadas otra vez; ambas soncache verificadas.

DosSOURCE ciclos14/6 separados/error0/cap0; normal negativa ciclos-26 preservados.
En exact_pair_plus (gap2^-48), referenciaR=-999999, lambda2^-30:
proyección pierde2^-48BU; referencia+resta residual producen bPhase=5/65536rad,
supera presupuesto1/10^12 ->STOP. Fallo retenido, no ampliar presupuesto.
7/3 quotient divisiónRN64error>0: cap0 rechaza; cap1/10^12 sólo controla
una petición DISTINTA explícita/gaugeSHA nuevo; NOcampo/nativo/promoción.
ParamR=F(0.1)/lambda=F(0.1) pierde punto; secondSOURCE invalid ->0path arithmetic.
Bindings/units/bools/missinglambda/zeroλ/negativecap/model/parent identity STOP.
UpstreamworldthinSTOP no encoder ni vieja geometría.

Fallo inicial testSETUP retenido lossless+2fuentes originales: preparó request
DENTROdel parche que invalida parentSHA, excepción antes auditoría. Se movió
SÓLO preparación q antespatch; core byteidéntico/thresholds/modelo intactos.
Oráculo independiente stdlib sinimportprod/spawn/replay comprueba pins/fuentes,
cambio único, IEEE RNties-even, parámetros/graph/CICLOS ORIGINALES/cotas exactas,
SOURCEatomic/gaugecaps diferenciados/oldSTOPretained. No nuevos FAIL ocultados.

CPUaffinity1/OMPBLAS1/hijo60s; GPUBlender/preflight/colas/reservas/kills/tickets
ajenos0/noGPUlibreclaim. 0337CLOSEDdeadline/conf1-v0-v4-0119-0315-nearestV2/
bounds/caps/frozenrunnersshadersguardsFAILs/ajenos intactos. Sharedboards locales
SINstage; versionar sólo propios. Sin SDKDrJit/Kaggle/pushmerge/JEVretry.
CPU64 metrología LOCAL NO Bpyfloat32/nativehi-lo/RN32FTZ/GPUALU/RT/óptica física/
materialphase/fullinference. Todos flags certificación nativa/física/phasecampo
False. Costes completosUNMEASURED_NOT_ZERO; tiempos tests no eficiencia/ganador.

Petición Claude ACK ID+SHA recibo; sólo artifacts YAEXISTENTES backendguard/
ABI ramaSOURCE/igual ORIGINAL-decoder-ABI-gauges-work-output-fullcosts ID/path/
SHA/bytes, no cargas relleno. Próximo link parámetros reales de escena/materiales/
nativeconsumer/cota campo y guard-reserva-preflight por nuevojob antesGPU.

SuitePASS rc0/0.6042095000157133s/raw46960SHA
b8e39f1ac7a421e005fed111969bd4fe2b128b7db0812a80c20a1136fd218b1c.
InitialsetupERROR rc1/0.6224588999757543s/raw45554SHA
e6939d538bdff787f324182d93095c66a383df4ae9b3a253b1e7e06a916bf0c2.
Ambos stdout+stderr/comandos íntegros enrecibo.
