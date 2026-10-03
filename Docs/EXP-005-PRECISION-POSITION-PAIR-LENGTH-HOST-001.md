# PRECISION-POSITION-PAIR-LENGTH-HOST-001

Opt-in precision-position-pair-length-HOST-v1, API audit(model,request).
Codex capacity_audit/EXP005; base a4e22fdb0e4dea51680eb101b2054fad7c07bfa2.
JEV SECURITY_BLOCKED_NO_RETRY; fallback LOCAL sin aval remoto.

## Alcance y entradas

Padre RECENTER001, recibo
coordinacion/respuestas/PRECISION-POSITION-PAIR-RECENTER-NATIVE-CPU-001-CODEX.json,
SHA12ea3f705ab4397de8057854dc1ba11bfd6fa2f704bb68492f2c29e77d9a7944/90899bytes.
Se leen capturas verificadas/pins/oráculo, NO se ejecuta el productor,
restas nativas, encoder, Blender, GPU ni suites antiguas.

Veinte registros cerrados: ocho pares HILO admitidos, cuatro SINGLE con
hueco perdido y ocho contactos S0/S1 STOP. No permutaciones/barridos nuevos.
Selector siete strings: record_id,parent_receipt_sha256,
parent_record_sha256,original_geometry_sha256,relative_geometry_sha256,
representation,intent. Modelo e intent explícitos.
Representación EXACT_HOST_PAIR_WORDS_RATIONAL_ROOT_INTERVAL_96BITS.
Intent LENGTH_AND_SAME_GEOMETRY_END_REFERENCE_ONLY.

ALL15 coordenadas ordenadas únicas -> palabras binary64 LE normal/cero ->
suma EXACTA HOST de hi+lo -> cotejo ORIGINAL punto-source_origin antes
de cualquier norma. No sumar hi+lo mediante scalarRN64. La metrología HOST
racional NO implementa norma nativa/GPU ni sustituye inferencia desde escena.
Palabras subnormales/no finitas/malformed o desacuerdo ORIGINAL: STOP.
Dominio racional de limbs128bits/magnitud<=1e6; no aumentar bounds antiguos.
El contexto conserva ORIGINAL, frame_origin y geometry SHA.
No trasladar el origen óptico/reference/gauge silenciosamente.

## Longitud y referencia espacial

Se mide desde source_origin hasta end y cada uno de tres vértices:
s=sum(delta[k]^2), L=sqrt(s) en BU.
Solo root_bracket puro propio congelado de
Blender/benchmarks/capacity_audit/oblique_common_detector_length_CPU_v1.py,
SHAf510517d0c91c45e9ebaadfe593a4c8116e4587bb3eb4d06be7a0ab651079c49.
BITS=96 INTACTO. No importar su fixture/audit/nearest ni invocar productores.
k=isqrt(floor(s*2^192)); lo=k/2^96;
hi=lo si lo^2=s, en otro caso (k+1)/2^96.
Prueba lo>=0,lo^2<=s<=hi^2,hi-lo<=2^-96,retícula fija.

Referencia ESPACIAL explícita R=L(source,end) de esa misma geometría.
Para vértices, [Llo-Rhi,Lhi-Rlo], sin asumir correlación/cancelación.
La identidad de end consigo mismo da [0,0] exactamente; no restar dos
intervalos como si fueran variables independientes idénticas.
No lambda, fase, ALLSOURCE, referencia óptica ni suma coherente certificadas.
Estas longitudes a vértices NO son paths renderizados/reflejados ni hits.
Se conserva cada registro/source_context por separado; no mezcla S0/S1.

## Límite preservado

Tres casos representativos xy/xz/yz outside_2m60 tienen un vértice con
s=4+2^-120; el hueco posicional 2^-60 permanece en los limbs.
L>2 matemáticamente, pero bracket96=[2,2+2^-96].
La extensión L-2 está estrictamente entre0 y2^-122
porque (2+2^-122)^2>4+2^-120.
No se certifica positividad con lower=0 del intervalo; test/recibo guardan
UNRESOLVED_EXTENSION_AT_FIXED96BITS. NO incrementar BITS/caps para PASS.
Tilted tiene otra métrica; no generalizar este control a los cuatro planos.
Control tiny sqrt(2^-240)=2^-120 también produce [0,2^-96].
La resolución posicional NO garantiza presupuesto de longitud/fase.

## Verificación y costes

Cinco grupos,31main=8 HOST_PAIR_LENGTH_ENCLOSURE_ONLY/23STOP
(12padres+11selector/model),8 mutaciones internas STOP antes raíces:
última palabra inválida/Inf/subnormal/desacuerdo ORIGINAL,
coordenada duplicada,exactitud falsa,contexto/geometry alterados.
Cinco helpers raíz separados;API pública y recibo ausente aparte.
Suite propia1hilo/afinidad1/hijo60s,GPU0,1.5758896000334062s,
raw172379bytes<2MiB/SHAab1e6d6d6b4da0752780f906b3549975402297d44111d1ddc73b58e917428194.
Captura íntegra, sin deduplicación ni fallos numéricos ocultos.

Oráculo independiente SIN importar core/isqrt/root helper:
decodifica IEEE64 por campos; ALL120 coordenadas contra ORIGINAL;
32 normas desde coordenadas world y pruebas de cuadrados/retícula minimal;
32 diferencias con identidad end,3 límites tangenciales y5 raíces control;
pins/selector/censo/flags/ASTno producer. Conserva contrastes/fallos ancestrales.
Ledger principal PARCIAL:240 palabras HOST,120 sumas exactas,32 normas,
32 root_bracket,48 restas de referencia (24 intervalos),8 identidades end.
Auxiliares/API pública/mutaciones separados. Internals racionales/isqrt,
validación/SHA/I/O/setup/upstream/memoria/energía UNKNOWN_NOT_ZERO.
Ni tiempo de suite ni cuentas parciales prueban eficiencia/ganadorRT.
RT16Mvs1M/salidas distintas/cruce extrapolado NO igual trabajo ni redRT.

Flags native/GPU/scene/uncertainty/fullvisibility/opticalreference/phase/
physical False; field/amplitude/powerNone; promociónSTOP.
CPU nativa del padre es histórica, no replay; nueva etapa HOST exacta.
No autointersección nueva/visibilidad completa/material/fase/campo claim.
Fixturesconf1/v0/v4/0119/0315/nearestV2/runners/shaders/contracts intactos.
Solo own4 versionados;sharedboards/checkpoint locales SINstage.
Solicitar Claude ACK ID+SHA y SOLO artifacts YA existentes backend/guard,
ingress-fence-readback/material-amplitud-completitud/igualtrabajo-costes
ID/path/SHA/bytes. No cargas de relleno ni ACK inventado.
