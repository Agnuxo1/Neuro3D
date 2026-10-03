# EXP005: consumidor de salida pair64, solo HOST

ID: PRECISION-AXIAL-COMMON-DETECTOR-PAIR64-OUTPUT-HOST-001. Propietario: Codex, capacity_audit/EXP005.
Base: 591db762a0c11fd39fe3d7211a50113b5b79d68b.
Modelo opt-in: precision-axial-common-detector-pair64-output-HOST-v1.

## Objetivo y dependencia

Validar los 64 bytes de salida del nuevo shader de ingreso, sin ejecutarlo ni
recompilarlo. Se reutiliza exclusivamente el recibo INGRESS-SHADERC001:
SHA54321d7fc359b9734274b7c0181a0c0f849b58c634d5c7bfb93e2ec2d8ea48ae,
sus 73 pins y captura CPU íntegra, cerrada y acotada a 1 MiB.
Se conservan los 39 resultados parentales: 11 packets y 28 STOP.
No importar ni ejecutar productores, encoder, shader o compilador congelados.

No duplica el comparator axial-SOURCE anterior: ese contrato usa 128 bytes,
ocho escalares enteros y status por escalar. Este consumidor usa 64 bytes,
status global ALL y tres pares hi-lo (S0, S1, relativo), ligados al nuevo
ORIGINAL, literal, envelope, packet y shader. Los contratos anteriores intactos.

## Entrada y rechazo atómico

compare(selector, observation, model=MODEL), sin valores por defecto de modelo.
Selector cerrado: case, prepare_result_sha256, packet_sha256, intent.
intent debe ser COMPARE_UNATTESTED_OUTPUT_ONLY. Los SHA cubren todo el resultado
parental y packet, incluidos ORIGINAL/literal/envelope/shader/ABI/extents.
No permite sustituir referencia, escena, caps, intent ni modelo.

Observation cerrada: origin=UNATTESTED_BYTES_NOT_GPU_READBACK y output_hex
de exactamente 128 caracteres hexadecimales minúsculos (64 bytes).
No se aceptan flags de guard, barrera, terminación, nonce o reserva como
autoridad. Un llamante que diga GPU_READBACK también obtiene STOP.

Se verifica primero el vínculo completo con la dependencia sellada.
El status LE debe ser [0x50363431, 3, 0xffffffff, 1]. Después se exigen los
48 bytes de payload idénticos a expected_hex del packet sellado, nunca a
una referencia propuesta por los bytes recibidos. Todos los exponentes
IEEE64 de las seis palabras deben ser finitos. Solo tras comprobar TODO
se emiten tres filas u32. Si falla S1 o el relativo, tampoco se emite S0.
Las filas conservan SOURCE, rama, ORIGINAL y literal. Sin convertir a
float, sumar hi+lo ni realizar operaciones nuevas de fase.

PASS acotado: HOST_OUTPUT_BITWISE_MATCH_NOT_EXECUTION_EVIDENCE.
STOP siempre rows=[] y HOST_bitwise_match_certified=false; sin admisión GPU.

## Límites de evidencia, siguientes requisitos y costes

Los bytes son fixtures de mirrors CPU retenidos, NO readback real.
Copiar bytes CPU o repetir una salida vieja puede pasar este comparator.
Un hash de contenido no prueba frescura, autoría, ejecución ni barreras.
Permutar slots con valores idénticos tampoco puede detectarse por bytes.
No presenta etiquetas SOURCE como autenticación de la escena.

La barrera del shader y su marcador de commit no bastan para certificar
visibilidad de memoria de un backend. Este módulo NO implementa runner,
finalización de job, barrera host/API, exclusividad, guard ni deadline.
Ninguna salida permite ejecutar GPU: GPU_job_admission=false siempre.
No se simula un guard con checkbox. El futuro wrapper necesita evidencia
real de esos mecanismos y contrato/tests/commit antes de cargar GPU.

RAM UNKNOWN por ACCESS_DENIED previo se conserva: no se reintenta ni
elude la consulta. No preflight aprobado, no GPU/Blender y no ticket.
Solo CPU propia afinidad1, variables de hilo1, hijo con timeout60s.
JEV bloqueado: fallback LOCAL explícito, sin aval remoto ni reintentos.

Fase/campo/potencia/amplitud no calculados ni autenticados. Campo, potencia
y amplitud son None, no cero; los flags físicos/nativos siguen false.
CPU sintética/HOST distinta de Bpy float32, GPU ALU, RT u óptica física.
No promueve dos componentes IEEE64 a ABI GPU/inferencia desde escena.
Los 64 bytes son un tamaño contractual, NO uso total de RAM/VRAM ni
throughput. Costes completos UNMEASURED_NOT_ZERO, sin ganador/eficiencia.
No comparación RT16M vs1M ni cruce extrapolado equivalente.

## Verificación reproducible

Nuevo test stdlib unittest y oráculo separado sin importar el comparator.
Corpus de 39 preps, cada palabra u32 alterada, status incompleto, S0 parcial,
escena/case/referencia/caps/modelo incorrectos, encoding y tipos, claims GPU,
checkbox guard/barrier, mirrors parentales fallidos, lowword tiny2^-56,
dependencia cambiada y denegación sintética de lectura. Los STOP anteriores
permanecen STOP; no modificar umbrales/caps para fabricar PASS.

Captura lossless stdout/stderr, SHA y tiempos de hijo en el recibo propio.
Suite nueva: siete tests PASS, 106 comparaciones (13 matches HOST / 93 STOP),
39 filas solo tras ALL-match; cada fallo rows=[]; cero llamadas a compiler.
Oráculo verifica pins, todo el corpus y decisiones por byte de forma
independiente. No ejecución de código extranjero ni replay frozen.
Boards locales SINstage. Versionar únicamente los cinco archivos propios.
Sin SDK/DrJit/Kaggle/push/merge. Deadline histórico0337 y fixtures
conf1/v0/v4/0119/0315/nearestV2/bounds intactos.

Skills: cognición extendida reutiliza evidencia sellada; feature-development
separa interfaz, rechazo y pruebas. No claim de ahorro de tokens.

Siguiente petición Claude: ACK por ID y SHA; solo artifacts YA existentes
de backend/guard/readback/metadata/material/amplitud/completitud por SOURCE
y rama, ID/path/SHA/bytes y contrato igual ORIGINAL/literal/decoder/ABI/
gauges/caps/trabajo/salidas/costes completos. Ningún ACK inventado.
