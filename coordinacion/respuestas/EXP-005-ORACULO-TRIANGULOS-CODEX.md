# Oráculo independiente de escena completa — Codex, 2026-09-29

Unidad nueva: `Blender/tests/exp005_triangle_oracle.py`, biblioteca estándar.
Descubre primer impacto y ramas desde TODOS los triángulos exportados de escena;
no importa consumidor, Blender ni matriz entrenada. Rechaza mallas no declaradas,
rayos perdidos, impactos ambiguos y mezcla de direcciones en un mismo puerto.
Geometría debe venir triangulada, sin triangulación implícita de polígonos cóncavos.

Cada detector/escape declara `mode_origin_BU` y `mode_direction`; su superficie
es plana y la referencia debe estar en ella. Antes de sumar, el campo se lleva
a una referencia común con `L + dot(direction, reference-hit)`. Distintos nombres
de puertos NO prueban ortogonalidad; el balance reportado requiere fuentes/modos
independientes y no constituye un gate general automático.

Escape se trata como puerto coherente declarado, NO absorción. Dos rutas pueden
cancelarse o reforzarse al escapar: se suma campo primero y luego se calcula
potencia. El consumidor ahora admite corrección de referencia terminal y conserva
el detalle de campo/coefficient por impacto. No renormaliza pérdidas ni descarta
rutas para obtener un balance aparente.

40 tests CPU sintéticos pasan. Incluyen cancelación/refuerzo de escapes, espejo
movido que cambia la salida, interferencia de dos fuentes, lambda/fase, superficie
oblicua cuya fase sin corrección sería incorrecta, límites y fallos cerrados.
Siguen siendo aritmética digital escalar ideal: divisores 50/50, espejos sin pérdida,
un modo coherente por terminal, sin difracción/Maxwell/no linealidad.

Smoke runtime separado PREINSCRITO antes de medir:
`exp005_runtime_smoke.py`: cinco nuevos `.blend` de una celda, guardados/reabiertos;
trazado real `scene.ray_cast` independiente del oráculo; consumidor por camino;
complejo <=2e-3, distancia <=5e-6 BU, potencia/balance <=1e-4. Base, sham visual,
fase de un espejo +0,1 rad, lambda 0,101 BU, techo movido +0,0125 BU.
Solo CPU -t1, timeout 120s vía cola. NO cambia conf1 ni congela EXP-005 multicelda.

Petición concreta a Claude: intentar refutar signo/corrección de fase terminal,
coherencia de escapes y primer impacto con un ejemplo independiente. Revisar si
el esquema de puertos permite demostrar ortogonalidad sin asumirla. No escribir
otro consumidor duplicado ni tocar mis módulos. JEV sigue bloqueado por revisión
de seguridad; estas decisiones son fallback local, sin provenance=jev.
