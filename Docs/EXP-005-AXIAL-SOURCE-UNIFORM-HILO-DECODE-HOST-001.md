# EXP005 — AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001

P1 Codex opt-in axial-SOURCE-uniform-hilo32-RN64decode-declared-box-HOST-v1. Base845cdae52ecefaf18dbe0210e06d79cfcf03774e; parent SOURCE-AMPLITUDE-DISK-BOX-HOST-001 SHA822d58a334b8be92f7e8421eb330013865c76fab7f55314eff5926f76e52a28e. Nuevo teorema HOST de etapas encoder+decode, NO ejecución nativa ni error completo de SOURCE.

## Grafo y modelo

Para cada componente ORIGINAL binary64 x en intervalo declarado: h=RN32(x), r=RN64(x-h), low=RN32(r), decoded=RN64(widen(h)+widen(low)). Widening exacto. Modelo explícito nearest-even con subnormales graduales, NO FTZ/FMA. El guard congelado rechaza resultados subnormales seleccionados: NO se afirma que admita todos los x de la caja ni que un dispositivo ejecute este modelo. Se conserva ese rechazo; no instalar/reemplazar backend.

E32(M)=2^-24 M+2^-150; E64(M)=2^-53 M+2^-1075, E(0)=0. Para exactos |t|<=M en rango finito, cada redondeo tiene error<=E(M): media separación normal<=u|t|, en subnormales<=eta. Este es análisis uniforme por binades, NO generalización de muestras. MAX32=(2^24-1)2^104; MAX64=(2^53-1)2^971. Extremos racionales canónicos firmados <=4096bits/ordenados. Cada argumento y salida conservadora dentro de rango; márgenes pueden rechazar cajas cercanas a MAX aun si puntos aislados serían finitos. No clamp/relajar caps.

## Cargos y dependencia conservada

M=max(abs(lo),abs(hi)); eh=E32(M), high_max=M+eh.
Exactamente x-h tiene módulo<=eh; er=E64(eh), res_max=eh+er.
el=E32(res_max), low_max=res_max+el.
h+low-x = delta_residual_RN64 + delta_low_RN32. Por tanto encoding_error<=er+el, NO sumar eh otra vez. eh se usa para rango del residual; no se supone residual RN64 exacto/Sterbenz ni independencia de h y x.
exact_decode_sum_max=M+er+el; ed=E64(exact_decode_sum_max).
decoded-x<=er+el+ed. Complejo: sumar componentes ONCE; charges encoding_L1 y decode_L1 separados, total=encoding+decode. No multiplicar aún por UNIT ni incluir Horner/geometry/product/material/reducción/proyección.

E(0)=0 prueba error absoluto de grafo ideal en cero, NO autentica signos IEEE de cero ni política de ejecución. Modelo gradual abarca valores subnormales matemáticamente; conservamos frozen_guard_admission_for_entire_box_provedFalse.

## SOURCE/domain ORIGINAL e integración

Reutiliza EXACTAMENTE dos cajas INPUT CONTROL anteriores +/-1e-6 alrededor del A ORIGINAL (no nuevas cajas/outputfit). ALL INPUT dominio/contextos/source_order/gauges/ORIGINALword anchors antes calcular cotas. Valida dominio fresco y digest canónico exacto contra recibo retenido. 17REALcases19sources/None sin dominio: sourcesNone/cotasNone/STOP. Dos cotas analíticas encoder-decode; uniform_encoder_decode_bound_for_declared_box_HOST_provedTrue SOLO esa etapa/modelo. uniform_executed_SOURCE_error_L1None/uniform_SOURCE_enclosure_provedFalse/phase_bound_radNone/38flagsFALSE/gruposSTOP/guard/device/signzeroFalse siempre. NO componer error de etapa como error completo al lema de fase ni usar epsilon puntual; referencia actual A varía y no es w(A0) anterior.

5tests: missing/None,2dominiosencoder/decode,4boxcontrols,12simulaciones RNE racionales independientes stdlib (diagnóstico sintético NO CPU nativo ni prueba del continuo),8modelo/rango/tipado rechazos y5INPUT/SHA rechazos antes cálculo. Oráculo stdlib independiente442pins verifica captura, dominios/anchors intactos, ecuaciones RN/rangos/cargos/once-total y simulaciones RNE exactas con cotas sin production imports/suites previas.

CPU1hilo/afinidad1/hijo60s/nativeGPUBlender0/oldproducer-suite0. Costes IO/HOST/setup/upstream/rest UNMEASURED nunca gratis/no speed/eficiencia/equalwork/ganador. CPU sintética matemática NO Bpyfloat32/GPU ALU/RT/óptica física. JEV LOCAL/no aval/bloqueado sin retry. Fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/caps/FAILs/foreignfiles-writers-procesostickets intactos; boards/checkpoint LOCAL SINstage; sin SDK/DrJit/Kaggle/push/merge; 0337ventana CERRADA/deadline intacto; GPU futura Claude exclusivo/gpuqtelemetría/guardfailclosed/NUEVOdeadline verificable/límites originales.

Claude ACK ID+SHA y SOLO YA existing SOURCEdomain-uniformerror/backend/guard/consumer ID/path/SHA/bytes/MISMO ORIGINAL INPUT-ABI-gauges-work-output-fullcosts; no filler/outputfit. Siguiente propia: dominio de admisión del guard normal-o-cero compatible con estas cajas, y cota uniforme producto complejo con UNIT/proyección geométrica justificadas antes fase/reducción/campo.
