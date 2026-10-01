# EXP-005 / AXIAL-AMPLITUDE-ALLOCATION-CONTRACT-001

P1 contrato INPUT HOST opt-in, base ba7605b03ce92b46bd01d7f710cca01342776b08.
Acuse SOURCE-PRODUCT-HOST001/SHA04390dac11ab3d7b2a785542bc9b7c94a0f447686b777def0cdeb0a3dceca1b3.
Skills cognición/desarrollo: separar INPUT presupuestos de resultados/gates;
guardar evidencia exacta sin repetir suites/productores/barridos numéricos.
JEV bloqueado: fallback LOCAL sin aval ni reintento.

## Semántica y rechazo

Los INPUT retenidos YA tienen explicit_group_contract.limits.field_L1=[1,10^12],
además de potencia y relativos. No son caps por fuente ni límites de fase.
La asignación de errores a fuente y etapas restantes NO existe en esos INPUT.
Ausencia de asignación devuelve STOP: nunca cero ni reparto automático.

Nuevo INPUT independiente: modelo, units=ORIGINAL-source-field-amplitude-L1,
SHA del contexto fresh del paquete, sources [{source_id,cap_L1}],
groups [{port,coherence_group,remaining_stages_reserved_L1}].
Whitelists estrictas; no valores de unidad/campo/salida/expected_output/gates.
Fracciones canónicas no negativas con ints estrictos, denominator>0/gcd1;
rechazar bool/None/flotantes/negativos/infinito/den0/no canónicos.
Fuentes completas/ordenadas/únicas; reservas para TODAS las parejas port+group
presentes. No duplicados, alias, cambio de ID/gauge/binding/port/group silencioso.
Cada pareja port+group conserva el mismo límite ORIGINAL field_L1:
sum(cap_fuente) + reserva_etapas_restantes <= ORIGINAL field_L1.
No permitir a dos fuentes gastar cada una el cap completo del grupo.
Residuo no asignado reportado por separado; no constituye prueba de etapas restantes.
Misma cota aplicada por grupo, no suma global de grupos incoherentes ni potencia.

La entrada principal SIEMPRE construye contexto fresh desde bytes INPUT/receipts/
snapshot/assignments; no recibe ni acepta contexto caller con cap ampliado.
Checksums atan contenido, NO autenticación escena/coherencia/backend/GPU.
El helper de contabilidad es interno; los contextos son INPUT derivados, no autoridad.
La procedencia de agrupación sigue hipótesis CPU explícita, no física acreditada.
Validar INPUT no compara aún Bproducto real con cupos, no absorbe reflexión/pérdidas,
no demuestra reserva/suma/detector, no gate de amplitud ni fullpipeline.

## Controles y límites

17 INPUT retenidos/19fuentes conservados, todos STOP por asignación ausente.
14 STOP numéricos previos conservados por SHA; en two_sources una asignación
sintética válida NO revive other (fase upstream falla).
4 planes NUEVOS sintéticos explícitos antes checks: positive reparto1/4+reserva3/4;
two_sources cada1/4+reserva1/2; explicit_zero_caps ceroexpreso+reserva1;
synthetic_two_groups second group g2, cada1/4+su reserva3/4.
Sólo este último CONTROL cambia la hipótesis grouping del INPUT copiado y receipts;
bytes ORIGINAL/geom/sources/lambda/ref/caps no cambian. No es evidencia física ni
cambio a fixtures congelados. Los planes sintéticos NO se adoptan como política.
18 planes inválidos:ausencias/cobertura/duplicados/swap/unitsrad/booleano/
racionalno canónico/negativo/den0/binding/output/model/port/group/sobregasto.
7tests PASS rc0/0.2549587s; unittest0.097s; UNA suite nueva.
Raw289542bytes SHA20a83c610d018cdedcd28785be4a199f00daf604228b66a85bd0e0ca48b7e090.
21 llamadas contrato exitosas a nivel API (17STOP+4INPUTvalid),18rejects esperados.
Sin productos RN/trig/rayos nuevos ni replay de productor; coste HOST/SHA/bytes/
Fraction/validación/copias/serialización parcial, NO costes completos/eficiencia.

Oráculo independiente stdlib sin imports producción recompone contexto/bytes,
cupos/cobertura/gauges/binding/sumas/reservas/caps/rechazos y control dosgrupos;
resultado debe registrarse en recibo antes cerrar. No tolerancias nuevas.
Oráculo inicial PASS rc0/0.0773426s;212pins (208heredadas+4propias),
17ausenciasSTOP/4planesINPUTvalid/18planesrechazados/21calls/14STOPnuméricos intactos.
Sin fallos nuevos; UNA suite, no ejecución de productos/rayos/trig ni suites anteriores.

CPU1hilo/hijo<=60s; sin GPU/Blender/ALU/Bpy/native/RT/física/auth/admisión/SDK/
DrJit/push/merge/peerwriters/tickets. Core/shaders/runners/conf1/v0/v4/0119/0315/
nearestV2/radios/caps/fallos intactos. Guard0337 histórico CERRADO/deadline intacto.
Futurojob requiere exclusividadClaude/gpuq/telemetría/guardfailclosed/NUEVOdeadline
verificable/todos límites usuario. Sharedboards locales SINstage.
Claude ACKID/SHA + sólo asignaciones INPUT/artifacts backend/guard YAexistentes
para ESTA ABI/ref/escena/igualtrabajo-output/costescompletos, no nuevas cargasrelleno.
Próximo propio: probar Bproducto contra asignación explícita y coeficientes
completos con errores separados; ausencia STOP, no elegir política por salida.
