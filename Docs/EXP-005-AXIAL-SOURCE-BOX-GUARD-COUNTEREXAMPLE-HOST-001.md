# EXP005 — AXIAL-SOURCE-BOX-GUARD-COUNTEREXAMPLE-HOST-001

P1 Codex opt-in negativo HOST, modelo axial-SOURCE-box-frozen-guard-exact-counterexample-HOST-v1. Base139ef7b3534bc6481d055e24cdd6445cfc6c50c6; parent AXIAL-SOURCE-UNIFORM-HILO-DECODE-HOST-001 SHA0c0bba56d7a617280bf7d8bce70b18fe201cccd86cb367adb5845b2997987602.

## Resultado y alcance

Las dos cajas SOURCE retenidas tienen componente imaginaria [-1e-6,1e-6]. Contienen x=2^-149. Este x es normal binary64 (exponente -149 > -1022), word64=(1023-149)<<52, y es exactamente representable como mínimo subnormal binary32 (word32=1). RN32(x)=x por representabilidad exacta, sin ejecutar cast nativo. El guard congelado check_RN empieza por bits(word32,32) con normal=True y rechaza "normal-or-zero selected word". La fuente completa sustituye SOLO esta componente del anchor ORIGINAL; la otra word se conserva, ambas entradas binary64 normales-o-cero, y la fuente pertenece a la caja exacta.

Un contraejemplo basta para refutar admisión del guard en TODA la caja. No se afirma un porcentaje, ni que falle el anchor original, ni que las cotas analíticas encoder/decode anteriores sean falsas. No se cambia caja/caps/bounds/fixtures ni el guard. No se recorta el dominio para convertirlo en PASS. No se ejecuta la conversión nativa, residual, low, SOURCE graph ni dispositivo; se ejecuta SOLO el validador HOST puro sobre words literales y racionales. Esta es evidencia local negativa del contrato de selección, no prueba empírica de CUDA/Blender/RT/óptica física.

API de búsqueda acotada a +/-2^-149. Encontrar testigo activa SOLO whole_box_frozen_guard_admission_disproved_HOST. No encontrarlo deja witnessNone/flagFalse/STOP: NO demuestra admisión normal-o-cero de high/residual/low/decode. Zero numérico no autentica signed-zero execution. Todas las 38flags heredadas false, guard/device admission false, SOURCE error uniforme completoNone y fase/gruposNone/STOP.

## Binding, aceptación y costes

ALL INPUT dominio/contexto/ordenSOURCE/gauges/anclas/digest tipado/parent encoder-certificate antes buscar testigos. Cajas y SHA exactamente retenidos; cota anterior solo SHA, no recomputada/compuesta como error completo. 17REALcases19sources sin dominio conservan sourcesNone. Los testigos son variaciones matemáticas de INPUT dentro del dominio sintético, no nueva escena REAL autenticada.

Cinco tests: missing/None; dos dominios ligados y contraejemplos; cuatro controles (positivo, negativo, caja solo cero sin testigo, caja normal sin testigo); siete rechazos de tipado/modelo/dominio; cinco rechazos INPUT/SHA antes checker. Oráculo stdlib independiente447pins, clasificación IEEE y representabilidad exactas, fuente completa contenida, SHA de dominio/encoder retenidos, tipos y flags. No suites/productores previos ni inferencia desde escena nueva.

CPU1hilo/afinidad1/hijo60s/nativeGPUBlender0. IO/setup/upstream/fullcosts UNMEASURED NOT zero. JEV LOCAL bloqueado sin retry/aval. No SDK/DrJit/Kaggle/push/merge; ventana0337 cerrada/deadline intacto. Fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/caps/FAILs/foreign intactos; boards/checkpoint local SINstage. GPU futura exige reserva exclusiva Claude/gpuq/procesos/RAMVRAM/temp/guardfailclosed/NUEVOdeadline/límites originales.

Claude ACK ID+SHA; pedir SOLO YA existentes dominio SOURCE admisible, backend/guard y contrato mismo ORIGINAL INPUT/ABI/gauges/trabajo/salidas/costes completos. Próximo paso propio: producto complejo uniforme condicionado por UNIT y geometría justificados, manteniendo este bloqueo de admisión separado. No escalar ni promover antes resolver el dominio ejecutable por contrato.
