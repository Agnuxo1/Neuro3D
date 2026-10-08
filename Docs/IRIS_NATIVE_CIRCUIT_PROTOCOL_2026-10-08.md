# Punto 6: protocolo prospectivo de ejecución nativa del circuito Iris

La red congelada corresponde a `Blender/demo_lattice_iris/trained_lattice.json`: 16 celdas Mach–Zehnder, 8 modos, 16 fases, haz de referencia y ganancia escalar; 150 muestras con partición guardada 120/30 y scaler ajustado sólo al entrenamiento. No se sustituye por el prototipo Clements de otro directorio.

## Alcance declarado antes de ejecutar GPU

El primer hito ejecutará **todo el circuito escalar canónico** mediante compute OpenGL nativo, a partir de características sin escalar, pesos, scaler y constantes de geometría. El shader hará escalado, normalización, todas las celdas locales, propagación de fase, ocho campos y potencias, tres logits y decisión. No recibirá una matriz global aprendida, campos calculados en CPU, predicciones ni etiquetas de verdad.

Esto es `GPU_ALGEBRAIC_CIRCUIT`. No afirma recorrido de triángulos GPU ni óptica física. El punto 6 permanecerá abierto si falta cerrar su integración con la geometría entrenada. La ruta geométrica requiere su propio readback completo y certificado; el éxito de este circuito no se utilizará para inventarlos.

## Entradas, controles y aceptación

- Activos originales congelados por SHA256; sus bytes y particiones no se modifican.
- Tres paquetes: baseline; fase de la celda 0 incrementada 0.1 rad; sham de payload idéntico al baseline, con nonce nuevo. Cada uno contiene las mismas150 características originales y los parámetros ópticos explícitos. No incluye etiquetas.
- Cada dispatch debe devolver las150 filas, campos de los8 modos, potencias, amplitudes codificadas, logits y decisión. Header, nonce/complemento, completion y conteo16 celdas deben comprobarse; echo idéntico en todos los bytes, readback almacenado antes de evaluar valores.
- Auditor independiente posterior con referencia de alta precisión: amplitudes<=1e-12, campo complejo L1<=1e-11, potencias<=1e-11, logits<=1e-9, y todas las decisiones coincidentes. Toda fila y salida cuentan; no basta acertar clases.
- El baseline debe reproducir117/120 y29/30 de la partición histórica. No se presenta como generalización nueva ni se utiliza el holdout para retocar pesos.
- La intervención de fase debe cambiar algún campo > 1e-3 y coincidir con su referencia; sham debe preservar los bits numéricos de salida. Cualquier resultado negativo se conserva y no cierra el punto.
- Supervisor versionado conserva la admisión, cola exclusiva gpuq, proceso privado, límite 100 s, presupuestos host/device <= 2 GiB, reserva RAM 4 GiB, temperatura <= 80 °C, VRAM global <= 18 GiB, fijación de fuentes y limpieza. Sólo se adapta la validación tipada del payload/recibo nuevo; no se modifica el supervisor original.

## Equivalencia algebraica y reducción

El circuito es un DAG de puertos locales `ax(i,j)` y `ay(i,j)`. Cada puerto tiene posición, dirección, longitud de onda y referencia de fase comunes; todas las contribuciones anteriores se acumulan como campos complejos, con sus fases de propagación incluidas. El operador futuro del puerto es idéntico para cada prefijo. Por la prueba del punto 5, esa reducción es lineal y no equivale a sumar intensidades ni eliminar caminos por amplitud. La implementación nativa deberá evaluar cada una de las16 celdas y todas sus conexiones, sin cargar la matriz global `U` que la rutina de entrenamiento construye en CPU.

La codificación conserva características negativas que puedan aparecer fuera del rango del scaler de entrenamiento; no introduce un clamp nuevo. La amplitud de referencia impide una normalización nula. La ganancia positiva no modifica argmax, pero sus logits se calcularán y verificarán en GPU para conservar la ejecución completa.

La fuente técnica de la representación FP64/packing es la [especificación oficial GLSL 4.50](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.50.pdf). La exactitud numérica del shader se aceptará sólo tras readback y auditoría, no por el nombre del tipo ni por compilación. Este es un protocolo prospectivo local, sin registro externo ni revisión por pares.
