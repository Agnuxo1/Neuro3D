# Intersecciones geométricas nativas en GPU: componente verificado

Contrato previo `a5cc165`, ensayo 30/09/2026 02:21:01–09 UTC. Resultado
numérico y operativo PASS; **no es RT ni una red completa en GPU**.

## Qué calculó la GPU

Blender 4.5.14 LTS, OpenGL, RTX3090. Shader nativo recibe todos los vértices
mundiales de una escena reabierta y rayos crudos. Busca exhaustivamente el
triángulo más cercano y calcula distancia, normal y ambigüedad: no recibe
intersecciones ni objetivos precalculados. FP64 interno, salida FP32.

25 consultas fijas por caso: fuentes y rayos intermedios procedentes de trazas
CPU previas, más dos misses externos. Estos inputs sirven para verificar
intersecciones, **no demuestran propagación/reflexión/ramificación GPU**.

| Caso | Triángulos | Consultas | Resultado causal/control |
|---|---:|---:|---|
| Base | 30 | 25 | Dos misses explícitos, sin ambigüedad |
| Color decorativo | 30 | 25 | GPU exactamente igual a base |
| Dos espejos movidos +0,03125 BU | 30 | 25 | Cuatro consultas cambian |
| Espejo eliminado | 28 | 25 | Dos consultas cambian; cuatro misses |
| Espejo duplicado coincidente | 32 | 25 | Dos impactos ambiguos; inferencia rechazada |

125 readbacks re-auditados en CPU desde snapshots retenidos. Objeto/estado
coinciden con oráculo independiente de triángulos. Error máximo de distancia
5,960465e-8 BU y normal absdot 1,711428e-8. También se compara con
`scene.ray_cast` real para las 123 consultas no ambiguas: distancia máxima
1,192093e-7 BU y normal absdot 3,422855e-8. Umbrales **anteriores** al ensayo:
1e-5 BU/1e-6 normal. No se dejó una fase libre ni se ajustaron tolerancias.

106 tests CPU PASS (4,034s). La llamada sincronizada dispatch/readback de
este componente toma 0,580–0,910ms: **no es latencia de inferencia completa,
ni comparación de rendimiento**, ni coste total de escena/transferencias.

## Seguridad y evidencia

gpuq exclusivo, guard120s y cierre absoluto06UTC. Job7,606s/rc0, sin causas
de corte; RAM libre mínima7,2851GiB, VRAM máxima0,63184GiB, temperatura33°C.
PID propio32328 finalizado; ningún Blender restante. Reserva liberada. No
se tocó el proceso ajeno31980. No se guardó sobre los cuatro inputs0119;
sus SHA256 se comprobaron intactos después. `quit.blend` es recuperación,
no un nuevo fixture de despliegue.

- `D:/PROJECTS/.cognition/neuro3d/exp005_intersection_native_20260930_0221.json`
  SHA256 `c9e927ee78b3801e8a9021c00f9d4da8a6c9553031520aba9805452c6abb2714`.
- Cinco snapshots/consultas/readbacks/oráculos en carpeta del mismo nombre.
- Guard `exp005_intersection_guard_20260930_0221.json` en la misma raíz.
- Fuente `Blender/tests/exp005_intersection_runtime.py`, ABI en
  `Blender/benchmarks/capacity_audit/gpu_geometry_probe.py`, shader separado
  `Blender/shaders/exp005_intersections.glsl`.

## Contraste independiente del divisor: alcance separado

La entrega de Claude02:03 fue leída y contrastada: 7 configuraciones ×3
bases ×3puertos, 63 valores; maxΔcampo1,322189e-5 frente al shader de divisor.
Siete puertos a.Y ausentes para b.col son exactamente oscuros en la salida
nativa, comprobados antes de asignarles cero para comparación. Su retrazador
no importa el consumidor propio, pero omite rayos perdidos y tiene defaults
para T/fase. Esta evidencia es de **21 bases**, no las superposiciones, live
updates ni rechazos de tipos/rangos. No promoverla a un gate adicional.

## Siguiente paso

Propagación/ramificación/reflexión y suma coherente desde fuentes crudas,
sin lista CPU de rayos intermedios ni readback de frontier entre etapas;
contrato nuevo primero. Conservar este componente como contraste. RT/OptiX
permanece asignado a Claude: coordinar interfaz y pedir un adversario de
nearest-hit/ambigüedad antes de duplicar un backend.

No BVH/RT, Maxwell/Fresnel, perfiles modales físicos, red escalable ni ventaja
comparativa demostrada. EXP-005 completo sigue pendiente. JEV bloqueado por
seguridad; decisión local identificada. Nada publicado/fusionado.
