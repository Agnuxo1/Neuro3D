# PRECISION-OBLIQUE-TOTAL-PHASE-READBACK-HOST-001

P0 propio capacity_audit/EXP005; base d7cd5c7b0283c5ff29431927b90d06a40a434139.
Modelo nuevo opt-in precision-oblique-total-phase-readback-HOST-v1.
La revisión de desarrollo/pruebas/cognición extendida conserva contratos congelados y reutiliza capturas, sin agentes.

## Entrada y evidencia

API compare(model,request,input_bytes,output_bytes,origin); evidencia internamente sellada, sin override público.
Carga SHADERC001 SHA6316b24df16dfb9080c5aee9d8563c4644541ef500029546e822dcf626723606 y TOTALCPU001 SHAacc107cb584dba1d7845584ac1040569fa3a2dd4be7d2f9c39d702d2ce06b6c3.
Valida pins ancestrales y captura acotada con longitud/SHA, zlib sin trailing/unconsumed bytes.
Reconstituye 96 bytes de P0/P1/gamma0/gamma1/mu exclusivamente de palabras capturadas; no replay de producer, RN, encoding, geometría, sqrt, shaderc o Blender.
Control esperado de 64 bytes retagueado explícitamente del CPU, no readback de dispositivo.
Selector cerrado: caso, recibo compilador, input SHA, SPIRV SHA, ORIGINAL escena, literal, overlay de fase, selector nativo, abi_tag, intención. Tipos exactos; campos extra y cambios STOP.
Input96/header TAG0x54504731,count10,fuentes2,marker1; output64/header mismoTAG,count6,fuentes2,marker1.
CPU_TAG0x43545031/V2propagation0x4f444632 no son este ABI y quedan STOP. Preserva 46 controles sellados: once preparables y35 STOP antes de mirar bytes.
Los dos fallos previos de SHADERC001 permanecen sellados; no se vuelven a compilar ni se alteran.

## Validación y orden

Comprueba exponente crudo de TODOS10 inputs y TODOS6 outputs, y dominio |componente|<=2^40, antes de cualquier decodificación racional.
Input debe coincidir exactamente con paquete ligado a escena/overlay; una copia finita con SHA/selector obsoleto queda STOP antes decode.
Decode binary64 mediante enteros y Fraction; cero operaciones nativas FP64/RN.
Para SOURCE0/1: delta=|readback_value-captured_value|; cota=parent_conservative_rad+8*delta.
El factor conservador8 del protocolo existente se conserva, no se cambia conversión/cota.
Para relativa: cota=8*(geometric_error+gamma_radius+gamma_encoding_error+SOURCE_add_error+sum_SOURCE_deltas+|readback_relative-(readback_SOURCE0-readback_SOURCE1)|).
Exige cada cota SOURCE y relativa<=literal_cap_rad y comprueba que domina distancia a ambos extremos capturados. NO sharedmu rescate SOURCE.
Solo DESPUÉS compara TODOS los bytes con controlCPU esperado. Una salida dentro de cota pero con bits distintos todavía STOP.
STOP es atómico lógicamente: rows=[],verified_rows0,output_sha256=None aunque conserva diagnostics.
MATCH tiene tres filas pero permanece UNATTESTED: dispositivo/fence/guard/scene/material/native/physicalauth False; GPU_launch_allowed False.
Cabecera lógica completa no prueba frescura, sesión, fence, barrera, transmisión, exclusividad ni autenticación. Copiar control y entrada correctos pasa cotejo numérico sin aval GPU.
El selector liga el TRABAJO declarado; no inventa un ticket/deadline de GPU ni autentica procedencia. No integra automáticamente un backend.

## Pruebas y límites

Suite cuatro grupos,154corridas:11 MATCH,143 STOP =35 heredados+108 mutaciones/controles nuevos.
24 nofinitos output (Inf/-Inf/qNaN/sNaN x6);10 nofinitos input. Spy confirma cero llamadas decode en ambos grupos.
33 mutaciones lo+1 (tres componentes bajos por once casos) siguen dentro de las tres cotas pero STOP exactbits.
Tres alteraciones hi+1 fallan cota SOURCE/relative, y traslación exactamente igual de SOURCE0/1 conserva valor relativo pero no rescata cotas SOURCE.
Otros controles: rawdomain2,headers8,legacyTAG4,extent6,staleinput1,selector10+extra,tipos3,modelo/origen2.
No cambia cotas para pasar, no repite barridos de PRECISION005/006, no recomputa cuentasRT.
Verificador independiente inline reconstruye los racionales mediante escala fraccionaria separada, los presupuestos, inputs/outputs/selector, mecanismos de mutación y todos los flags, sin importar core; comprueba pins/AST/API.
QA local no son costes completos de motor: UNMEASURED_NOT_ZERO, ningún ratio/ganador.
Sin GPU ni RAMCIM retry/elevación/bypass (UNKNOWN histórico); CPU1hilo/afinidad1/hijo<=60s.
No SDK/DrJit/Kaggle/push/merge. JEV LOCALsinaval remoto/seguridadNOretry.
No evidencia Bpyfloat32/GPUALU/RT/óptica física. U/GEMM compilada no sustituye inferencia desde escena.
Fixturesconf1/v0/v4/0119/0315/nearestV2/bounds/caps/frozen intactos; Claude dueño capacity/nebulatrace/research/RT, sus archivos no se modifican.
Cuatro propios versionados; checkpoint/tableros LOCAL SINstage.
PedirClaude ACK por ID/SHA y SOLO artifactsYAexistentes guardfailclosed/Float64-floatcontrols/TOTALphasebackend/ingress-fence-readback/material-amplitud-completitud ID/path/SHA/bytes e igual ORIGINAL-overlay-lambda-reference-caps-trabajo-salidas/costes completos; no cargas de relleno.
