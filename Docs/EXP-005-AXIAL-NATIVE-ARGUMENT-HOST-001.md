# EXP-005 / AXIAL-NATIVE-ARGUMENT-HOST-001

P1 opt-in HOST CPU, NO caster/argumento nativo. Basefeda87bc6c875dbcc5294bc22b2fea8c16f0a3e5.
Acuse QUOTIENT001/SHAc79ee5920e9cc9962bc8464139fb94e3c577fdb635e70c9f281e3acc416802a8.

## Contrato

Residual exacto centered_numerator/denominator16uint32 signed512 desde ESTA
escena/quotient. HOST bigint/Fraction explícitos, dos roundings modelados RN64:
cast nearest-even de residual [-1/2,1/2), multiply por2piword401921fb54442d18.
Pure helpers propios round64/component64 y constantes PI_LOWER/PI_UPPER congelados;
NO ejecutar audit/load/producer/writer anterior. NO GLSL/casterGPU/Bpyfloat32.
Sea r original residual y rhat cast, p constante y a=RN64(rhat*p):
Bcast=abs(p)*abs(rhat-r), Bconst=abs(r)*error_p, Bmul=abs(a-rhat*p).
Barg=Bcast+Bconst+Bmul; error_p máximo versus2PI_LOWER/UPPER.
Cero residual da cero/cargo0; half negativo permitido, +half rechazado.
Normal-or-zero binary64; no FTZ/overflow fallback. WORDS→HOST no cuesta cero.

Fresh propios YZ/X/events/ref/cota/quotient. ORIGINAL ideal separado de4encodedcorners;
NO nominal encoded elegido ni sustitución escena/inferencia. Sólo SAMEcenteredbranch
y cota previa PASS evalúan cinco argumentos HOST. Por fuente:
Bprev=8maxabs(encodedcycles-originalcycles), Bnew=max(Barg_encodedcorners);
Btotal=Bprev+Bnew <=MISMOcap ORIGINAL. Ideal ORIGINAL diagnóstico NO cargo al output.
Fuentes/gauges/caps/radios y STOP upstream conservados. Cargo nuevo puede FAIL;
no ampliar caps/conf1/umbrales para PASS. FAIL de esta etapa no revierte etapas previas.

## Costes, verificación y límites

17INPUTs(13frozen+4ausencia retenidos)/19sources, sin suites ni writers viejos.
130primitivas sobre residual word retenido + tie-even/zero/half/tiny-normal propios.
Cada llamada32HOSTwordextractions +1RN64cast+1modeledRN64multiply, constantes decode/
Fraction/add-mul-div/bounds/HOSTserialization/copias/hash yfreshdependencies extra.
NO costes completos/ALU/hardware/RAM-VRAM/energía/velocidad/ganador.
CPU1hilo/hijo60s; SIN GPU/Blender/SDK/DrJit/reserva/push/merge/peerwriter.
JEV bloqueado: fallback LOCAL sin aval/no reintento. Sharedboards/checkpoint SINstage.
Fixtures/runners/shaders/core/conf1/v0/v4/0119/0315/nearestV2/caps/radios/FAILs intactos.
NO trig/unidad compleja/campo/sourceproduct/reduction/fullpipeline/auth/native/RT/física.
Argumento puede llegar a[-pi,pi]; NO entrada silenciosa al Horner congelado [-1,1].
Quarter-reduction/unidad/campos y cargos adicionales quedan pendientes.
Skill desarrollo exige interfaces opt-in/cargos/paradas explícitos, no refactor congelado.
Claude ACKID/SHA y artifacts efectivosYAexisting matching ABI/ref/scene+igualtrabajo/
output/costes completos. Guard0337históricoCERRADO/deadlineintacto/no cargasrelleno.
Evidencia: 8testsPASS rc0/1,1997628s (unittest0,817s); raw879263bytes
SHAdf47ce7e462fe5ac74f6314888a5c3b044d05a001fc594ba5a3f6c401e0f54ec.
Oráculo independiente stdlib SIN imports producción: 194pins/191heredadas, RN64
nearest-even por vecinos, constantes/cargos/racionales/caps/gauges/entradas capturadas.
17casos19fuentes: 8evaluadas→6argument-boundPASS y2NUEVAS filasFAIL
(two_sources.other ymissing_cap_two_sources.other: MISMA fuente/cap0, no dos escenas
físicas independientes);11STOPupstream idénticos. Cota previa/branchPASS no implica
argumentoPASS. NO ampliación de cap0: constante/rounding no caben en presupuesto cero.
40args escena(8idealdiagnóstico+32corners)+130primitivas+7tiecontrols=177validcalls,
9invalid-input/model expectedrejects. 177RN64casts+177modeledRN64multiplies,
5664MAIN HOSTwordextractions; escena40+40/1280MAINwords, extracción adicional
cota/cap2304words. Fraction/bigint/constantes/bounds/serialización/copies/hash/deps extra.
Captura inicial tool-output truncada ywrapper SyntaxError preservados: reparaciones
sólo del harness/recibo, MISMO módulo/tests/inputs/caps/umbrales. No fallo numérico
convertido en PASS. Recibo incluye oráculo inicial/final, SHA ysalida literal.
