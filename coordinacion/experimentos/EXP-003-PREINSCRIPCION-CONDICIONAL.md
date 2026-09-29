# EXP-003 · Longitud de camino obtenida de geometría 3D

Estado: **preinscripción condicional, no ejecutada** (2026-09-29). La
prueba es un escalón híbrido CPU: Blender decide impactos y distancias
mediante `ray_cast`/BVH sobre espejos de la escena; código numérico suma
amplitudes complejas y detecta intensidades. **No** acredita que la luz
de Blender calcule por sí sola, fotónica física, ni una red 16×16.

## Pregunta falsable

¿Puede la geometría de una línea de retardo de dos espejos cambiar la
longitud óptica que entra en una celda Mach–Zehnder, sin introducir una
fase de fórmula desvinculada de los impactos? Toda fase usada por el
combinador debe derivarse de la suma de segmentos trazados desde matrices
de objetos reabiertos, con un registro por impacto (objeto, punto,
dirección, longitud, status). Si falta un impacto, se declara pérdida; no
se usa un valor analítico de respaldo.

Antes de lanzar el primer caso, fijar y revisar en Git las coordenadas,
normales, radios, orden de impactos, fuente y detectores de la escena base.
La misma geometría congelada se usa en todos los controles; no se ajusta
después de ver resultados. Partir de una sola celda, fuente unitaria,
`λ = 0,1 BU`, coherencia 1 y absorción 0. La malla OPT-007 y cualquier
clasificador quedan **fuera** de este gate.

## Intervenciones y aceptación congeladas

1. Desplazamiento normal coordinado de la pareja de espejos:
   `d ∈ {0; 0,0025; 0,005} BU`. Exigir todos los impactos previstos,
   `ΔL = 2d` respecto de `d=0` con error absoluto ≤`1e-4 BU`, y
   `Δφ = 2π·ΔL/λ` con error ≤`1e-2 rad`. Para la celda ideal cuyo
   puerto A base es oscuro, comparar `P_A` con
   `sin²(Δφ/2)` a ≤`1e-3` de potencia; el puerto B complementa.
   La referencia solo evalúa el resultado; no alimenta la inferencia.
2. **Sham:** mover la pareja `0,01 BU` tangencial a los planos de espejo
   sin cambiar su camino. Exigir `|ΔL|≤1e-4 BU` y
   `|ΔP_A|≤1e-3`; si un rayo deja de impactar, el control falla.
3. **Ablación:** retirar uno de los espejos del camino. Exigir status de
   impacto perdido y registrar esa potencia como escape/no detectada;
   nunca devolver el resultado de la fase analítica como si hubiera rayo.
4. Para los casos con dos brazos válidos: potencia total de ambos puertos
   más escape y absorción igual a la entrada dentro de `1e-6`; potencia
   no resuelta cero dentro de `1e-9`. Guardar y reabrir la escena, reconstruir
   impactos y potencias; matrices mundiales a ≤`1e-6 BU` y potencia de
   cada puerto a ≤`1e-3` del registro previo al guardado.

Registrar tanto los fallos como las medidas. No cambiar umbrales ni
geometría para convertir un fallo en éxito; cualquier variante posterior
será otro experimento. Un éxito demuestra **dependencia causal del trazado
geométrico en un modelo híbrido**, no que el modelo 3D haga toda la
aritmética óptica. La siguiente promoción requiere revisión técnica
independiente del trazador y una vía explícita para acumulación/interferencia
en la propia escena o en un shader gobernado por esa escena, no una malla
matricial de NumPy disfrazada de objetos.

## Recursos y autorización

Diseñar, revisar y escribir pruebas puras puede hacerse con CPU ligera.
El usuario autorizó expresamente en este hilo el 2026-09-29 a usar GPU y
Blender para las pruebas necesarias. Antes de cada ejecución hay que
comprobar recursos y reserva `gpuq`, coordinar con Claude y fijar límites;
la autorización no sustituye los gates científicos ni justifica una carga
innecesaria. El experimento inicial sigue preinscrito como Blender CPU;
una variante GPU/render exige protocolo separado. Antes de ejecutar,
Codex comprueba que ninguna potencia esperada se inyecte en el trazador.
