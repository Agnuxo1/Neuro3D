# BATCH-001: preparación, NO contrato congelado ni GPU implementada

Se persigue saturarGPU con variasentradas independientes, no enumerar todos
losrayos enunaúnicainvocación. Propagacióncompartida actual agrupa puertos
pero una sola entrada pordispatch no asegura utilización deldispositivo.
No esperar ventaja deRT/coremillonesrayos sin medircampos/costes.

ABIpreparado frontier_batch_inputs.py: K3/K4, batch1/8/32 (máximo32), escena
estática compartida yfuentes crudas distintas porentrada;ningúnpathCPU ni
matriz. Solo copia/empaqueta/especificaformato. bytesestimados corresponden
texturastransporte/outputs, NO memoriarealdriver/compiler/temporales; seguir
reservas conservadoras/guard ymedirVRAMreal. Cualquierestadoincompatible
antesGPU rechaza elbatchentero. Orden fuente/modo/input inmutable.

Próximo contrato/kernel nuevo separado: una invocación lógica porentrada,
outputcampos/statsinput×port, ledgerinput×port×128 yworkporinput. Compartir
triángulos/props; no readbackfrontier ni transformaciónpesos. Flags específicos
deerror, ausencia decontaminación entreentradas, ceroentreentradasnoparciales,
identidadscenehash+kernelhash. Cumplirboundsigualesshared yfailclosed decoder.

AntesGPU testsCPU ABI/indexado ykernelhelpersexactos, oráculosporentrada
(base/pares1/i/all1/zero) ystaleoutputs. Medir batch1/8/32 conlatenciadebatch,
latenciap95porpetición ythroughput; costeextrabatch/espera/sync/readback y
preparación/compilación explícitos. Comparar mismojob noescogerganadores.
Controls intervención/sham/cono causal, geometry/T/λ/modechanges invalidan.
Mismosumbralescampo1e-4/balance2e-4/longitud1e-5, sinreinterpretarprecision.

RT deClaude sigueindependiente; esta preparaciónALU no seatribuyecómputoRT.
Corepersonalizado OptiX/CUDA/UnrealRDG comparaciónposterior, editorBlender
no reemplazado todavía. DLSS/FSR visor/aproximación: untestCPU deoráculo
encuentramismos endpointsintensidad aphase0/2π pero intermediophaseπ cambia
>.1: interpolación deRGB/intensidades no garantiza resultadocoherente.
No certifica queDLSSfalleunbenchespecífico, sírefuta usarlo como garantía.
RevisiónClaude solicitada; JEVbloqueado/fallbacklocal. Guard120s,corte06UTC.
