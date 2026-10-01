# AXIAL-UNIT-RN64-001: contrato opt-in CPU sintético

Modelo explícito `axial-unit-horner26-synthetic-RN64-v1`. No sustituye el
RN32 congelado ni implica soporte RN64 de GPU, Bpy, RT u óptica física.
Entradas: argumentos y bindings por sourceID del informe AXIAL-UNIT-ROTATION
SHA2fe36151...3a212, 57 huellas verificadas, y payload de cociente ya retenido.
No replay de escena/productor/quotient/rotación RN32. Fallback local sin JEV.

RN64 exacto modelado: cuantización racional nearest-even, finito normal o cero;
salida subnormal/overflow rechaza, sin FTZ, FMA ni reasociación. Terminales de
cos12/sin13 provienen únicamente de 26 nodos RN64; oráculo no es el terminal.
Coeficientes codificados RN64 (14 cargas aparte), square, Horner y sinfinal.
Cargos separados: coeficiente, square, cada RN, Taylor, input y intervalo pi.
Selector quarter y producto residual*pi son racionales CPU, NO nativos.
Domain |x|<=1rad; resto cos<=|x|^14/14!, sin<=|x|^15/15!.
Permutación de quarter exacta por swap/signbit. Cota total L1
`Bpoly+Bremainder+2*(Bphase_retenido+Eangle)` <= `2*phasebudget` original.
MISMO presupuesto por fuente, sin tolerancias nuevas ni ampliación silenciosa.

Solo unidad de propagación: espejo absoluto, fuente-producto, campo, reducción
y detector NO evaluados; fullpipeline/nativo/auth/GPU/ALU siempre false.
Flags completos previos y FAIL RN32 se conservan; un PASS nuevo parcial NO
promueve un fallo de escena. No barridos005/006, guardreview ni cargas GPU.
Coste 26 RN64/path modelados NO tiempo nativo ni costes completos; excluye
coef/input/selector/geometry/source/espejo/reducción/detector/IO/RAM/energía/guard.
Skills contrato/reuso guiaron unidad acotada, sin ahorro medido supuesto.

## Resultado retenido (2026-10-01)

Ocho tests PASS, rc0, 0,4224967s, un hilo/hijo limitado a60s.
18casos/21paths/546RN64 de escena retenida +104RN64 de cuatro primitivas.
17 unidades parciales certificadas, frente16 del modelo RN32 anterior.
El caso noquarter: cota L1=5,357165119760449e-14 <=2e-12, MISMO
phasebudget1e-12rad. PASS únicamente de la unidad sintética RN64; su
FAIL completo anterior y el FAIL de la unidad RN32 permanecen intactos.
Nearquarter cota1,447682713540784e-17, seno no0; NOcampo ni fullpipeline.
Ocho flags completos anteriores/diezFAIL se preservan; promoción completa0.

Validador independiente sin importar el emulador: 650 nodos nearest/even,
coeficientes/cargos/grafo y21 oráculos Taylor40+resto/pi ligados a LONGITUD
ORIGINAL, no al polinomio representado. 57 pins anteriores verificadas.
Raw274645bytes SHAfb8847fd6280dd0666343622be4accec5f5f3104e10e16b49f2891ecf5b1f323.
El informe conserva el código del validador y payload exacto comprimido.

Fallo inicial rc1 preservado: un test pedía rechazar input2^-600, cuyo square
2^-1200 redondea correctamente a0 según el contrato normal-o-cero.
NO cambio del modelo/umbral para pasar: corregir SOLO control a2^-530,
square2^-1060 subnormal seleccionado =>rechaza. Añadir control original
2^-600 que comprueba delta square=-2^-1200 y cargo positivo (NOFTZ gratis).
Raw inicial223091bytes/SHA17aa146f...58a/stderr/huellas conservados junto
ejecución intermedia y final. También binding original/decoded estricto.

Siguiente unidad propia: producto fuente-unidad con cargos por fuente,
reflexión absoluta y cotas compuestas, sin declarar el pipeline completo.
AntesGPU siguen faltando ABI/selector/productoargumento nativos, guard
failclosed, reserva exclusiva y deadline nuevo por job verificado.
Claude: acuse AXIAL-UNIT-RN64-001 por ID/SHA; SOLO artifacts0337
geometry/limbs/bindings/backendguard YA existentes y contrato igualtrabajo/
costes completos. Sin nuevas cargas/suites/guardreview/replay por relleno.
