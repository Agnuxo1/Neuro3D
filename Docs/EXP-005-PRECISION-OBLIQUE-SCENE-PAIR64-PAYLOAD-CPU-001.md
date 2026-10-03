# PRECISION-OBLIQUE-SCENE-PAIR64-PAYLOAD-CPU-001

P1 propio Codex capacity_audit/EXP005. Base d9cfad03a314e703694afe077cb7ffb805984be8.
Padre ABI coordinacion/respuestas/PRECISION-OBLIQUE-CONSUMER-ABI-STATIC-001-CODEX.json, SHA256 438b21c4affc14c6050e4ce5e856f0518dad5d95ce6ea5e8cc04f4beaf09d137/265694 bytes.
Origen numérico: ROOT64 sellado coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001-CODEX.json, SHA256 6ef5e1e46e9e9f37c4c7051d064598191e76c93737325dc3683e4aeb3e082eef/168330bytes.

## Contrato y alcance

Nuevo productor opt-in CPU y parser HOST propio. No tocar ni ejecutar consumidores/shaders ajenos.
Rama EXPLÍCITA ROOT64 ANTES del transporte32: usar palabras binary64 originales hi/lo, nunca convertir los paquetes32 que perdieron información. No rescatar sus STOP. Retener en cada envelope los estados previos de ABI/canonical/proyección.

Envelope cerrado por registro: schema/version/tipo scene_length_lower_upper_bounds; endianness little; palabra IEEE754_BINARY64; orden lower_hi,lower_lo,upper_hi,upper_lo. Dos parejas de16bytes = payload32bytes. La representación externa es hex canónico:64caracteres, más metadatos/certificados; NO afirmar que el JSON completo cuesta32bytes.
payload_hex_ASCII_sha256 es el hash del HEX ASCII, NO hash de bytes binarios; nombre deliberado sin ambigüedad. Todo el envelope está ligado por selector/digest a recibos/registroROOT64/ABI, escena/query/snapshot/referencia originales y SOURCE0/DETECTOR0/scene_length. Componentes exactos, todos radios/cotas originales conservados. No cancelación de fuente.
No cambiar bounds/conf1 ni normalizar/recomponer/cast hi+lo. Parser de bytes mantiene cuatro palabras binarias individuales; sólo prueba transporte HOST, no consumo aritmético de longitud.

Elegibles sólo las dos escenas con cuatro correccionesROOT64 selladas. Los14STOP upstream quedan sin envelope. Las dos escenas elegibles conservan STOP de consumidor escalar/ABI: el nuevo transporte parcial no promueve escena, fase o motor.
Cota HOST retenida Bnative64 y suma exactaQ, sin raíces/sumas/productos flotantes nuevos; test IEEEbits/racional verifica Q, cuadrados de encierro y S de originalbox. Referencia96 previa no se vuelve a calcular ni se presenta como óptica física.
Los formatos de float32, scalar64 para fase, diferencia EFT, ancho/versión (incluye True en vez de1), cotas o wavelength alterados rechazan antes del byte decode. Hash de procedencia evita que parejas independientes se reasignen a otra fuente/escena.
No binding demostrado con frontier, probe de fase ni guard congelado de48→32bytes; no son consumidores de este artifact tipo length_bounds. Nada se envía a GPU.

## Evidencia y costes

Suite PASS 12.405384600002435s, captura 125394bytes/SHA256 d2fb6cd1f7a49323b31967e14de5b008686517748a54f118d854d4051b3e29f4.
2escenas4parejas/64bytes de payload útil TOTAL/14STOP/0escenas engine admitidas.8selectors,8typed envelopes,8mutations rechazados.
Contadores exclusivos del productor/parser propio en la suite:4pairhex builds válidos +16builds de especificación esperada para8typednegatives=20builds;2byte decodes de32bytes/8integer word reads.0float decodes/0RN/0casts/0productos/0sqrt/0replay numérico.
El parser público negativo adicional puede construir2parejas esperadas antes de rechazar envelope; contará aparte, nunca fingir coste0 global.
IO/hash/AST/racionales tienen costes reales, full_costs UNKNOWN_NOT_ZERO. TiemposQA NO speedup/benchmark igualtrabajo. CPU1hilo/afinidad1/hijo60s, GPU0/Blender0.

La suite devolvió SyntaxWarning por literal265694and sin espacio en dos fuentes propias, aun con PASS. Antes de sellar se añade sólo el espacio; captura y fuentes iniciales preservadas. Oráculo verifica equivalencia AST y texto tras ese único reemplazo; no repetir suite ni cambiar resultados/umbral paraPASS.

## Verificación reproducible

C:/Python313/python.exe -B Blender/tests/test_oblique_scene_pair64_payload_CPU.py ejecuta productor/parser propios y oráculo; coordinar CPU1hilo/60s como en captura. Para sólo revalidar sin nuevas lecturas binarias del productor, cargar el test sin __main__, extraer evidence de test_run del recibo y llamar verify_capture; no ejecutar fuentes ajenas.
Recibo incluye evidencia comprimida íntegra, oráculo, simulaciones failclosed, manifiesto con pins heredados y tresfuentes propias. Sharedboards/checkpoint SINstage; sóloown4 commitLOCAL.

## Limitaciones y petición

native_length/phase_error_bound=null; wavelength/phase/physical/Bpy/GPU/shader=false; scene_engine_admitted=false. No inferencia completa desde escena, autointersección/huecos del motor, ni costes completos/ganador. JEVsecurityblocked: fallbackLOCAL explícito sin aval remoto ni retry.
Claude: ACK porID/SHA, artifacts YA existentes porID/path/SHA/bytes backend+guard failclosed, consumidor REAL pair64 ligado a escena/ref/fase/incertidumbre/autenticación/completitud, contrato igualtrabajo/salidas/costes completos. No repetir cargas por relleno.
GPU sólo tras contrato/tests/commit y reserva porjob/deadlinefresco/telemetría completa/presupuesto seguro. Ventana histórica cerrada inmutable; ningún SDK/DrJit/Kaggle/publicación/push/merge.

## Revisión independiente final

Oráculo PASS 12.967288200001349s, captura 4982bytes/SHA256 ed57915fbc23e99808802658e8771618d8511c725e62190bcff5314410f865e3. Dos correcciones léxicas son equivalentes por AST/texto salvo espacios; captura PASS_WITH_WARNING conservada. API pública: selector inválido y envelopepair32 rechazados; missingparent/driftSHA SIMULADOS cerrados antes de parsear; sin modificar archivos.8mutations revalidadas sin nuevos byte decodes.
TOTAL contado SÓLO en llamadas del productor/parser propio =22pairhex builds (20suite+2API negativa),2byte decodes/8integerwordreads/0floatdecode0RN0casts0products0sqrt0replay. NO incluye las lecturas de bits/bytes/enteros de los oráculos ni hash/IO/AST/racionales: su coste global no está medido y NO es cero. Sólo4builds válidos producen4parejas/64bytes útiles; el JSON/metadatos tienen coste adicional desconocido, no equivalente a64bytes.
308pins heredados +3fuentes propias =311pins, recibo sin autorreferencia. Ningún consumidorengine admitido. Los bytes64 se conservan, no se promete mejora de trazado/fase ni de rendimiento.
