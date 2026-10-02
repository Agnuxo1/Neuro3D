# EXP-005 / AXIAL-GROUP-REDUCTION-HOST-001

## Alcance opt-in

Modelo `axial-retained-corner-group-reduction-RN64-HOST-v1`.
Sólo CPU HOST, productos reflejados de esquinas codificadas ya retenidos, mirror ORIGINAL +/-0 y árbol retenido exacto.
No ejecuta productores numéricos anteriores, shaders, Blender, GPU, RT ni óptica física.
No prueba el continuo de una escena ni un detector completo: los datos son esquinas discretas retenidas.
La agrupación y las referencias de fase son hipótesis INPUT, no autenticación de coherencia física.

## Entrada y presupuesto

La API acepta únicamente nombres de casos retenidos y dos mapas completos de planes INPUT explícitos (o None).
Contexto derivado de los seis buffers originales; paquetes, escena, ABI, IDs ordenados y referencias deben coincidir
con productos/espejo/árbol por SHA. Ningún producto, aceptación o contexto aportado por un caller es admisión.
Planes nuevos de etapa: modelo, unidades L1 de amplitud ORIGINAL, context_sha256,
source_allocation_sha256 y grupos ordenados (port, coherence_group).
Cada grupo declara reduction_cap_L1 y other_stages_reserved_L1:
reduction_cap + other_reserved <= remaining_stages_reserved del plan de fuentes ya validado.
La reserva no es error probado; ausencia no equivale a cero y ninguna etapa adopta automáticamente una fracción.
Los repartos cuarto/cero usados por tests son nuevos controles INPUT sintéticos, no política aplicada a ejecución real.
No se altera field_L1, fase, potencia, relativos, radios, fixtures o STOP anteriores.

Un grupo necesita TODAS las fuentes: una fuente STOP/FAIL impide calcular/aceptar el grupo parcial.
Terminal_reference_id = common_terminal_reference_id en todas, mismo gauge y rebase_cycles explícito [0,1].
No se implementa rotación/rebase silencioso.
Enumeración cartesiana acotada: cuatro esquinas por fuente y máximo cuatro fuentes por grupo.
Es un límite nuevo de este backend, no ampliación de escena/ABI anterior.

## Aritmética y cota

Orden INPUT fijo, acumulador inicial = primera fuente (identidad bit a bit, sin suma con cero inicial).
Cada fuente adicional: dos sumas RN-even binary64, una por componente, sin reasociación ni FMA.
Cada nodo guarda palabras operandos/salida, suma racional exacta y error de redondeo absoluto.
No FTZ; ceros con signo, subnormales y overflow tienen tratamiento explícito.
Overflow/no finitos => REJECT, nunca clamp.
RN exacto cero da -0 únicamente si ambos operandos son -0; en cancelación da +0.

B_RN = máximo, entre combinaciones de esquinas, de suma de los cargos L1 de los nodos.
B_grupo = suma de B_fuente (hacia ORIGINAL) + B_RN.
Aceptación PARCIAL sólo si B_RN <= cupo explícito de reducción y B_grupo <= MISMO field_L1 ORIGINAL.
L1 admite suma por desigualdad triangular incluso cuando los valores cancelan; no inferir precisión relativa por ello.
Los otros cargos permanecen reservados/no probados.
No suma incoherente entre grupos, potencia, detector, autorización, costes completos o pipeline completo.
El primitivo reduce_words demuestra bits/arimética; nunca acepta evidencia de escena suministrada por caller.

## Verificación y fallos preservados

Tests propios: 17 casos/19 fuentes, 14 STOP numéricos conservados.
Cuatro grupos singleton pasan parcialmente, 16 esquinas/0 sumas RN nuevas de escena; 13 grupos STOP.
two_sources conserva other STOP y no produce suma parcial; cupo fuente cero permanece FAIL; ausencia de etapa STOP.
Siete controles primitivos sintéticos, 14 sumas RN: cancelación grande, empates par/impar,
ceros con signo, subnormales y singleton. NO multifuente desde escena validado.
24 rechazos previstos: stage whitelist/context/units/groups/canonical rationals/reserve overspend,
caller outputs, selección, ausencia allocation, NaN/inf/bool/overflow/empty.
Oráculo independiente stdlib sin imports de producción: RN-even mediante enteros y Fraction, no float/struct.
Relee y contrasta receipts, planes/cupos, fuentes/grupos/STOP, esquinas, trazas y cotas.

Primer suite intentó leer contexto de árboles STOP y dio KeyError/0 tests.
Reparación exclusivamente de manejo de fila STOP sin contexto, exige flag árbol FALSE y mismo packet SHA;
no se relajaron gates/cupos, no se ocultó fallo. Captura inicial preservada en JSON.
Fallo de creación read-only y error de wrapper Python antes de suite también registrados.
Suite exit0 posterior y oráculos inicial/final/postcommit quedan documentados en el reporte.
Los runners/shaders/contratos antiguos permanecen intactos; sharedboards locales SINstage.

## Continuidad

Base 04a5285c1b416b5ac700af7a0b9b630f9e6e7fd3.
Acuse AXIAL-TREE-LINEAGE-HOST-001 / SHA e9ad9731436da1f75724354e8e6fb4fae9ed043d936a01a0752dc936abce7ae6.
Siguiente propia: detector con cargos explícitos y límites originales; falta una prueba multifuente desde escena.
Claude: ACK ID/SHA y sólo artifacts YA existentes backend/guard matching INPUT/escena/ABI/fuentes/gauges,
planes INPUT fuente/etapa y contrato igualtrabajo/output/costes completos; no cargas RT/benchmark de relleno.
0337 histórico cerrado, deadline intacto. GPU futura requiere reserva Claude, gpuq, telemetría,
guard fail-closed y nuevo deadline por trabajo con todos los límites.
JEV bloqueado por seguridad: fallback LOCAL explícito, sin aval remoto/reintento.
