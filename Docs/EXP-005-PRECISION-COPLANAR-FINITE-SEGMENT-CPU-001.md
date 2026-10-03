# PRECISION-COPLANAR-FINITE-SEGMENT-CPU-001

Estado: candidato CPU opt-in, diagnóstico exacto; promoción de visibilidad completa, fase, GPU y óptica: STOP.
Base Git: 2f1b0fed8d604b4c2e361a1c6a1c94945441650f. Fallback LOCAL explícito: JEV bloqueado por seguridad, sin reintentos ni aval remoto.

## Contrato y alcance

Modelo `precision-coplanar-finite-segment-CPU-v1`; API pública `audit(model, request)`, sin evidencia sustituible por el llamador.
Selecciona exclusivamente las dos escenas coplanares ya capturadas por VISIBILITY001: `oblique/coplanar` y `tiny_gap_2m60/coplanar`.
Acuse VISIBILITY001 SHA caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5; sello JOIN001 SHA df45c70348c50838ba4ebc9169f13dacf05bbb9da3cf576cb212f2b3ff3953dc.
Verifica el sello, sus pins ancestrales y la captura con SHA, longitud y cierre zlib antes de leer escenas.
Selector cerrado de nueve campos: case, source_id, segment, primitive_id, parent_receipt_sha256, scene_sha256, literal_request_sha256, paths_sha256, intent.
Tipos exactos: bool no sustituye int. SOURCE S0/S1 separado; segmento 0/1; primitiva única.
Revalida SHA de escena ORIGINAL y petición literal, SOURCE, extremos, continuidad y certificado de longitud cuadrática. No recalcula inferencia, fase, sqrt ni RN64.

Dominio geométrico cerrado: r(t)=origen+t(fin-origen), 0<=t<=1, en unidades BU.
Racionales con entero de hasta128bits y denominador positivo; coordenadas <=1000000 BU (cota heredada sin ampliación).
Triángulo y segmento no degenerados. Coplanaridad exacta de origen y dirección, no una tolerancia.
Proyecta eliminando el eje de mayor normal absoluta; normaliza orientación para admitir ambos winding.
Cada arista impone start+slope*t>=0. Intersección de las tres desigualdades con [0,1], sin epsilon/snapping.
Certificado incluye normal, proyección, orientación, tres coeficientes, límites, aristas paralelas exteriores e intervalo de contacto NONE/POINT/SPAN.
Contacto en t=0 o t=1, vértice o arista: STOP `actual_coplanar_contact`. No exención coplanar de primitiva previa ni skip del objeto entero.
Separación exacta: `CPU_DECLARED_COPLANAR_FINITE_DISJOINT_ONLY`, una fila diagnóstica; NO admisión de fase ni visibilidad completa.
No coplanar, degeneración, selección inválida o evidencia ausente: STOP sin filas verificadas.
El certificado conservado en diagnostics de contacto no equivale a rows admitidas.

## Diferencia respecto al trabajo existente

`history_lineage_cpu_v2.py` ya recorta SEMIRRECTAS t>=0 con respuesta booleana. Se leyó, pero no se ejecutó su escritor ni se cambió.
Este candidato aporta dominio FINITO [0,1], intervalo exacto y certificado completo, con controles de contacto antes/después del extremo.
No modifica el STOP coplanar conservador de `oblique_segment_visibility_CPU_v1.py`, ni el contrato de history.
Las dos escenas reales retenidas tienen contacto de todo el segmento con primitiva2: los ocho SOURCE/segmentos conservan STOP con intervalo [0,1].
NO se afirma un falso rechazo previo ni una admisión nueva de esas escenas.
Los 72 casos separados son explícitamente controles CPU sintéticos privados, no escenas nuevas autenticadas.
Fixture tiny_gap_2m60 y sus SOURCE/cotas originales permanecen intactos; los nuevos controles de hueco sintético también conservan 2^-60.

## Evidencia verificable

Suite de cinco grupos PASS: 256 registros principales, 72 separados y184 STOP.
216 controles sintéticos: cuatro planos (xy/xz/yz/oblicuo), seis permutaciones de vértices, nueve segmentos.
Incluyen antes/entrada/cruce/después, vértice terminal/de salida, arista cerrada y posiciones +/-2^-60 respecto a una frontera.
Resultado sintético:72 separados,144 contactos STOP.
Escenas selladas:8 contactos STOP;16 consultas no coplanares STOP.
Selección/modelo:16 negativos STOP (nueve campos, seis variantes, modelo ajeno).
Fuera del censo principal:8 racionales/geometrías malformados STOP, contacto API pública STOP y ausencia simulada de recibo STOP;266 invocaciones totales.
Suite rc0,2.327599099953659s; stdout501280bytes SHA a44e326ddacb20bf2e265529afe7378f38c6473869e5162d7aa77ab226191a29.
Captura íntegra y código del verificador en el recibo hermano. PRE independiente PASS rc0/2.090663000009954s/168pins; POST y comprobación own4/index vacío/boards sin stage obligatorios antes de marcar DONE.
Oráculo independiente NO importa el núcleo: coordenadas baricéntricas 3D mediante matriz Gram, distinto del recorte proyectado.
Comprueba intervalo cerrado, coeficientes/certificados, hashes ORIGINAL/literal/SOURCE, controles negativos, API, pins y flags.
Costes completos UNMEASURED_NOT_ZERO; tiempos de QA no son benchmark equivalente ni coste físico/inferencia.

## Límites y preservación

CPU1hilo/afinidad1/hijo<=60s. GPU0/Blender0/compiler0/producer0/RN64ops0.
No reejecutar PRECISION005/006 ni barridos históricos; sin generación de fixtures ancestrales.
Frozen runners/shaders/contratos, conf1/v0/v4/0119/0315/nearestV2, bounds/caps/umbrales y archivosClaude intactos.
Sharedboards/checkpoint locales SINstage; versionar solo cuatro propios revisados.
CIM_RAM_ACCESS_DENIED/UNKNOWN histórico sin retry/elevación/bypass, ventana histórica cerrada/deadline intacto.
Futuro jobGPU requiere reservaClaude/gpuq/procesos/telemetría válida/guardfailclosed/deadline nuevo y presupuesto conservador completo.
SinSDK/DrJit/Kaggle/push/merge/instalación/cancelación de tickets ni kill de procesos ajenos.
CPU sintética y escena declarada CPU NO Bpyfloat32/GPU ALU/RT/óptica física. U/GEMM no sustituye inferencia desde escena.
16Mvs1M/salidas distintas/cruce extrapolado NO comparación equivalente ni redRT; no winner ni promesa de eficiencia.
Skills cognición/desarrollo/pruebas guiaron contrato acotado, controles independientes y evidencia conservada; sin agentes.
PedirClaude ACK por ID+SHA y SOLO artifacts ya existentes backend/guard/fence/material/completitud, path/SHA/bytes, contrato igual trabajo y costes completos.
