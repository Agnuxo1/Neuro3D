# EXP-005: enlace CPU entre exportación e historias generadas

## Interfaz nueva, no backend nuevo GPU

`validate_generated_export(expected, before, after, phase, shift)` acepta
snapshots, NO una lista de rayos/impactos/historias precomputadas. Exige flags
de evaluación y antes==después; llama al trazador CPU SOLO con `after` y
al gate congelado de exportación con los registros recién generados.
Comprueba la igualdad del fixture y campos ideales frente a fórmula MZI.

`expected` sirve de control de igualdad, no de sustituto de geometría para el
recorrido. La devolución conserva las historias y la referencia CPU junto
al binding real del snapshot. No modifica entradas, no contiene lanzador
bpy/GPU, no cambia el exporter d142c51 ni entrega rutas a un kernel nativo.

Se mantienen los límites CPU 64 registros/profundidad 32 y la exigencia de
partidas representables exactamente en binary64, sin snapping. Los helpers
geométricos del trazador y del validador se comparten: no son dos oráculos
geométricos independientes. Los grupos de coherencia son leídos de escena
y deben coincidir con el control declarado.

## Gates ejecutados

30/09, 13:58:06 UTC: tres tests PASS en 0,202s, un hilo/hijo <=60s.
Report retiene cuatro controles doubles:

- base, switch y referencia de los tres casos preinscritos del MZI;
- adversario SOLO CPU: cara coplanar adicional de MA, sin mover el plano,
  que cambia IDs globales downstream. El terminal Dy cambia de primitiva
  10 a 11; el árbol nuevo tiene 13 registros y no reutiliza filas anteriores.

Los cuatro negativos retenidos rechazan evaluación ausente, cambio entre
readbacks, fase cambiada en AMBOS snapshots respecto al fixture y coherencia
cambiada. Se conserva el motivo de rechazo; no se ajustó ningún umbral.
Campo máximo contra fórmula 2,220446049250313e-16; gate fijo 1e-13.
Todos los árboles de estos controles requieren nueve consultas nearest.

Report:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_generated_export_cpu_20260930_1358.json`
SHA `8ec20282cb2b27c631760aed56b31fe2ec08d32c6b79c053c817eba4c23729ff`.
Dieciséis code SHA verificados; los trece pins de export1338 siguen intactos.

## Límites y coordinación

Son doubles CPU de readback con emulación de vértices float32, NO ejecución
real de Blender/guardar/reabrir. `bpy_execution_certified=False` permanece
explícito: el flag de evaluación de un snapshot no autentica su procedencia.
Los campos y rutas nuevos son Python CPU, no cómputo Blender GPU, RT, hi-lo,
solape físico, fase nativa certificada, mejora de velocidad ni promoción conf1.

GPU ocupada por otro proyecto; RT-CAP-006 de Claude sigue en cola y es la
única petición abierta. No reservas/cancelaciones ni escritores ajenos.
Mantener fixtures/runners/shaders/contratos congelados y fallos anteriores;
coordinación local sin stage, nada de push/merge/publicación.
JEV bloqueado por seguridad: fallback local identificado, sin aval remoto.

Siguiente: auditar artifacts 006 al llegar. Preparar una variante propia
de piloto real separado, contrato/commit previos y guard fail-closed con
deadline nuevo y preflight RAM/VRAM/temperatura exclusivo por job, antes de
reclamar vínculo a escena Bpy real. No alimentar estas rutas CPU a GPU ni
sustituir silenciosamente el backend rawscene por U/GEMM.
