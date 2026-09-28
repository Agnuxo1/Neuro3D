# EXP-001 · Propuesta de preinscripción cerrada (Claude)

Estado: **PROPUESTA de Claude, no aprobada.** Complementa, sin sustituirlo,
`EXP-001-BORRADOR.md` (de Codex). Codex la revisa y JEV decide si se adopta
tal cual, con cambios o no se adopta. Todas las cifras de esta propuesta son
predicciones del oráculo independiente (`Blender/oracle/`) calculadas en CPU,
no resultados de Blender. Una vez aprobada, los umbrales no se tocan después
de medir.

## Pregunta

¿Cambiar solo la geometría de objetos Blender, o solo una propiedad óptica de
material, redirige la potencia entre los dos detectores de un Mach–Zehnder
según la óptica estándar de ondas planas? ¿Desaparece ese efecto cuando la
fuente se declara incoherente o cuando se rompe un brazo? En todos los casos
debe cumplirse el balance de energía por canal.

## Escena fija

- MZ **no rectangular** (DEC-007), β = 60°, construido con
  `geometry_oracle.NonRectMZ(60, X, Y).scene()`. BS1 en el origen, entrada
  por +x, normales de BS1 y BS2 ∥ (1, −1, 0), divisores 50/50 y espejos con
  R = (1, 1, 1).
- Fuente: potencia 1, rgb (1, 1, 1), f = 100 y v = 10 (λ = 0,1 BU), fase 0,
  beam_waist 0,2 BU, mutual_coherence 1, absorción 0.
- Detectores a 1 BU de BS2 en las direcciones de puerto `port_a_direction` y
  `port_b_direction`, con radio 0,2.
- BS2 y los dos detectores agrupados bajo un empty padre («grupo
  combinador»), de modo que la edición geométrica sea un solo movimiento de
  escena más el de M1.
- Convención (DEC-005): con fases iguales, toda la potencia sale por B.

## Controles y predicciones (P_in = 1, suma sobre RGB)

| ID | Qué cambia respecto de A | Predicción A / B | Otras predicciones |
|---|---|---|---|
| A | Base: P = (2, 2) | 0 / 1 | status ok, interference_valid |
| B-geo | M1 y el grupo combinador: P se desplaza t = 0,323205 BU a lo largo de v2 (M2 fijo) | 1 / 0 | ΔL = λ/2 en frente de onda |
| B-mat | Solo `phase_shift` de M2 = π (geometría de A) | 1 / 0 | — |
| C | Escenas A, B-geo y B-mat con mutual_coherence = 0 | 0,5 / 0,5 | independientes de la fase |
| D | Escena A con M2 girado 10° en el plano | 0,25 / 0,25 | escapada = 0,5 |
| E | Barrido de `phase_shift` de M2 en 16 pasos, con τ1 = 0,5 y con τ1 = 0,8 | P_B = ½(1 + V·cos Δφ) | V = 1 y V = 0,8 |
| F | Paridad: circuito monocamino EXP-000 | 0,7053474966 / activación 0,3657724623 | fase 2,6376104167 rad |

En todos los casos el residuo del libro mayor por canal es ≤ 1e-12 y no hay
ningún NaN ni Inf.

## Tolerancias (fijadas antes de medir)

- **CPU Python:** puertos y escapada, |error| ≤ 1e-12. Visibilidad,
  |V − V_pred| ≤ 1e-9.
- **Blender:** el motor recibe posiciones en float32. Estimación en CPU
  (`D:/PROJECTS/.cognition/neuro3d/exp-001/float32_tolerance.py`, redondeando
  posiciones y normales a float32): puerto oscuro ≤ 6,3e-12, separación
  transversal 2,2e-7 BU, status ok. Tolerancia propuesta: puerto oscuro
  ≤ 1e-9, puerto brillante ≥ 1 − 1e-9, residuo ≤ 1e-12 (el balance se calcula
  en doble precisión) y V con error ≤ 1e-6. Además, volver a trazar en CPU con
  los valores leídos del `.blend` debe coincidir con Blender en 1e-12.
- **Límite de la estimación:** se redondearon las componentes de las normales,
  no los ángulos de Euler reales. Hay que confirmarlo midiendo en OPT-003.

## Procedimiento

1. **CPU:** construir y trazar A-F; guardar un JSON con las entradas, las
   salidas y el commit del motor.
2. **Blender background CPU** (presupuesto de EXP-000: 1 hilo, RSS ≤ 1,5 GiB,
   RAM libre ≥ 2,5 GiB, 45 s por fase; sin GPU ni render): crear A, guardar,
   reabrir, trazar; aplicar la edición de B-geo sobre objetos, guardar,
   reabrir, trazar; repetir con B-mat, C y D.
3. Comparar con esta tabla y registrar cualquier desviación sin ajustar
   umbrales.

## Criterios

- **Pasa** si todos los controles cumplen la tolerancia en CPU y en Blender.
- **Falla** si un control incumple su tolerancia, si C depende de la fase, si
  D sigue interfiriendo o si el balance no cierra. Un status distinto de ok en
  A, B o C se registra como fallo, no como exclusión.
- **Parar** si falta margen de RAM, se supera el presupuesto o aparece
  energía imposible.

## Límites de lo que demostraría

Demostraría que objetos y propiedades guardados en Blender gobiernan un
cálculo de interferencia escalar de ondas planas con solape gaussiano
fenomenológico. No demostraría propagación física de haces, difracción,
comportamiento de fotones reales ni aprendizaje. `mutual_coherence` es una
propiedad declarada de la fuente, no derivada de un espectro.

## Comprobación exploratoria en CPU (2026-09-28 21:32 UTC, no confirmatoria)

`D:/PROJECTS/.cognition/neuro3d/exp-001/controls_cpu.py` (motor sin commit de
las 21:31) → `controls_cpu.json`: A 0/1; B-geo 1/0; B-mat 1/0; C 0,5/0,5 en
las tres escenas; D 0,25/0,25 con escapada 0,5 (status `missed_bs2`);
V = 1,0 y 0,8; F 0,7053474966 / 0,3657724623 / 2,6376104167. Residuo
≤ 1,1e-16 en todos los casos. Sirve para detectar errores de diseño de la
propuesta, no como resultado de EXP-001.

## Decisiones que quedan para Codex/JEV

- Aceptar el MZ no rectangular con λ = 0,1 o fijar otro f/v. Con λ = 1, B-geo
  necesitaría t = 3,23 BU, fuera del rango alcanzable con β = 60° e Y = 2.
- Si la agrupación mediante empty padre se considera una sola edición de
  escena.
- Si E y F entran en el criterio de promoción o solo se registran.
