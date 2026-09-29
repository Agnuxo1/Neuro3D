# Oráculo geométrico independiente y primer smoke real

Resultado: **PASS acotado a una celda**, Blender 4.5.14 LTS, CPU de un hilo,
sin render ni carga GPU intencionada. No es el gate multicelda EXP-005.

Tres mecanismos contrastados:

1. Blender decide impactos/distancias mediante `scene.ray_cast` real.
2. Un oráculo de biblioteca estándar descubre las rutas con Möller–Trumbore sobre
   triángulos mundiales exportados DESPUÉS de reabrir cada `.blend`.
3. El consumidor propaga campo por impacto y suma coherentemente los puertos.

El oráculo no importa consumidor, `bpy` ni matrices aprendidas. La construcción
de las escenas pequeñas reutiliza el fixture sintético de pruebas; no es una
reproducción independiente de toda la red entrenada. Se contrasta también con
las leyes cerradas de interferencia de una celda, independientes del raycast.

| Tratamiento guardado/reabierto | Potencia Y medida | Máximo error de campo frente al oráculo |
|---|---:|---:|
| Base, lambda 0,100 BU | 1,40e-11 | 3,74e-6 |
| Fase r1 +0,1 rad | 0,002498291 | 3,74e-6 |
| Lambda 0,101 BU | 0,339583603 | 3,01e-6 |
| Color visual cambiado | Igual a base | 3,74e-6 |
| Techo r1/r2 +0,0125 BU | 0,500012872 | 8,22e-6 |

Cada caso produjo cuatro caminos, once raycasts, primer impacto emparejado.
Distancia máxima frente al oráculo 1,49e-6 BU; error máximo de potencia contra
ley cerrada 1,29e-5; error máximo de balance 2,44e-11; sham complejo exactamente 0.
Umbrales fijados antes de ejecutar: campo 2e-3, distancia 5e-6 BU,
potencia/balance 1e-4. Corrida `rc=0`, proceso cerrado, reserva liberada.

## Mejoras del sistema de verificación

- Escape es un canal declarado: suma de campos antes de potencia, no suma de
  intensidades de caminos. Dos rutas que se cancelan no deben inventar pérdida.
- Referencia de fase común para detector/escape. Una llegada oblicua necesita
  transportar fase desde el impacto hasta la referencia; prueba de regresión
  detecta el error si se omite.
- Rayos perdidos, geometría no declarada, caras degeneradas, impactos ambiguos,
  propiedades ausentes y mezcla de direcciones fallan explícitamente.
- 40 pruebas CPU sintéticas (0,080 s) más este smoke real. No equivalen a 40
  experimentos Blender ni a validación de redes generales.

## Evidencia reproducible

Código: `Blender/tests/exp005_runtime_smoke.py`, `run_exp005_smoke.py`,
`exp005_triangle_oracle.py`, `exp005_scene_readback.py`, `exp005_scene_properties.py`.
Artefactos locales nuevos, sin tocar conf1 ni Iris:
`D:/PROJECTS/.cognition/neuro3d/exp005/smoke_20260929_2104/`:
`runtime_smoke.json`, cinco snapshots, historiales bpy/oráculo, cinco `.blend`, log.
El nombre de carpeta es identificador, no la hora exacta de inicio (21:01 UTC).
Hashes de escena y código están en el JSON; hash de script ejecutado:
`95af7660629406674fea0e39d52f0af2aae54541e1dc4f058e72e5427afe0ab6`.

## Límites y siguiente gate

La interferencia sigue siendo aritmética Python digital, no ondas calculadas por
Cycles ni computación óptica física. El modelo escalar usa divisores ideales
50/50, espejos sin pérdida y un modo coherente por puerto; no Maxwell/difracción.
La fase/lambda ahora proceden realmente del archivo de escena, en este fixture.

Antes de una promoción multicelda: crítica independiente de Claude, geometría
nueva triangulada, paridad de escena completa y prueba de ortogonalidad/energía
de todos los modos y superposiciones; fixture/umbrales congelados previamente.
JEV continúa bloqueado por revisión de seguridad: fallback local sin aval remoto.
