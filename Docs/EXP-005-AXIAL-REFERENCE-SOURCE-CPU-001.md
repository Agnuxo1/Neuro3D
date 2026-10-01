# EXP005 — AXIAL-REFERENCE-SOURCE-001 (CPU opt-in)

Base e1ff9867adac55eec71840c550edf174e8433188. Parent UNIT report
SHA 555348ada0093f288e075f8428246ed1a406a7666fd3a8102d3ccb14c1cd1591.
Fallback LOCAL, sin aval JEV; JEV bloqueado sin reintento.

## Contrato acotado

Fuente ORIGINAL de scene_snapshot, source IDs ordenados completos, ABI y
binding SHA, gauge original-source-zero y terminal fixed-original-plane-mode.
Sólo mirror M con phase_rad=0: coeficiente explícito -1; puerto D.
Producto desde ESTA unidad referenciada, no desde Lgeom ni unidad compilada
sustitutiva. No Fresnel general ni óptica física demostrada.

Con A original, A32 suma exacta de limbs, A64 decodificado y U observado:
L1 superior = |A32-A|1 |U|1 + |A64-A32|1 |U|1
+ |A|1 Eunit_ref + Eproducto_RN64. Conserva error encoding distinto de cero;
.1 original tiene error 2^-55. No sumar unidad antigua ni sus gates.
Cap explícito racional no negativo por sourceID; sin default. Audit declara
1e-12, MISMO cap previo source, NO conf1/phase/group/relative. Control cap0
aparte debe fallar con mismas palabras, numerics y cotas, sin relajar umbrales.

Cache matemática exacta: source racional -> cuatro limbs RN32; cuatro limbs
+ unidad reflejada -> ocho nodos RN64. Clave modelo, código y origen SHA.
Nunca reutiliza IDs/binding/gauges, cotas/caps/gates, autorización o costes
hardware. Las palabras/outputs cached no son ejecuciones nuevas.
Reflexión usa dos XOR de bit de signo (incluido cero firmado).
Nuevos cargos/binding se comprueban por fuente. No replay de productores
UNIT/ARG/TREE/geometría/source previos, runners ni shaders.

Un control NUEVO complex ABI (.2,-.15 original binary64) usa unidad numérica
ya retenida: cuatro RN32 HOST modeladas, dos restas exactas residual y ocho
RN64 producto nuevas, costes aparte. No cambia escena ni autoriza GPU.
Controles de modepoint ya retenidos reconstruct binding sin producer replay.

## Alcance y verificación

Ocho tests propios; fail-closed por cap/model/SHA, binding/coverage/gauge,
owner y cache corrupta. Verificador independiente stdlib con RN32 ties-even,
ocho RN64 del nuevo producto y oracle Taylor racional desde M/S/R/lambda
original por fuente. Pin parent y documentos/código; stdout comprimido sin
pérdida de enteros. CPU un hilo, hijos <=60s.

Fixtures conf1/v0/v4/0119/0315/nearestV2, frozen runners/shaders/contracts
y FAILs intactos. Sin reducción, detector, cota coherente/grupal/relativa,
fullpipeline, Bpy/ALU GPU/RT, autenticación de ejecución ni validación física.
Los conteos matemáticos no son benchmark ni costes completos igualtrabajo.
GPU no usada; cola desconocida; sin preflight/reserva/deadline nuevo porque
no hay job. Deadline nocturno histórico cerrado e intacto.

Skills aplicadas: contrato/tests narrow y cache exacta con evidencia factual.
Boards/checkpoint locales SINstage. Sólo estos archivos propios versionables.
Claude: ACK ID/SHA y artifacts efectivos YA existentes de backend/guard
matching scene/limbs/sourceIDs/reference/model/binding, igualtrabajo/salidas
y costes completos. 0337/guard histórico ubicado no acredita esta cadena.

## Evidencia CPU retenida (2026-10-01 17:55 UTC)

Ocho tests PASS, rc0, hijo0.6514688000024762s, stdout85502 bytes SHA
570cd7e553a3c83d48010d96f2a24b3cc9ad7dbde263beee04b9161d917c887e.
139 pins previos + tres propios =142 huellas verificables.
13 casos/14 IDs, seis productos, cinco cases per-source aceptados, sin promoción.
FAILs geom/phase y two_sources relative=false conservados.

Audit: 24 RN32 encoding +12 restas residual y48 RN64 producto cached
NOejecutadas;12 XOR nuevos. Mode-.25:4/2/8 cached NOejecutadas y2XOR;
mode.1cap0 upstream STOP. Negativo cap0: mismas palabras/cargos,
4/2/8 cache +2XOR, FAIL explícito. Control complex nuevo separado:
4RN32 +2restas exactas +8RN64 y2XOR, sin escena/admisión nueva.

Verificador independiente rc0, hijo0.2718037999875378s, código SHA
b41a3330fd54341a5e21352760606bef6dfe2f09698568e5dd9ec8034cb80735:
16 bindings/17IDs (incluye negativo), ocho oracles de campo desde M/S/R/lambda
original, ocho encodings y ocho graphs de cache/origenSHA, cuatro encodings
RN32 y dos residuals exactas NUEVAS, ocho nodos RN64 NUEVOS y18XOR comprobados.
No productor antiguo ejecutado; checks cached por digest/origen, no cargas
de relleno. Report preserva stdout exacto comprimido y script independiente.
La documentación sólo añade esta evidencia; módulo/tests/raw/caps/FAILs no
cambian. Report distingue huellas at-run y documento final. Falta reducción
ESTOS terminales + cotas grupo/power/relativas/native/igualtrabajo/fullcosts.
