# Preregistro P1-8 · límite de la lectura cuadrática de rango restringido

Fecha de compromiso: 2026-10-09, antes de ejecutar nada de esta carpeta. Un resultado negativo (no hay brecha) también se publica.

## 1. Teoría (se verifica numéricamente en la ejecución)

Entrada real x ∈ R⁴ (la misma dimensión que Neuro3D: cuatro atributos) con referencia constante, así que x̃ = (x, 1) ∈ R⁵.

Cada detector de potencia es P_k(x̃) = |a_kᵀ x̃|², con a_k ∈ C⁵. Entonces P_k(x̃) = x̃ᵀ (u_k u_kᵀ + v_k v_kᵀ) x̃, con u_k = Re a_k y v_k = Im a_k. Por tanto P_k es una forma cuadrática de **rango ≤ 2** en R⁵.

La frontera de decisión entre dos clases es x̃ᵀ (Q_i − Q_j) x̃ = 0, con rango ≤ 4.

Una frontera cuadrática general en R⁴ (la de un clasificador cuadrático completo, QDA) puede tener rango 5. Así, la lectura óptica con 3 detectores no puede representar en general todas las fronteras cuadráticas.

## 2. Hipótesis

- **H0 (sin límite práctico):** en tareas gaussianas con covarianzas distintas, la lectura óptica (O) iguala al clasificador cuadrático completo (Q) con diferencia menor que 0,02 en exactitud de prueba.
- **H1 (límite demostrado):** la diferencia Q − O es mayor que 0,02 con IC95 inferior > 0,02.
- **Control de cordura:** en tareas gaussianas con covarianza común (frontera lineal), la diferencia Q − O debe ser menor que 0,01. Si no lo es, la prueba no es válida y se declara.

## 3. Modelos

- **O (óptico, rango restringido):** 3 detectores P_k(x̃) = |a_kᵀ x̃|² con a_k ∈ C⁵; decisión argmax_k P_k. Entrenamiento: máxima verosimilitud softmax sobre P_k / T con T = 0,05; Adam, tasa 0,01, 3000 pasos, inicialización aleatoria con semillas 0 a 4; se elige el de menor pérdida de entrenamiento (no el de prueba). Escalado de x ajustado solo con entrenamiento.
- **Q (cuadrático completo):** QDA en forma cerrada (medias y covarianzas de cada clase con estimador de máxima verosimilitud, sobre entrenamiento).

## 4. Tareas

- **Tareas de frontera cuadrática (principal):** 40 tareas, semillas 0 a 39. Cada tarea: 3 clases gaussianas en R⁴ con medias aleatorias y covarianzas aleatorias distintas por clase (matrices SPD). N = 600 (400 entrenamiento, 200 prueba, estratificado).
- **Tareas de frontera lineal (control):** 40 tareas, semillas 100 a 139, covarianza común por clase.

## 5. Análisis

- Exactitud de prueba de O y Q por tarea. Diferencia Q − O por tarea.
- IC95 bootstrap sobre tareas (10 000 remuestreos, semilla 0) y prueba de Wilcoxon bilateral.
- Verificación de la teoría: rango numérico de (Q_i − Q_j) de los modelos O entrenados (debe ser ≤ 4) y de las matrices de QDA (rango 5 en la mayoría de tareas).

## 6. Decisión

- **Límite demostrado:** H1 cumplida en las tareas de frontera cuadrática, y control de cordura cumplido.
- **Sin límite práctico demostrado:** H0 no refutada en esas tareas. Se reporta el resultado tal cual.
- **Prueba inválida:** el control falla.

## 7. Integridad

- Semillas fijas (listadas), código y versiones de Python, numpy y scipy registrados. Hashes de los resultados. CPU, sin GPU.
- No se usa el conjunto de prueba para elegir nada.

## 8. Limitaciones

- Solo tareas sintéticas gaussianas. Un límite demostrado aquí no dice nada sobre Iris, Wine ni otros conjuntos reales.
- Q es óptimo solo si las clases son gaussianas; por eso se elige esa familia.
- Solo la lectura de rango 2 por detector. No se incluye una no linealidad de campo (ver P1-8, rama de no linealidad, fuera de este preregistro).
