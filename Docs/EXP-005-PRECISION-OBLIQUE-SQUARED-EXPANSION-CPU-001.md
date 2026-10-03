# PRECISION-OBLIQUE-SQUARED-EXPANSION-CPU-001

Contrato opt-in CPU64, política SEALED_PRODUCTS_HOST_BOX_SELECTION_NATIVE_GROW_FIXED4.
Base fae668febf400686ea729c05aed093dba17415ac; padre coordinacion/respuestas/PRECISION-OBLIQUE-SQUARED-PAIR-BUDGET-HOST-001-CODEX.json, SHA256 743749e2d0b9742c740a54d3cfad25933750a91cb3a73eab4310a8e41d608d1e, 78633 bytes.
Los runners/shaders/contratos anteriores permanecen congelados. JEV bloqueado: fallback LOCAL sin aval remoto.

## Dominio y procedencia

Sólo dos registros elegibles desde PRODUCT-EFT y las MISMAS cajas originales inciertas de SOURCE0/DETECTOR0.
Los 14 STOP previos no se rescatan; los 15 radios y el paquete de 240 bytes se comprueban por la cadena sellada.
Selección mínima/máxima de extremos por eje es preprocesado HOST explícito, NO inferencia desde escena en motor nativo.
Si el intervalo de diferencia cruza cero, el mínimo cuadrado es cero por el teorema de caja continua.
Cada eje entrega ocho palabras: cuatro productos sellados hh/hl/lh/ll, cada uno con hi/lo; cero literal sustituye sólo el eje mínimo que cruza cero.
Cada suma consume 24 palabras, en orden eje/termino/hi-lo. No se repiten productos, transportes ni raíces.
No se introduce S ni un residual calculado HOST como salida del grafo.

## Grafo fijo

Grow-expansion, hasta CUATRO componentes, con TwoSum de SEIS operaciones binary64 RN:
s=a+b; bb=s-a; ab=s-bb; db=b-bb; da=a-ab; err=da+db.
Registrar operandos, salida, orden y coste de cada nodo. q comienza en la palabra de entrada.
Iterar componentes del estado: q,err=TwoSum(q,component); conservar err si no es cero exacto; al final conservar q si no es cero o si no hay componentes.
Cero es la única eliminación: sin EPS, FMA, nextafter, división ni sqrt.
Dominio palabras canónicas finitas normales/cero con magnitud hasta 2^66 para sumas cuadradas y nodos;
NO se cambian los bounds geométricos originales de 2^32.
Subnormal, overflow, resultado no cero exacto redondeado a cero o salida fuera del dominio -> STOP con ledger parcial.
Si grow requiere cinco componentes -> STOP_CAPACITY, salida aceptada null y cinco palabras parciales conservadas;
NO truncar ni subir la capacidad después de fallo.
Representación exacta auditada; NO afirmar normalización/canonicidad/nonoverlap de una pareja o exactitud en todo el dominio.
Las pruebas certifican las cuatro sumas capturadas, no un teorema universal de aceptabilidad.

## Verificación independiente

Oráculo bit/racional sobre captura, sin ejecutar otra vez grafos/productores: RN nearest-even por vecinos IEEE enteros,
seis conexiones por TwoSum e identidad s+err=a+b; filtro exacto cero y cada prefijo; suma exacta de palabras nativas.
Reconstrucción independiente de las cajas originales con TODOS los radios y selección de extremos.
Revalidar SHA/pins en cada prueba; contraste padre bit/racional una vez por verificación.
Conservar rechazo anterior STOP_CANONICAL_PAIR_EXACT_SUM y sus residuales firmados: política canónica de DOS limbs distinta e intacta.
Este backend nuevo con hasta cuatro componentes no convierte el contrato antiguo en PASS.
Controles: tres componentes exactos [1,2^-60,2^-120]; cinco [1,2^-60,2^-120,2^-180,2^-240] STOP con 60 nodos;
cancelación exacta; seis entradas inválidas antes de aritmética; un STOP de dominio después de un nodo con parcial previo.
Ocho selectores rechazados y ocho mutaciones rechazadas.
Pruebas API independientes públicas y simulación de padre ausente claramente etiquetada en recibo.

## Recursos, costes y límites

CPU propia, stdlib, un hilo/afinidad máscara1, cada hijo límite duro60s. Sin GPU/Blender/SDK/DrJit/red/JEV/push/merge.
Conteos de grafos nuevos incluyen controles y nodo fallido; fixture-preparation, decodificación, verificación racional,
selección HOST/provenance/IO y costes completos UNKNOWN_NOT_ZERO, no cero.
Los tiempos son de pruebas CPU locales con auditores, NO benchmark comparable ni ahorro de motor.
Salida sólo extremos de distancia CUADRADA scene_length_squared.
NO raíz/longitud/fase/longitud de onda/referencia física/GPU/RT/óptica, ni precisión completa de backend ni interior de caja.
U/GEMM compilada no sustituye inferencia de escena.
Solicitar Claude sólo artifacts existentes backend+guard e igual-trabajo/salidas/costes completos por ID/path/SHA/bytes.
Cuatro archivos propios revisados para commit LOCAL; sharedboards/checkpoint SINstage.

## Evidencia

Suite y oráculo independientes, API y metadatos quedan sellados en
coordinacion/respuestas/PRECISION-OBLIQUE-SQUARED-EXPANSION-CPU-001-CODEX.json. Las palabras y rationales completos permanecen en captura Python comprimida,
sin reserialización mediante Numbers de JavaScript. Aceptación y costes específicos se documentan desde esa captura.
Resultados capturados: dos escenas/cuatro sumas exactas; outside necesita [1,1] componentes y 276 RN; fino necesita [3,3] y 732 RN. Total 1008 RN de escenas +90 de controles +1 nodo STOP=1099 RN de la suite. Capacidad fija4 intacta, caso5 STOP con parcial. Máximo observado3 NO umbral reducido ni capacidad ampliada. Suite4.61182159999953s; captura234203bytes SHA256 b747cafe1d848bdd3ea568d6016267b605807d251c7124a2ae9784a26370df8c. Oráculo bit/racional1.6123935000032361s PASS.281pins heredados antes own3. API pública thin adicional, si PASS, cuenta separadamente sus732RN; no productos/raíces antiguos ejecutados.
