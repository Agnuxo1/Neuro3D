# Nearest V2: reparación geométrica verificada en GPU

Contrato congelado en `abbe543` antes del job0546. La RTX3090/OpenGL de
Blender4.5 ejecutó la variante V2, que busca primero el mínimo global exacto
y después la banda inclusiva de empates. Propagación, ramificación, fases,
campo e intensidad siguen dentro del shader. Exportación, empaquetado,
transferencias, lectura y oráculos siguen en CPU. NO hardwareRT ni BVH.

## Resultado del piloto

- 21 casos raw sintéticos: doce ambigüedades rechazadas con status2 y sin
  campos parciales, un escape con status1, ocho controles válidos.
- Seis permutaciones CE3 rechazadas por V2. V1 acepta incorrectamente una
  de las seis en runtimeGPU: el fallo histórico quedó reproducido, no inferido.
- Cuatro probes reales: K3/K4 con basis0 y todas las fuentes1, reabriendo
  escenas congeladas0315 sololectura y contrastando el readback evaluado.
- Total31dispatches. Auditoría CPU posterior: doce probes válidos contrastados
  contra el oráculo triangular completo, campos/ledger/contadores; negativos
  específicos y orden de fixtures comprobados. 174testsCPU PASS8,580s.
- Máximo error complejo2,855e-7; balance1,252e-6; longitud1,066e-14BU.
  Umbrales preinscritos: campo1e-4, potencia/balance2e-4, longitud1e-5BU.

Los adversarios subnanométricos son arrays float64 sintéticos, NO geometría
Blender float32 reabierta. Las cuatro escenas reales son otra categoría.
Los empates de normales siguen el nuevo rechazo canónico conservador;
no equivalen a certificación física de modos ni a una red general.

## Evidencia y guard

- Reporte `D:/PROJECTS/.cognition/neuro3d/exp005_nearest_native_20260930_0546.json`.
- SHA `b855a6ff5626149bc4744b377864f351debb0d585c7db904d1a2774c20d7accb`.
- Reauditoría `D:/PROJECTS/.cognition/neuro3d/exp005_nearest_audit_20260930_0550.json`.
- Guard0546: completed/rc0,7,521s; RAMmín9,916GiB, VRAMmáx0,815GiB,
  temperatura36°C. Job liberado05:47:34UTC; PID29224 terminado. Sin Blender
  activo al revisar. No preferencias guardadas ni cambios a las doce escenas.
- Veinte hashes de dependencias y doce hashes de escenas verificados después.
  Aviso quit.blend@ en TempC por permisos retenido; no se eludieron permisos.

## Límites y siguiente paso

Variante opt-in, sin sustituir el shader histórico. No hay medición pareada
de coste V1/V2; dos pasadas pueden aumentar trabajo y no se declara speedup.
Bias1e-6 que salta un gap1e-8 y tolerancia angularGPU1e-6 frente a oráculo1e-9
siguen pendientes. No ampliar bounds, conf1 ni generalidad por este piloto.
Pedir crítica retenida de Claude de normales/ties/ledger y preparar adversarios
CPU de bias y terminal antes de cualquier nuevo contrato/runtimeGPU.
JEV sigue bloqueado por seguridad; decisión local sin aval remoto.
