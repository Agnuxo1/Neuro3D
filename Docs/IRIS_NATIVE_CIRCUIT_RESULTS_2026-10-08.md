# Punto 6: red Iris completa ejecutada y evaluada en GPU nativa

**Cerrado para el circuito escalar canónico congelado**, con puente geométrico verificado. No certifica recorrido de triángulos GPU, la captura Blender float32, RT, Maxwell, fabricación ni aprendizaje enhardware físico. Esas rutas tienen requisitos adicionales en los puntos7/10/19–23.

## Evidencia reproducible

El job `native02` evalúa las150 muestras originales en cada uno de los tres controles prospectivos, con las16 celdas,8 modos y18 parámetros guardados. EnGPU se calculan scaler de entrenamiento, normalización, referencia, operaciones locales de splitters/espejos, fases y conexiones, ocho campos/potencias, tres logits con ganancia entrenada y argmax. El payload sólo contiene características crudas, pesos, scaler y constantes locales; no se carga una matriz global, resultados CPU ni etiquetas.

Auditor separado sin imports del productor/Blender/GL: matriz de transferencia construida después del readback mediante coeficientes analíticos 2x2 a 90 dps, frente a las operaciones de splitters/espejos del shader. Compara cada campo, potencia, amplitud, logit y decisión de las450 filas. Sus criterios empíricos no constituyen un certificado riguroso de toda la aritmética nativa ni una medición física.

|Comprobación|Resultado|
|---|---|
|Dispatches/readbacks completos|3/3; 150 filas * 8 modos por caso|
|Decisiones frente a referencia|450/450 coincidentes|
|Error máximo de amplitud|1.991e-16|
|Error máximo de campo complejoL1|1.282e-13|
|Error máximo de potencia|3.323e-14|
|Error máximo de logit|3.202e-12|
|Desequilibrio máximo de energía ideal|2.554e-15|
|Baseline histórico entrenamiento|117/120 = 97.5%|
|Baseline histórico test guardado|29/30 = 96.6667%|
|Intervención theta0 + 0.1 rad|cambio máximo de campo 0.0461345; referencia coincidente|
|Sham|todos los bits numéricos idénticos; nonce nuevo|
|Supervisor|PASS; exit 0; cleanup_confirmed=true|

No es una nueva estimación de generalización: conserva una partición histórica pequeña, usada previamente. No se cambian pesos tras observar su test. El margen mínimo de clases de baseline es 0.0002496185, muy por encima de los errores observados en potencia.

## Integración con geometría y justificación de reducción

`verify_iris_geometry_bridge_v1.py` construye los104 objetos ópticos/208 triángulos del **plano geométrico canónico racional** de la red aprendida. El desplazamiento de r1/r2 de cada celda se deriva de la fase guardada; conserva los incrementos irregulares X/Y, entradas/salidas y planos de referencia. Para baseline y fase explora exhaustivamente136 estados geométricos únicos, resolviendo cada first-hit con Fraction y sin bias/epsilon. Todos los objetos/celdas/puertos quedan alcanzados, sin contacto ambiguo ni descarte por amplitud; la ordenación topológica demuestra un DAG completo.

En cada estado se pueden reducir prefijos únicamente porque comparten punto, dirección, plano anterior y operador futuro. Sus fases de longitud ya se aplican al campo local antes de sumar. La inducción sobre el orden topológico y la linealidad del siguiente operador prueban equivalencia entre el grafo y la enumeración de caminos; el punto 5 documenta las condiciones. No se suman intensidades ni se carga una matriz global en GPU.

La composición de todos los enlaces geométricos a 90 dps coincide con los 64 coeficientes del modelo canónico con error máximo<=2.701e-16. Ese residual incluye distinguir el pi binary64 original usado para el desplazamiento y el pi de la referencia de fase. La verificación de first-hit/topología es exacta; la comparación numérica del operador es diagnóstica. Esto vincula el circuito GPU con la geometría canónica aprendida. La geometría exportada por Blender usa transformaciones/vertices float32 y requiere su propio presupuesto de error: no hereda automáticamente esta precisión.

## Ensayo negativo y límites

`native01` obtuvo transporte/supervisión PASS, pero su auditor numérico FAIL. Arrays privados mostraron pérdida de precisión hasta valores binary32; campos fuera de umbral. Se conservan los bytes, fuentes, auditor y diagnóstico. El cambio prospectivo a arrays shared FP64 con una única invocación y768 bytes conservó algoritmo, entradas y umbrales; `native02` superó el mismo auditor. Esto demuestra la corrección del resultado comprobado, sin afirmar una causa universal del fallo del controlador.

Worker1.0663 s y supervisor4.6934 s; reserva/payload explícito por dispatch 114944 bytes; readback agregado 246528 bytes. Son observaciones de este ensayo, **no coste completo, memoria máxima efectiva, energía ni ventaja**. El punto 16 debe incorporar preparación, compilación, cola, transferencias, auditoría y decisión con mediciones apropiadas. La ejecución serial de una invocación busca validez; no acredita escalado ni rendimiento.

## Recibos y huellas

- [Protocolo prospectivo](IRIS_NATIVE_CIRCUIT_PROTOCOL_2026-10-08.md) y [enmienda de almacenamiento](IRIS_NATIVE_STORAGE_AMENDMENT_2026-10-08.md).
- [WorkerGPU](validation/iris-native-circuit-2026-10-08/native02/worker.json):SHA256 `6dcd43b344960a275d3945b7d706d09c4fdaecfbf341d925387ee559f44589ce`.
- [Supervisor](validation/iris-native-circuit-2026-10-08/native02/guard.json):SHA256 `35d116e3879654e79adc44b65b4dc1e4c221fd5221255d84f61a636981b79ef5`.
- [Auditor independiente](validation/iris-native-circuit-2026-10-08/native02/independent_audit.json):SHA256 `21e06485be491d99d9938afc04a58b3207ce8ce7277380c68c33faeaa1517811`.
- Readback conjunto:SHA256 `0f48a27f8edf9567d7ef4e72126e356495ca21e05ef2bba2e7e2e55c57c8e34e`.
- [Puente geométrico](validation/iris-native-circuit-2026-10-08/geometry_bridge01/receipt.json) y [9 pruebas CPU de admisión/rechazo](validation/iris-native-circuit-2026-10-08/cpu_admission01/receipt.json).
- Ambos ensayos conservan preimágenes de fuentes. Las rutas absolutas históricas del job/guard identifican su ejecución original; no se alteran para fingir reproducción en otro checkout.

Producción requiere Blender 4.5.14/OpenGL nativo NVIDIA RTX 3090 en Windows; auditor y puente requieren mpmath 1.3.0. La reproducción desde checkout limpio y declaración general de dependencias se completará en el punto 9.
