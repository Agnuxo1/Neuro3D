# Punto 5: operaciones sobre caminos y sus condiciones matemáticas

Se justifican las operaciones activas del motor completo del punto 3, el first-hit del punto 2 y su certificado del punto 4. No se declara compresión general de caminos ni se promueven automáticamente heurísticas de motores históricos.

## Inventario vinculante

| Operación activa | Razón y condición | Efecto sobre caminos físicos del modelo |
|---|---|---|
| Elegir una faceta canónica entre impactos equivalentes | Mismo objeto, punto, plano y propiedad óptica; cobertura interna probada | Un evento de superficie, no dos caminos distintos |
| Excluir contacto propio de salida a parámetro0 | Origen construido en el mismo plano, tras interacción; incidencia no tangente | Evita repetir el mismo evento; retorno posterior sigue admitido |
| Excluir triángulos fuera del rayo/segmento certificado | AABB separada, baricéntricas exteriores o orden exacto/intervalar probado | No pueden ser la próxima interacción |
| Omitir fuente/camino de coeficiente exactamente0 | Modelo lineal, coeficientes finitos y fijos; soporte certificado | Su contribución es exactamente0 |
| Sumar contribuciones al mismo puerto | Misma longitud de onda, modo, coherencia y referencia | Superposición compleja; no suma de intensidades de caminos |
| Reducir numéricamente esas contribuciones | Todas las contribuciones conservadas; error de salida certificado por punto4 | Aproximación con cota explícita, sin equivalencia exacta ficticia |

## Equivalencia de facetas y salida

Si dos normales no nulas del mismo plano cumplen `n2=c*n1`, con `c!=0`, sus operadores de reflexión son idénticos:

`D - 2(D·n2)n2/(n2·n2) = D - 2(D·n1)n1/(n1·n1)`.

Si además pertenecen al mismo objeto y al mismo impacto, tienen el mismo coeficiente declarado. Una arista interna cubierta representa un único evento de esa superficie. El historial conserva todas las identidades de facetas coincidentes y elige una canónica. Una arista exterior, pliegue o dos objetos distintos no cumplen las hipótesis: se rechazan sin seleccionar arbitrariamente una solución.

Tras una interacción, `O` pertenece a su plano. Para un rayo `O+tD` con `n·D!=0`, la ecuación del mismo plano es `t(n·D)=0`, cuya única solución es `t=0`. Excluir ese contacto de salida no elimina otra colisión positiva. Después de cambiar de origen/dirección en otro objeto, esta ecuación ya no implica que la llegada sea cero: el retorno se conserva. Un contacto de otro objeto no satisface la identidad y no se elimina.

La exclusión AABB usa una inclusión de todos los puntos hasta el próximo impacto probado. Si la caja del segmento y la del triángulo se separan en un eje, sus conjuntos reales son disjuntos. Esto no permite excluir una superficie simplemente por ser paralela, pequeña o visualmente imperceptible.

## Cero exacto y linealidad

Para un camino `p`, su campo es `a0 * product(c_j) * exp(i theta_p)`. En el modelo declarado los coeficientes son finitos y dependen de parámetros ópticos fijos, no del campo de ese camino. Si `a0=0` o un coeficiente es exactamente0, su contribución y la de cada continuación lineal son cero. Añadir o quitar cero no cambia la suma del campo ni la intensidad final. Esto justifica exclusivamente esa omisión.

Un valor pequeño, una cancelación observada o un intervalo que contenga0 no demuestran igualdad a cero. Si una caja de entrada permite activar una fuente/rama nominalmente nula, el certificado exige nuevo recorrido o devuelve UNKNOWN_SOURCE_SUPPORT/UNKNOWN_BRANCH_SUPPORT. Fuentes espontáneas, ruido físico y no linealidades no son parte de esta prueba y no se suponen ausentes en una plataforma física.

## Reducción coherente y contraejemplo

Para caminos del mismo modo coherente, `E=sum(E_p)` y `I=|E|²`. La identidad incluye términos cruzados `2 Re(E_p conjugate(E_q))`. Por ejemplo, dos campos `a` y `-a` producen intensidad0, mientras que la suma de sus intensidades sería `2|a|²`. Por tanto, ninguna reducción a potencias individuales preserva en general el cálculo.

En el motor actual los historiales distintos se mantienen separados hasta el terminal. La suma flotante no se declara exacta: el certificado del punto4 encierra cada contribución, la suma completa y la intensidad, y mide la distancia de las salidas efectivamente producidas a esos conjuntos.

## Cuándo se podría fusionar, sin afirmar que ya se hace

Una fusión futura sólo será algebraicamente exacta si ambos prefijos alcanzan el mismo estado de continuación: origen y dirección exactos, lado/evento de salida, configuración óptica, longitud de onda, modo, coherencia, referencia de fase y condiciones de terminación. Deben trasladarse sus fases al mismo gauge antes de sumar campos. Por linealidad, para un mismo operador futuro `L`, `L(a)+L(b)=L(a+b)`.

La igualdad del estado geométrico por sí sola no demuestra igualdad de fases ni de operadores futuros. Los límites de profundidad/recursos deben conservarse por historial; fusionar prefijos con distinto presupuesto podría cambiar si el cálculo se declara completo. La procedencia original debe retenerse. El motor vigente **no implementa esa fusión** y no reclama ahorro validado de memoria o tiempo.

## Toda poda aproximada necesita presupuesto

Si se eliminaran caminos con campos `z_p`, el error de campo satisfaría `|delta E| <= B=sum(|z_p|)`. Para campo retenido `E`, la diferencia de intensidad sería como máximo `2|E|B+B²`. Un umbral individual no basta: `N` contribuciones pequeñas en fase suman `N*epsilon`. Cerca de un puerto oscuro no existe una cota relativa útil deducida de una cota absoluta fija.

Para ciclos infinitos, una cola geométrica sólo puede acotarse tras demostrar contracción del operador completo de continuación, no sólo coeficientes pequeños de caminos aislados. Un bucle ideal de espejos de módulo1 no tiene esa garantía. El motor devuelve RESOURCE_LIMIT e INCOMPLETE, conserva historial y no descarta el resto silenciosamente. No se suprimen puertos escape ni se renormalizan detectores para simular conservación de energía.

## Alcance científico

Estas son justificaciones del algoritmo y del modelo declarado, no una prueba de novedad. La linealidad de campo con parámetros fijos tampoco demuestra una red neuronal universal no lineal; esa caracterización corresponde al punto13. Cualquier ruta nativa nueva del punto6 debe satisfacer el mismo inventario o aportar una prueba adicional antes de usar una reducción diferente.
