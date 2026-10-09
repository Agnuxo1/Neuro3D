# Métodos más cercanos a C1+C2+C3 · P1-6

Ejecución del 2026-10-09 según `PROTOCOLO-BUSQUEDA-P1-6.md`. Selección sobre la tabla `EXTRACCION-P1-6.json` (marcas basadas en título y resumen; no se leyó el texto completo de ninguno). Orden: de más a menos cercano a la combinación C1+C2+C3. Descripciones en palabras propias.

Ninguno de los ocho cumple C1+C2+C3. Solo el primero toca a la vez C1, C2 y C3, y lo hace de forma parcial.

| # | Trabajo | Identificador | C1 | C2 | C3 | C4 |
|---|---------|---------------|----|----|----|----|
| 1 | Universal Function Approximation via Diffractive Optical Processors | arXiv:2608.04582 (2026) | sí | parcial | parcial | no |
| 2 | Unified, Verifiable Neural Simulators for Electromagnetic Wave Inverse Problems | arXiv:2404.00545 (2024) | no | parcial | parcial | no |
| 3 | Inverse Design of Unitary Transmission Matrices in Silicon Photonic Coupled Waveguide Arrays | arXiv:2409.18284 (2025) | sí | sí | no | no |
| 4 | Scalable Photonic Neural Networks via Surrogate Scattering-Matrix Inverse Design (y registro de título casi idéntico: doi:10.1002/nap2.70302) | arXiv:2604.21301 (2026) | sí | sí | no | no |
| 5 | Efficient multi-body shape optimization of on-chip nanophotonic neural network | doi:10.1038/s44310-026-00144-2 (2026) | sí | sí | no | no |
| 6 | ADEPT: Automatic Differentiable DEsign of Photonic Tensor Cores | arXiv:2112.08703 (2021) | parcial | parcial | no | no |
| 7 | Unified ray-wave model for end-to-end imaging in refractive-diffractive hybrid optics | doi:10.1364/oe.583744 (2026) | no | sí | no | parcial |
| 8 | DiffRayve: Differentiable Ray-Wave Method for Polarized and Unpolarized Diffractive-Refractive Optical Systems | arXiv:2609.16404 (2026) | no | sí | no | parcial |

Los números 4, 5 y 8 no entran en el criterio mecánico de inclusión del protocolo (solo un grupo de términos en título y resumen); se añadieron tras revisión manual y se cuentan aparte (ver VEREDICTO).

## 1. Aproximación universal con procesadores ópticos difractivos (arXiv:2608.04582)

- **Qué hace.** Trabajo teórico: relaciona la teoría de aproximación universal con procesadores difractivos de fase y coherentes, y deriva cotas analíticas del error de aproximación, límites de presupuesto de fotones y de aprendizaje, y el efecto de la iluminación incoherente.
- **Qué comparte.** Óptica coherente con propagación difractiva (C1) y cotas explícitas de error (C3 parcial). Las cotas separan fuentes de error (truncación, síntesis, ruido, lectura).
- **En qué difiere.** Las cotas son analíticas y de clase de funciones, no cotas numéricas verificadas sobre la salida de una instancia concreta de red. No entrena posiciones ni geometría de una escena (C2 solo parcial: optimiza máscaras/PSF). No usa una escena capturada (C4 no). Es el trabajo que más se acerca a C3 en espíritu, pero no certifica salidas.

## 2. Simuladores neuronales verificables para problemas inversos electromagnéticos (arXiv:2404.00545)

- **Qué hace.** Un simulador neuronal único para dispersión electromagnética con miles de grados de libertad. Demuestra una cota superior del error de predicción calculable en tiempo constante, que da garantía de precisión en inferencia, y lo usa en diseño inverso fotónico de forma libre.
- **Qué comparte.** Cota rigurosa de error (C3 parcial) junto con optimización de geometría de estructuras (C2 parcial).
- **En qué difiere.** La cota se refiere al error de un simulador sustituto, no a la salida de una red óptica. No es una red óptica con detección por potencia y argmax (C1 no). Geometría de materiales/dispositivo, no de una escena de render. Sin C4. Es el único caso donde aparecen a la vez cota rigurosa y diseño inverso de geometría; sirve como antecedente directo de C3 por analogía, no como anticipación.

## 3. Diseño inverso de matrices de transmisión unitarias en arrays de guías acopladas (arXiv:2409.18284)

- **Qué hace.** Diseña por optimización con gradiente, apoyada en una red sustituta, patrones de perturbación del índice de refracción en una matriz de guías de onda para implementar matrices unitarias 3x3 (fidelidad media 0,94).
- **Qué comparte.** Operación coherente lineal unitaria (C1) y entrenamiento de la geometría del dispositivo (C2).
- **En qué difiere.** Geometría de dispositivo integrado (patrón de perturbación), no posiciones o retardos en una escena de render. Evalúa fidelidad, sin cotas de salida (C3 no). Sin escena capturada.

## 4. Redes fotónicas escalables por diseño inverso con matriz de dispersión sustituta (arXiv:2604.21301; doi:10.1002/nap2.70302)

- **Qué hace.** Separa el aprendizaje de la tarea (resuelto en espacio de matrices con operador complejo de valores singulares acotados) de la realización electromagnética (geometría libre ajustada con un problema adjunto). Valida con clasificación de imágenes.
- **Qué comparte.** Red óptica coherente de operadores complejos (C1) con geometría entrenada por gradiente adjunto (C2).
- **En qué difiere.** La cota sobre valores singulares es una restricción de diseño, no un certificado sobre la salida. El solver es de onda completa sobre un dispositivo, no un trazado de rayos sobre una escena leída de Blender. Sin C3 ni C4. Este y el siguiente son los más próximos a C1+C2 con geometría realmente entrenada.

## 5. Optimización de forma de múltiples cuerpos en una red nanofotónica en chip (doi:10.1038/s44310-026-00144-2)

- **Qué hace.** Optimiza la forma y disposición de dispersores elípticos de una red neuronal nanofotónica con una estrategia de desacoplo lineal que evita simular Maxwell completo en cada paso; valida en Iris y MNIST.
- **Qué comparte.** Red óptica (C1) y parámetros de posición/forma de elementos entrenados (C2), lo más parecido a "posiciones de elementos".
- **En qué difiere.** Entorno de simulación FDTD de dispositivo, no escena capturada. Sin certificado de salida (C3 no). Sin evidencia en el resumen de intervalos o cotas.

## 6. ADEPT: diseño diferenciable de núcleos tensoriales fotónicos (arXiv:2112.08703)

- **Qué hace.** Marco totalmente diferenciable que busca topologías de núcleos tensoriales fotónicos adaptadas a restricciones de área y a la tecnología de fabricación; reporta mayor compacidad y mejor robustez al ruido.
- **Qué comparte.** Diseño de la estructura de una red fotónica por descenso de gradiente (C2 parcial, topología más que posiciones).
- **En qué difiere.** Busca arquitectura de circuito, no coordenadas de una escena. La robustez al ruido es empírica, no una cota verificada. Sin C4.

## 7. Modelo unificado de rayos y ondas para imagen extremo a extremo (doi:10.1364/oe.583744)

- **Qué hace.** Modelo diferenciable que une trazado de rayos geométrico (ley de Snell generalizada) con propagación de onda y permite aprender los parámetros ópticos junto con la red de reconstrucción (corrección de aberraciones, profundidad de campo extendida).
- **Qué comparte.** Entrenamiento de geometría óptica mediante trazado diferenciable (C2) y mezcla de rayos y ondas, la parte más cercana a la idea de propagar sobre geometría evaluada.
- **En qué difiere.** Es óptica de imagen con red digital posterior, no una red óptica coherente con decisión por argmax (C1 no). Sin certificados (C3 no). La geometría proviene de un modelo de diseño óptico, no de una escena de Blender.

## 8. DiffRayve: método diferenciable de rayos y ondas con polarización (arXiv:2609.16404)

- **Qué hace.** Algoritmo de disparo y rebote de rayos totalmente diferenciable que modela óptica geométrica y física a la vez, para optimizar sistemas refractivos-difractivos polarizados; demuestra el diseño de una lente acromática de gran campo con varios elementos difractivos.
- **Qué comparte.** Trazado de rayos diferenciable que permite entrenar la geometría de elementos ópticos (C2) con estilo de render.
- **En qué difiere.** Aplicación de diseño de lentes, sin red neuronal óptica (C1 no) ni cotas (C3 no). Es el antecedente más claro de que "render diferenciable + elementos ópticos entrenables" ya existe como técnica, separada de C1 y C3.

## Lectura conjunta

Los componentes C1, C2 y C4 (en su forma parcial: trazado de rayos diferenciable sobre geometría) aparecen por separado y, en el caso de C1+C2, también juntos en diseño inverso de dispositivos nanofotónicos (métodos 3 a 5). Ningún resultado combina esos dos con certificados de intervalo sobre la salida de la red (C3), ni con una escena leída desde una herramienta estándar como Blender (C4). Los trabajos 1 y 2 tocan cotas, pero sobre aproximación teórica o sobre el error de un simulador, no sobre la salida de la red óptica.
