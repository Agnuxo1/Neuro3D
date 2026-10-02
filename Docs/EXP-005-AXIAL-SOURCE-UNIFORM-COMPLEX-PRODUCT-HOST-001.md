# EXP005 — AXIAL-SOURCE-UNIFORM-COMPLEX-PRODUCT-HOST-001

P1 Codex opt-in HOST, axial-variable-SOURCE-box-fixed-represented-UNIT-uniform-product-HOST-v1. Baseff54076e85206ab76d001b56bdba379fbd333405; parent BOX-GUARD-COUNTEREXAMPLE SHA54ec7a9d9dcb98354685d7751ad1ed14012e05497543f520d54f05a3e1583f35.

## Cambio de dominio y referencia explícito

SOURCE ORIGINAL A varía dentro de las dos cajas INPUT retenidas; UNIT representada se conserva como dos words binary64 del producto CPU puntual retenido, ligadas a mismo contexto/orden/gauges. Target matemático A*UNIT_representada fija, NO A0*UNIT, NO A*exp(i thetaORIGINAL). No se añade el error de UNIT frente a fase/geometría ideal ORIGINAL. Por tanto NO cota completa SOURCE ni fase, material, reducción o proyección. La ruta antigua NONZERO-SOURCE-DOMAIN mantiene SOURCE fija y UNIT variable; este nuevo dominio es distinto y no la sustituye.

Modelo explícito RN32/64 nearest-even/subnormales graduales/widening exacto/noFTZ/noFMA. Las ecuaciones de la cota encoder/decode retenida se verifican por racionales; no se reejecuta su constructor, productor ni suite. Sean T0,T1 los máximos de componentes SOURCE decodificadas. Sean c,d componentes exactas de UNIT representada, L=abs(c)+abs(d).

## Seis nodos y tres cargos

ac: M=T0*abs(c); bd: T1*abs(d); ad: T0*abs(d); bc: T1*abs(c).
Cada mul RN64 tiene e=E64(M)=2^-53*M+2^-1075 si M>0 (0 si M=0), output_max=M+e.
real=RN64(ac-bd): argumento máximo output_max_ac+output_max_bd; imag=RN64(ad+bc): output_max_ad+output_max_bc. Ambos incluyen los errores entrantes de multiplicación, sin cancelación favorable. Sign flip exacto matemático para -bd, NO policy signedzero ejecutada.
N=suma de seis errores RN64. Para TODO A de la caja y el grafo RN asumido, errorL1 frente a A*UNIT_fija <= Eencoder*L + Edecode*L + N. Propiedad submultiplicativa L1 y telescopado de cuatro mul/dos add; cargos separados ONCE, no cargo UNIT-error omitido disfrazado de cero. Rangos de argumento/salida conservadores <=MAX64 obligatorios; cerca overflow STOP/no clamp.

Un nuevo flag solo certifica este target limitado. uniform_executed_SOURCE_error_L1None/uniform_SOURCE_enclosure_provedFalse/phaseNone/38flagsFALSE/gruposSTOP/admisiones0. Los dos contraejemplos guard anteriores permanecen ligados por SHA: las cajas completas SIGUEN inadmisibles. Cotas matemáticas NO promoción de ejecución ni backend opt-in con guard relajado.

## Verificación y límites

ALL INPUT dominios/contextos/anclas/ordenSOURCE/gauges/encoder/guard-negativo/UNIT antes nuevos mayorantes. 17REALcases19sources sin dominio: sourcesNone/no inspección puntual/no cota. Exactamente mismas cajas +/-1e-6 y words UNIT; no bounds/caps/outputfit.

5tests: missing/None; dos dominios UNIT ligados; cuatro UNITcontrols y ocho simulaciones RNE racionales independientes dentro de la caja (diagnóstico, NO prueba por muestras); ocho rechazos modelo/rango/word/cert y cinco INPUT/SHA antes cálculo. Oráculo stdlib independiente452pins, IEEE exactos, seis mayorantes, cargos ONCE y simulaciones racionales, sin imports de producción/suites previas.

CPU1hilo/afinidad1/hijo60s/nativeGPUBlender0. CPU sintética NO Bpyfloat32/GPU ALU/RT/óptica física. Costes IO/HOST/setup/upstream/full UNMEASURED NOT zero, no speed/eficiencia/igualtrabajo/ganador. JEV LOCAL bloqueado sin retry/aval. Sharedboards/checkpoint locales SINstage; fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/caps/FAILs/guard/foreign intactos; no SDK/DrJit/Kaggle/push/merge. Ventana0337 cerrada/deadline intacto; GPU futura Claude exclusiva+gpuq/procesos/RAMVRAM/temp+guardfailclosed+NUEVOdeadline/límites originales.

Claude ACK ID+SHA y SOLO YA existentes dominio SOURCE ejecutable/UNIT-ORIGINAL/backend/guard/costes completos, mismo ORIGINAL INPUT-ABI-gauges-work-output. Próxima propia: enlace uniforme de error UNIT a ORIGINAL bajo geometría fija y sin autenticar ejecución de las cajas guard-bloqueadas.
