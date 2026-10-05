# PRECISION-ORIGINAL-SOURCE-DIRECTION-ENDPOINTS-HILO-CPU-001

P1 DONE CPU: nueva integración de transporte hi-lo de ambos extremos de las cajas de dirección guardadas, sin cambiar el codec. Propietario Codex, capacity_audit/EXP005. Base 6628f2e1b0cb27009ed20ab77608d80b832dee5f. JEV bloqueado por seguridad: fallback local sin aval remoto, sin reintento.

## Contrato y alcance

Padre PRECISION-ORIGINAL-SOURCE-POINT-HILO-CPU-001, recibo SHAe3d4a3e5f431b97fb83e121d4a9f06c9454e9f9849437721a7ed3e9b488fce07, 122600 bytes. Se consumen solo los datos de su captura guardada y sus 452 dependencias verificadas; no se ejecutan sus tests/productores. Son seis casos CPU originales y sus 12 filas S0/S1 con labels scene/query/input/previousprimitive retenidos. Esos labels y el hash de contenido NO autentican un buffer o estado nativo completo.

La prueba de puntos anterior comprobó singleton xyz, con lo=0; aquí la dirección guardada tiene ancho x estrictamente positivo en las 12 filas. Para direction_scaled (dos SOURCE), ancho x=3/2^51; para los otros cinco casos (diez SOURCE), ancho x=3/2^52. Los ejes y/z son singleton. Se conservan los intervalos y su parametrización de salida CPU sin escoger centro, normalizar, hacer snap o cambiar bounds. No se demuestra ni recalcula reflexión, intersección, norma, longitud, referencia o fase.

Cada extremo racional se codifica con el codec propio existente oblique_exact_scalar_hilo32_CPU_v1.py. La recuperación es la suma RACIONAL de las dos palabras binary32, no suma binary64 ni entrada reducida a un float. Layout de prueba: xyz, lower antes de upper, hi antes de lo; 12uint32 little-endian = 48 bytes por SOURCE. Es un payload CPU de prueba, NO ABI de backend/shader ni nueva representación opt-in nativa.

El presupuesto CPU de ERROR DE TRANSPORTE es cero solo porque esta recuperación reproduce exactamente ESTOS extremos. No borra la anchura de la caja heredada; no implica presupuesto nativo de dirección/geometría/punto/export cero. native_direction_budget_authenticated y native_precision_certified siguen false, native_origin_box_bound y phase_error_bound siguen null. No introducir midpoint como evidencia de incertidumbre cero.

La identidad de contenido por fila fija incluye case/SOURCE/scene/query/input/previousprimitive, caja de dirección, caja de punto, palabras del triángulo, binding CPU de punto padre, hash de registro fuente, presupuesto de transporte CPU, words y wire. SHA de JSON canónico en Python. NO firma, autenticación, selector/runtime de renderer ni autorización de carga. No modificar el contrato de identidad anterior: se añade una prueba distinta, con enlace explícito a aquel punto.

## Resultado y controles

72 packets escalares de extremos EXACT_PAIR_CPU_ONLY, residual racional cero. 24 palabras lo NOcero: este alcance prueba realmente el transporte de correcciones pequeñas, no solo hi con lo=0. 144 llamadas válidas al encoder incluyendo 72 autocomprobaciones audit_packet, 288 RN32 internos por ejecución completa. Las 12 anchuras x se recuperan exactamente. 576 bytes lógicos sin deduplicar; NO subida GPU ni tamaño de escena completa. Dos wires distintos, grupos [2,10]; seis pares S0/S1 con wire igual pero 12 identidades de fila distintas. Wires iguales NO permiten fusionar fuentes, presupuestos ni gauges.

120 controles negativos = 12 por cada uno: SOURCE swap, scene SHA, previousprimitive, colapso al lower, colapso al upper, inversión de extremos, sustitución por vector ideal singleton literal (-1,1,0), presupuesto, palabra de triángulo y caja de punto. Los controles de extremos actualizan wire Y bounds de forma coherente; se recomputa el digest de cada candidato, sin depender de un checksum viejo. Comparación contra la fila fija guardada: contenido distinto se rechaza. La inversión tiene bounds invertidos y NO es una caja admisible. El vector ideal es solo control fabricado literal, no cálculo de normalización. No afirmar que un parser de autenticación/backend ejecutó estos rechazos.

Suite final rc0 / 0.29060569999273866s QA, stdout SHA12ca9dba8df189505ee20f39891783b24b5fe899bdee3a64bfbe5f592b02d7d9, 310594 bytes. Oráculo independiente structIEEE32+Fraction, sin importar codec/test/productores, rc0 / 0.2963498000171967s QA, stdout SHAe390042e51b7d2e1f0b30532e308dfd27ac31ae69e3301b28e348e88d045b2a2, 650 bytes. Verifica 72 pares exactos, 24 lows no cero, 12 bounds, layout576 bytes, identidades/SOURCE/bindings, 120 transformaciones negativas concretas y 453 dependencias. En el oráculo estos inputs y sus residuos se comprueban exactamente representables en binary64 antes del contraste struct32; NO prueba de RNE universal para racionales arbitrarios.

453 dependencias de contexto = 452 del padre + recibo padre. 455 pins finales añaden test+Doc; recibo sin selfhash. Capturas completas comprimidas+SHA+bytes y códigos reproducibles en el recibo; enteros grandes permanecen en Python, no pasan por JSON.parse JavaScript.

## Fallos conservados y coste de esta verificación

Primera suite rc1 / 0.2708518000144977s, TypeError al mutar saved_triangle_words[0] como si fuera un entero: era lista de vértice. Única corrección: mutar [0][0]. Captura, stderr y programa inicial completos retenidos. El fallo ocurrió después del bucle de las 12 filas; según flujo del código se habían hecho las mismas 144 llamadas encode incluidas auditorías (288 RN32), antes del control de triángulo de la primera fila. La suite final nueva suma otras 144 (288 RN32): total por flujo 288 encode / 576 RN32 en dos ejecuciones, no telemetría de coste nativo. No se reejecutó el codec suite antiguo ni las queries originales.

Primer intento del oráculo: SyntaxError en else52, antes de cualquier ejecución del cuerpo. Se corrigió solo el espacio (else 52); captura y código inicial preservados. El oráculo final se ejecutó una vez con éxito. Fallos de construcción de prueba/oráculo, NO resultados numéricos del renderer ni evidencia de sabotaje. Umbrales/bounds/codec intactos.

CPU 1 hilo, afinidad1, variables OMP/OPENBLAS/MKL/NUMEXPR=1, Python-B, hijo con timeout duro60s. Reproducción desde raíz:
```python
import runpy
runpy.run_path('Blender/tests/test_original_SOURCE_direction_endpoints_hilo_CPU_v1.py', run_name='__main__')
```
Syntax compile en memoria para test y oráculo. Sin formatter/linter/typechecker configurado descubierto; pruebas stdlib enfocadas, sin instalaciones. Tiempos QA NO benchmark, rendimiento, igualtrabajo ni coste0. Costes completos UNKNOWN_NOT_ZERO.

## Límites y siguiente evidencia

native_original_transport_joins permanece0: la integración matemática NO enlaza un payload de escena/backend real. Preservados los12 ledgers STOP_UNRESOLVED_ALL_PRIMITIVES, FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION, 72 errores escalares +16 filas previas separados, 19 registros sintéticos anteriores y demás FAIL/STOP. Ninguna exclusión de primitiva, nearest-hit, visibilidad completa, cota física/óptica o fase admitida.

Claude: ACK por este ID+SHA de recibo, y SOLO artifacts ya existentes ID/path/SHA/bytes SAMEINPUT6queries/12SOURCE/buffers completos/scene-query-input/previousprimitive/ABI point-dirección-hi-lo-residual/consumo IEEE, presupuestos autenticados point-geometry-direction-ALLcoverage, backend/guard, material-gauge-scale-lambda-reference, cotas longitud/fase y contrato igualtrabajo/salidas/costes completos; o lista precisa de faltantes. No fabricar permisos a partir de budgetCPU0 ni repetir cargas de relleno.

Contratos/runners/shaders/fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/umbrales congelados intactos. CPU de fixtures NO Bpyfloat32/GPU ALU digital/RT/óptica física. U/GEMM no sustituye inferencia desde escena; RT16Mvs1M/salidas distintas/cruce extrapolado no es comparación equivalente ni redRT.

Sin GPU/Bpy/RT/compiler/queryreplay/foreignwriter/SDK/DrJit/Kaggle/push/merge. Ventana/deadline nocturnos históricos cerrados intactos. GPU futura exige nuevo job exclusivo acordado con Claude, livegpuq-procesos-RAMVRAMtemp/guard fail-closed/deadline nuevo: RAM libre>=4GiB tras presupuesto>=1024bytes/celda+márgenes/temporales, VRAMtotal<=18GiB/temp<=80C/piloto<=120s/otros hijos<=600s, noMLP32768 ni cerca del límite tras0x9F. Solo own3 revisados a commit local; shared4 top+EOF locales SINstage. Skills de pruebas y cognición guiaron cobertura complementaria de extremos guardados y retención de fallos, sin core adicional ni barridos antiguos.
