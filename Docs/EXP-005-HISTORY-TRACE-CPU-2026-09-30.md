# EXP-005: generar historias desde escena, perfil CPU acotado

## Unidad entregada

`history_trace_cpu_v1.trace_scene(snapshot)` deriva el árbol completo desde
fuentes, triángulos y roles del snapshot. No recibe rutas del fixture ni
matrices entrenadas. Devuelve registros con padres, fuente, primitiva global,
origen/dirección, profundidad y binding de escena; comprueba la completitud
con los helpers congelados antes de devolver un resultado.

**Todo el recorrido nuevo es CPU Python racional.** No se ha ejecutado Blender
ni GPU, no se entregan estas rutas a un backend nativo y no se ha modificado el
exportador preparado. No sustituye inferencia GPU desde escena por rutas CPU.
No evidencia RT, hi-lo, precisión nativa, óptica física ni ventaja de velocidad.
Fallback local explícito: JEV sigue bloqueado por seguridad, sin aval remoto.

## Contrato opt-in

- Límites máximos del perfil congelado: 64 registros y profundidad 32.
  Solo se pueden reducir para un caso; superar cualquier límite aborta,
  sin árbol parcial, poda, truncación ni cierre artificial en detector.
- Usa `nearest` exacto y la exención de partida certificada del helper V2
  existente. No añade epsilon, desplazamiento de origen ni cutoff positivo.
- Conserva ambas ramas del divisor incluso con T=0, T=1 o campo cero;
  una raíz por fuente, ancestros separados aunque coincidan espacialmente.
- El serializador exige representación binary64 EXACTA de cada partida
  racional. Si un impacto/dirección no es representable, rechaza en vez de
  redondear. Es una limitación del perfil CPU, no un fallo del hardware ni un
  requisito impuesto a Blender general. No promoción a geometría arbitraria.
- La generación y la validación comparten el helper `nearest` congelado;
  NO son dos oráculos geométricos independientes. La comparación de MZI
  usa además registros fijados previamente y una fórmula de campo independiente.

## Evidencia CPU retenida

Ejecución 13:48:30 UTC, cuatro tests PASS en 0,299s, un hilo y cada hijo <=60s.
Tres controles base/switch/referencia: registros generados iguales al fixture
MZI anterior, 13 registros/9 consultas nearest/4 caminos terminales por escena;
campo complejo CPU contra fórmula, error máximo 2,220446049250313e-16.
Los cinco negativos de caps (12 registros, profundidad 3, exceso 65/33 y bool)
rechazan sin devolver resultado parcial.

Tests adicionales: T extremos/campo cero conservan cuatro terminales; dos
fuentes producen 26 registros/18 consultas con ancestros separados, intensidad
ideal coherente 2,25 frente a independiente 1,25. El impacto racional (2,2/3,0)
del caso de detector aislado rechaza por no ser representable, sin snapping;
control diádico 1/8 acepta. Estas pruebas son sintéticas CPU, NO readback Bpy.

Report local:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_trace_cpu_20260930_1353.json`
(1353 es etiqueta de archivo; ejecución real 13:48:30), SHA
`138f56b95abafa8cb510ce0c0b22a3fef773a4cbf560e744af12d6d2e8004beb`.
Diez code SHA verificados. Preparación inicial 1351 conservada; se añadió
la prueba integrada de impacto no representable antes de congelar este commit.
Los trece pins de export1338 siguen intactos, sin alterar runners/shaders/fixtures.

## Coordinación y siguiente paso

GPU sigue reservada a otro proyecto y RT-CAP-006 de Claude sigue en cola.
Esta unidad no reserva ni cancela tickets, no ejecuta escritores ajenos ni
instala/publica nada. 006 sigue la única petición abierta a Claude, entregar
artefactos retenidos o bloqueo real; no añadir una revisión de guard por este hito.

Después de recibir 006, auditar sus artefactos. La incorporación del generador
al exportador o a una corrida Blender será otra variante/contrato explícito;
no tocar d142c51 ni alimentar estas rutas CPU silenciosamente a un kernel GPU.
Un eventual job requiere reserva exclusiva, guard fail-closed, preflight real y
deadline nuevo, sin modificar el deadline nocturno cerrado ni bajar márgenes.
