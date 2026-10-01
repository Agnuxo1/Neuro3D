# EXP-005 / AXIAL-SOURCE-PRODUCT-HOST-001

Opt-in HOST CPU, base 46e312aa485ad5f60117832da913415582f8b92b.
Acuse UNIT-HOST001 / SHA9391669247fa4b6b3576ac640174f1cd853535c78591d67ae27adc72f19beaba.
Skills cognición/desarrollo: interfaz explícita, cálculo acotado y evidencia reproducible.
JEV bloqueado: fallback LOCAL sin aval remoto ni reintento.

## Interfaz y referencia

Fuente ORIGINAL compleja binary64 de bytes INPUT, stride32words=128bytes,
offset112 del record; dos uint64 little-endian. Mismos IDs, gauges, snapshot
y bindings de escena. No U/GEMM ni fuente unitaria sustitutiva.
Fresh propia escena/ref/quarter/unidad; catorce STOP upstream no reviven,
ni siquiera por amplitud cero. Cuatro corners encoded por cada fuente apta.
Read-only hashes de reportes retenidos; no ejecutar suites/productores anteriores.

Por producto: encoder HOST original64→hi32→residuo EXACTO HOST→lo32 congelado.
Luego dos sumas RN64 modeladas hi+lo (no decodificación gratuita asumida);
cuatro mul y dos add RN64, SIN FMA/reasociación. Cada operación conserva
inputs exactos, word salida y delta RN. Cero exacto canonizado por round64;
ceros firmados ORIGINAL se preservan en input, no promesa IEEE signedzero nativa.
Elegir subnormal/overflow RECHAZA, no FTZ/clamp. Modelo opt-in obligatorio.

Sea s ORIGINAL, sh codificado hi-lo exacto, sd decodificado RN64,
uh unidad representada y u ORIGINAL ideal. Norma L1 compleja.
es=norm1(sh-s), ed=norm1(sd-sh), bu>=norm1(uh-u).
E_RN=sum(abs(delta)) de cuatro mul y dos add del producto.
Entonces:
norm1(producto_RN64-s*u) <=
  es*norm1(uh) + ed*norm1(uh) + norm1(s)*bu + E_RN.
Los cuatro cargos son distintos, no doble cobro de error de unidad ni
referencia sustituida por ORIGINAL redondeado. Usar bu=2*Bphasequarter+max(Eunit)
ya probado en UNIT-HOST001; fase previa/caprad permanecen SIN cambios.
No comparar error L1 del producto contra caprad. No introducir capamplitud,
normalizar fuente, resucitar FAIL, sumar fuentes ni aplicar detector.
El helper primitivo toma bu matemático externo EXPLÍCITO: NO evidencia autenticada.
Wrapper de escena sólo deriva bu de su propia unidad fresh ligada al INPUT.

## Alcance y costes

Se evalúa fuente por unidad de propagación solamente: coeficiente de reflexión,
pérdida/transporte de amplitud, mezcla de caminos, suma de campos, detector,
port y cotas de potencia/relativo pendientes. No fase-del-producto para fuente
oscura; fase de unidad no acredita fase del campo. Todos gates de amplitud,
fullpipeline/admisión/auth/native/GPU/RT/física siguen FALSE.

Por producto: cuatro HOST RN32 casts, dos restas exactas HOST;
dos adds RN64 decode + cuatro mul/dos add RN64 producto=8modelRN64.
Decodes/racionales/copies/SHA/validación/serialización y dependencias fresh
EXTRA. NO costes completos, instrucciones hardware, memoriaVRAM/energía,
velocidad/eficiencia/motor ganador. Guard histórico0337 CERRADO, deadline intacto.
Futuras cargas sólo con nuevo jobdeadline verificable/reserva exclusivaClaude,
gpuq/telemetría/guardfailclosed y TODOS límites del usuario. Esta unidad SIN GPU.
CPU1hilo/hijo<=60s, sin peerwriters/tickets/SDK/DrJit/Kaggle/push/merge.
Core/runners/shaders/conf1/v0/v4/0119/0315/nearestV2/caps/radios/fallos intactos.
Sharedboards locales SINstage. Claude ACKID/SHA + SOLO artifacts YAexistentes
backend/guard matching ESTA ABI/ref/escena/igualtrabajo-output/costes completos.

## Evidencia

Suite nueva única:7tests PASS rc0,0.8044329s; unittest0.526s.
Raw252989bytes SHAbb876c76a4f36ae3fc56ebd419852d753ee9af1f5a011c8e3fa4f3f292acb26e.
17casos19fuentes:5sourceproduct evaluadas/14STOPprevios conservados;
20products corners +6primitivos=26,11rejects primitivos esperados y
tamper sourceword rehashed rechazado. No nuevo capamplitud ni promoción.
Costes nuevos104HOST RN32/52HOSTrestas +52decodeRN64/104mul52add=208RN64.
Scene20products80HOSTRN32/40restas+40decode80mul40add=160RN64.
Fresh dependencias unidad/escena/ref/quarter/cap adicionales, sin costes completos.
Fallo write apply_patch directo preservado en recibo; reparación ONLYshim
apply_patch escalado para archivo autorizado, sin cambios numéricos/umbrales.
Oráculo independiente stdlib sin imports producción y contraste trig ORIGINAL
40términos/restos/anchoPI; resultado se registra en recibo antes cierre.
Oráculo inicial PASS rc0/0.4192352s:207pins (203heredadas+4propias),
208nodosRN64/26products y20contrastes trig contra ORIGINAL verificadas.
Fallo adicional de tamaño del patch de recibo detectado ANTES ejecutarlo;
recibo parcial completado por fragmentos pequeños, mismo raw/SHA, SIN repetir suite.
