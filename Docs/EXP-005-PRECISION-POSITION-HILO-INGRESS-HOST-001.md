# PRECISION-POSITION-HILO-INGRESS-HOST-001

Nuevo receptor opt-in `precision-position-hilo-ingress-HOST-v1`:
`receive(model, request, raw_frame)`. Solo CPU/HOST exacto, in-memory.
No ABI GPU, red, fence, Blender, inferencia desde escena ni certificación física.

## Identidad y contrato

Padre POSITION-HILO-ENCODING-CPU-001:
`coordinacion/respuestas/PRECISION-POSITION-HILO-ENCODING-CPU-001-CODEX.json`,
SHA `db093b5430ce3ec6e43e748e2d5cf839b0bfaea6369a9d8528fbe7dfd3a41b33`.
Se verifica recibo, captura acotada a 2MiB, oráculo y todos los pins.
Se reutilizan 160 registros de geometría/modo: 120 admitidos HOST y 40 STOP;
los diez selectores inválidos del ensayo padre no son nuevas geometrías.
Los 120 MATCH son exclusivamente controles CPU sintéticos (72 HILO y 48 SINGLE).
Los 40 STOP son 24 pérdidas de hueco SINGLE y 16 contactos declarados S0/S1.
El contexto sintético liga su scene SHA con source_position_BU; no se convierte
en SOURCE autenticado. Contextos S0/S1 sellados siguen STOP antes del frame.

Selector cerrado de seis strings: record_id, mode, parent_receipt_sha256,
parent_record_sha256, geometry_sha256, intent. Intent obligatorio:
`SEALED_POSITION_PACKET_HOST_RECEIVE_ONLY`. Geometry/context incluye SOURCE
del original; el SHA del registro liga también selector, palabras y certificado.
No alias, autodetección por tamaño, presupuesto de error del llamador ni
manipulación de identidad para promover otro registro.

Cabecera LE de 112 bytes:

| Offset | Contenido |
|---|---|
| 0 | 8 bytes ASCII N3DPHI01: versión del contrato receptor |
| 8 | uint32 modo 1=SINGLE32 o 2=HILO32 |
| 12 | uint32 cuenta 15 o 30 |
| 16 | 32 bytes SHA del recibo padre |
| 48 | 32 bytes SHA del registro padre completo |
| 80 | 32 bytes SHA de geometría ORIGINAL y contexto |

Payload LE uint32, origen/fin/v0/v1/v2, XYZ, hi-lo intercalado si HILO32.
SINGLE32: 60 bytes payload, 172 bytes frame. HILO32: 120 bytes payload,
232 bytes frame. No afirmación de trabajo/costes equivalentes.

Orden: modelo/selector -> padre admitido -> tipo bytes y longitud exactos ->
cabecera ORIGINAL/registro/modo -> ALL palabras normal/cero ->
ALL bytes idénticos a captura -> decodificación exacta -> ALL errores contra
ORIGINAL -> certificado sellado idéntico -> MATCH HOST UNATTESTED.
Negativos se rechazan antes de cualquier decodificación escalar.
SINGLE32 y HILO32 no rescatan contacto ni pérdida del hueco 2^-60 previamente STOP.
Un frame diagnóstico de un STOP también se rechaza aunque sus bytes sean finitos.

La suma hi+lo es racional EXACTA HOST, no RN32/RN64 ni FMA.
Cada radio es abs(decoded-original), comparado con el radio sellado.
Todos los 15 componentes, endpoints y vértices cuentan; no correlación cancelada.
No recomputación de encoder, clip ni separadores: reuse solo de certificado exacto.
Signed zero con igual valor racional pero bytes distintos se rechaza.
Subnormal/NaN/Inf STOP; no cambiar dominio normal/cero ni umbral congelado.

## Verificación y límites

Suite propia cinco grupos: 222 principales, 120 MATCH, 102 STOP
(40 bloqueos padre y 62 controles nuevos: selector/modelo, extents, cabecera,
30 corrupciones de palabras, NaN/Inf/subnormal, low borrado, limbs permutados,
signed zero no canónico, contexto/payload cruzado y diagnóstico STOP).
API pública y recibo ausente son auxiliares, no sumados a ese censo.
Se preservan fallos ancestrales. Capturas originales se leen, no se reejecutan.

Oráculo independiente sin importar core: cabecera/bytes, gates y causas,
2880 words exactos, 1800 errores contra ORIGINAL, geometría y contexto,
SHA del certificado y payload, identidad de 120 certificados, censo y pins.
No repetir las cotas geométricas previas para rellenar.

Ledger semántico PARCIAL principal: 2880 decodes exactos, 1080 sumas exactas
hi+lo, 1800 diferencias absolutas contra ORIGINAL, 120 matches y 120 reuses.
Validación, comparaciones, SHA, racionales internos, serialización, I/O/setup,
upstream, auxiliares y memoria no instrumentados integralmente:
UNKNOWN_NOT_ZERO. Se informa tiempo acotado de prueba, no benchmark competitivo.
Ningún ahorro/eficiencia/velocidad/GPU/RT winner se infiere.

Resultado admitido: HOST_POSITION_FRAME_MATCH_UNATTESTED, frame_verified=True.
Promoción STOP, scene/uncertainty/full_visibility/phase/physical/GPU flags False;
field/amplitude/power None. STOP no publica rows, geometría/radios ni frame SHA.
Bpyfloat32 no ha demostrado conservar 1+2^-60. CPU sintética no es RT ni óptica.

Fallback LOCAL: JEV bloqueado por seguridad, sin retry ni aval remoto.
Fixtures/runners/shaders/contratos congelados intactos. No GPU/compiler.
Solo cuatro archivos propios versionados; sharedboards/checkpoint sin stage.
Pedir Claude ACK por ID+SHA y artifacts YA existentes backend/guard fail-closed/
ingress-fence-readback/material/completitud y mismo ORIGINAL/inputs/outputs/costes
completos. No nueva carga por relleno; 16M vs 1M no equivalencia.

Capturas, pins y fuentes de verificación reproducibles están en el recibo propio.
