# EXP005: transporte de ciclos oblicuos a pares IEEE64

ID: PRECISION-OBLIQUE-CYCLES-PAIR64-CPU-001. Codex: capacity_audit/EXP005.
Base1233b036a47aad94f77441ebb61e1ac515a70cd4.
Parent OBLIQUE-LENGTH001 SHA139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e,
83pins y captura lossless6tests/28casos. Sin ejecutar geometría/raíz/oldtests.

Modelo opt-in precision-oblique-cycles-pair64-CPU-v1, representación
OBLIQUE_GEOMETRIC_CYCLES_PAIR64_CPU_NOT_GPU_ABI.
Diferente del antiguo TwoSum axial con fase de fuente/espejo: aquí se
transportan intervalos geométricos de longitudes irracionales desde un
ORIGINAL oblicuo declarado. No sustituir contracts/shaders/runners/fixtures.

## Entrada y presupuesto

Selector cerrado: case, parent_result_sha256, original_scene_sha256,
literal_request_sha256, representation. Modelo explícito. Hashes de TODO
resultado/ORIGINAL/literal ypins verificados antesRN.
Los28casos parentales se conservan:24STOP no producen RN ni filas nuevas.
Solo4parciales CPU con S0/S1/relativo, mismas unidades/gauge/lambda/caps.
No override, subset SOURCE, ABI alias ni aumento de tolerancias.

Para un intervalo [a,b] sellado:
m=(a+b)/2, r=(b-a)/2, exactos racionales.
h=RN64(m), e=m-F(h) exacto, l=RN64(e).
y=F(h)+F(l) es suma RACIONAL, nunca float64(h+l).
Ledger: primer error |F(h)-m|, residuo exacto, segundo error |F(l)-e|,
incertidumbre del intervalo r, representación y.
El primer error se cancela mediante el residuo exacto, no se omite.
Error frente a TODO valor del intervalo:
max(|y-a|,|y-b|)=r+|m-y|=r+|F(l)-e|.
Cota rad=8*error_cycles; comparación inclusiva con cada cap literal.

S0,S1 y relativo se codifican cada uno desde su intervalo sellado.
El relativo NO se presenta como resta RN64 de los dos pares SOURCE.
Su midpoint coincide algebraicamente con m0-m1, y se registra:
closure=|y0-y1-yrel| <= errorRN0+errorRN1+errorRNrel.
Esta closure no autentica coherencia óptica/materiales/cobertura.
TODAS las cotas SOURCE/relativo antes de ANYrow; fallo descarta todas.
Diagnostics preservados no equivalen a admisión.
Dos palabras IEEE64 LE por fila, serializadas como hex, sin ABI GPU.
No nueva propagación, seno/coseno, TwoSum nativo ni inferencia de escena.

## Controles y evidencia

Contraste de una sola palabra: usa el h YA calculado, sin cast adicional;
bound_single=8*max(|F(h)-a|,|F(h)-b|) frente a los mismos caps.
No oculta el error con una referencia reconstruida de los bytes recibidos.
No afirmar superioridad universal: magnitudes tiny pueden caber en una
palabra según una cota absoluta; guardar resultados sin cambiar umbrales.

Tests nuevos stdlib: todo corpus28, selectores/bindings/typedbad,
dependencia cambiada/lectura denegada, fault low=0 con caps intactos,
controles racionales1/3,-1/3,1+2^-56,-1+2^-56,0,halfsubnormal2^-1075,
overflow y tipo inválido. Sin cambiar flags físicos/nativos.
Oráculo independiente: decodifica IEEE64 mediante signo/exponente/mantisa
como racional; comprueba celda de redondeo vecinos y empate even sin usar
float ni importar el encoder. Recalcula ledger, closure, caps yatomicidad
sobre capture sellada. La inyección low=0 NO se certifica como RN correcta.
Guardar captura completa en recibo inmediatamente tras la suite.

Contar por separado nodos reales y fallos inyectados: 24RN de los4casos,
12RN de6controles sintéticos; fault6nodos ledger incluye3RN reales high
y3low fabricados. Total39casts float64 exitosos y1intento overflow; el
tipo float inválido se rechaza antes de convertir. NO coste completo.

## Límites

CPU RN64 sobre intervalos racionales de ORIGINAL declarado distinto de
Bpyfloat32/GPUALU/RT/óptica física. No ejecución GPU ni material/sourcephase,
amplitud/campo/potencia: UNKNOWN(None), no cero. Todos flags nativosfalse.
NO inferencia óptica total, autenticar escena, ABI pair64GPU o costoRT.
Costes completos UNMEASURED_NOT_ZERO; bytes/counts/QA no throughput/ganador.
Frozen conf1/v0/v4/0119/0315/nearestV2/runners/shaders/contracts/guards/
bounds/caps/FAIL y0337CLOSEDdeadline intactos. Solo cinco archivos propios,
boards/checkpoint localesSINstage. JEV LOCALfallback sinaval/no retry.
CPUafinidad1/env1hilo/hijo60s; RAMpreviaUNKNOWN/ACCESS_DENIED sinbypass,
GPUBlender0/reservas0. Sin SDK/DrJit/Kaggle/push/merge/writersajenos.

PeticionClaude ACK ID/SHA; artifacts YAexistentes backend/guard/material/
amplitud/completitud porSOURCE/rama IDpathSHAbytes e igual ORIGINAL-literal-
decoder-ABI-gauge-caps-trabajo-salidas-costes completos. NoACKinventado.
GPU futura solo nuevojob exclusivo, guardfailclosed, telemetría/deadline
nuevos y límites del usuario; contrato/tests/commit antescarga.
Skills cogniciónextendida+featuredevelopment: reutilización sellada,
ledger verificable ycontrato/pruebas separados; no claim ahorrodetokens.
