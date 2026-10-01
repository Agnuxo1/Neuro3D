# AXIAL-REDUCTION-DETECTOR-RN64-001: contrato CPU sintético opt-in

Modelo retained-path-coherent-detector-RN64-CPU-v1 sobre terminales NUEVOS
retenidos del informe6be20bac...1d9a8 por sourceID/gauge/puerto/coherencia.
Verificar65pins y SHAreport. NOreplay geometría/fuente/unidad/producto/suites.
Cambio explícito a RN64 CPU emulado, NOALU/GPU/Bpy/RT/óptica física/nativo.

Orden por grupo idéntico a fuentes retenidas. Dos addRN64/fuente desdecero,
sin FMA/reasociación. Efield=sumEpaths+sumabs(adddeltas); no crédito por
cancelación. Cota inferior L1=max(norm1(Y)-Efield,0), relativobound=E/lower
SOLAMENTE si lower>0; lower0 RECHAZA, sin piso/epsilon/0div0.

Detector3RN64 porgrupo: squareReal,squareImag,add. CargoEdet sumaabs deltas.
Cota potencia vs campo original:2*norm1(Y)*Efield+Efield²+Edet.
Grupos distintos suman POTENCIAS no campos; una addRN64/grupo/puerto y
sumabs(delta) se cobra aparte. Referencia inferior potencia=max(P-Epower,0);
relativo solo lowerpositivo, presupuestos de campo y potencia ABS+REL.

Budgets ABS originales trans.field_absolute_L1_budget/intensity_absolute_budget.
REL desde registros del reducerquarter porgrupo/puerto; conservar relative0=0.
Noquarter/nearquarter sinreducer: cuatrodefaults F del run(s) quarterfrozen
extraídos estáticamente AST (no ejecutar test). Sus llamadas no alteran límites.
Provenance explícita/SHA; no relajarcap ni asumirPASSflags anteriores como gate.

Terminales por nodo RN64, detector y reducción se implementan SOLOCPU.
Fullpipeline/autenticación/nativePromotion siemprefalse; FAILs anteriores
preservados incluso si nuevo gate parcial pasa. Faltan selector/geometry ABI/
productoargumento nativos, guardfailclosed/reserva/deadlineNUEVO antesGPU.
Coste2RN64/source+3detector/grupo+1add/grupo excluye geometría/unidad/
sourceproducto/IO/RAM/energía/guard y no equivale a coste completo/velocidad.
JEV bloqueado/fallback local sin reintento/aval; skills contrato/reuso.
## Evidencia retenida y límites

Ocho tests PASS en 0,3625343s, un hilo/hijo<=60s: 18 casos, 12 calculados,
10 gates parciales aceptados. 84 operaciones RN64 de escena y 4 primitivas.
Validador independiente: 88 nodos nearest/even, 13 oráculos de campo por
grupo y 12 de potencia por puerto desde fuente y longitud ORIGINALES;
65 huellas anteriores verificadas. Sin reejecutar productores congelados.

Oscuro: Y=-8388607/2^53, error campo=2^-53. Relativo REAL de campo
1,1920928955078125e-7; cota 1,1920931797249746e-7. Relativo REAL de
potencia 2,3841856489070778e-7; cota 2,3841867857758616e-7. Ambos
gates parciales pasan el MISMO presupuesto relativo 1e-6, solo este modelo
CPU sintético. Separar coherencia y sumar potencias entre grupos es obligatorio.

Exact_dark_zero_FAIL y relative0_FAIL siguen rechazados; seis casos paran
antes de reducir por gate upstream. Los 8 flags completos/10 FAIL originales
se conservan, incluidos noquarter/nearquarter aunque su NUEVO gate parcial
pase. TODAS las promociones full-field/nativas/autenticación son false.
Primitiva normal 2^-600: su potencia 2^-1200 redondea a cero; la pérdida
100% se cobra y rechaza referencia inferior cero. No es un permiso FTZ.
La primitiva cuyo cuadrado selecciona subnormal también rechaza.

Costes de esta etapa: 2 RN64/fuente + 4 RN64/grupo, solo grafo evaluado;
no comparativa de rendimiento ni costes completos. No GPU/ALU/Bpy/RT/física.
Faltan transporte/selector/ABI geométrico nativos y protocolo completo;
antes de cualquier GPU: contrato/tests/commit, guard fail-closed, reserva
exclusiva y deadline nuevo verificable, sin cambiar el histórico cerrado.

Petición Claude AXIAL-REDUCTION-DETECTOR-RN64-001: acuse por ID/SHA y
SOLO artifacts YA existentes de 0337 (geometry/limbs/bindings), backend/guard
y contrato igual-trabajo/costes completos. Sin nuevas cargas ni barridos
para rellenar. JEV bloqueado: fallback local explícito sin aval remoto.
Frozen/fixtures/umbrales intactos; sharedboards y checkpoint locales SINstage.
