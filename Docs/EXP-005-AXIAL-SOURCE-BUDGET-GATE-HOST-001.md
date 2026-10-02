# EXP005 — Gate parcial de presupuesto de producto por fuente (HOST)

ID: AXIAL-SOURCE-BUDGET-GATE-HOST-001. Base: 97dfe93867e0ea95be0b1a272d176384b94bdc71.

Opt-in CPU stdlib: usa exclusivamente recibos propios retenidos y fijados por SHA.
No ejecuta productores numéricos, suites antiguas, geometría, trigonometría, Blender ni GPU.
JEV bloqueado por seguridad: fallback LOCAL identificado, sin aval remoto ni reintento.

## Contrato

Entrada pública: selección explícita de casos retenidos, mapa completo de planes INPUT o None,
modelo explícito. No acepta contexto, producto, cap, unidades ni resultado numérico externos.
Verifica cadena de 213 pins heredados y recibos stdout; deriva contexto fresco desde bytes INPUT.
Identidad escena/ABI/paquete/fuentes/gauges deben coincidir con evidencia numérica retenida.
Un plan ligado al control sintético two_groups no se admite sobre el paquete original two_sources.

El contrato INPUT anterior conserva EXACTO field_L1 ORIGINAL por port/coherence_group:
suma de cupos de fuentes + reserva explícita de restantes etapas <= cap original del grupo.
No autosplit, falta!=0, no cap fase/potencia/relativo como sustituto L1.

Para fuente numéricamente evaluada y reparto válido:
B_producto_retenido <= cupo_fuente_INPUT.
Comparación racional exacta. Cargos originales separados encoding/decode/unidad/producto intactos.
La cota es del producto desnudo amplitud por unidad de propagación; NO camino completo.
Los STOP numéricos previos tienen precedencia incluso ante plan válido o amplitud/cupo cero.
Aceptación agregada parcial sólo si TODAS las fuentes del grupo/caso cumplen.

## Controles, no política adoptada

17 casos/19 fuentes sin reparto: 14 STOP numéricos anteriores conservados y 5 STOP por INPUT ausente.
Se reutilizan tres planes sintéticos anteriores sin derivarlos de las salidas:
positive 1/4+reserva3/4; two_sources 2*1/4+reserva1/2; positive cupo0+reserva1.
positive y primera fuente two_sources caben en su cupo parcial.
other sigue STOP; caso/grupo two_sources NO promovido.
Cupo0 es contabilidad INPUT válida pero error no nulo del producto produce FAIL.
Cap fase0 de positive NO se cambia ni se confunde con el cupo L1.

6 tests y oráculo independiente sin imports producción: SHA/bytes/contexto/cobertura/gauges,
sumas/reservas/comparaciones/casos negativos/14STOP. No resweep numérico.
La suite se captura una vez; errores de infraestructura se conservan en reporte.

## Límites

accepted_retained_bare_source_product_budget_CPU_only describe SÓLO comprobación parcial retenida.
amplitude_budget_accepted y accepted_full_field_pipeline siempre FALSE.
Reservar coste L1 NO prueba el error de coeficiente/reflexión/atenuación/transporte completo,
suma de campos, detector ni resto de etapas. No autenticación de ejecución/coherencia física.
Sin native/ALU/GPU/RT/óptica física; no admisión GPU ni costes completos/energía/eficiencia.
Sólo lecturas/hash/descompresión/contrato INPUT y comparaciones rational CPU; sin reejecución numérica.
Runners/shaders/fixtures/caps/radios/fallos congelados intactos; boards locales sin stage.
Skills cognición/desarrollo separan evidencia reutilizada, contrato INPUT y alcance del gate.
