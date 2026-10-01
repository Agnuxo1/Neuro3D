# EXP-005 — AXIAL-NATIVE-SOURCE-ENCODER-001

Encoder HOST opt-in desde bits de fuentes ORIGINALES del ingreso LE32.
Dependencia INGRESS-001 report SHA
c20ddf4f856b8932c9394d1d60c6c4e44b3170bac72e4a3922a673c778dfb855.
Frozen ingreso/contratos/shaders/runners sin modificaciones.

Por componente: decode binary64 exacto → RN32 ties-even → resta HOST exacta
del hi → RN32 del residual → 2words little-endian. Cuatro words porfuente.
RN usa cociente entero y empatepar; no seedfloat/libm/double-round/FTZ/FMA.
Es aritmética **HOST racional exacta**, NO implementación ALU GPU.
Cada componente cobra dos RN32 y una resta HOST exacta; NO resta RN64/nativa
ni residual gratuito. Costes son conteos semánticos, NO timings/energía
ni equivalencia de coste con un shader.

Sólo limbs normal-or-zero: elegir subnormal o overflow rechaza, nunca clampa.
Rounding legítimo a cero cobra error exacto; mínimo binary64 no se convierte
en entrada cero. Limb cero canónico +0 compatible con el encoder Fraction
congelado; signo del cero ORIGINAL se preserva aparte como bit64.
Se retiene porID/binding/wordABI/sourcegauge/error exacto L1/norma original,
traza HOST y recibo SHA de inputpacket input-only sin cambios.
Paquetes cerrados por13SHA: corrupción rehasheada/case/source swaps rechazan.
No consulta palabras esperadas, unidades, productos, salidas o U/GEMM.
Tests pueden contrastar únicamente seis encodings fuente retenidos disponibles,
NO productos/campos evaluados ni gates antiguos.

Codifica todas14fuentes originales de13casos, incluidos STOP, sin admitirlos.
Cota de encoding sigue pendiente multiplicarse por unidad observada y sumarse
a cargos de referencia/producto/reducción/detector; caps/grupos intactos.
No kernel/upload/inferencia/árbol/native evidence/fullpipeline/coherencia física/
GPUadmisión/promoción/RT/óptica/ventaja demostrada. Implementación faltante
de esta subetapa queda cubierta SOLOHOST, no acelera ni sustituye sceneinference.

CPU1hilo/hijo<=60s; sin GPU/reserva/instalación/publicación/merge.
JEV bloqueado: fallbackLOCAL sin aval remoto. Boards/checkpoint SINstage.
Skills: cambio acotado/controles frontera/cacheinputs exactos sin productores.

## Evidencia

9 tests PASS rc0/0,1979749s;13casos14IDs, todas fuentes originales .1+0i;
limbs [1036831949,2966211789,0,0], error exacto L1=2^-55 porfuente.
56 RN32 HOST y28 restas HOST exactas NUEVAS en lote principal, no cachehit.
5controles adicionales20RN32/10restas; tests adicionales instrumentados aparte,
incluyen ties de ambos signos/binade, subnormal elegido/overflow rechazados,
tinybinary64 roundzero con cargo2^-1074, signedzero original preservado,
componentes complejas distintas y rechazo de swaps input incluso rehasheados.
Contadores completos de llamadas RN32/encodings del proceso en report;
NO costes máquina/dispositivo/energía de pipelinecompleto.
Validador independiente: búsqueda monótona porpalabras binary32, no comparte
algoritmo productor cociente/exponente ni importa módulos de producción.
Seis encodings fuente retenidos disponibles se contrastan sin productos,
unidades/gates/scene-replay. FrozenFAILs/budgets/referencias/grupos intactos.
Verificación inicial independiente rc0/0,2162137s:162huellas/13casos14IDs/
6encodings retenidos/224bytes fuentehi-lo. Proceso completo instrumentado:
116RN32 intentados,110salidas y6rechazos esperados,25encodings y50restas
HOST exactas; incluye principal+controles+tests, sin dobles contadores de cache.
Hardening posterior: tipo bits estricto, copia de palabras ORIGINALES sinalias
de caller; test mutaciónlista/casosbitsfloat-bool rechazados. MISMOraw119396bytes,
SHAafa9cfef607cd694ed9f20000645005d4b8ddb11247d91412f6510ea43baedb2,
sin cambiar cotas/gates/thresholds. Verificación final consignada en report.
