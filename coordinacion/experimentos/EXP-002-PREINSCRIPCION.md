# EXP-002 · Ajuste de una celda óptica mediante geometría de escena

Estado: **diseño previo a ejecución**, 2026-09-29. No hay resultado de
aprendizaje ni autorización de ejecutar Blender/GPU en esta tarea de diseño.
No confundir una celda calibrable con una red neuronal entrenada.
JEV remoto (`status=connected`, `provenance=jev`) eligió
`geometry_parameter` con confianza 1,0 frente a fase de material,
malla inmediata o espera pasiva. El plan de ruta eligió agente principal,
sin paralelismo.

## Hipótesis y causalidad

La salida óptica del Mach–Zehnder no rectangular de EXP-001 puede ajustarse
por **una coordenada geométrica** de los objetos Blender, manteniendo fijos
potencia, frecuencia, fase material y propiedades de superficie. No basta
ajustar una variable en una fórmula analítica: en la prueba confirmatoria
cada evaluación debe mover los objetos de la escena y llamar al motor que
lee sus matrices/propiedades. Blender calcula con CPU; no se renderiza luz.

Unidad: BU = unidad Blender. Se parte de la escena A de EXP-001. Sea
`u ∈ [0,1]` y `t = u · t_pi`, donde
`t_pi = 0,323205080756888 BU` es la magnitud de B-geo. Aplicar
`u · group_delta` al empty padre de BS2 y detectores, y
`u · mirror1_delta` a M1, usando los del plan congelado
`Blender/tests/mz_exp001_plan.py`. M2, fuente, BS1, fases de material,
RGB, frecuencia, coherencia, absorción y radios permanecen fijos. Dos
objetos se editan coordinadamente; no afirmar que uno solo entrena la celda.

La expresión ideal `P_A(u) = sin²(πu/2)` sirve únicamente como referencia
de diseño. Una comprobación analítica previa predijo 20 actualizaciones
para cada objetivo descrito abajo; **no** es una ejecución del motor ni
evidencia de éxito de EXP-002. Ninguna salida esperada se inyecta al trazador.

## Protocolo congelado antes de medir el motor

Dos carreras independientes, restaurando A antes de cada una:

| Carrera | Objetivo P_A | u inicial | P_A ideal al inicio | u ideal final |
|---|---:|---:|---:|---:|
| Entrenamiento 1 | 0,75 | 0,10 | ≈0,02447 | 2/3 |
| Replicación con otro objetivo | 0,25 | 0,90 | ≈0,97553 | 1/3 |

En cada evaluación, obtener `P_A` del resultado de la escena, no de la
expresión ideal. Estimar `g = [P_A(min(1,u+h)) -
P_A(max(0,u-h))] / [min(1,u+h)-max(0,u-h)]`, con `h=1e-4`.
Actualizar `u ← clip(u + 0,2 · (objetivo-P_A(u)) · g, 0, 1)`.
Detener si `|P_A-objetivo| ≤ 1e-4`, a lo sumo 50 actualizaciones.
Registrar cada `u`, potencia A/B, escape, pérdida, status, solape y balance,
incluyendo las evaluaciones de diferencias finitas.

## Criterios y controles negativos

- En **ambas** carreras, alcanzar error absoluto de puerto A ≤1e-4 en
  ≤50 actualizaciones, sin usar fase material. En todas las evaluaciones:
  `status=ok`, `unresolved=0`, balance por canal ≤1e-12 y
  `mode_overlap≥1−1e-9`. El resultado final debe persistir: guardar,
  reabrir y reconstruir desde matrices/propiedades leídas, con diferencia
  de potencia ≤1e-9 respecto del resultado previo al guardado.
- Control **geometría congelada**: repetir las dos condiciones iniciales
  sin aplicar actualizaciones; no debe alcanzar ninguno de los objetivos
  dentro de 1e-4. Si lo hace, el experimento no distingue aprendizaje.
- Control **coherencia nula**: con `mutual_coherence=0`, repetir la primera
  carrera. El puerto A debe permanecer dentro de 1e-9 de 0,5 en cada
  evaluación y no alcanzar 0,75. Es un control causal de interferencia,
  no un dato de entrenamiento.
- Registrar cualquier fallo, estancamiento, pérdida de alineación o
  discrepancia con el modelo ideal sin cambiar después tolerancias,
  objetivos, pasos ni el dominio de `u`. El control incoherente puede
  terminar pronto cuando el gradiente observado sea cero.

Los dos objetivos evalúan si el mismo procedimiento puede **recalibrarse**,
no generalización a entradas no vistas ni clasificación. El siguiente gate
de red requerirá entradas, topología multicelda, parámetros entrenables y
una tarea con datos separados de entrenamiento/validación. EXP-002 por sí
solo no acredita una red neuronal ni hardware fotónico.

## Recursos y revisión

Preparar primero código y pruebas estáticas/CPU ligeras. Ejecutar Blender
background únicamente tras una nueva comprobación de recursos y
autorización aplicable; un hilo, sin render y con límites de memoria/tiempo.
No usar GPU para EXP-002 sin autorización nueva. Solicitar crítica de Claude
del contrato después de su auditoría OPT-013; registrar su contraejemplo
antes de cualquier corrida confirmatoria.
