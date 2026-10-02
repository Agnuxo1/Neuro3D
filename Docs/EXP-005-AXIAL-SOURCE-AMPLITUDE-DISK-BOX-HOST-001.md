# EXP005 — AXIAL-SOURCE-AMPLITUDE-DISK-BOX-HOST-001

P1 Codex opt-in axial-ORIGINAL-SOURCE-amplitude-box-conditional-disk-HOST-v1. Basefed692ac6f7682bfacfad97263b8d500a718ec91; parent SOURCE-PHASE-QUOTA-CONSUMER-HOST-001 SHA7acd92eb57129f998f2eb8b3ab8a315f43118c18ca77682bea0f48ed7eca43c3. Este trabajo NO sustituye el power-box anterior ni el Horner uniforme: trata la fase PRINCIPAL de una SOURCE reflejada respecto a una referencia ideal cuya amplitud puede variar. Runners/shaders/contratos y pruebas puntuales congelados.

## Lema condicionado exacto

Caja real cerrada de amplitud ORIGINAL A: Ire x Iim. Extremos racionales canónicos firmados <=4096bits, ordenados, no bool/float/nonfinite; sin swapping/clamping. Sea d(I)=0 si I contiene0, y min(abs(lo),abs(hi)) en otro caso. m=max(d(Ire),d(Iim)). Para TODO A en la caja, |A|>=max(abs(ReA),abs(ImA))>=m. Esto es analítico por monotonía del valor absoluto, NO prueba obtenida de muestras.

SI adicionalmente PARA TODO A un algoritmo produce z(A) tal que |z(A)-w(A)|_1<=epsilon, con w(A)=A exp(i theta_ORIGINAL)(-1), epsilon>=0 y m>epsilon: al rotar por arg(w(A)), la proyección radial es >=m-epsilon>0 y la transversal <=epsilon. Por tanto distancia de fase PRINCIPAL <=atan(epsilon/(m-epsilon))<=epsilon/(m-epsilon) rad. atan(t)<=t para t>=0 se sigue de integrar 1/(1+t^2)<=1. No evalúa atan/arg/trig, no fase desenrollada ni afirmación sobre branch cuts o ejecución nativa.

epsilon es HIPÓTESIS SINTÉTICA explícita en la primitiva matemática, NO evidencia de ejecución. conditional_amplitude_box_phase_lemma_HOST_proved indica solo teorema condicionado. uniform_executed_SOURCE_error_L1=None/uniform_SOURCE_enclosure_proved=False SIEMPRE. Una caja que alcance el origen da m=0; epsilon>=m o falta margen STOP/rechazo. Cero epsilon explícito puede dar cota condicionada0 lejos del origen, NO certifica error ejecutado0.

## Vinculación ORIGINAL sin fabricar enclosure

API de escena recalcula contexto SHA de packet/snapshot/ABI y compara con contexto retenido. INPUT dominio con whitelist model/units/context_sha256/scope/sources, scope SOLO SOURCE_field_reim; geometría/wavelength/path/material/gauges ORIGINAL fijos. Cobertura ordenada completa SOURCE, phase/terminal/common_terminal exactos. Caja contiene el A ORIGINAL exacto obtenido de snapshot binary64, con palabras uint64 y racionales ancla conservados. No acepta epsilon/error/cap/expectedoutput/authority del caller: TODOS dominios de escena dejan error uniforme y fase uniforme None, domain_authenticationFalse, 38flagsFALSE/casosSTOP/groupadmissions0. Contener el ancla NO prueba imagen uniforme ni que el dominio esté autorizado físicamente.

Dos cajas INPUT CONTROL sintéticas +/-1/10^6 alrededor del ancla INPUT (NO outputfit) y epsilon hipotético literal1/10^16 ilustran el lema; no reutilizan epsilon puntual. 17REALcases19sources sin dominio siguen STOP/None. Ni el encoder hi-lo/decodificación/RN/Horner/material ni todos sus rangos se certifican sobre esas cajas. No alterar caps ni bounds anteriores para encajar.

5tests: missing/None,2domainINPUT ligados sin error uniforme,4lemascondicionados (incluye negativos/axis0),11origin-margin-type-sizeSTOP,10domain-gauge-SHArejects. Oráculo stdlib independiente437pins verifica captura, contextos/anchors exactos binary64/cajas con radio CONTROL retenido, ecuaciones racionales por análisis de intervalos y None/FALSE. No imports productivos/replay de suites/nativos.

CPU1hilo/afinidad1/hijo60s/GPUBlendernative0/oldproducer-suite0. Costes IO/HOST/setup/upstream/rest UNMEASURED nunca gratis/no speed/eficiencia/equalwork/ganador. CPU sintética/hipótesis matemática NO Bpyfloat32/GPU ALU/RT/óptica física. JEV LOCAL sin aval/no retry seguridad. Fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/caps/FAILs/foreignfiles-writers-procesostickets intactos; boards/checkpoint LOCAL SINstage; sin SDK/DrJit/Kaggle/push/merge. 0337ventana histórica CERRADA/deadline intacto; GPU futura Claudeexclusiva/gpuqtelemetría/guardfailclosed/NUEVOdeadline verificable/límites originales.

Claude ACK ID+SHA y SOLO YA existing SOURCEdomain/uniformerror/backend/guard/consumer ID/path/SHA/bytes/MISMO ORIGINAL INPUT-ABI-gauges-work-output-fullcosts; no filler/outputfit. Próximo propio: demostrar el error uniforme del encoder hi-lo32 sobre un dominio declarado antes de componerlo con este lema. No convertir una cota puntual en cota uniforme ni promover grupos/reducción/campo.
