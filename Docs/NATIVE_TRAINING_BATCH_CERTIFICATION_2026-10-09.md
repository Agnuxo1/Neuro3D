# Certificación secundaria de las 150 salidas nativas del entrenamiento

Estado: preparado, no ejecutado. Se analizarán observaciones anteriores ya publicadas del entrenamiento propio dentro de Blender, sin obtener nuevas filas ni elegir semillas. Es una certificación matemática secundaria, no un ensayo neuronal confirmatorio nuevo.

[Perfil](research/native_training_batch_certificate_profile_2026-10-09.json), UUID `1a5ef921-d322-4e4f-b765-bff322428e3a`, SHA-256 `440c8cb2d06d011ba42af370a94c326b6d345f1cb748a83fc55a03828838b070`, 23 pins. [Recibo GitHub autorizado](research/native_training_batch_certificate_registration_2026-10-09.json); registro externo/IPFS pendiente, sin identificadores.

Se fijan campos, potencias, entradas complejas y decisiones de las 150 filas, geometría y grafo nativos finales, recibo de finalización, petición original, CSV Iris y perfil de entrenamiento. Se verifica identidad del resultado con el recibo del proceso real y de la petición con el resultado. La auditoría independiente de primeros hits, ramas y vecindades se repite antes de componer los intervalos; no se importa el propagador productor ni el entrenamiento en el análisis científico.

Dos referencias independientes se conservan para cada fila:

1. Grafo escalar exacto con las entradas complejas representadas registradas por Blender.
2. El mismo grafo con codificación matemática ideal: cuatro variables, mínimos/máximos obtenidos únicamente de las 120 filas de entrenamiento, referencia real de amplitud 1 y normalización por la norma compleja. No se recortan valores reservados fuera del rango.

Los números CSV se interpretan como valores **binarios64 ya analizados**; la incertidumbre de medida y la conversión decimal previa no se toman como cero. Aritmética racional dirigida de 128 bits encierra restas, divisiones, cuadrados y raíz de la norma, y luego la composición coherente. El error observado del codificador frente a ese ideal tiene presupuesto previo `10⁻¹²` por componente complejo L1. Campo L1 y potencia conservan el presupuesto anterior `10⁻¹¹` en las ocho salidas.

Se certifica argmax sólo si el intervalo de potencia de su detector queda estrictamente por encima de los otros dos. Superposición o empate quedan `UNKNOWN`, incluidos estímulos nulos en controles. Se informan por separado decisiones certificadas correctas y equivocadas, 120/30 aciertos y márgenes. No se exige un mínimo prefijado de decisiones certificadas: todas las indeterminaciones o cotas que excedan el presupuesto se publican.

Cuatro controles previos pasan: codificador con referencia independiente de 90 dígitos y entradas fuera del rango/signed, rechazo de rango inválido/IDs duplicados, propagación de extremos de una entrada intervalar con salida adversa y empate de tres modos nulos. No son evidencia del resultado de las 150 filas.

Límites: 240 s, un núcleo, sin GPU, RAM libre inicial ≥4000 MiB/suelo ≥2500 MiB, RSS propio ≤1500 MiB y evidencia ≤64 MiB. Se debe publicar y verificar el perfil y todos los blobs antes del análisis. Una cota válida que exceda el presupuesto conserva métrica 0; interrupción o evidencia inválida conserva métrica nula.

```powershell
python Tools/run_frozen_native_batch_certificate_v1.py --profile Docs/research/native_training_batch_certificate_profile_2026-10-09.json --registration Docs/research/native_training_batch_certificate_registration_2026-10-09.json --out D:/PROJECTS/.cognition/neuro3d-sequential-20261008/native-training-batch-cert-20261009-run01
```

Siguen sin cotas: geometría pretendida y preimágenes de captura, redondeo de transformaciones Blender frente a esa intención, perturbaciones geométricas o de medida, ejecuciones GPU no observadas y discrepancia del modelo escalar frente a la red física. La decisión representada certificada no prueba generalización, acierto biológico ni ventaja del clasificador.
