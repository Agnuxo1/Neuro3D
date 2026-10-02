# EXP005 — Reflexión exacta HOST del espejo ORIGINAL de fase cero

ID AXIAL-MIRROR-ZERO-HOST-001. Base8f32dcb90be75f8eb3494fe7b181f2a7dfeb8f46.
Opt-in CPU stdlib; no cambia ningún contrato/runner/shader/fixture congelado.

## Modelo ligado a escena

Modelo ideal existente: mirror = -exp(i*phase_rad). Este módulo SOLO admite
phase ORIGINAL binary64 exactamente +0 o -0, por bits, no por redondeo float32.
Entonces el coeficiente complejo ORIGINAL es [-1,0] exacto.
No cubre fases no cero, Fresnel/transmisión/divisores/atenuación general ni óptica física.

La entrada pública selecciona casos propios retenidos y planes INPUT completos/None.
Verifica SHA del gate anterior y 218 pins heredados, receipts stdout y bytes INPUT.
Un producto eligible exige recibo previo de eventos ligado al MISMO paquete/escena/ABI/sourceorder:
M owner0 primero, D owner1 segundo, salida del espejo derivada del primer evento,
fuente y recibo exactos. No acepta evento ni coeficiente externo.
Datos originales M/D y fase se leen del INPUT original_scene_json autenticado por receipt SHA
(NO autenticación física/de ejecución); no se inventa buffer nativo de materiales.

## Implementación y cota

Por cada producto complejo finito binary64 retenido, XOR bit63 a ambas componentes.
Incluye ceros con signo y subnormales sin FTZ; NaN/inf/bool/rango inválido rechazan.
No mul/add/RN nuevo: negación exacta p->-p.
L1(-p - (-ideal)) = L1(p-ideal), por lo que cargos sourceencoding/decode/unit/product
y cota ORIGINAL anterior permanecen exactos. Coeficiente y negación añaden error L1 cero.
No se utiliza cap de fase como presupuesto de campo, ni se ensancha ningún cap.

17 casos/19fuentes:5productos-source eligible (4corners cada uno),14STOPprevios intactos.
MissingINPUT continúa STOP; reservas contables NO prueban etapas posteriores.
Planes sintéticos previos positive/two_sources/zero se reutilizan sin derivarlos de las salidas.
positive partialPASS; primera fuente two_sources partialPASS pero otherSTOP/casoNOpromovido;
cupo cero INPUTválido mantiene FAIL porque Bproducto no cero, incluso tras reflexión exacta.

6 tests nuevos + oráculo stdlib sin imports producción. Rechazos fase ORIGINAL diminuta no cero,
menor subnormal64, fase general, bool/missing, owner/admisión/departure swap,
inyección de coeff/evento/contexto; controles signedzero/subnormal/extremos.
Los controles nuevos NO son una ampliación del perfil/caps ni nuevos fixtures adoptados.

## Alcance y costes

Sólo reflejos de productos retenidos HOST. No suma campos, detector,
prueba restante de transporte/árbol completo, gate completo de amplitud ni admisión GPU.
No oldproducer/test/trig/geometría/producto recomputado; no native/ALU/Bpy/GPU/RT.
Dos XOR HOST por corner; hash/descompresión/verificación INPUT/gate son coste EXTRA,
no costes completos, tiempo nativo, energía, eficiencia ni motor ganador.
amplitude_budget_accepted/remaining_stages_error_proved/accepted_full_field_pipeline FALSE.
Skills cognición/desarrollo: reutilizar evidencia por SHA y aislar subperfil exacto sin alterar frozen.
JEV bloqueado, fallback LOCAL sin aval remoto/reintento. Boards locales SINstage.
