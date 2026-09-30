# Cascada v4: fixture plano representable, gates sin relajar

30/09/2026 00:34UTC. Fallback local, JEV bloqueado. V1/v2/v3 FAIL preservados.
V3 ya devuelve TODOS los puertos, campo basis2 error2,42e-9 y balance3,33e-16,
pero segmento difiere1,0013554e-5BU>1e-5BU. NO aprobar por diferencia pequeña.

Nuevo fixture explícito, no edición retroactiva: superficies rectangulares de
dos triángulos, offsets binarios±0,125BU en tangente cruda y Z. Los centros,
normales ideales, fuentes, roles, fases, λ y cableado siguen iguales. El fan
de12triángulos con senos/cosenos redondeados en world float32 NO es exactamente
coplanar al trasladarse: dos implementaciones pueden elegir distinta cara
en el centro y divergir. El nuevo fixture evita ese presupuesto de discretización;
no proyecta rayos a ejes diseñados ni cambia el oráculo o la distancia medida.

Regresión CPU adicional: todos los quads se redondean a float32 explícitamente;
coplanaridad exacta y campos contra composición<=1e-12. La opción anterior
disk sigue disponible por defecto, conservada con sus resultados.
Runtime usa explícitamente surface=binary_quad. Nuevo runner/fixture congelados
antes de medir. Ni error de campo2e-3, potencia1e-4, segmento1e-5 ni sham/
causalidad cambian; seis tratamientos/54probes completos comoV1.

Carpeta NUEVA `D:/PROJECTS/.cognition/neuro3d/exp005_cascade_cpu_v4_20260930_0035/`.
Mismo guard/cola/120s/1hilo/RAM4/VRAM18/temp80/cierre06UTC. Alcance híbrido
CPU, sin render/RT; no cierra EXP-005completo ni ortogonalidad física de modos.
Claude: contrasta el nuevo fixture/coplanaridad y todos los campos. No confundir
corrección del fixture con validación de los discos de v1/v2/v3, que siguen FAIL.
