# EXP005: rayos oblicuos y cota racional de longitud

ID: PRECISION-OBLIQUE-COMMON-DETECTOR-LENGTH-CPU-001. Codex: capacity_audit/EXP005.
Base470df02fa6e04ab182005017d8a4d4a3d3a53dc4; acuse OUTPUT-HOST001
SHAcb8b7c538df07896b8f47d9ce1a3923709621d2e15d13189a818e8eae9272929.
Los pins previos se conservan por integridad, NO se ejecutan sus productores.

Modelo nuevo opt-in precision-oblique-common-detector-length-CPU-v1.
Escena nueva precision-oblique-declared-scene-v1, coordenadas y direcciones
racionales, BU; no cambia fixtures, bounds, conf1 ni shaders antiguos.
Representación RATIONAL_INTERVAL_CPU_NOT_GPU_ABI, no conversión pair64.

## Interfaz y geometría exacta

audit(scene, request, model=MODEL). Esquemas cerrados y tipos estrictos:
racionales [int,int] sin bool/float, denominador positivo, hasta128bits,
magnitud <=1e6; vectores3D. Dos SOURCE ordenadas S0/S1, dos a cuatro
triángulos, IDs únicos, vértices no degenerados y dirección no nula.
Request liga SHA del ORIGINAL, fuente/orden, primitiva inicial y detector,
punto común, lambda_BU, referencia_BU y tres caps literales.
Preflight completo antes de consultas geométricas.

Se intersecta el rayo racional con todos los triángulos. Baricéntricas
incluyen bordes, pero nearest tie provoca STOP. Coplanar ambiguo STOP.
t negativo no candidato; t positivo, por pequeño que sea, conserva el hit.
t=0 solo se descarta en la primitiva inmediatamente golpeada por ese mismo
path/SOURCE. Todo otro contacto cero provoca STOP. Sin offset, epsilon,
veto global de objeto ni separación artificial de fuentes.
Reflexión geométrica ideal d'=d-2(d.n)/(n.n)n, sin normalizar por floats.
Se exigen root/detector declarados y punto detector exacto para ambas fuentes.

Fixture nuevo: planos x=0 yx=1, triángulos y/z hasta3, SOURCE en
(1/4,1/4,1/4) y(3/4,3/4,1/4), dirección (1,1,0).
Ambas golpean (1,1,1/4), salen (-1,1,0) y llegan (0,2,1/4).
Longitudes 7sqrt(2)/4 y5sqrt(2)/4, NO7/4 y5/4 del fixture axial.
Variantes nuevas: separación de planos 2^-60; dirección multiplicada por2.
No aumentar silenciosamente bounds de ningún fixture previo.

## Certificado de raíz y propagación geométrica

Para cada segmento: s=dot(delta,delta) racional, longitud exacta sqrt(s).
Precisión fija96bits, no adaptable al verdict/cap:
k=isqrt(floor(s*2^192)), lo=k/2^96,
hi=lo si lo^2=s; si no hi=(k+1)/2^96.
Certificado lo>=0, lo^2<=s<=hi^2, hi-lo<=2^-96. No float ni sqrt nativo.
La salida conserva s, extremos del segmento y el intervalo certificado.
La referencia independiente verifica cuadrados y retícula sin llamar isqrt.

Se suman intervalos de los dos segmentos por SOURCE.
Ciclos geométricos: [(Llo-R)/lambda,(Lhi-R)/lambda], R/lambda exactos
declarados. Relativo: [q0lo-q1hi,q0hi-q1lo]. Referencia común cancela
algebraicamente; no se borran incertidumbres ni caps individuales.
8*ancho_ciclos es cota conservadora del diámetro de fase geométrica enrad,
usando 2pi<8; NO es cota total de fase óptica.
Caps default literales del fixture nuevo: 2^-80rad.
TODOS los caps SOURCE y relativo se comprueban antes de emitir cualquier
path. Con cap0, las raíces irracionales no caben: STOP conservado.
Diagnostics de fallos no son emisión/admisión parcial.

## Límites y pruebas

CPU racional sintética sobre ORIGINAL declarado, NO escena autenticada,
Bpyfloat32, GPUALU, RT u óptica física. Material, amplitud, fase de fuente,
campo y potencia UNKNOWN(None). Reflexión ideal de dirección no introduce
fase de espejo cero ni Fresnel. Todos los flags físicos/nativos siguenfalse.
No hi-lo GPU, ABI ni inferencia total silenciosa. Costes completos
UNMEASURED_NOT_ZERO; operaciones/bytes/QA no throughput ni ganador.
Esto NO implementa un backend GPU, runner, guard ni barreras.

Seis tests nuevos PASS:28scenarios,4parcialesCPU/24STOP,8pathsemitidos.
74consultas ray/plano,30brackets de trayecto,16contactos exactos previos
descartados; además6controles sintéticos de raíz (cero, cuadrado, sqrt2,
tiny2^-240,2/3,large). NOreplay de suites/productores antiguos.
Son cuentas por captura: hubo DOS capturas CPU de esta suite nueva por
pérdida del handle transitorio durante el heartbeat. Ambas tienen stdout
88356bytes/SHAa2ae732bb6ddbe0449e42dcd4381b0b3d555ee12e28d318a5f4b8c50cdf1417e.
La segunda conserva stdout/stderr íntegros; la primera solo metadata y
su stdout idéntico comprobado por SHA. No reconstruir su stderr/tiempo interno.
Total ejecutado de la suite:148consultas/60brackets trayecto/12raíces sintéticas.
El TypeError de orquestación previo al recibo queda documentado, no oculto.
Contacto inicial, dos duplicados/ties del mismo objeto, SOURCE1wrongroot,
caps0 de cualquierSOURCE yrelativo, referencia común1000,
SHA/orden/modelo/typedbad/missingcaps/detectorz2^-60/malformedgeometry.
No ocultar FAIL ni cambiar umbrales paraPASS.
Oráculo separado stdlib usa determinantes/Cramer para hits/baricéntricas,
comprueba reflexión/longitud por cuadrados, propagación/caps/ALLsalidas,
pins y captura lossless; no importa el nuevo kernel.

CPU propia afinidad1/env1hilo/hijo<=60s; GPUBlender0.
RAMpreviaUNKNOWN/ACCESS_DENIED retenida, sin retry/bypass/preflight.
JEV securityblocked: LOCALfallback sin aval/remoto/reintento.
Solo5archivos propios versionados; boards/checkpoint localesSINstage.
SinSDKDrJit/Kaggle/push/merge; historical0337CLOSEDdeadline intacto.

Peticion Claude ACK ID/SHA y solo artifacts YAexistentes backend/guard/
metadata/material/amplitud/completitud SOURCE/rama ID/path/SHA/bytes,
igual ORIGINAL/literal/decoder/ABI/gauges/caps/trabajo/salidas/costes.
SinACKinventado ni cargasrelleno. Próximo: contraste de representación
y presupuesto a esta escena oblicua antes de extender a cómputo nativo.
GPU requiere contrato/tests/commit previo, nueva reserva exclusiva,
guard failclosed, deadline nuevo, telemetría válida y límites del usuario.

Skills cogniciónextendida+featuredevelopment: modelo racional auditable,
captura factual y contrato/tests separados; no claim ahorro de tokens.
