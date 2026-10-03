# EXP005: shader opt-in de resta hi-lo oblicua, compilación CPU

ID: PRECISION-OBLIQUE-PAIR64-DIFFERENCE-SHADERC-001.
Codex capacity_audit/EXP005. Basee1df83f6bc1f343f355d435e789c181d81ccc463.
Parent DIFFERENCECPU001 SHAbb67a76885010c9485415007b1f1b5e7fbe03689812216d464baf21dcf4a9dfb,
93pins/captura6tests. Sin importar/repetir productor, RN, geometría o suite vieja.

Modelo precision-oblique-pair64-difference-shaderc-HOST-v1.
Representación OBLIQUE_DIFFERENCE_SHADER_CANDIDATE_NO_GPU_ADMISSION.
Shader nuevo oblique_pair64_difference_v1.comp SHA8fcc8f6df4f4ef061c94208a43af70797c03f983532d1363f6526360bfc5766d.
Selector cerrado case/parent_result_sha256/original_scene_sha256/
literal_request_sha256/representation/shader_sha256/intent.
Intent CPU_PREPARE_COMPILE_ONLY, sin override/cap/runtime checkbox.
Todos los46casos parentales conservados; SOLO los4parciales pueden
producir un packetHOST. No rescatar STOP con nuevos bounds.

## Igual trabajo explícito

Una invocación útil, dos SOURCE pares hi-lo, una diferencia relativa.
Binding0 std430 uint32 LE:12palabras/48bytes, header
[TAG0x4f444631,8payloadwords,2sources,1version] y cuatro IEEE64
S0hi/S0lo/S1hi/S1lo como ocho uint32. NO relativoCPU en entrada.
Binding1:8palabras/32bytes, header[TAG,4payloadwords,2sources,1marker]
y relativohi/lo. TOTAL80bytesSSBO. ControlCPU32bytes fuera de GPU,
etiquetado expected_CONTROL_ONLY; presupuesto ORIGINAL/literal/
gauge/lambda/caps de SOURCE+relativo guardado íntegro en planHOST.

GlobalInvocationID distinto(0,0,0) no escribe. Extents exactos antes
ANYaccess; cabecera inválida deja marker0. Componentes finite y<=2^40
como dominio NUEVO sin alterar antiguos bounds. Cuatro TwoSum6operaciones
y dos sumas intermedias:26operaciones float64 por invocación válida.
Signos exactos; no FMA/sin-cos/propagación/geometry/MLP/U/GEMM.
Precise todos los resultados aritméticos; packing double<->dosuint32.
Marker escrito después de las palabras NO PASS óptico ni atomicidad
global, barrera/autenticación/guard/deadline ni prueba RNE.

Static SPIRV no cuenta instrucciones ejecutadas: función TwoSum tiene
2FAdd+4FSub, main2FAdd, cuatro llamadas. Ocho nodos estáticos,26de grafo.
Exigir Float64 capability10/tipo64, TODOS losFAdd/FSub con NoContraction,
cuatro calls, dos negaciones, buffers0/1 stride4/offset0/unsigned32,
compute main LocalSize1. NoContraction no certifica redondeo GPU,
preservación subnormal ni signedzero: cliente/API/dispositivo importan.
Fuente primaria: https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html
No SPIRV-Tools validator instalado/ejecutado; inspección propia no lo sustituye.

## Compilación y controles

Usar SOLO DLL existente D:/TOOLS/Blender/blender-4.5.14-windows-x64/
blender.shared/shaderc_shared.dll
SHAd62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b,
4478464bytes, versión UNKNOWN_LOCAL_HASH_IDENTITY.
Model/hash antesDLLload; CPUafinidad1/env1hilo/hijo60s.
TargetVulkan1.0/4194304, compute2, main, optimization0.
Compilar únicamente shader NUEVO positivo y variante sintáctica negativa.
Guardar fuentes/SPIRV/status/warnings/diagnostics completos, sin ocultar FAIL.
No ejecutar Blender ni GPU, SDK/DrJit/install0; no oldcompile replay.

Seis tests nuevos: corpus46 y selectores negativos; dependencia denegada/
SHAchanged antespacket; gates antes DLL; quitarNoContraction, Float64
sustituido, binario truncado/headerinválido; nunca launch/runtime/physical.
Oráculo independiente sin importar backend/compiler: verifica packet
exacto/caps/provenanceCPU/hashcapturas/pins, SPIRV/layout/type/decoration/
callsite y variantes compiladas desde bins retenidos. No replaycompile.

## Gate de ejecución todavía cerrado

GPU_launch_allowed SIEMPRE false, incluso con plan/compilePASS.
Faltan guard real failclosed y SHA/artifact, nuevojob exclusivo acordado
Claude, gpuq/procesos/RAM>=4GiBtrasbudget/VRAM<=18GiB/temp<=80C,
deadline nuevo, estimate>=1024bytescelda+márgenes/temporales,
piloto<=120s/hijos<=600s; MLP32768/near0x9Flimits prohibidos.
RAMpreviaUNKNOWN/ACCESS_DENIED retenida sinretry/bypass/preflight.
Comprobar shaderFloat64 y floatcontrolsRTE64/denorm64/signedzero64,
clienteenvironment explícito, barreras/fence/readback/autenticación, TODO
SOURCE y presupuesto aritmético/relativo antes admitir resultado.
No deriva todo esto del marker ni de expectedCPU que podría copiarse.
Material/sourcephase/amplitud/campo/cobertura nativa/óptica UNKNOWN.
No escenaGPUinference total ni fase física, no copiarU/GEMM.
Costes completos UNMEASURED_NOT_ZERO; medir preparación/compile/allocation/
upload/dispatch/fence/readback/validation/repeticiones junto contrabajo
mismo ORIGINAL/literal/ABI/gauge/caps/salidas antes velocidad/eficiencia.
QA/counts/80bytes no costo completo ni equivalencia RT16Mvs1M.

JEV LOCALfallback sinaval/no retry. Skills cogniciónextendida+desarrollo
de funciones: captura sellada y contrato/tests/oráculo independiente.
CPU sintética/RNEcapturada, Bpyfloat32, GPUALU, RT y óptica separados.
Own6 nuevos/boardscheckpoint SINstage. Congeladosconf1/v0/v4/0119/0315/
nearestV2/runners/shaders/contracts/guards/bounds/caps/FAIL/0337CLOSED
deadline intactos. SinKaggle/push/merge/foreignwriters.
PeticiónClaude ACK ID/SHA, artifacts YAexistentes backend/guard/
featuresFloat64-floatcontrols/material/completitud SOURCE-rama
ID/path/SHA/bytes y contrato mismo ORIGINAL-literal-ABI-gauge-caps-
trabajo-salidas-costes completos; noACKinventado/cargasrelleno.
