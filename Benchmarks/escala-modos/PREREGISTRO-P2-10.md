# Preregistro P2-10 · escala a ≥ 64 modos con representación compacta

Fecha de compromiso: 2026-10-09, antes de implementar la malla y de ejecutar ningún entrenamiento.

## 1. Pregunta

¿Una malla óptica de 64 modos, representada de forma compacta, se puede evaluar con un coste que crece polinómicamente con el número de modos, y clasifica dígitos de forma competitiva frente a líneas base de parámetros comparables?

## 2. Representación compacta (sin caminos)

- Malla de Clements de N modos: N(N−1)/2 interferómetros Mach–Zehnder, cada uno con dos fases. Para N = 64 son 2016 interferómetros y 4032 fases.
- La matriz de transferencia se aplica por capas de acopladores 2×2 (N capas). Coste por entrada: O(N²). Almacenamiento: O(N²).
- La enumeración de caminos crece exponencialmente con el número de elementos; no se usa en esta prueba.

## 3. Hipótesis

- **V (verificación de implementación):** para N ≤ 8, la aplicación por capas coincide con la matriz de transferencia densa calculada a partir de los elementos, con diferencia máxima < 10⁻¹². Es una comprobación de código, no un resultado científico.
- **H2 (escala):** el tiempo de inferencia por entrada crece como N^p con p entre 1,8 y 2,2 en N = 8, 16, 32, 64 (ajuste log-log). El almacenamiento crece como N².
- **H3 (utilidad, dígitos):** con N = 64 modos y 10 detectores, la exactitud de prueba de la malla es igual o superior a la de una regresión logística multinomial (≈ 650 parámetros) con diferencia de intervalo ≥ −0,01 (IC95 inferior ≥ −0,03). Resultado de equivalencia o superioridad: **soportado**. Inferioridad: **no soportado**.
- **Control frente a MLP de parámetros comparables** (una capa oculta de 48 unidades, ≈ 3500 parámetros; comparable a 4032 fases de la malla): se reporta la diferencia sin criterio de decisión.

## 4. Datos y particiones

- Conjunto: `sklearn.datasets.load_digits` (1797 muestras, 64 atributos, 10 clases; incluido en scikit-learn 1.4.0, sin descarga).
- 10 particiones estratificadas 80/20 con semillas `20261009 + k`, k = 0..9. Índices con SHA-256.
- Preprocesado: escalado min-max de cada atributo ajustado solo con entrenamiento. Después, normalización de la entrada a potencia unitaria (‖x‖ = 1). La misma codificación para todos los modelos.

## 5. Modelos

- **Malla (N = 64):** entrada real en los 64 modos de entrada; detectores en los primeros 10 modos de salida; decisión argmax de las potencias. Fases iniciales aleatorias con semillas 0, 1 y 2. Entrenamiento por máxima verosimilitud softmax sobre P_c/T con T = 0,05; Adam, tasa 0,01, 2000 pasos. Se elige la semilla de menor pérdida de entrenamiento, no la de prueba. Gradiente analítico, verificado contra diferencias finitas.
- **Logística multinomial:** L2 = 0,001, misma codificación. Función objetivo convexa, sin semillas.
- **MLP:** una capa oculta de 48 unidades, `max_iter` = 500, sin parada temprana, semilla de la partición. Los avisos de no convergencia se registran.

## 6. Escala (H2)

N ∈ {8, 16, 32, 64}. Para N < 64, cada atributo se reduce a N componentes principales ajustadas solo con entrenamiento (la misma partición de la sección 4). Medición: tiempo de inferencia por entrada (promedio de 1000 evaluaciones tras calentamiento), memoria de las matrices, y ajuste log-log del tiempo frente a N.

## 7. Análisis y decisión

- Exactitud de prueba por partición y modelo. Diferencia malla − logística por partición; IC95 bootstrap (10 000 remuestreos, semilla 0) y Wilcoxon bilateral.
- Decisión de H3 según la sección 3. Ajuste de H2 con su intervalo de confianza.
- Resultados negativos se publican tal cual.

## 8. Integridad y límites

- CPU sin GPU. Se registran versiones de Python, numpy, scipy y scikit-learn, y el tiempo de CPU de cada entrenamiento (para P1-9).
- Límite: la malla se evalúa en dígitos con 10 detectores; no se afirma nada sobre la geometría de Neuro3D ni sobre hardware fotónico. El paso de 64 modos es escalado numérico de la representación, no una malla física fabricable.
- La estimación de la escala con cuatro puntos tiene poca precisión; el intervalo se declara.
