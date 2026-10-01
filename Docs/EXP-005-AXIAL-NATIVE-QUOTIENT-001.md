# EXP-005 / AXIAL-NATIVE-QUOTIENT-001

P1 opt-in, nuevo espejo CPU de división/selector signed512 por fuente.
Base c5395b00ac04d0da161bffd3e2fefacac5b41ee1. Acuse PRESENCE-STOPS001/
SHA50bb8f64361b645394596a3982a8a811f9f2aaac3dcde9c7561661dadcd96e06.
Los módulos HOST anteriores usan Fraction/RN32; este módulo nuevo NO los sustituye.

## Contrato

Entrada Lref firmada y lambda positiva, escala BU*2^149 común, 16 uint32
little-endian complemento a dos. q=floor(L/lambda), r=L-q*lambda, 0<=r<lambda.
División restauradora de magnitud unsigned (512 rondas); INT_MIN no requiere
abs signed ni producto q*lambda dentro del dominio signed512.
Selector centrado n=floor(L/lambda+1/2), residual=L-n*lambda;
-1/2 <= residual/lambda < 1/2. Empate medio giro SIEMPRE -1/2, no epsilon/snap.
Comparar r con lambda-r evita 2*r overflow. Salidas words exactas, SIN RN32/RN64,
float/Fraction en el core nuevo; error nuevo de reducción racional exactamente0.
NO unidad compleja/trig ni campo. Cota fase previa no se relaja ni se reutiliza
como autorización completa de campo; costes de trig/argumento/redondeo aún pendientes.

Escena: fresh propios YZ/X/eventos/ref/cota ORIGINAL64, no answers lookup.
Sólo fuentes con cota previa PASS evalúan 1ORIGINAL ideal y4encoded corners.
ORIGINAL no es nominal encoded ni inferencia sustitutiva. Fuentes/gauges separados.
Misma rama centrada para ORIGINAL y cuatro esquinas requerida; cruce STOP sin
cambiar caps/radios. División exacta por esquina NO vuelve continuo un intervalo
que cruce la rama. Casos STOP upstream conservan razón/sin reducción inventada.
Perfil exactYZ +/-X dos owners/dos eventos, NO autointersección3D general.

## Verificación y recursos

Nueva etapa sobre INPUTs congelados13cases14fuentes y cuatro controles de ausencia
retenidos (5fuentes adicionales). No invoca suites ni writers anteriores.
Primitivas signed extremos/zero/half/near-half y64aleatorios reproducibles; oráculo
stdlib independiente int/Fraction, nunca se usa ese oráculo como implementación.
Costes por reducción:512rondas/8192unsignedwordshifts más comparaciones/sustracciones/
correcciones firmadas/selector; fresh dependencias redundantes/HOSThash-copies extra.
NO instrucciones GPU/tiempo hardware/energía/VRAM/costes completos/ganador.
CPU1hilo/hijo<=60s; SIN GPU/Blender/reserva/SDK/DrJit/push/merge/peerwriters.
JEV bloqueado: fallback LOCAL sin aval y sin reintento.
Frozen/runners/shaders/conf1/v0/v4/0119/0315/nearestV2/caps/radios/FAILs intactos.
Sharedboards/checkpoint locales SINstage; sólo cuatro propios versionables.
La skill de desarrollo mantiene interfaces y paradas explícitas en esta pieza opt-in.

Claude: ACKID/SHA; sólo artifacts efectivos existentes matching ABI/ref/escena
y contrato igualtrabajo/output/costes completos. Guard0337histórico CERRADO;
ventana histórica no se reabre ni se modifica; ningún nuevo job autorizado aquí.
NO phase-unit/field/fullpipeline/nativecompile/auth/GPUadmisión/RT/óptica física.
## Evidencia verificada

Suite inicial8PASS/1,0160594s preservada; ampliación propia añade selector
cruce/empate y captura de llamadas, sin modificar core congelado/caps/radios.
Suite final9PASS rc0/0,9396415s; raw597148bytes
SHAbd6eb0e397b60908784d65912230fcdf3f780484db64aac9641f676f86570397.
17casos19fuentes:8cotaPASS→40reducciones nuevas (8ORIGINAL+32encodedcorners);
11STOP upstream conservados (incluye2FAIL fase y4presencia). 8ramas escena PASS,
0cruces en estas escenas; control selector SINTÉTICO propio cruceSTOP/samePASS.
130vectores primitivos +14controles firmados/half/zero/near-half +9selector +
40escena =193reducciones válidas capturadas;8rechazos esperados de inputs/model.
193*512=98816rondas/1581056wordshifts; escena20480rondas/327680wordshifts.
Comparaciones/sustracciones/correcciones porword verificadas independientemente.
NO coste completo: validación/negación/add-sub firmadas/copies/hash/HOST/fresh
dependencias repetidas y8rechazos además; no tiempo ALU ni instrucciones compiladas.
Oráculo inicial stdlib rc0/0,3780579s PASS:190huellas187heredadas3propias,
identidades exactas y costes de193llamadas sin imports producción.
Refuerzo final verifica además selección concreta de130vectores/8dominios inválidos;
recibo final y comprobación postcommit se registran en reporte/checkpoint.
