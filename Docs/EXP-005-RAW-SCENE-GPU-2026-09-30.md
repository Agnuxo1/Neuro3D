# Piloto óptico gobernado por escena: recorridos y campos en GPU

El piloto de **dos celdas conectadas** pasó su contrato local: las
intersecciones, reflexiones, ramificaciones, distancias, fases, acumulación
coherente y detección de intensidad se ejecutaron en un shader de GPU nativo
dentro de Blender. No se suministraron rutas ni impactos calculados en CPU.

Esto es una **simulación escalar digital en GPU**, no óptica física, RT/BVH,
una red neuronal general ni evidencia de ventaja frente a otra arquitectura.

## Qué permanece en CPU y qué pasó a GPU

CPU: abrir el archivo, exportar vértices mundiales y propiedades, validar
tipos/roles y exclusiones modales conservadoras, transferir datos y leer el
resultado final. Los oráculos CPU se ejecutan para comprobar resultados,
no como parte de la inferencia del shader. En las nueve pruebas base también
se retrazó con `scene.ray_cast` para validación; esas rutas no entran al shader.

GPU: desde posiciones/direcciones/campos de las fuentes y triángulos completos,
descubre recorridos con una pila DFS, calcula normales y reflexión especular,
aplica los coeficientes ideales del divisor y espejo, transporta fase hasta la
referencia terminal, suma amplitudes y calcula |campo|². Emite además campos
por camino con fuente y longitud efectiva. No recibe una matriz aprendida ni
una tabla de conexiones calculada fuera de la escena.

Cada puerto repite el trazado completo: diseño pequeño de verificación,
**no un diseño escalable ni un benchmark de capacidad**. Longitudes y álgebra
en FP64, sin/cos en FP32 tras reducción del ángulo en FP64; salida FP32.

## Contrato y resultado retenido

Commit **cd6282c** anterior al ensayo: `EXP-005-FRONTIER-GPU-V1.md`.
Siete tratamientos de escena reabierta: base, color decorativo, fase de
espejo, longitud de onda, desplazamiento de dos espejos, T=0,2 y T=1 en
divisor. Cada uno con tres bases y seis pares 1+1/1+i: **63 pruebas**.
Tres puertos, incluido escape coherente. **840 contribuciones por camino**
producidas en GPU y re-auditadas desde los snapshots retenidos.

| Magnitud | Máximo observado | Umbral anterior al ensayo |
|---|---:|---:|
| Campo complejo vs oráculo triangular | 2,183450e-7 | 1e-4 |
| Potencia vs oráculo | 3,764546e-7 | 2e-4 |
| Balance detectores + escape | 7,003546e-7 | 2e-4 |
| Campo de cada camino del ledger | 1,080009e-7 | 1e-4 |
| Longitud efectiva por camino, BU | 3,552714e-15 | 1e-5 |
| Suma del ledger vs campo GPU | 5,960465e-8 | 1e-4 |
| Campo vs raycast Blender + consumidor CPU (nueve bases/pares base) | 2,981089e-6 | 1e-4 |

Conteo de recorridos terminales exacto (4, 10, 14 o 20 por prueba según las
fuentes activas); conteo de raycasts GPU igual al oráculo. No fase global
libre, renormalización ni pérdida eliminada. Sham exactamente igual.
Cambios máximos de potencia para basis0: fase0,012365; λ0,084428;
espejos0,980067; T0,2→0,092304; T1→0,461517, todos >1e-3 preinscrito.

Seis controles reales rechazados por el **shader**, con resultado parcial
borrado y flags específicos: espejo ausente y fuente perdida, superficies
coincidentes, dirección terminal incompatible, límite de pasos y profundidad.
Overflow de pila/ledger y rol inválido tienen decoder/flags defensivos, pero
no se presentan como negativos runtime ejecutados en este ensayo.
**119 tests CPU PASS**, 3,717s antes de la ejecución.

## Seguridad, trazabilidad y reproducibilidad

Blender4.5.14 LTS/OpenGL/RTX3090, reserva gpuq02:40:47–56UTC, guard120s;
job8,7135s/rc0. RAM libre mínima7,308GiB, VRAM total máxima0,64258GiB,
33°C. PID propio31620 finalizado, sin Blender restante. Reserva liberada;
proceso ajeno31992 conservado. Inputbase0119SHAintacto; ningún fixture antiguo
sobrescrito. Recuperación `quit.blend` no es un nuevo activo de despliegue.

Informe: `D:/PROJECTS/.cognition/neuro3d/exp005_frontier_native_20260930_0240.json`
SHA256 `edf126dd6466c5534fcf05968ee5dc221ea113efd85dbec95ddf7000336761ac`.
Carpeta homónima contiene siete snapshots/probes/ledger/oráculos y seis
controles; guard `exp005_frontier_guard_20260930_0240.json` en la misma raíz.
63 resultados se recomputaron independientemente en CPU desde el readback
guardado, después de finalizar el proceso. Los resultados anteriores se
preservan: este piloto no promociona retroactivamente el backend híbrido.

La duración dispatch+sincronización+readback observada fue1,821–26,016ms;
incluye el ledger de auditoría y no es latencia extremo a extremo ni comparación
de rendimiento. No atribuir speedup, eficiencia ni máximo de neuronas.

## Aclaración del auto-impacto y revisión pendiente

Claude02:26 señaló dos rayos del componente previo que, sin bias/t_min, se
auto-interceptan a5,96e-8BU. Reproducidos en consultas3/19 del snapshot base:
origen sin desplazar toca a.bs1, mientras el lanzamiento sesgado alcanza a.m2/
a.r1 a2BU. El contrato previo ya fijaba desplazamiento1e-6 y epsilon1e-9;
no se modificó para conseguir este resultado. El piloto nuevo documenta lo
mismo explícitamente y compensa el bias al medir longitud. No certifica
geometrías con separación inferior al bias. El comentario de Claude es
inline, sin script/artefacto propio; no presentarlo como una auditoría completa.

Próximo: crítica independiente del shader/ledger/límites por Claude y piloto
multicelda nuevo con contrato congelado. Plan RT/OptiX sigue siendo suyo;
no sustituirlo por ALU ni por Cycles incoherente sin etiquetarlo. Modos físicos,
polarización, Fresnel/Maxwell, redes grandes, entrenamiento y comparaciones
requieren gates propios. **EXP-005 general sigue pendiente**. JEV bloqueado
por seguridad: fallback local, sin aval remoto. Nada publicado ni fusionado.
