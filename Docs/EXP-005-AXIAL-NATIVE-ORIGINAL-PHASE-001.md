# EXP-005 / AXIAL-NATIVE-ORIGINAL-PHASE-001

Estado: 8tests CPU/HOST y oráculo stdlib PASS; unidad restringida verificada. Base deb9220e16d484c8432912d3a2399c2b3c4e4ab2.
Acuse REFERENCE-001/SHA7ecf0339e4b7dc0a3383ef8c48d32cc45dab24c9435f8a0e8bfac071c9ae3890.

## Contrato

Overlay INPUT-only, ligado a SHA canónico parent INGRESS, snapshot ORIGINAL,
word ABI, escena y orden de fuentes. HOST serializa ORIGINAL64 little-endian
M.X,D.X,R.X,lambda y ordered source.X. Cap: flag uint32 +numerador16 y
denominador16 uint32. Ausente flag0/reservados cero NO cap numérico0.
Lector verifica bits/racional/recibos/roles. SHA NO autenticación nativa.
Decode ORIGINAL64 -> signed512 BU*2^149 exacto; fuera de grid/subnormal/no
finito/overflow STOP; nunca redondeo ni ampliación de radios.
Se reevalúan dependencias PROPIAS YZ/X/eventos/referencia; trabajo redundante
explícito, NO replay de respuestas/suites viejas. Perfil exact-YZ +/-X, dos
propietarios y dos eventos, NO geometría3D general. ORIGINAL Lref=sigma(2M-S-R),
NO Lgeom ni R=D silencioso; MISMO D cancelado/cota correlacionada directa.
Longitud efectiva firmada/cero; lambda estrictamente positiva, caps separados.
Cada esquina E,lambdaE con original O,lambdaO y cap p/q:
8*abs(E*lambdaO-O*lambdaE)*q <= p*lambdaE*lambdaO.
Factor8 conservador sobre 2*pi, NO división/trig/unidadfase/campo.
Todos intermedios checked signed512; overflow STOP incluso cociente simplificable.
PASS de cota NO PASS del campo/backend/fullpipeline.

## Costes y límites

13 overlays:66 ORIGINAL64/528bytes +14caps/1848bytes =2376bytes INPUT extra.
NO VRAM/fullcost. Encoder170HOSTpacks/gridchecks (104planos+66valores),
288uint32 cap packs+14flags. Reader66HOSTpacks/bits+66decodes. JSON/base64/hash/
copias/controles/dependencias+limbs extra; no coste completo ni hardware.
0 NUEVOS RN32encoders/RN64subtractions. CPU1hilo/hijo60s; SIN GPU/Blender/
SDK/DrJit/RT/JEV. Fallback LOCAL sin aval JEV. Fixtures/runners/shaders/caps/
radios/FAILs congelados intactos. RT16Mvs1M/distintosoutputs NOequivalente.
No speed/energía/eficiencia/motor ganador ni ejecución/autenticación nativa.

## Coordinación

Claude ACKID/SHA, sólo artifacts efectivos YA existentes matchingABI/ref/scene,
igualtrabajo/output/costes completos. Guard0337histórico CERRADO no nuevojob.
Sin cargas de relleno. AntesGPU contrato/tests/commit/guard/reserva/deadline
NUEVOjob verificable. Unidadfase/campos/portkernel/inferencia completa pendientes.
Sharedboards/checkpoint locales SINstage.

## Evidencia de suite

13cases/14fuentes:7PASS de cota/2FAILfase preservados/5STOPupstream intactos;
36esquinas,150dominios decoder,11controles corner,13overlays malformados
rehash rechazados,7caps invalidas rechazadas. Suite rc0/0,5112705s.
Raw1252150bytes SHA46aeba1189d04c97b718c3de4116c17c1a56dd6f3c144b445d16aeef42b63937.
Inicial 1ERROR de TEST KeyError gauge en fila upstreamSTOP (sin ese campo).
Conservado raw1252151 SHA7cfef97a11ea0f0d39e573ce48e9bedd432d789d470de54b8725bb607c288bed,
captura repetida sin cambios rc1/0,5792595s; primera consola rc1/2,043595s.
Corrección sólo TEST: gauges contrastados en filas realmente evaluadas.
MISMAproducción/inputs/arithmetic/caps/radios/FAILs; no relajación numérica.

Oráculo independiente stdlib rc0/0,4480836s:183huellas=180heredadas+3propias,
66originales/36corners,441decodes64exactos/79rechazos esperados.
4714limbcalls:790add/1208sub/676mul/714compare/1326decode32;1mul+1sub
overflow esperados. NOhardwarecost. 13HOSTmalformados rehash rechazados.
Revisión de alias TEST usa copia de bytes previa (no self-comparison);
suite reforzada8PASS0,5226766s EXACTAMENTE MISMO rawSHA/cases/aritmética.
Reporte JSON inicialmente ensamblado en orden incorrecto por contexto de
patch repetido: JSONDecodeError Extra data, SHA69375485bd9e353b84b2dfc1186413bf33828904645fed33be0da7302d4a566c.
Reparación mecánica sólo almacenamiento mediante apply_patch; ambas capturas
raw idénticas verificado, código/caps/radios/FAILs no cambian. Intento de
patch-move excedió longitud Windows; primer splice falló por separador
newline (sin escribir); reparación validó183pins/180heredadas antesoráculo.
