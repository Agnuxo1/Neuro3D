# AXIAL-ARGUMENT-PI-RN64-001: residual ABI a argumento, CPU sintética

Modelo opt-in: residual signed256 little-endian uint32[8], escala2^-149
ciclos, abs<=1/8; proveniente del selector retenido porSHA/IDs/gauge/bindings.
Conversión RN64 explícita por bit_length/extracción mantisa/guard-sticky y
tie-even, sin usar Fraction/float para decidir bits de conversión. RN64mul
modelada (racional exacta para emular cada operación, NOhardware/driver).

Constante TWO_PI uint64=0x401921fb54442d18. No pi racional generado como
argumento final ni libm oculto. Error constante se certifica contra intervalo
PIlower/PIupper frozen; NOconstante exacta gratis. Producto RN64 sin FMA.
Eangle=abs(P64)*Edecode + abs(residual_original)*Econstant + abs(delta_mul).
Tres cargos separados, no doble conteo. Cota fase = upstream_retenido+Eangle;
misma phase_budget_rad oFAIL; NOensanchar bounds/fixtures/conf1.

Castzero o tie-even se cobra exactamente; residual mínimo no nulo 2^-149
es normal RN64 (noFTZ). abs>1/8, malformedABI/bool ysourceID/gauge/binding
incoherentes rechazan. Quarter/turn se retienen sin ejecutarse otra vez.
Angle <=1rad permitido SOLOdominio actual; NOescala de dominios silenciosa.

No se calcula campo/trig/reflexión/sourceproducto/detector ni se promueve
fullpipeline/autenticación/nativo/GPU/ALU/Bpyfloat32/RT/óptica física.
Preservar flags8completos/10FAIL antiguos. UnidadRN32noquarterFAIL no se borra.
Coste conversión bitABI+1RN64mul/path modelados; decode/P64load HOST/IO/RAM/
energía/guard/upstream/costes completos NOincluidos como gratis ni velocidad.
ABIgeométrico/selector/producto nativos pendientes. AntesGPU contratos/tests/
commit, guard fail-closed/reserva exclusiva/deadlineNUEVO verificable;
ventana histórica cerrada intacta. JEV fallback local sin reintento/aval.
Skills contrato/reuso; CPU1hilo/hijo<=60s; boards/checkpoint locales SINstage.

## Resultado verificado

Ocho tests PASS rc0/0,4309079s, un hilo/hijo60s. 18casos/21paths calculados/
17gates parciales; mode upstream no calcula. Validador independiente:
31conversions bits +31RN64mul (21retenidos+10primitivas), vecinos/tie-even
verificados, 21oráculos desde longitud ORIGINAL. 73huellas congeladas;
96contrastes adicionales de conversión en tests, sin repetir suites anteriores.

Noquarter: cargo nuevo argumento 7,165209388379241e-17rad; cota compuesta
1,7835220487886298e-14rad, oráculo original+intervalopi
8,299232301336925e-15rad <= cota <= MISMO presupuesto1e-12rad. Esto
certifica SOLOargumento CPU sintético; previo unitRN32FAIL/casefullFAIL
intactos. No equivale a nuevo campo ni motor GPU/RT correcto.

Cast con tie-even arriba/abajo/carry y signo negativo cobra pérdida; caso
residual0 tiene error0 SOLOcaso. Mínimo±2^-149 no desaparece/NOFTZ.
Constante 2pi tiene cargo distinto de cero; rounding del producto distinto
se suma. Overflowdominio/ABI/IDs/gauge/bindings/budget0 rechazos probados
en copias; no cambios de límites/casos congelados para obtenerPASS.

TODOSfullpipelinefalse; 8flags completos/10FAIL originales conservados.
Espejo absoluto/trig/propagación fuente/reducción/detector no evaluados,
selector/ABIgeométrico/producto argumento nativos yguard no certificados.
Siguiente integrar argumento NUEVO con unit opt-in/cotas antes campos;
no pasar este payload como inferencia desde escena silenciosamente.

Claude: acuseID/SHA y SOLO artifacts0337 geometry/
limbs/bindings/backendguard YAexistentes, contrato igualtrabajo/costes
completos; no nuevasGPU/suite/barrido/guardreview.
