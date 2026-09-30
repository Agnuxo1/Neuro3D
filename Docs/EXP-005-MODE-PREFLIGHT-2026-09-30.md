# Gate modal conservador antes del cálculo GPU nativo

30/09/2026, 01:38 UTC. Contrato congelado en `b4ea165` antes del ensayo.
Decisión local: JEV continúa bloqueado por revisión de seguridad, sin consulta
remota ni bypass. Unidad de desarrollo acotada con criterios previos y checkpoint.

## Resultado nuevo

Ocho adversarios de copias del readback y registros reales se rechazan ANTES
de compilar/despachar el shader: alias de fuente coincidente y longitudinal,
dirección nula en fuente apagada, referencia fuera plano, salida duplicada,
dirección de llegada incompatible, offset adulterado y posición de impacto ausente.
No se trata de ocho escenas inválidas guardadas ni de ocho trazados RT.

Después, nueve probes (tres bases y todos los pares1/i) con raycasts nuevos CPU
y campos GPU nativos de Blender conservan los resultados del fixture escape:

| Medida | Máximo observado | Umbral previo |
|---|---:|---:|
| Campo complejo vs oráculo completo | 2,797025e-6 | 1e-4 |
| Intensidad vs oráculo | 3,083031e-6 | 2e-4 |
| Detectores + escape vs entrada | 5,291775e-6 | 2e-4 |

Reauditoría CPU independiente: recalculados los nueve campos con el oráculo de
triángulos desde el snapshot, comprobados nueve IDs únicos, ocho rechazos con
contador de dispatch cero, dos hashes de entrada intactos y desaparición del hijo.
93 tests CPU pasan en 2,957s (siete nuevos). Una comprobación AST añadida después
del ensayo falló inicialmente por comparar solo líneas de dos llamadas en la misma
línea; corregida a posición línea/columna. No hubo fallo ni repetición GPU.

Los entrypoints nativos ahora llaman al gate antes de pack/dispatch. El ABI de
bajo nivel `pack_paths` sigue siendo un empaquetador, NO un validador de modos;
otros consumidores deben invocar explícitamente el gate si desean esas garantías.

## Seguridad y artefactos

- gpuq: adquirido01:35:24/liberado01:35:32UTC, rc0. Guard7,5004s, sin motivos
  de parada. PID31672 terminado, sin Blender residual en la comprobación.
- Muestras guard: RAMlibre mínima9,6315GiB, VRAMglobal máxima0,6143GiB,
  temperatura máxima33°C. No garantía de picos entre muestras.
- Solo lectura de `exp005_escape_native_20260930_0119/base.blend` y snapshot;
  no guardar sobre esos archivos. `quit.blend` es recuperación temporal del
  proceso nuevo, no una escena de despliegue ni una modificación del fixture.
- En `D:/PROJECTS/.cognition/neuro3d/`: `exp005_modes_native_20260930_0135.json`
  y `exp005_modes_guard_20260930_0135.json`. Resultado SHA256:
  `55dfa805d4a667cc627079f032ad28dfa1b15b8d53800459859de5197b50cc18`.
- Shader previo sin modificaciones. Evaluación geométrica CPU; propagación,
  suma de campos y detección shaderGPU dentro de Blender4.5.14LTS/OPENGL/RTX3090.

## Límites y siguiente paso

Es un filtro conservador de rayos puntuales, NO una prueba Maxwell de modos
ortogonales, polarización o perfiles finitos. Las cajas coplanares solapadas se
rechazan conservadoramente aunque algunos polígonos dentro de ellas no se toquen.
Puntos distintos de un mismo terminal no quedan certificados como un modo físico
por esta comprobación. `geometry_gate_passed=False` permanece explícito.
Tampoco es RT, óptica física, EXP-005 completo ni prueba de velocidad/capacidad.

Claude: aportar un contraejemplo de independencia modal que sobreviva al filtro,
o revisar el rechazo longitudinal y el plano común sin duplicar la ejecución.
Codex: continuar por cobertura modal/propiedades o contrato separado para
geometría GPU/RT, coordinándolo con el dueño del backend. No repetir este PASS.
Reloj actualizado mediante la app: mismos cinco minutos y cierre06UTC, con los
hitos nativos/escape/modos actuales y las limitaciones pendientes.
