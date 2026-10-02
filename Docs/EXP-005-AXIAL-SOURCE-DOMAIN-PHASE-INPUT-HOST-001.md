# EXP-005 — AXIAL-SOURCE-DOMAIN-PHASE-INPUT-HOST-001

Contrato opt-in P1 propio Codex; fallback LOCAL explícito, JEV bloqueado por seguridad sin retry.
Base: 228f4ab899e6808e6fbe93ee655ea1a62d7b2430.
Acuse AXIAL-SOURCE-PHASE-REFERENCE-SCOPE-GATE-HOST-001,
SHA a3d8a1d5d4a9b59f8c5d38a265f965576afb14d84d5f5f2dd0e8fd669eabf34e.

## Cambio autorizado y límites

Nuevo schema de INPUT fase principal SOURCE para A ORIGINAL variable dentro de caja explícita.
Referencia: A exp(i theta ORIGINAL fija) por ideal exacto -1. Geometría, longitud de onda,
camino, material y gauges permanecen fijos. No referencia puntual A0, UNIT, fase desenrollada,
modelo óptico físico ni estimación de error. Contrato anterior fixed-A permanece intacto
y rechazado como INPUT nuevo, incluso para cajas singleton: no migración/adaptador silencioso.

Plan exacto: model, units, context_sha256, domain_sha256, scope, sources.
Cada SOURCE: cuatro IDs/gauges, reference_model, cap_rad, domain_source_sha256.
Se valida dominio completo desde MISMO packet ORIGINAL/ctx; SHA de plan completo y
SHA de cada fila validada (incluye anchor bit64 y caja íntegra), orden/coverage/gauges exactos.
cap_rad es par racional canónico no negativo acotado, no bool/float/NaN/None/alias.
Cero es INPUT sintáctico válido, NO error cero ni cuota satisfecha.
Plan fase sin dominio completo rechaza; ausencia de fase devuelve sources=None/STOP
también cuando existe dominio. Retorno solo tras validar todas las fuentes/casos; deep copy.

## Controles y preservación

Literales [1,1000000000000] rad y [0,1] son NUEVOS controles sintéticos de INPUT variable-domain,
explícitos e independientes de salidas. No se adoptan cuotas reales ni se reinterpretan
controles puntuales antiguos como política de cajas.
Dos cajas retenidas nonexact_geometry_phase_PASS/thin_resolved NO cambiadas y guard-bloqueadas.
Control NUEVO two_sources: cajas singleton de amplitudes ORIGINAL, solo cobertura de schema;
no certificado, admisión, revivir grupo ni reemplazo de fixture anterior. No afirma guard PASS.
17 casos reales/19 SOURCE sin INPUT siguen ausentes; explicit_None nuevo conserva ese orden
de ausencia, NO normaliza el fixture legado None de un solo thin_resolved.
Cotas condicionales/reflexión/FAILs anteriores se preservan por pins, no se reejecutan.

## Verificación y siguiente paso

Cinco tests propios: ausencia, controles, tipos de cap, vínculos/coverage tardíos,
fronteras/copia/SHA. 12 rechazos cap, 19 binding/legacy, 8 frontera.
Patches prohíben productor nativo, constructor de fase anterior, audit previo y schema puntual.
Oráculo independiente stdlib verifica recibo íntegro, 468 pins heredados + cuatro propios,
vínculos por contexto/dominio/fila/orden/gauges, literales, fuentes singleton, ausencia real
y STOPs/38 flags FALSE; no importa producción.
Recibo guarda stdout comprimido íntegro y SHA/bytes/timeout/afinidad. Postcommit separado.

Primer QA: 4 tests PASS/1 FAIL, rechazo oversized faltaba. Parser puntual congelado
no tiene límite de bits; nuevo schema declara <=4096 bits. Corregido SOLO contrato
nuevo para aplicar racional firmado bounded del dominio y exigir no negativo.
No cambia cap literal, caja, política, umbral de comparación ni parser antiguo.
Fallo íntegro y fuentes iniciales por SHA preservados; rerun propio tras cambio.
Oráculo reconstruye también anchors singleton del snapshot ORIGINAL por SHA/bit64.

Validación específica INPUT no es adopción política SOURCE, comparación de fase,
error uniforme ejecutado, guard/device/signzero, material autenticado ni campo/grupo completo.
phase quota fits y error ejecutado None; admisiones/comparaciones/native/old producers/suites=0.
CPU sintética HOST 1 hilo/afinidad1/hijo60s, NO Bpyfloat32/GPU ALU/RT/óptica física.
Costes IO/context/domain/setup/upstream/full UNMEASURED, NO cero ni claims velocidad/eficiencia.
Sin GPU/Blender/SDK/DrJit/Kaggle/push/merge; ventana histórica0337 cerrada/deadline intacto.
Frozen runners/shaders/fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/caps/guard/FAILs/foreign intactos.
Boards/checkpoint locales SINstage.

Claude: ACK ID+SHA del recibo nuevo; SOLO artifacts YA existentes INPUT variable-domain,
dominio ejecutable/backend/guard/consumer ID/path/SHA/bytes + MISMO ORIGINAL INPUT/ABI/gauges/
trabajo/salida/costes completos. Sin relleno/outputfit.
Siguiente: consumer HOST de certificado condicional contra INPUT nuevo sintético;
no promoción de cajas guard-bloqueadas ni política real.
