# AXIAL-GROUP-RELATIVE-HOST-001 — límites ORIGINAL en esquinas HOST

P1 Codex capacity_audit/EXP005. Base 7eae7d24ac5b4ba17c9909e62dcfd62b782ea631.
Fallback LOCAL explícito: JEV bloqueado por seguridad, sin reintento ni aval remoto.

## Contrato opt-in y referencia

El contrato congelado axial_relative_gate_cpu_v1 define campo complejo relativo por norma
L1, denominador del campo ideal ORIGINAL. No cambiamos norma a L2/inf ni usamos
el valor observado como denominador. Para palabras HOST finitas z y cota retenida B:

- n = abs(Re z) + abs(Im z), calculado exactamente como racional.
- lower = max(0, n - B) por desigualdad triangular inversa.
- error relativo <= B / lower si lower > 0; STOP si lower = 0, sin epsilon.
- Comparación contra el MISMO relative_field del INPUT ORIGINAL.

Modelo explícito axial-retained-corner-relative-L1-ORIGINAL-HOST-v1.
La API de escena sólo admite nombres de casos retenidos, variante y modelo: ningún
campo, cota, nuevo cupo o resultado del caller. Las primitivas sintéticas no autorizan escenas.
Los seis buffers INPUT, ABI, snapshot, IDs, orden completo, grupos y gauges se vuelven
a enlazar a los recibos de campo y potencia por SHA. No se ejecuta otro productor numérico.

## Composición limitada

accepted_retained_corner_field_power_limits_CPU_only sólo es true cuando pasan
campo absoluto, campo relativo ORIGINAL y los dos gates de potencia retenidos.
No se inventa un nuevo presupuesto relativo ni se transforma reserve en proof.
Una ausencia de plan de potencia continúa STOP aunque el nuevo relativo campo pase;
los cupos potencia absoluta/relativa cero siguen FAIL con su razón original.
Una fuente bloqueada impide el grupo; no suma parcial ni rescate two_sources/other.

Esto certifica únicamente los puntos codificados de las esquinas HOST retenidas,
no todos los puntos del intervalo, transporte continuo, kernel nativo, detector completo,
autenticación de ejecución/coherencia o cierre de otras etapas. Las asignaciones/políticas
INPUT sintéticas previas no se adoptan como política de escena. Todos los flags full
pipeline, remaining stages proved, detector, native, GPU y autenticación permanecen false.

## Evidencia reproducible y costes

Una única suite nueva (no replay de suites numéricas anteriores): seis tests PASS.
17 casos / 19 fuentes, cuatro grupos singleton partial PASS, 13 STOP de grupo y 14 STOP
de fuente preservados. 16 comparaciones relativas en la variante explícita y 16 sin
plan de potencia, más ocho diagnósticas: 40 comprobaciones de denominador.
Nueve primitivas sintéticas incluyen L1 vs L2, igualdad del cupo, cap insuficiente,
referencia cero/cancelación representada, signed zero y subnormal con referencia positiva.
245 comprobaciones racionales de referencia diamante L1; 22 rechazos previstos.
Nuevas operaciones RN/producto/reducción/potencia/trig/ray-tracing: cero.

Suite propia 0.6640439000038896 s (unittest 0.500 s), raw 173050 bytes:
SHA da474a7d6c161f9a138a598784568267fad0f7b84f2eaea0bc944b4e8907287c.
El oráculo nuevo no importa producción, verifica 242 pins y recalcula sólo los
cocientes racionales/bindings/rechazos; el transcript comprimido se almacena sin
repetir la suite. CPU stdlib, un hilo / hijo con timeout duro de 60 s.
Los tiempos incluyen el nuevo trabajo HOST y lecturas/hash; NO costes completos
del backend, inferencia de escena, equivalencia 16M/1M, RT, eficiencia o física óptica.

## Procedencia y siguiente unidad

Acuse POWER-HOST-001, reporte SHA
d6510bb52617324272bc47b45b2b2c09ecc4578e865b06f0fc1d332a51998763.
Campo REDUCTION-HOST-001 SHA
44e1af7a17f3fdb9577d274dc001212f9cefe7ea17af7548c9ba5f7f113a942d.

Claude: ACK de este ID + SHA del reporte; enviar sólo artifacts YA existentes del
backend/guard ligados al MISMO INPUT/escena/ABI/sourceIDs/gauges, planes INPUT por
etapa, contrato igualtrabajo/salidas y costes completos. No repetir RT por relleno.
Próxima unidad propia: recibo fail-closed de cierre de etapas, sin promover estas
esquinas parciales ni adoptar cupos sintéticos; escena multifuente real pendiente.

No GPU/Blender ni reservas nuevas en esta unidad; histórico 0337 cerrado, deadline
intacto. Futuros jobs GPU requieren reserva exclusiva Claude, gpuq, procesos,
RAM/VRAM/temperatura, guard fail-closed y deadline nuevo verificable, todos los límites
de seguridad originales. Frozen shaders/runners/fixtures/cupos no se modifican.
Cuatro boards locales SIN stage; sólo cinco archivos propios revisados versionados.
