# PRECISION-COPLANAR-CLEARANCE-CPU-001

Estado: candidato opt-in CPU, garantía condicional de separación. Fase, visibilidad completa, dispositivo y óptica: STOP.
Base: 3e3087a55a20ddc4213b71c562e7778e12d25541. JEV: fallback LOCAL por bloqueo de seguridad; sin reintentos ni aval remoto.

## Contrato

Modelo `precision-coplanar-clearance-CPU-v1`; API `audit(model, request, declared_uncertainty)`.
Evidencia geométrica solo del recibo FINITESEGMENT001 SHA8ea19cd01ea348a381f739f7cd480ebe264718d7f680408f8aa6ff23367147b9.
Verifica168pins ancestrales, identidad/cierre/longitud de capturas y PASS independiente previo; no importa ni ejecuta productores anteriores.
Selección cerrada de80 registros:72 separaciones sintéticas explícitas y8 contactos de escenas declaradas S0/S1.
Selector5campos exactos: case, parent_receipt_sha256, parent_record_sha256, geometry_sha256, intent.
La geometría incluye contexto original sellado, SOURCE y extremos/vértices; no hay sustitución pública.
Contacto real del padre sigue STOP antes de buscar separadores: ni radios cero ni incertidumbre grande lo rescatan.

`declared_uncertainty` tiene exactamente schema=`DECLARED_INDEPENDENT_COORDINATE_BOXES_ONLY` y points_BU.
points_BU contiene cinco vectores de radios no negativos por coordenada, en orden origen, fin, vértice0, vértice1, vértice2.
Cada entrada es racional tipado estricto [numerador, denominador positivo], hasta128bits; bool/float/NaN/Inf no son enteros.
Nominales y radios <=1000000 BU (límite de entrada, NO nuevo presupuesto admitido de escena/fase/conf1).
Son cajas DECLARADAS por el llamador, no medidas/atestadas ni probabilidades. No se presume correlación cancelable.
No se altera ningún cap, radio, fixture, contrato ni bound anterior. No se afirma que las posiciones perturbadas satisfagan un contrato de inferencia anterior.

## Cota

Para un eje exacto a normalizado con suma|a_k|=1, cada punto p con radios r tiene proyección dentro de
[a·p-suma|a_k|r_k, a·p+suma|a_k|r_k].
Los extremos proyectados del segmento y triángulo se obtienen tomando min/max sobre TODOS sus puntos.
La convexidad incluye cualquier segmento y triángulo cuyos extremos/vértices estén en las cajas, incluso si dejan el plano nominal.
Candidatos: tres normales de aristas en el plano, una normal de segmento en el plano y tres ejes cartesianos.
Gap = max(minTri-maxSeg, minSeg-maxTri). Se cobra el soporte de ambos lados, no solo un SOURCE o vértice.
Si algún gap>0, la distancia L∞ entre ambos conjuntos es al menos ese gap BU; se devuelve el máximo de los siete.
Esto es una COTA INFERIOR, no la distancia mínima exacta ni un clasificador completo para toda incertidumbre.
Si no hay separador estrictamente positivo, STOP `uncertainty_exhausts_separator`: no implica intersección física demostrada.
Igualdad gap=0 conserva STOP; contacto t0/t1 cerrado, epsilon0 y sin exención de objeto/primitiva.
`CPU_CONDITIONAL_DECLARED_BOX_SEPARATION_ONLY` tiene una fila y verified_queries1; promotion y todos los flags físicos/GPU/fase siguen STOP/false.
Certificado: geometría/contexto, cinco cajas, siete ejes L1, centros, soportes, rangos de ambos conjuntos, gaps, mejor eje y cota.

## Pruebas y verificación

Suite5grupos PASS rc0/0.5587362000369467s/raw1568947bytes/SHA5371e0ae910a45372771c04d32f97098184cd8398922ef42a1ac6930fd0d1a22.
246 registros principales:96 separación condicional y150 STOP.
72 separaciones nominales × radios0 y1000000:72 condicionales y72 STOP.
24 huecos sintéticos2^-60 × radio por punto/coordenada {hueco/4,hueco/2,hueco}:24 condicionales con margen hueco/2 y48 STOP, incluidos24 igualdades.
8 contactos sellados × radios0 y1000000:16 STOP conservados.
5 controles agrandan individualmente cada extremo/vértice:todos STOP; no se puede omitir un punto.
9 selectores/modelo inválidos STOP;12malformados fuera censo, API pública condicional y evidencia simulada ausente STOP.
260 invocaciones totales. Captura íntegra en recibo hermano; no se reejecutó recorte nominal ni scripts/escritores ajenos.
Verificador independiente no importa núcleo: enumera8esquinas por caja/punto, proyecta y reconstruye62.000aprox (61880 exactas) proyecciones.
Comprueba centros/soportes/rangos/gaps, censos/mutaciones/igualdad/flags, SHA/contexto SOURCE, API y pins.
PRE independiente PASS rc0/1.1984747999813408s/172pins/61880proyecciones. POST y own4/index vacío/boards sin stage requeridos para cerrar.

## Límites

CPU1hilo/afinidad1/hijo60s; GPU0/Blender0/compiler0/producer0/RN64ops0.
Costes completos UNMEASURED_NOT_ZERO; tiempos de QA no son coste de inferencia ni benchmark equivalente.
CPU sintética/captura CPU declarada NO Bpyfloat32/GPU ALU/RT/óptica física ni incertidumbre física autenticada.
NO nueva longitud/fase/field/amplitud/potencia/coherencia; U/GEMM no sustituye inferencia desde escena.
Los STOP y fallos ancestrales quedan preservados por hashes, sin cambiar umbrales para obtener PASS.
Frozen/fixturesconf1-v0-v4-0119-0315-nearestV2/bounds/caps/Claude intactos; sharedboards/checkpointLOCAL SINstage.
No SDK/DrJit/Kaggle/push/merge/killajeno/canceltickets/JEVretry/telemetría retry; ventana histórica cerrada/deadline intacto.
FuturoGPU requiere reservaClaude/gpuq/procesos/RAMVRAMtemp válidas/guardfailclosed/deadline nuevo porjob/presupuesto conservador.
16Mvs1M/salidasdistintas/cruceextrapolado NO equivalencia/winner/redRT.
Skills cognición/desarrollo/pruebas limitaron contrato/controles/verificación independiente; sin agentes.
Claude: ACK por ID+SHA y SOLO artifacts existentes backend/guard/fence/material/completitud con ID/path/SHA/bytes y contrato igual trabajo/costes completos.
