# PRECISION-POSITION-HILO-ENCODING-CPU-001

Estado: candidato HOST opt-in de codificación de posiciones. No inferencia de escena, ABI de hits ni ejecución GPU.
Base: 97617a323e912fec3d59854b6f134c2c01299a95. JEV LOCAL por bloqueo de seguridad, sin retry ni aval remoto.

## Entrada ligada y formatos explícitos

Modelo `precision-position-hilo-encoding-CPU-v1`; API `audit(model, request)`, sin radios/escena/evidencia sustituibles públicamente.
Padre CLEARANCE001 SHA7b17d4f38db66357ff6c8589325283e1b5a85e041304d4233179a93a6013c9e1/111912bytes.
172pins ancestrales verificados antes cálculo; capturas con SHA/longitud/zlib<=2MiB; no ampliación de límite.
Lectura sellada de80geometrías y cajas cero previas, ligadas a original finite y a SHA/contexto SOURCE.
72geometrías de separación son CPU SINTÉTICAS;8contactos vienen de dos escenas CPU declaradas S0/S1.
Selector6campos: case, mode, parent_receipt_sha256, parent_record_sha256, geometry_sha256, intent; todos strings exactos, sin extra/omisión.
Modos `HOST_SINGLE32` y `HOST_HILO32`, sin sustitución silenciosa de uno por otro.
Contacto de padre STOP antes de codificar, aunque se solicite hi-lo; ningún oldSTOP cambia.

Orden de posiciones: origen, fin, vértice0, vértice1, vértice2; XYZ de cada uno.
SINGLE32:15uint32/60bytes little endian. HILO32:30uint32/120bytes little endian, hi seguido de lo por coordenada.
Estos tamaños describen un paquete HOST, NO una ABI GPU aprobada ni comparación de coste entre backends.
Valores originales racionales sellados BU con límite heredado de128bits/1000000BU.
RNE32 implementado con enteros/racionales: normal finito o cero. Subnormal/no finito/domainoverflow STOP, sin relajar guards previos.
Cero racional se codifica +0 canónico; no se afirma preservación de un signedzero que el racional no contiene.
Para hi-lo: hi=RNE32(original), residual=original-exactDecode(hi), lo=RNE32(residual).
Residual y suma hi+lo son operaciones EXACTAS HOST, NO suma float32 ni restasRN64/operacionesGPU.
Centro = exactDecode(hi) [+exactDecode(lo)]; radio por coordenada = abs(centro-original), DERIVADO, no elegible por el llamador.
Los quince radios encierran la coordenada original respecto al centro codificado, sin presuponer error de hit/material/posición física medido.
No se presume correlación cancelable ni se suma/reemplaza un cap de fase.

## Separación y reutilización factual

Se conserva contexto ORIGINAL/SOURCE, pero la geometría codificada y sus radios quedan explícitos y separados.
Si centro==ORIGINAL por contenido exacto y todos los radios0, se reutiliza SOLO el certificado sellado de cajas0 idéntico; SHA/original/radios/status verificados.
Si cambia el centro/radio, nuevo recorte de soportes de separación en la geometría CODIFICADA, no repetir el clip nominal.
Se llama solo a la biblioteca matemática propia `coplanar_clearance_CPU_v1._bound`, que permanece intacta; no sus runners/escritores.
Cobro por los cinco puntos y las tres coordenadas, ejesL1=1, gap estrictamente positivo. Gap0/negativo STOP.
Requisitos nominales de esa biblioteca y límite128bits también se mantienen para centros/radios derivados; ningún bound nuevo para admitirlos.
STOP mantiene diagnóstico/palabras perdidas, pero rows=[], packet_words=[], packet_sha256None y encoding_error_derivedFalse (sin paquete admitido).
Admisión `HOST_POSITION_ENCODING_SEPARATION_ONLY` es SOLO certificado HOST: nunca scene/uncertainty/GPU/fase/fullvisibility/physical auth.

## Evidencia nueva y costes diferenciados

Suite5grupos PASS rc0/0.5421167999738827s; raw2086705bytes (<2097152), SHA90a531da01aba7a05d4e88166e1a16d8b85da2b738562c4528cbb933bf6f6854.
170principales:120HOST separación y50STOP.
72miss×2formatos:48SINGLE32+72HILO32 separaciones HOST;24SINGLE32 pérdidas de hueco2^-60 STOP.
8contactos×2formatos=16STOP antes codificación.10selector/model negativosSTOP.
16auxiliares de codificación (0/+-1/ties-even/racional1/10/mínimo normal);12negativos de subnormal/residuo subnormal/overflowdomain/noFraction/words no finitos-tipos-extensión.
API pública hi-lo admitida HOST y ausencia simulada de evidencia STOP. Censo principal separado de auxiliares.
Principal:3240RNE32+3240decodeexactos,1080restasresiduoexactas y1080sumasexactas;24separadores NUEVOS,120certificados reutilizados.
Auxiliaresválidos:24RNE32/24decodes/8residuales/8sumas, sin separadores; operaciones de controles negativos y API aparte, no esconderlas como coste principal.
Costes completos UNMEASURED_NOT_ZERO; contadores lógicos PARCIALES HOST no tiempo/energía/ocupación/RT ni rendimiento comparable. Decodificar originales, diferencias de error, internals enterosRNE, validación, serialización e I/O no están instrumentados íntegramente: UNKNOWN, nunca0. Controles negativos conservan inputID/status/reason; sus costes no están completos.
Captura y código verificador en recibo hermano. PRE independiente PASS rc0/0.5011459999950603s/176pins; POST e identidad own4/indexvacío/boardsSINstage antes cierre.
Verificador independiente NOimporta núcleo: celdas de vecinoIEEE32/mitades/tiepar, error exacto por coordenada, layout/SHA, identidadcaché y8esquinas para24separadores nuevos (6720proyecciones).
Compara SOURCEcontext y cajas derivadas, rechazos/censos/flags/pins/API. No ejecuta productores ancestrales ni recompila shaders.

## Límites y preservación

CPU1hilo/afinidad1/hijo60s/GPUBlendercompiler0/producer0/RN64ops0. RNE32 es modelo HOST, no Bpyfloat32 ni GPUALU.
No generar nuevas escenas ni volver a barrer PRECISION005/006. Los casos hi-lo no prueban que un origen Bpyfloat32 conserve1+2^-60.
No inferencia/hit/traversal/longitud/fase/material/amplitud/potencia/coherencia; field-amplitude-powerNone y promociónSTOP.
Todos fixturesconf1-v0-v4-0119-0315-nearestV2/frozenrunners-shaders-contratos/bounds-caps-umbrales/archivosClaude intactos.
Sharedboards/checkpointLOCAL SINstage; versionar soloown4revisados. Failancestrales preservados y sin umbral relajado.
JEVseguridadNOretry y CIM_RAM_ACCESS_DENIED/UNKNOWN histórico sinretry/elevación/bypass; ventana históricaCLOSED/deadline intacto.
FuturoGPU requiere exclusivaClaude/gpuq/procesos/telemetríaRAMVRAMtempválida/guardfailclosed/deadlinejobnuevo/presupuesto conservador y límites usuario.
Sin SDK/DrJit/Kaggle/push/merge/killajeno/canceltickets. U/GEMM no sustituye inferencia de escena;16Mvs1M/salidas distintas/extrapolaciónNOequivalencia/winner/redRT.
Skills cognición/desarrollo/pruebas guiaron contrato/palabras/coste lógico/caché/verificador independiente; sin agentes.
Claude: ACKID+SHA y solo artifactsYAexistentes de backend/guard/fence/material/completitud/igualtrabajo/costes con ID/path/SHA/bytes.
Siguiente obligación para dispositivo: ABI/decodificación y errores reales ligados a ORIGINAL/SOURCE/caps; paqueteHOST no los avala.
