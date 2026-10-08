# Punto 5: justificación cerrada de las operaciones activas

La [demostración](PATH_OPERATION_PROOFS_2026-10-08.md) cubre cada equivalencia, exclusión y reducción aplicada por la referencia completa y su certificado. El motor no fusiona historiales distintos ni poda por umbral de amplitud. Una optimización futura queda condicionada a demostrar igualdad del estado de continuación, referencia/coherencia y presupuesto de error.

El [recibo final](validation/path-operation-proofs-2026-10-08/attempt02/receipt.json) pasa ocho comprobaciones. Conserva el recorrido completo, campos y certificado de un puerto oscuro: dos caminos de potencia individual1/4, longitud5y7BU, norma de dirección1, longitud de onda1/8BU y giros0y2. Sus fases ópticas son40y56 ciclos; sus campos ideales son+1/2y-1/2. La cancelación se comprueba con aritmética gaussiana racional independiente de las funciones trigonométricas.

La suma incorrecta de intensidades sería0.5; la intensidad ideal coherente es0. La implementación flotante devuelve5.401864479965209e-29, y su certificado encierra la intensidad ideal0. Cambiar la fase del espejo en1e-6rad conserva ambos historiales y produce campo no nulo. Descartar caminos por la cancelación observada antes de modificar parámetros perdería ese comportamiento.

El mismo recibo muestra que4096 contribuciones de2^-20 en fase suman2^-8: un umbral por camino no es una cota del error total. Ningún ahorro de tiempo/memoria ni fusión general queda probado por estos ejemplos. Son testigos del inventario matemático, no réplicas estadísticas ni evidencia física o de novedad.

```text
python -I -B Blender/tests/verify_path_operation_proofs_v1.py --out <directorio_nuevo>
```

La siguiente implementación nativa completa deberá conservar estas condiciones o justificar sus cambios antes de validarse.
