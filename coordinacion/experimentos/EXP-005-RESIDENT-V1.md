# RES-001: contrato residente V1, antes de GPU

30/09/2026. Nuevo backend/runner; shader compartido previo inmutable.
No modifica ni sustituye backend/fixtures congelados. NO RT/BVH, batching,
cache de respuestas, matriz, física óptica hardware o ventaja vs MLP.

Dos variantes del MISMO shader: fresh asigna/sube geometría/optics/sources y
outputs por llamada; resident retiene4texturasestáticas+4outputs y asigna
2texturasfuente por llamada. CPU sigue exportando estado evaluado y validando
identidad; NO inferencia sin CPU residual ni costes externos ocultos.

Cuatroinputs K3/K4basis0 yTODAS1, mismos12blends0315 sololectura.3warmups
porbackend/input y20paresAB/BA alternados (160medidos+24warmups), todos
readbacks retenidos. Reloj caliente incluye actualizarfuentes/export/check/
transfer/GPU/sync/readback/decode. Reapertura/compileAPI/setupresidente y
oráculo/I/O aparte, todasmuestras, ratiofresh/residente>1favoreceresidencia.
No equivalencia temporal ni aceleración puraGPU sinGPUeventos/profiler.

Gates sin relajar: campos/ledger/analítico<=1e-4, balance/potencia<=2e-4,
longitud<=1e-5BU; todospuertos/sources/paths/counters según oráculo completo.
Por cada una de4sesiones: secuencia basis+pares complejos+zero en MISMAS
allocaciones;17inputsK3/26K4 (86extra). No readbackintermediofrontier.
Shaderrecorre/trabaja cada llamada. Artefactos nuevos no pisanprevios.

Editar realphase_rad del últimoespejo enBlender, leerestadoevaluado y exigir
rechazoantesGPU/asignación, cierre/referenciasvacías. Otra llamada conestado
viejo tambiénrechazada. CPUtests geometría/T/λ/modos/origen-dirección/orden/
objetoausente/extra/NaN. Al cambiar cualquier estado estático no se reutiliza
el caché: reconstrucción explícita enuncontratonuevo. Setup8alloc+2porcall.

Shader/baseline/manifests/12assets/runner/dependencias SHA antesydespués.
GPUvendedor NVIDIAcontextnative, una reserva120s/hijo110s/host1,5/device1,
floorRAM4/VRAM18/temp80/deadline06UTC. No esperarocupacióndeClaude ni
cancelartickets; abandonar turnosinlanzar si venciera ventana. Si falla,
retenerFAIL ycorregirconcontrato/commitnuevo sin cambiar gates posteriores.
JEVbloqueado/fallbacklocal; revisiónClaude solicitada sinavalremoto.
