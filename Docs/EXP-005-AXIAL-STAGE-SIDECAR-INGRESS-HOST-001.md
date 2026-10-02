# AXIAL-STAGE-SIDECAR-INGRESS-HOST-001

P1 propio EXP005, opt-in axial-seven-stage-sidecar-UTF8-SHA-bounded-HOST-v1. Base9798032. JEV LOCAL sin aval/noretry por bloqueo seguridad.

## Formato INPUT
Sidecar separado UTF-8 JSON: schema=axial-seven-stage-allocation-sidecar-v1, input_packet_sha256 del paquete COMPLETO, plan del contrato seven-stage previo. Recibo de bytes separado: bytes entero estricto y sha256 lowercase64hex. SHA y longitud se comprueban ANTES de parseo. Hashes atan contenido, NO autorización/autenticación de escena/coherencia/ejecución/GPU.

Preflight léxico ANTES del JSON global: bytes1..65536, profundidad<=12, contenedores<=2048, enteros<=96dígitos, strings decodedUTF8<=256bytes/tokenescapado<=1538chars. UTF8 estricto, sin BOM, comentarios, float/nonfinite, strings con surrogate aislado ni gramática inválida. Parse global rechaza claves duplicadas ya decodificadas, incluso alias escapados. Whitelists de envelope/receipt/plan, binding freshcontext y cupos del contrato previo. Estos límites son PROTOCOLO opt-in de recursos, no cambio de umbral científico/conf1 ni cuantización de quotas; inputs que no caben STOP, nunca se redondean.

Ausencia de sidecar produce STOP sin plan/zero/default. Sidecar presente con plan:null se RECHAZA; no equivale a ausencia. Serializador acepta sólo plan válido, emite JSON canónico+recibo, no escribe archivo ni elige cuotas. Reader acepta whitespace JSON válido pero preserva raw-wireSHA separado del canonical-envelopeSHA. Es INPUT válido sólo, no adopción de política ni comparación de cargos ni campos. Resultado atómico: si falla una entrada del lote no retorna resultado parcial; no escritores externos.

## Validación y alcance
17paquetes reales sin sidecar siguenSTOP; controles sintéticos de3planes INPUT fijos anteriores se SERIALIZAN/RECIBEN, NO se adoptan, no se cambia metadata congelada. Sin reejecutar comparación de cargos numéricos, productores/suites anteriores/geometry/Horner/material/reduction/power/readout/GPU.

Suite nueva4tests: roundtrip y whitespace; SHA/longitud/types/duplicatekeys/schema/null/binding/quotas/UTF8/BOM/NaN/comments/trailing; recursos ANTES del parserglobal y boundaries permitidos (65536bytes,depth12,integer96,string256); fallo segunda entrada sin resultado parcial. Oráculo stdlib independiente sin imports producción: verifica SHA/rawbytes, scanner separado/estructura después del parse, uniqueness y controles registrados, reconstruye INPUT/plan/accounting y diagnósticos; no inferencia/RT/physical.

La cota máxima de bytes con padding se registra como base_wire+cantidad exacta de espacios+reciboSHA, no miles de espacios en reporte. Rechazos conservarán wirebase64 o descriptor exacto reproducible. Captura suite completa en recibo.

38flagsampliasFALSE; caps/radios/FAIL/fixturesconf1-v0-v4-0119-0315-nearestV2 intactos. CPU1hilo/afinidad1/hijo60s. Costes HOST parsing/SHA/racionales/IO/setup/upstreamretained/remaining UNMEASURED no cero; wall suite no eficiencia/igualtrabajo. GPU/Blender/SDKDrJit/Kaggle/pushmerge0. Ventana0337CERRADA/deadlineintacto; GPU futura sólo reservaClaudeexclusiva/gpuq/procesosRAM-VRAM-temperatura/guardfailclosed/NUEVOdeadline/límitesusuario. Sharedboards/checkpoint local SINstage; archivos/escritores/procesos/tickets ajenos intactos.
