# Punto 3: propagación multicamino completa de referencia

**Cerrado en el alcance CPU de óptica escalar ideal fijado antes de las pruebas.** La integración de la red completa en GPU continúa en el punto 6; las cotas del campo siguen en el punto 4. Los motores históricos conservan su alcance anterior.

## Resultado observado

- 17 pruebas de aceptación PASS, sin fallos ni errores.
- 41 estímulos analíticos independientes: 16 de K3 y 25 de K4. Error máximo de campo 1.1320881853012132e-13; balance máximo 1.3944401189291966e-13, ambos dentro del umbral preregistrado 1e-11.
- Las diez variantes K3/K4 alcanzan salidas declaradas. Los cambios de fase, geometría, transmisión y longitud de onda mantienen el efecto causal exigido; sham produce diferencia cero.
- Ocho ejecuciones adicionales mediante la interfaz JSON real conservan entradas, historiales exactos y resultados adversos. El hueco 2^-44 y la arista interior cubierta se resuelven; contacto independiente, empate, borde exterior, retorno cíclico, rayo perdido y modo incompatible se declaran explícitamente incompletos.

Recibos: [aceptación y 41 historiales](validation/robust-multipath-2026-10-08/attempt01/receipt.json), [interfaz y resultados adversos](validation/robust-multipath-2026-10-08/adverse01/receipt.json). El protocolo anterior al ensayo está en [MULTIPATH_EXACT_PREREGISTRATION](MULTIPATH_EXACT_PREREGISTRATION_2026-10-08.md).

## Implementación y significado

`Blender/benchmarks/capacity_audit/robust_multipath_v1.py` procesa directamente la escena existente, descubre impactos y ramifica transmisión/reflexión. No recibe una matriz aprendida, lista de caminos ni respuestas analíticas. La aritmética racional conserva intersecciones, orden, puntos y reflexiones. La norma cuadrada de la dirección permanece exactamente invariante; no se introduce sesgo espacial.

La longitud óptica se conserva simbólicamente como `phase_length_numerator / sqrt(direction_norm_squared)`. Cada camino contiene amplitud de fuente, producto racional de potencias, fase de espejos y giros de cuarto de vuelta. Esto permite certificar el campo posteriormente sin reconstruir una longitud ya redondeada.

Un contacto de salida sólo se excluye tras demostrar identidad de objeto y plano a parámetro cero. Se admiten retornos posteriores a la misma primitiva. Las aristas internas se aceptan con una prueba de cobertura mediante terceros vértices opuestos. Los casos sin interpretación óptica única mantienen candidatos e historial; `INCOMPLETE` siempre tiene `fields=null` y `powers=null`. Alcanzar un límite no equivale a terminar el cálculo.

No se fusionan caminos. Sólo se eliminan fuentes o ramas exactamente nulas. La potencia de entrada como suma de cuadrados presupone modos de entrada independientes; el balance observado corresponde a las cadenas declaradas, no prueba independencia de fuentes arbitrarias coincidentes.

## Reproducción e interfaz

Desde el checkout:

```text
python -I -B Blender/tests/run_robust_multipath_validation_v1.py --out <directorio_nuevo>
python -I -B Blender/tests/record_multipath_adverse_v1.py --out <otro_directorio_nuevo>
python -I -B Blender/benchmarks/capacity_audit/trace_exact_scene_v1.py --scene escena.json --out resultado.json
```

La interfaz devuelve código 0 sólo para recorrido completo y código 2 para recorrido incompleto, conservando el resultado. Acepta racionales JSON explícitos. El campo flotante sigue marcado `field_certified=false`: la geometría representada exacta no convierte automáticamente la fase aproximada en una magnitud certificada, ni constituye una medición física.
