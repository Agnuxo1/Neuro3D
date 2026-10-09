# EXP005 — longitud condicional desde cajas de posición propagadas

ID `PRECISION-ORIGINAL-SOURCE-NEXT-CHORD-LENGTH-CPU-001`, Codex, P1. Padre local
`1a21ffe52730fc68c58ef2436aefcaf444ca007e`. Modelo opt-in
`original-SOURCE-next-chord-length-CPU-v1`.

## Alcance obtenido

28 normas nuevas para 12 SOURCE originales desde las cajas P y Q modeladas del
recibo de posición siguiente. Q incluye incertidumbre de dirección/parámetro
y el grafo binary64 multiplicación-suma sin FMA, no sólo un endpoint ideal.
Cada nueva norma produce intervalo de desplazamiento BU, cuadrado BU² y longitud
BU con 2 certificados de raíz enteros. SOURCE permanecen separadas.

Se preservan 12 interiores condicionales, 12 contactos STOP y 4 MISS. Todos los
12 ledgers siguen STOP y firstID null. Los resultados para contacto/MISS son
diagnósticos algebraicos, no pasos de camino admitidos. No se recalculan
triángulos/contactos/posiciones viejos ni se trasplantan cotas ideales de norma
o fase. Son raíces NUEVAS de cotas propagadas, no replay de raíces previas.

## Contrato numérico y permisos

`enclose(P, Q, model=...)` recibe 2 cajas tridimensionales con extremos
racionales canónicos `[n,d]`, enteros estrictos, d>0, máximo128bits y magnitud
<=1e6 por extremo, orden cerrado. Por eje: `[Qlo-Phi, Qhi-Plo]`, mínimo cuadrado
cero si cruza cero y máximo de ambos cuadrados; se suman los 3 intervalos.
Se pierde correlación P/Q conservadoramente: no se presume contacto exacto
cuando dos cajas inciertas iguales admiten diferencias no nulas.

Se reutiliza sólo aritmética pura de
`oblique_trace_endpoint_length_enclosure_HOST_v1.py`, SHA
`8f3b77dba20a755754f1c0da4bc9b779d35056a02240b6602d0c7d1d34d330e8`.
Sus límites congelados siguen128bits de entrada, 512bits para la racional
cuadrada, cuadrado <=2^64 y BITS=96. No se llama a productores/evaluate/run
antiguos. Para q>=0: k=floor(sqrt(q)*2^96), certificado por
`k²*d <= n*2^192 < (k+1)²*d`; raíz inferior k/2^96 y superior igual si exacta,
o (k+1)/2^96. El límite inferior de longitud usa la raíz inferior del cuadrado
mínimo; el superior, raíz superior del cuadrado máximo.

Esto es norma HOST racional exacta de cajas de endpoints modelados, NO modelo
de instrucciones nativas de longitud. El parámetro no normalizado tau nunca
se equipara con longitud. No se conoce error frente al camino físico/nativo.
`native_length_error_bound`, `length_reference_phase_bound`, `phase_error_bound`
son null. Precisión nativa, budget de longitud, nearest, exclusión, visibilidad
completa, fase y lanzamiento GPU false; costes completos UNKNOWN, no cero.

`compose` exige contrato de posición, clasificación retenida, identidad S0/S1,
IDs primitivos estrictos, STOP de ledger sin firstID/ignorados/offset y todos
los permisos previos false. Es caller-condicional: padre null.
`run` coteja SHA del recibo fijo y sus fuentes capturadas, capture rc/deadline,
bytes/SHA/zlib cerrado y 28 identidades únicas, y sólo entonces adjunta padre.
La identidad de contenido no autentica escena ni ABI/ingress nativos.

## Pruebas y límites conservados

4 tests PASS, 64 registros: 28 normas fijas, 8 controles nuevos, 1 aislamiento
caller, 17 NEG de promoción/identidad y 10 NEG de entradas/capacidad.
37 normas nuevas y 74 certificados de raíz, no cómputo gratuito.
Se comprueban1792 combinaciones de esquinas fijas +512controles +64caller:
incluyen duplicados singleton, no muestras únicas ni medida de velocidad.

Controles: desplazamiento (6,8,0) norma10 (no tau2), mismo contacto incierto
P=Q con hull [0,2], cruce por cero, coordenadas negativas, hueco2^-60,
norma2^-97 que conserva intervalo [0,2^-96] por resolución fija, bit bajo de
posición 2^-53 y cajas parcialmente solapadas. No se elevan BITS ni capacidades
para estrechar cotas y convertirlas en PASS. 2^-149 se rechaza por128bits;
suma cuadrada de fracciones independientes que excede512bits se rechaza con
`root_capacity`. Fallos del padre, 72 errores escalares y 16 filas anteriores
permanecen en recibos históricos intactos.

Suite: stdout124567bytes/SHA
`86713289978f38258d1914d6d788962c10c972b0636b4e1be9d2e3bd451ca05a`.
CPU propio1hilo, RAM libre9843597312bytes antes de presupuesto128MiB,
timeout30s/deadlineUTC nuevo35s, rc0 dentro del plazo. QA no benchmark.
461 pins congelados cotejados intactos; fuentes y captura completas en recibo.

Oráculo independiente sin importar helpers/suites/productores: verifica36 filas
capturadas (28fijas+8controles),72certificados enteros de raíz,2304combinaciones
de esquinas,28bindings/12SOURCE,12intervalos positivos con ancho no cero y los
12STOP. Verifica27NEG, los límites96/128/512bits sin elevación,2snapshots de
fuentes y461pins. El caller/2raíces/64corners adicional está en QA, no en el
censo del oráculo. stdout477bytes/SHA
`7e817017206d414773408accc9f5f3b0bc384259b106ec0e13a0e6fe5c9c24f1`.

## Siguiente y coordinación

Componer referencia/longitud de onda y ciclos de fase sólo con presupuestos
explícitos ligados a SOURCE/escena; no transportar silenciosamente cotas ideales.
Esta unidad no tiene presupuesto de fase ni determina un camino. Claude: ACK
ID+SHA y SOLO artifacts EXISTENTES originalSOURCE/ABI-ingress, error nativo
punto-dirección, previous-instancia y credencial origen/exclusión, ALLcoverage,
referencia/lambda/material, guard exclusivo por job/deadline y contrato de igual
trabajo/costes completos; o faltantes precisos M03/M04/M05/M08/M13.

No GPU/Blender/RT/SDK/push/merge. No se afirma GPU libre/ocupada sin telemetría;
no carga solicitada. Shared4/checkpoint SINstage; versionar sólo4own revisados.
JEV bloqueado por seguridad: LOCAL sin aval remoto ni reintento.
