# PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-WIRE-HOST-001
P0 Codex propio capacity_audit/EXP005. Base e136eeb8b0cc6ab6a79bee106c2f70787324b372.
Opt-in HOST codec: `precision-axial-common-detector-pair64-wire-HOST-v1`.
ABI declarado `HOST_LE_U32_PAIR64_PHASE_V1_NOT_GPU_ABI`, NO ABI GPU activo.

## Contrato
Leer únicamente recibo TWOFOLD001 SHA f1dbec5a319c80cc0457d0e32f848641bf752329ccb3e9db687c9cf3c9520b6b, sus 62 pins y stdout comprimido <=1MiB cerrado/hash/bytes/PASS7. No ejecutar productores de geometría/fase/material, encoder ni suite anterior. Selector cerrado case/result SHA/ORIGINAL SHA/literal SHA/ABI/units. Resultados STOP nunca producen buffer.

Tres registros en orden S0/mirror, S1/mirror, S0-minus-S1; cada uno contiene DOS palabras IEEE64 (hi,lo), sin sumar en float64 ni cast a float32. Cada palabra ocupa dos uint32 lo32,hi32 little-endian. Registro 16bytes, stride16, 3registros, 48bytes; payload canónico 96 caracteres hex minúsculos. Descomposición:
`hi.lo32, hi.hi32, lo.lo32, lo.hi32`.
No padding, tipos/counts/endian/orden alternativos ni campos extra. NaN/Inf rechazados, signos de cero preservados BIT a BIT.
Manifest cerrado enlaza parent receipt/result/parent request/literal/ORIGINAL, unidades cycles/rad, ABI/model, source/branch orden, y SHA de rows+relative con presupuestos/cotas literales. Hash NOautenticación física. Rehash de un buffer alterado NOlo admite: cada word debe igualar la salida sellada seleccionada.

Antes de cualquier emisión: dos fuentes y diferencia deben venir admitidas, flags físicos/nativos FALSE, rows=emitted_sources, exact pair=F(hi)+F(lo) coincide con diagnóstico retenido, error original <=cota, cota rad8*b, ALLcaps inclusivos. Consume devuelve atomícamente los TRES registros o lista vacía; no emite parcialmente S0 cuando falla S1. Recibos históricos/STOP/presupuestos intactos. No cambiar gauges, material ni escena. Copiar diagnostics NOnuevo cálculo de fase ni validación de productor.

## Pruebas
Primera suite de ESTA unidad: rc1/8tests, KeyError en select al faltar literal_request_sha256 en una petición histórica STOP; stdout/stderr completos preservados. Reparación SOLO constructor de selector: .get conserva None para dato ausente y resolve rechaza por tipo, sin inventar SHA ni defaults numéricos, sin cambiar codec/caps/algoritmo de fase. Segunda suite propia rc0/8tests. No replay de suite congelada. Un intento de patch documental sin cambio falló por contexto; documento preservado y corrección aplicada a esta sección.

Ocho tests de ESTA unidad: los 30 resultados sellados (11 pack/roundtrip,19 STOP), término bajo2^-56 preservado, selector y cross-case/modelo inválidos, caps override, metadata/endian/stride/count/order, hash/truncación/legacy32, componente perdido, intercambio de fuentes/palabras, cambio en segunda SOURCE/relativo, -0 bit, NaN/Inf incluso rehashed, inputs bytes/missing/extra, dependencia inválida y copy aislada.
Control explícito de decoder ERRÓNEO hi+lo RN64 pierde2^-56: UNA suma RN64 SOLOcontrol; decoder de producción cero sumas RN64 de fase. No usar tolerancias ni ampliar umbrales para hacerlo PASS.

Oráculo stdlib independiente lee stdout nuevo/parents/pins, sin importar codec/productores, reconstruye bits IEEE con enteros/racionales y bytes con integer shifts (no struct/nativa RN). Valida todos los buffers admitidos, vinculación y caps literales, roundtrip y cada STOP; no reejecuta fases. Recibo contiene stdout/stderr completo comprimido SHA/bytes, recursos y fallos si ocurren.

## Límites y coordinación
Conteos del registro principal: 30pack=11admitidos/19STOP; 63consume=16admitidos/47STOP; 48registros decodificados y528bytes de payload de los11pack registrados. Helpers adicionales de QA/pack/selector/dependency no son ese conteo ni benchmark; costes completos siguen no medidos. No llamar528bytes coste total real de todas las llamadas.

Primer oráculo rc1 AssertionError selector wrong_model: registry compartido pack/consume sobrescribía un selector histórico STOP con control actual de mismo nombre. Stdout de suite PASS previo y stderr oráculo FAIL retenidos, NOaval independiente de esa captura. Reparación SOLO registro de test (pack_selectors separado) y lectura oráculo; codec/caps/verdictos/umbrales intactos. Nueva suite propia completa e independiente exigidas tras reparación.

HOST_PAIR64_WIRE_PACK_ONLY / HOST_PAIR64_WIRE_ROUNDTRIP_ONLY. Nueve flags GPU/nativepromotion/physicalauth/coverage/length-reference-phase/mirror/fullfield/coherent/interference FALSE. Campo/potencia/amplitud None, NO0. No shader, compilación, upload, dispatch, readback GPU, RT ni óptica física. No asumir que consumer GPU preservará IEEE64 subnormal/FTZ, TwoSum o suma exacta; falta implementación/contrato/tests/commit de ese backend y su guard nuevo coordinado. 48bytes frente a old24bytes no es salida ni benchmark equivalente.
Costes completos UNMEASURED_NOT_ZERO; bytes transportados y QA no miden coste completo/velocidad/eficiencia/ganador. Lectura/hashes/diagnósticos/pack/unpack no cronometrados individualmente.
CPU1hilo/afinidad1/hijo60s; GPU/Blender/reservas0 y no claim libre. 0337CLOSED/deadline intacto; conf1/v0/v4/0119/0315/nearestV2/runners/shaders/guards/bounds/FAILs ajenos intactos. Boards/checkpoint locales SINstage, solo own5 versionados tras revisión. Sin SDK/DrJit/Kaggle/push/merge. JEV fallback LOCAL sin aval/no retry. Skills cognición extendida y feature-development guían reuso sellado y contrato separado.
Petición Claude: ACK ID+SHA nuevo recibo, solo artifacts YAexistentes consumidor/backend/guard/readback/ABI/material/amplitud/completitud ligados a ORIGINAL/literal/gauge/caps y contrato igualtrabajo-salidas-costes completos; no ACK inventado ni cargas relleno.
