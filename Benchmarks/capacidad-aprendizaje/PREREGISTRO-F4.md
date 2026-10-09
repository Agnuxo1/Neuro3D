# Preregistro F4 · capacidad y aprendizaje de la familia pasiva

Fecha de compromiso: 2026-10-09, antes de ejecutar nada de esta carpeta. Frente 4 del mandato del usuario: condicionamiento, estabilidad y límites de la familia pasiva; reinicios; tareas adicionales.

## 1. Familia estudiada

Malla pasiva sin pérdidas de N modos (Clements, N capas, fases entrenables), entrada real en los modos de entrada y detección por potencia en K modos de salida con decisión argmax. Es la misma familia que P2-10 (ver `Benchmarks/escala-modos/PREREGISTRO-P2-10.md`), no la geometría capturada de Neuro3D. Esta diferencia se declara en cada resultado.

## 2. Preguntas e hipótesis

- **C1 (condicionamiento de la malla):** la matriz de transferencia de una malla sin pérdidas es unitaria. Predicción: κ(U) = 1 con error < 10⁻¹² para cualquier configuración de fases. Es una verificación; si falla, la implementación está mal.
- **C2 (condicionamiento de la entrada):** el número de condición de la matriz de Gram de las características escaladas (solo entrenamiento) de cada conjunto. Se reporta sin criterio de decisión: describe la codificación, no el modelo.
- **C3 (estabilidad frente a ruido de fase):** la exactitud de prueba del mejor reinicio, tras perturbar cada fase con ruido gaussiano de desviación σ ∈ {0; 0,01; 0,03; 0,1; 0,3} rad. **H3a:** la pérdida media de exactitud en σ = 0,03 rad es menor que 0,01 en los cuatro conjuntos. **H3b:** la exactitud decrece de forma monótona con σ (tolerancia de 0,005).
- **C4 (dispersión entre reinicios):** diez reinicios por partición con semillas 0 a 9. **H4:** la diferencia entre el mejor reinicio (elegido por pérdida de entrenamiento) y la mediana de los reinicios es menor que 0,01 de exactitud de prueba en la media de particiones. Si no se cumple, la familia es sensible a la inicialización y se declara.
- **C5 (límite de rango):** ya tratado en P1-8 (`Benchmarks/limite-lectura/`). No se repite aquí.

## 3. Conjuntos y particiones

- **Iris** (4 atributos, 3 clases) y **Wine** (4 de 13 atributos, 3 clases): las particiones de P0-4 (`Benchmarks/lineas-base/resultados/splits.json`).
- **Breast Cancer Wisconsin** (30 atributos, 2 clases) y **Digits** (64 atributos, 10 clases): 10 particiones estratificadas 80/20 con semillas `20261009 + k`, k = 0..9 (mismas que en P1-5 y P2-10).
- Reducción de atributos: PCA ajustado solo con entrenamiento hasta el número de modos de entrada: N = 8 para Iris, Wine y Breast Cancer; N = 16 para Digits. Iris y Wine usan 4 entradas en 8 modos (cuatro modos de entrada a cero).
- Detectores: K = número de clases.

## 4. Protocolo de entrenamiento

- Escalado min-max ajustado solo con entrenamiento, luego normalización a potencia unitaria.
- Entrenamiento: máxima verosimilitud softmax sobre P_k / T con T = 0,05; Adam, tasa 0,01, 2000 pasos.
- Diez reinicios por partición (semillas 0 a 9); la selección del reinicio para C3 se hace por pérdida de entrenamiento, nunca por prueba.
- Gradiente analítico, verificado contra diferencias finitas antes de cualquier resultado.

## 5. Medidas y análisis

- C1: κ(U) y error de unitariedad por configuración de fases (una por reinicio).
- C2: κ(Gram) por conjunto, media y mediana sobre particiones.
- C3: exactitud de prueba media y desviación para cada σ; cinco extracciones de ruido por fase y por partición. IC95 bootstrap sobre particiones (10 000 remuestreos, semilla 0) para la pérdida frente a σ = 0.
- C4: exactitud de prueba por reinicio; la diferencia mejor − mediana por partición; IC95 bootstrap; Wilcoxon bilateral.
- Tiempo de CPU por entrenamiento (para P1-9).

## 6. Controles

- Control de cordura: la unitariedad de C1 debe cumplirse; si no, todo el experimento se declara inválido.
- Control de ruido: σ = 0 debe reproducir exactamente la exactitud del reinicio elegido.

## 7. Integridad y límites

- CPU sin GPU. Versiones de Python, numpy, scipy y scikit-learn en el resultado. Hashes de entrada y salida.
- Límite: la familia es la malla de P2-10, no la geometría capturada de Neuro3D. Ninguna conclusión sobre el dispositivo físico.
- Los resultados negativos se publican tal cual.
