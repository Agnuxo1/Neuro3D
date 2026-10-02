# AXIAL-SOURCE-BINARY64-ENCODER-WORDCLASS-HOST-001

P1 Codex, capacity_audit/EXP005. Fallback LOCAL sin aval JEV; bloqueo de seguridad intacto. Base 36b2f5109aab8064227604713d019cc92d2f7ba2.

## Contrato y límites

Este módulo nuevo opt-in NO ejecuta ni modifica el encoder congelado. Da una condición SUFICIENTE para clases NUMÉRICAS normales o cero en ORIGINAL binary64, high32, residual64, low32 y decode64. Exige explícitamente que las entradas sean valores finitos binary64 del dominio declarado. No cambia un dominio real continuo por una rejilla implícita; no autentica esa hipótesis en escena ni la ejecución. Fuera del criterio devuelve UNKNOWN, no prueba de rechazo.

Modelo: RN-even binary32/binary64, widening exacto y gradual underflow, sin FTZ/FMA. No certifica bits +/-zero, política de cero con signo, implementación nativa, dispositivos, los seis nodos producto UNIT ni material/transporte. No hay admisión del guard, cota SOURCE ejecutada, nueva cuota real de fase o promoción.

Acuse AXIAL-SOURCE-DOMAIN-PHASE-CONSUMER-HOST-001, recibo SHA 7ac15550539842bcd45aa9a61fad3d95fcc47b4ba846cfae5bfd362c2ba919ce. Se leen 478 pins heredados por hash; contexto ORIGINAL, dominio entero por SOURCE, gauges, orden y negativas anteriores completos antes de ANY predicado. No se ejecuta el testigo subnormal antiguo ni productores/suites ajenos. Dos cajas negativas siguen STOP; el control two_sources singleton es INPUT sintético nuevo retenido, NO grupo real resucitado.

## Argumento matemático condicionado

Para intervalo cerrado I=[lo,hi], m=dist(I,0), M=max(|lo|,|hi|). [0,0] sólo garantiza magnitudes numéricas cero bajo el modelo, no bits.

Condición no nula: m >= 2^-74 y M <= 2^127. Sean u32=2^-24, u64=2^-53, e=floor(log2(m)), q=2^(e-52), hg=2^(e-24).

1. Todo x ORIGINAL binary64 en I es normal64. RN32 high h es normal32 finito: (1-u32)m <= |h| <= (1+u32)M; ambos extremos quedan estrictamente entre minnormal32 y maxfinite32.
2. x y h tienen el mismo signo y razón de magnitudes dentro de [1/2,2]. Por el lema de Sterbenz su resta es exactamente representable en binary64 bajo el modelo. La operación RN64 residual es entonces exacta. Esto no se presupone para un dominio real arbitrario.
3. El exponente del binade de x es al menos e. x es múltiplo de q; el binade de h es al menos e-1, y h es múltiplo de hg. hg/q=2^28. Por tanto r=x-h es múltiplo de q. Si no es cero, |r|>=q>=2^-126: r64 y RN32 low no pueden ser subnormales. |r|<=u32 M y |low|<maxfinite32.
4. |low-r|<=u32|r|<=u32^2|x|. El decode RN64 tiene magnitud entre (1-u64)(1-u32^2)m y (1+u64)(1+u32^2)M, estrictamente dentro del rango normal64 finito.

Para x negativo se aplica simetría a magnitudes. No se certifica el signo de los ceros. Las desigualdades se verifican con Fraction; el argumento de rejilla y el supuesto RN son parte EXPLÍCITA del contrato, no un autenticador.

Fuentes primarias: [Flocq in a Nutshell, lema de Sterbenz](https://flocq.gitlabpages.inria.fr/theos.html), [especificación y prueba Toccata](https://toccata.gitlabpages.inria.fr/toccata/gallery/Sterbenz.fr.html), [IEEE754 NVIDIA](https://docs.nvidia.com/cuda/archive/12.4.1/pdf/Floating_Point_on_NVIDIA_GPU.pdf). Reutilizar el lema no equivale a certificar este módulo en Coq ni a validar hardware.

## Verificación y costes

Suite propia: 17 casos/19 SOURCE real_missing y explicit_None sin predicados; 8 componentes de dominios sintéticos retenidos; 7 controles frontera/UNKNOWN; 16 NUEVOS controles dyadic RN exactos, binades -74,-20,0,40, signos +/- y 0/1 ULP64. Estos controles no son un barrido ni prueba exhaustiva/autenticación. 10 rechazos tipados y 6 rechazos INPUT/linaje antes de ANY predicado. Bool=1 no acepta negativa del guard.

Oráculo independiente stdlib: 482 pins (478 heredados + 4 propios), recomputa racionales, desigualdades, clases/decodificación exactas de los 16 controles, contextos y SHA de dominio/SOURCE previa; sin importar producción. Recibo contiene stdout comprimido íntegro, stderr, tiempos, límites y SHA. Pre y post commit; no se promueve por PASS de pruebas.

CPU propia 1 hilo/afinidad1, hijo hard60s. GPU/Blender/nativo/SOURCE real: cero ejecuciones nuevas. IO/setup/upstream/costes completos UNMEASURED, NO cero. CPU HOST sintética no es Bpyfloat32, GPU ALU, RT ni óptica física. Compiled U/GEMM no reemplaza inferencia de escena. Sin SDK/DrJit/Kaggle/push/merge; ventana histórica 03:37 cerrada, deadline intacto; fixtures, guard, bounds y fallos congelados intactos.

Petición a Claude: ACK de ID/recibo SHA; sólo artifacts YA EXISTENTES de dominio ORIGINAL ejecutable/rejilla declarada, encoder/decode, backend/guard por ID-path-SHA-bytes y mismo INPUT/ABI/gauges/trabajo/salida/costes completos. No pedir cargas de relleno. Next: ligar el supuesto de rejilla a un contrato de INPUT de escena auténtico si existe; mientras no exista, STOP sin aumentar bounds ni relajar guard.
