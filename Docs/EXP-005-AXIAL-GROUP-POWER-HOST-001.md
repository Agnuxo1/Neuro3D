# EXP-005 / AXIAL-GROUP-POWER-HOST-001

## Contrato opt-in HOST

Modelo `axial-retained-group-power-3RN64-HOST-v1`, unidad absoluta
`ORIGINAL-group-power-absolute` (cuadrado de la amplitud de campo del contrato ORIGINAL).
Consume únicamente casos/variantes de reducción ya retenidos por SHA y planes INPUT de potencia explícitos.
Es |campo complejo|² por grupo, no un detector completo, área/gain/ADC, puerto sumado,
escena continua, GPU ALU, RT ni óptica física. La agrupación sigue siendo hipótesis INPUT.
El campo/espejo/árbol anterior NO se recalculan.

La variante de receipt es obligatoria: missing, explicit_synthetic_INPUT_controls, missing_stage, zero_source.
Se distingue explícitamente el control INPUT sintético de una política autorizada/ejecución real.
El backend verifica todas las huellas heredadas y deriva contexto fresco de los seis buffers INPUT.
Los planes de potencia ligan modelo/unidades/contexto/variante y SHA de los planes INPUT fuente y reducción.
Grupos en orden exacto; todas las fuentes requeridas por el receipt anterior.
STOP/FAIL campo => STOP potencia, mismo motivo/IDs, sin rescatar fuentes válidas parciales.

## Cupos y ausencia

Cada grupo declara field_to_power_cap_abs, power_RN64_cap_abs,
other_power_stages_reserved_abs y relative_power_cap.
Suma de los tres cupos/reservas absolutos <= MISMO límite ORIGINAL power.
El cupo relativo <= MISMO límite ORIGINAL relative_power.
Planes ausentes STOP; no defaults, autosplit, cupos basados en resultados ni outputs caller.
Los repartos cuarto/cuarto/medio son controles INPUT estáticos nuevos, NO política adoptada.
El presupuesto de potencia es separado: NO se interpreta una reserva de field_L1 como potencia.
Las reservas de otras etapas NO prueban esas etapas.
Los cuatro límites field_L1/power/relative_field/relative_power, fase y radios permanecen sin cambios.

## Operaciones y cotas exactas

Para palabras RN64 retenidas r,i:
a=RN64(r*r), b=RN64(i*i), P_hat=RN64(a+b).
Tres nodos, sin FMA/reasociación; palabras y valores racionales exactos en cada traza.
No finitos/overflow REJECT, sin clamp. Squares de +/-0 producen +0.
Subnormales/underflow se contabilizan explícitamente; no FTZ.

B = cota L1 de campo a ORIGINAL ya retenida.
M = max(|r|,|i|).
La desigualdad | |z+delta|²-|z|² | <= 2 M B+B² sigue de
|Re(conj(z)*delta)| <= M ||delta||1 y ||delta||2² <= B².
Cargo propagación = 2MB+B²; cargo nuevo RN = suma errores absolutos de los tres nodos.
Cargo total potencia = propagación+RN, sin doble uso del cap fase como amplitud o potencia.

Denominador ORIGINAL:
P_original >= max(0,M-B)².
Si esa cota es cero, potencia relativa STOP; no epsilon/dividir por observado/cancelación-rescate.
Si es positiva, error relativo <= cargo_total/P_original_lower.
Cada grupo contrasta máximos entre sus esquinas con cupos INPUT abs/rel y límites ORIGINAL intactos.
Cumplimiento sólo parcial de esquinas retenidas. No prueba uniformidad del continuo,
etapas restantes, potencia incoherente entre grupos, coherencia física ni detector completo.

## Evidencia

17 casos/19 fuentes del receipt previo: 4 grupos singleton parcial PASS y 13 grupos STOP;
14 motivos de fuente STOP previos preservados. two_sources other sigue STOP/no cálculo parcial.
16 esquinas elegibles, 48 RN64 de potencia nuevas.
Controles INPUT con cupos absolutos cero y relativo cero siguen FAIL:
8 esquinas/24RN adicionales diagnósticas, no nuevas escenas elegibles.
7 primitivas SINTÉTICAS/21RN: +/-0, subnormal y underflow, magnitud grande,
error de campo no nulo, cota relativa ORIGINAL posiblemente cero y caso no exacto.
Total 93RN64 de potencia NUEVAS, no coste completo (lecturas/hash/bytes/bounds/CPU extra).
31 rechazos esperados de planes/unidades/context/SHA/groups/canonical/overspend/calleroutputs/
selección/variante/wordshape/nonfinite/overflow/bounds.
6 tests nuevos; NO suite/productor numérico anterior. Primera ejecución PASS; ningún fallo nuevo oculto.
Oráculo stdlib SIN imports producción: RN-even entero/Fraction independiente, 237pins,
93 nodos y 124 contrastes exactos extremos de diamante L1 contra ORIGINAL.
Preserva fallos anteriores por herencia de reporte y sus huellas; no modifica evidencia congelada.

## Continuidad

Base 44a5a8e8af2b1b619b145d2f759e10ac52826a60.
Acuse AXIAL-GROUP-REDUCTION-HOST-001 / SHA44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d.
Próxima propia: admisión de variantes sin política sintética/referencia y campo relativos
o cerrar contrato de etapas restantes antes de cualquier promoción; multifuente de escena sigue sin validar.
Claude: ACK ID/SHA; sólo artifacts YA existentes backend/guard matching INPUT/scene/ABI/sourceIDs/gauges,
planes INPUT fuentes/etapas y contrato igualtrabajo/output/costes completos. No repetir RT de relleno.
0337 histórico cerrado/deadline intacto; GPU futura con reserva exclusiva Claude/gpuq/telemetría,
guard fail-closed y NUEVO deadline porjob/límites originales.
CPU1hilo/hijo60s; sin SDK/DrJit/Kaggle/push/merge. Sharedboards locales SINstage.
JEV seguridad BLOCKED: fallback LOCAL sin aval remoto/reintento.
