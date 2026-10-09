# Certificación secundaria de las 150 salidas nativas del entrenamiento

Estado: análisis completo, ambas referencias y todos los presupuestos pasan. Se analizarán observaciones anteriores ya publicadas del entrenamiento propio dentro de Blender, sin obtener nuevas filas ni elegir semillas. Es una certificación matemática secundaria, no un ensayo neuronal confirmatorio nuevo.

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

## Resultado conservado

Publicado y verificado antes de analizar en `3935fa4bc73a1901e58b69466c209f85a779a82e`, todos los 23 pins idénticos a Git. [Certificado completo](validation/native-training-batch-certificate-2026-10-09/analysis01/worker/certificate.json) e [índice de hashes/fuentes](validation/native-training-batch-certificate-2026-10-09/analysis01/evidence_index.json). Estado `CERTIFIED_OBSERVED_NATIVE_BATCH_AND_ENCODER`, métrica 1; 27,4638 s, RSS máximo 35,770 MiB.

| Referencia | Error campo L1 máximo | Error potencia máximo | Decisiones certificadas / desconocidas |
|---|---:|---:|---:|
| Entradas complejas registradas | 2,768280064335375×10⁻¹⁵ | 9,805711007964366×10⁻¹⁶ | 150 / 0 |
| Codificación matemática ideal desde valores CSV analizados | 2,767110017198810×10⁻¹⁵ | 1,036527463460674×10⁻¹⁵ | 150 / 0 |

El error L1 máximo observado del codificador es ≤1,578666018378917×10⁻¹⁶ frente al presupuesto `10⁻¹²`. Margen inferior mínimo de decisión ≥0,0002111971201181 en ambas referencias. Cada cota exacta racional está conservada; las cifras de error se redondean hacia arriba y las de margen hacia abajo.

Las 150 decisiones certificadas incluyen **137 correctas y 13 equivocadas**. Se mantienen 110/120 aciertos de entrenamiento y 27/30 de evaluación. La certificación no corrige ni oculta los errores neuronales: demuestra que esos trece errores no se explican por el presupuesto aritmético analizado. No se han añadido nuevas etiquetas para entrenar ni cambiado los umbrales.

![Decisiones certificadas y cotas observadas](assets/native-training-batch-certification-2026-10-09.png)
