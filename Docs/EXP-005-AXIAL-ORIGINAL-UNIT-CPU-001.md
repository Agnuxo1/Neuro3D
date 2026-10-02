# EXP005 — AXIAL-ORIGINAL-UNIT-CPU-001

Modelo opt-in `axial-ORIGINAL-reference-RN64-Horner26-point-CPU-v1`. Propietario Codex, prioridad P1. Predecesor AXIAL-ORIGINAL-ARGUMENT-CPU-001 / SHA702cf4c070b7184d0e177d107a081a6eba8b373afa2668e1fec485af96409469.

## Contrato y alcance

Dos fuentes elegibles nonexact_geometry_phase_PASS/s y thin_resolved/s: nuevo cálculo exacto racional de raíces positivas, referencia y selector desde ORIGINAL binary64 del INPUT fijado, seguido por nueva conversión residual y multiplicación2pi CPU, Horner26 sin FMA y permutación bit exacta del cuadrante. Se reutilizan primitivas propias de referencia sin ejecutar auditorías/suites anteriores; ninguna cápsula de ángulo/unidad retenida sirve de entrada numérica. Comparación con recibo anterior sólo DESPUÉS de derivar trace/argumento. Coeficientes fijados por SHA y su ledger Taylor; no encoder/hi-lo traversal ni general3D.

26 nodos observados por fuente. Cargos adimensionales separados: coeficientes, cuadrado redondeado, nodos RN observados, resto Taylor. Recurrencia: Ec=|z|Ec+|c-c_exact|; Es=|z|Es+|H_exact(x²)| |z-x²|; Er=|z|Er+|delta_mul|+|delta_add|. La rama impar multiplica cargos por |x| y añade delta final. Es una cota nueva de PUNTO, no una interpolación de ocho testigos ni admisión uniforme.

B es suma L1 de ambos términos (incluido Taylor); 0<B<1/2. Delta es suma de los tres cargos de argumento en radianes hacia fase ORIGINAL reducida. Misma permutación exacta: L1 hacia ORIGINAL <= B+2Delta y distancia angular <= B/(1-B)+Delta. El factor2 usa Lipschitz por componente, no identifica radianes con unidades de campo. Cap INPUT de fase permanece1e-12rad; amplitud no recibe presupuesto inventado. Ideal es unidad geométrica antes de aplicar SOURCE/material, no campo completo ni detector.

Guard fail-closed de entorno antes de ejecutar; modelos/casos/coefs/pins/contextos estrictos. Perfil seleccionado nozero/normal, |argumento|<=1, nodos normales; no FTZ, canonicalización, epsilon, aumento de radio ni tolerancia. Mantener exactamente 17 fuentes noejecutadas, grupo two_sources sin parcial, 17 casos STOP, SOURCE8FAIL/12signos previos y todos indicadores amplios false. TestsPASS o cota puntual que cabe NO significan backendPASS.

## Verificación y costes

Suite propia CPU un hilo/afinidad1/hijo60s; oráculo independiente stdlib sin imports de producción, enteros IEEE RN-even por nodo y reconstrucción racional de cargos, snapshot/selector/PI y fuentes/gauges. Control cuadrantes cuatro, mutaciones de modelo/caso/pin/contexto/coefs/límites/guard. Testigos sintéticos separados de las dos escenas.

Contar dos referencias exactas, 2 casts+2mul de argumento, 52 nodos Horner y seis probes; no son conteo de rayqueries GPU. IO/pins/snapshot/coeficientes/coste racional/guard/setup/remaining UNMEASURED, nunca cero. Sin afirmación de eficiencia, igualtrabajo, ganador, RT u óptica física. JEV LOCAL sin aval remoto por bloqueo de seguridad; no retry. Sin GPU/Blender/SDKDrJit/Kaggle/push/merge; ventana histórica cerrada e intacta. Boards/checkpoint SINstage; versionar sólo cinco nuevos propios.
