# Enmienda prospectiva: reducir sobreestimación por dependencias

El intento04 pasa 13 pruebas y 41 certificados exactos; cli01 certifica cuatro cajas K3/K4 no nulas. Sin embargo, para radio1e-8 las cotas K4 llegan a 3.14 en campo y 6.24 en intensidad: son válidas pero no acreditan precisión útil. Fuentes y resultados se conservan antes de cambiar el evaluador.

Se fijan dos identidades para afinar la inclusión, sin omitir incertidumbre:

1. Si la dirección sólo tiene una componente no nula y su radio mantiene el signo, con radios cero en las otras componentes, todas las realizaciones son múltiplos positivos del mismo vector. La trayectoria geométrica, longitud física y reflexión son invariantes bajo ese cambio de parametrización. Se puede usar el vector nominal para esas magnitudes, conservando los radios declarados en el recibo. Una caja angular no satisface esta condición y continúa sin certificado modal.
2. Con plano y dirección constantes, la intersección es la transformación afín `P=(I-D nᵀ/(n·D))O+(D nᵀ/(n·D))A`. Se calcularán los coeficientes racionales primero para conservar cancelaciones estructurales. El parámetro se encerrará con `t=n·(A-O)/(n·D)`. Esto evita que la misma coordenada del origen, añadida y restada, aparezca artificialmente como dos datos independientes.

Se mantienen todos los criterios anteriores. Se repetirá la aceptación y la interfaz de las mismas cuatro cajas, conservando cotas previas y nuevas. Una mejora de anchura acredita utilidad del evaluador, no mejor tolerancia física medida ni mejor precisión de hardware.

Refinamiento prospectivo adicional tras PASS13/41 del intento05: para un argumento encerrado en `[m-r,m+r]`, se calculará un intervalo riguroso de seno/coseno en el punto racional `m` y se ampliará por `r`. El teorema del valor medio y las derivadas de módulo <=1 garantizan la inclusión. La reducción de argumento del punto sigue usando pi encerrado y resto de Taylor; no se reduce el radio de ninguna entrada. Se repiten los mismos gates y cajas tras este cambio en las funciones elementales.
