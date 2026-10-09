# Selección espacial exacta: controles de software

El piloto congelado agotó 90 segundos sin producir resultado. Se implementa por separado un índice de cajas por objeto para reducir los triángulos enviados al selector racional. **No reemplaza el worker archivado, no convierte el piloto en éxito y todavía no tiene una ventaja de coste medida sobre la captura completa.**

El método de cajas envolventes es un antecedente estándar de aceleración, descrito en [PBRT, cuarta edición](https://pbr-book.org/4ed/Primitives_and_Intersection_Acceleration/Bounding_Volume_Hierarchies). Esta implementación usa cajas racionales cerradas por objeto, sin jerarquía BVH ni código copiado de PBRT. No se reivindica originalidad por ese ingrediente.

## Conservación de todos los candidatos

Cada vértice de cada triángulo pertenece a la caja de su objeto. La caja es convexa: contiene el triángulo entero. Si el rayo toca ese triángulo con parámetro `t ≥ 0`, también toca la caja. El recorte exacto de las tres bandas conserva todos esos parámetros. Por tanto, descartar únicamente cajas con intersección vacía no puede descartar un hit geométrico del modelo representado.

Se conservan extremos cerrados, ejes de dirección cero, contactos en `t=0`, coplanaridad, empates y huecos arbitrariamente pequeños. Los triángulos candidatos mantienen su orden original; el selector exhaustivo anterior decide interiores, abanicos, exclusión de contacto previo y reflexión. Se rechaza geometría degenerada y la reutilización del índice con otra lista geométrica.

## Evidencia y alcance

Pasan **74 controles**: ocho nuevos del índice y 66 del contrato, captura, ingreso, abanicos y supervisor. Los nuevos controles incluyen 160 consultas racionales con semilla 1940 comparadas con la selección exhaustiva, hueco `2^-120`, contacto, borde, empate, coplanaridad, salida perdida, retorno positivo y las dos ramas no nulas del divisor. La comparación de recorridos de fixtures conserva todos los campos del resultado anterior. También pasaron los 17 controles históricos de multicamino y ocho de abanicos junto con la primera versión de los siete controles del índice.

El primer comando de esos controles históricos falló por el import de `exp005_chain_fixture` al faltar `Blender/tests` en la ruta Python; la ejecución corregida pasó. Los controles nuevos usan fixtures propias y se ejecutan desde la raíz sin ese ajuste. El [recibo](validation/exact-object-index-2026-10-09/controls-receipt.json) y el [índice de fuentes/logs](validation/exact-object-index-2026-10-09/artifact_index.json) documentan el control final de 74 tests.

La paridad con el selector anterior valida una optimización del mismo modelo; no es una referencia óptica independiente ni una cota del error nativo/GPU. No hay poda de amplitud, normalización automática o reducción de coherencia. Las estadísticas cuentan consultas, cajas y oportunidades de prueba de triángulos; no sustituyen la medición de preparación, ejecución y lectura completas.

```text
python -m unittest Blender.tests.test_exact_object_index_v1 -v
```

Código: [índice](../Blender/benchmarks/capacity_audit/exact_object_index_v1.py). El hook optativo en el motor vivo conserva el selector original por defecto. El protocolo congelado utiliza su propia preimagen intacta, sin ese hook.
