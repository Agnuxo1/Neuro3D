# EXP-005: gate geométrico previo al consumidor GPU nativo

Contrato local, 30/09/2026. JEV sigue bloqueado por revisión de seguridad;
fallback local, sin aval remoto. No modifica fixtures congelados ni el shader.

Objetivo: rechazar alias de fuentes colineales/copropagantes aunque tengan IDs
distintos, referencias terminales no planas, aperturas de salida coincidentes y
registros terminales incompletos/incompatibles ANTES de empaquetar/despachar.
Comprobar también fuentes apagadas: el contrato no depende del input del momento.

Límites: 1–8 fuentes, 1–512 caminos, 1–64 impactos/camino; tolerancia de posición
1e-6 BU y angular 1e-6 sobre el producto escalar de direcciones unitarias.
Referencias deben estar en superficies trianguladas planas y no rasantes.
Aperturas coplanares/copropagantes con cajas envolventes solapadas se rechazan
conservadoramente: no equivale a calcular solape exacto de modos finitos.

Ensayo: reapertura SOLO LECTURA de base.blend del nuevo escape0119, nueve probes
(tres bases y pares1/i), campos GPU frente al oráculo completo: campo<=1e-4,
potencia/balance<=2e-4. Ocho controles negativos sobre copias de snapshot/paths:
fuente alias coincidente; alias separado sobre la misma recta; fuente apagada con
dirección nula; referencia fuera del plano; salida duplicada; dirección de llegada
incorrecta; offset adulterado; dato terminal de posición ausente. Todos deben
rechazarse antes del dispatch. Ningún archivo .blend se vuelve a guardar.

Guardar hashes de entrada/código, rechazos, número de dispatch y guard separado.
GPU/Blender solo con gpuq, guard120s, estimaciones host1.5/device1GiB, piso RAM4,
VRAMtotal18, temperatura80, corte06UTC. Cierre con timer nativo ya validado.

No prueba ortogonalidad Maxwell, perfiles espaciales/polarización/coherencia
parcial, ni que campos de puntos separados sean un único modo físico. Es un
rechazo geométrico conservador adicional; nunca marcar geometry_gate_passed=True.
La geometría sigue CPU y los campos GPU: no RT ni ventaja comparativa.
