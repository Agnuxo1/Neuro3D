# Preregistro P1-5 · benchmark v1 con conjuntos públicos y líneas base fuertes

Fecha de compromiso: 2026-10-09, antes de ejecutar las líneas base nuevas de esta carpeta. El registro externo (OSF o IPFS) está pendiente de autorización explícita del titular del proyecto; este commit es la marca temporal interna verificable en git.

## 1. Pregunta

¿Cuánto rinde el clasificador óptico frente a líneas base fuertes en conjuntos públicos independientes, y qué referencias deben fijarse antes de probar cualquier modelo óptico nuevo?

## 2. Conjuntos (4) y alcance del claim óptico

| Conjunto | Muestras | Atributos usados | Clases | Modelo óptico |
|---|---:|---|---:|---|
| Iris | 150 | 4 | 3 | Sí. Protocolo P0-4 (`Benchmarks/lineas-base/PREREGISTRO-P0-4.md`). |
| Wine | 178 | 4 de 13 (protocolo P0-4) | 3 | Sí. Protocolo P0-4. |
| Breast Cancer Wisconsin | 569 | 30 (todos) | 2 | **No.** Solo líneas base. |
| Digits (sklearn, 8×8) | 1797 | 64 (todos) | 10 | **No.** Solo líneas base. |

Fuente: conjuntos incluidos en scikit-learn 1.4.0 (sin descarga). Se registra el SHA-256 de los arrays `X` e `y` de cada conjunto al ejecutar.

**Declaración de alcance:** el modelo óptico actual tiene 3 detectores y 4 entradas. No se afirma nada sobre el óptico en Breast Cancer ni en Digits. Un modelo óptico para esos conjuntos requiere un preregistro propio.

## 3. Particiones

Para cada conjunto, 10 particiones estratificadas con semillas `20261009 + k`, k = 0..9:
- Iris: 120/30 (la misma convención que P0-4 en tamaño).
- Wine: 141/37.
- Breast Cancer: 80/20 (455/114).
- Digits: 80/20 (1437/360).

Los índices de cada partición se guardan con su SHA-256. Sin validación interna: no se elige nada con el conjunto de prueba.

## 4. Preprocesado

Escalado min-max ajustado solo con entrenamiento, sin recorte en prueba, para todos los modelos. Ningún otro preprocesado.

## 5. Modelos

**Líneas base de referencia (todos los conjuntos):**
- B1. Softmax lineal con L2 = 0,001 (`Blender/blender_lab/classifier_comparison_v1.py`, `fit_baseline`, configuración lineal).
- B2. SVM con núcleo RBF, C = 1, gamma = `scale`.
- B3. Random forest, 200 árboles, semilla de la partición.
- B4. MLP de una capa oculta de 32 unidades, `max_iter` = 500, sin parada temprana, semilla de la partición.

**Líneas base con igual número de parámetros (Iris y Wine, según P0-4):**
- B5. Softmax lineal de P0-4 (15 coeficientes nominales).
- B6. Softmax cuadrático de P0-4 (45 coeficientes nominales).

**Modelo óptico (solo Iris y Wine):** el protocolo de P0-4, sin cambios. Con 3 semillas de inicialización (1049, 1050, 1051) en todas las particiones. El análisis primario ya no usa una sola semilla (ver sección 7).

## 6. Hiperparámetros

Todos fijados aquí. Ninguna búsqueda sobre el conjunto de prueba. Los hiperparámetros de B2 a B4 son los valores por defecto indicados arriba.

## 7. Criterios de decisión

**Claim óptico (Iris y Wine):**
- El resultado óptico se resume como la **media de sus tres semillas** por partición. El resultado de una sola semilla es sensibilidad, no resultado primario. Esta regla se fija aquí porque la extensión de P0-4 mostró que una semilla puede sobreestimar el resultado.
- Superior: IC95 bootstrap inferior > 0 y p Holm < 0,05, frente a B5 y B6.
- Equivalente: IC95 contenido en [-0,02; +0,02], frente a B5 y B6.
- Inferior o inconcluso: cualquier otro caso.

**Referencias (todos los conjuntos):** para cada conjunto se reporta la exactitud media de B1 a B6 y, para cada línea base, la diferencia pareada frente a la mejor línea base de ese conjunto, con IC95 bootstrap (10 000 remuestreos, semilla 0). No hay criterio de superioridad entre líneas base: es descriptivo.

## 8. Métricas y análisis

- Exactitud de prueba (principal) y exactitud equilibrada (secundaria), por partición y modelo.
- Diferencias pareadas por partición; IC95 bootstrap; Wilcoxon bilateral; corrección de Holm dentro de cada conjunto para las comparaciones del claim óptico.
- Tiempo de CPU por modelo y partición (para el coste de P1-9).

## 9. Integridad

- Código y entorno: versiones de Python, numpy, scipy y scikit-learn registradas en el resultado.
- Cada resultado guarda el hash de sus entradas y el hash del código que lo genera.
- Los resultados se publican tal cual, incluidos los negativos.

## 10. Limitaciones conocidas (antes de ejecutar)

- Wine usa 4 de 13 atributos; el claim óptico vale solo para este codificado.
- Iris y Wine ya se ejecutaron en P0-4: los nuevos resultados de B1 a B4 son complementarios; el claim óptico de P0-4 no cambia.
- Las particiones se solapan entre sí: los IC subestiman la incertidumbre.
- La decisión de conjuntos se tomó con confianza JEV baja (0,19), y se registra así en `coordinacion/jev/`.

## 11. Registro externo (pendiente de autorización)

Plataforma objetivo: OSF (o IPFS). Contenido: este documento, `Benchmarks/benchmark-v1/` y el hash del commit. No se envía nada hasta autorización explícita.

## Enmienda 1 (2026-10-09, antes de ejecutar nada de esta carpeta)

La sección 3 decía que las semillas `20261009 + k` se aplican a todos los conjuntos. Eso contradice la sección 7: el claim óptico de Iris y Wine compara con B5 y B6 sobre las particiones de P0-4, y la comparación pareada exige las mismas particiones.

Corrección: para Iris y Wine, B1 a B6 usan las particiones de P0-4 (`Benchmarks/lineas-base/resultados/splits.json`, con SHA-256 registrado). Las semillas `20261009 + k` se aplican solo a Breast Cancer y Digits. Esta enmienda se comprometió antes de ejecutar ninguna línea base nueva.
