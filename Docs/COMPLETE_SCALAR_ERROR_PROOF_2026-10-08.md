# Certificado integral del modelo escalar: demostración y límites

## Objeto de la prueba

La magnitud certificada es el campo del modelo CPU de óptica escalar ideal del punto 3, sobre la escena completa representada o una familia de entradas explícitamente acotadas. No se equipara este modelo a Maxwell ni a un dispositivo medido. La incertidumbre física permanece `UNKNOWN_NOT_ZERO`; no se certifican automáticamente kernels GPU/RT anteriores.

Un cierre matemático requiere dos cosas diferentes: demostrar que la familia conserva el recorrido y encerrar las magnitudes calculadas sobre él. Si no se prueba la primera, no se emite un certificado de campo completo.

## 1. Geometría y dirección

En la escena representada, todas las entradas y las operaciones de intersección/reflexión son racionales exactas. La primera colisión se ordena mediante comparación racional. Las aristas internas cubiertas y las salidas a parámetro cero siguen la semántica demostrada del punto 3. No existe un error de redondeo geométrico interno en esa referencia; esto no dice que los valores introducidos sean medidas físicas exactas.

Para una caja de entradas, cada coordenada se encierra con radio declarado. Una traslación rígida por objeto es compartida entre sus vértices y su referencia modal; sus aristas y normal permanecen constantes. El radio independiente de vértices se distingue de esa traslación. Se validan todos los radios: ninguno ausente equivale a cero.

El replay por intervalos encierra determinante, coordenadas baricéntricas, parámetro y punto. Se exige determinante separado de cero y llegada positiva. La cobertura se prueba por interior de triángulo o por unión convexa certificada de sus caras: ciclo exterior único, orientaciones coherentes, interiores disjuntos mediante ejes separadores y suma de áreas igual al polígono. Si la unión omitiera un punto interior, al ser una unión finita cerrada de triángulos omitiría una región abierta de área positiva, contradiciendo la igualdad de áreas. El tubo debe estar estrictamente dentro de los semiplanos exteriores.

Para cada competidor se prueba que no puede preceder la llegada elegida. Se admite exclusión por parámetro negativo, baricéntricas exteriores, orden de intervalos separado o separación entre su caja geométrica y **todo el segmento** `O+tD`, `0<=t<=t_hit_superior`. La última condición también excluye aperturas coplanares finitas que sólo se alcanzarían después de la siguiente interacción. Si nada lo demuestra, el resultado es UNKNOWN.

Después de una interacción, el origen está en la superficie por construcción. La misma primitiva no puede volver a intersectarse antes de otra interacción si la incidencia está separada de cero. Para caras coplanares del mismo objeto rígido, la identidad de plano demuestra lo mismo. El argumento se aplica sólo a esa salida; después de otra superficie se admiten retornos positivos.

La reflexión exacta es `D' = D - 2(D·n)n/(n·n)`. Para normales constantes se usa la matriz racional `R_ij = delta_ij - 2 n_i n_j/(n·n)`; conserva los ceros estructurales y satisface `RᵀR=I`. Para normales inciertos se propaga el intervalo completo y se exige `n·n>0`. Una dirección que pueda abandonar el modo común del terminal impide certificar un único campo escalar.

Cuando la caja de dirección sólo cambia la escala positiva de un eje cardinal, todas sus realizaciones describen el mismo rayo. Si `D'=sD`, la intersección cambia a `t'=t/s`, el punto `O+t'D'` es idéntico y `t'|D'|=t|D|`. La reflexión es homogénea en `D`, de modo que la identidad se conserva después de cada interacción. El certificado puede trabajar con el vector nominal sin perder esa incertidumbre declarada; una perturbación angular no cumple la hipótesis.

Para plano y dirección constantes, el punto de impacto se calcula como `P=(I-D nᵀ/(n·D))O+(D nᵀ/(n·D))A`. Los coeficientes racionales se calculan antes de aplicar intervalos. Así se conservan identidades como la cancelación de la coordenada inicial normal al plano, que la expresión `O+tD` evaluada con intervalos independientes puede sobreestimar. El parámetro conserva el intervalo de `n·(A-O)/(n·D)`.

## 2. Longitud y referencia

En el modelo exacto, `S=D·D` se conserva en cada reflexión. Si `T` es la suma de parámetros positivos y `beta=D_final·(referencia-punto_final)`, la longitud efectiva es:

`L_eff = (S*T + beta) / sqrt(S)`.

Cada segmento es `t*sqrt(S)`. El motor conserva `S`, `T` y el numerador racional sin redondear la longitud primero. En la familia perturbada se encierra cada `t*sqrt(D·D)` y el desplazamiento final `D·(referencia-punto)/sqrt(D·D)`. La suma intervalar contiene la longitud de todas las realizaciones admitidas. Se exige norma separada de cero y compatibilidad de plano/referencia/modalidad.

## 3. Aritmética de inclusión

Los extremos son racionales. Tras cada operación se redondean hacia fuera a múltiplos de `2^-128`: `floor(x*2^128)/2^128` y `ceil(x*2^128)/2^128`. La aritmética entera de Python no tiene overflow fijo; agotar memoria o un límite no produciría un certificado válido.

Suma, producto por las cuatro combinaciones de extremos, inversión de un intervalo separado de cero y cuadrado usan sus extremos exactos antes del redondeo. Para `sqrt(q)`, `isqrt(floor(q*2^256))` proporciona el extremo inferior. Una comprobación entera de cuadrado decide si se añade una unidad al extremo superior. Por inducción, cada operación contiene el valor verdadero, aun cuando se pierda correlación y la cota sea ancha.

## 4. Pi, fase y funciones trigonométricas

Se usa `pi = 16 atan(1/5) - 4 atan(1/239)`. La identidad se verifica con las fórmulas de tangente: `tan(2a)=5/12`, `tan(4a)=120/119` y `tan(4a-b)=1`, con `a=atan(1/5)`, `b=atan(1/239)` en el cuadrante correspondiente. Las series alternantes decrecientes de arctan encierran cada valor entre la suma de 64 términos y esa suma más el primer término omitido. [Serie oficial NIST DLMF](https://dlmf.nist.gov/4.24.E3).

La fase por camino es `theta=2*pi*L_eff/lambda+sum(phi_espejos)`. Longitud, longitud de onda positiva y fases se propagan por intervalos. Los signos de espejos y las reflexiones de divisores se representan como giros exactos de cuarto de vuelta; no se aproximan con otra constante pi.

Para `[m-r,m+r]` se encierra rigurosamente seno/coseno del punto racional `m` y se amplían ambos resultados por `r`; el teorema del valor medio y `|sin'|,|cos'|<=1` garantizan la inclusión. Se resta un múltiplo entero de `2*pi` usando **el intervalo** de pi. El entero sólo mejora el rango; cualquier entero mantiene la identidad y la inclusión. Para argumento reducido del punto de módulo <=4, seno y coseno se evalúan con 32 términos de Taylor mediante Horner. Se añaden restos de Lagrange `M^65/65!` y `M^64/64!`, ya que toda derivada real de seno/coseno tiene módulo <=1. Para un rango mayor se conserva la cota universal [-1,1]. [Series oficiales NIST DLMF](https://dlmf.nist.gov/4.19).

## 5. Coeficientes, campo, reducción e intensidad

Cada camino conserva campo de fuente `a`, producto de potencias `p`, fase `theta` y giro `q`. Su contribución exacta es `a*sqrt(p)*exp(i theta)*i^q`. Las cajas de fuente, transmisión y fase intervienen directamente; no se presupone un error upstream inventado. Si una rama o fuente nominalmente nula puede aparecer dentro de la caja, cambia el soporte y se rechaza el certificado.

Se encierran componentes real e imaginaria de **todos** los caminos al mismo puerto y modo. Su suma intervalar contiene la reducción coherente completa, sin acreditar cancelaciones entre errores independientes. La intensidad se encierra como `Re(E)^2 + Im(E)^2`, usando el cuadrado correcto si el intervalo cruza cero. No se suman intensidades de caminos que interfieren.

Las salidas flotantes efectivamente producidas se convierten a sus racionales exactos. Para un componente estimado `y` y referencia encerrada `[l,h]`, el error es como máximo `max(|y-l|,|y-h|)`. La suma de las dos cotas componentes limita el error L1 del campo. La misma operación sobre intensidad incluye la aritmética de detección flotante. Esto no requiere suponer un `sin/cos` nativo correctamente redondeado.

## Condiciones explícitas y unidades

Posiciones, vértices, traslaciones, referencias y longitud de onda usan BU; radios de dirección usan componentes de la dirección declarada; fase usa radianes; transmisión es adimensional; campo e intensidad usan las unidades normalizadas del modelo. No hay conversión a metros, vatios o joules físicos sin calibración.

Se consideran fuentes coherentes en una longitud de onda y una referencia de salida común por puerto. La suma de potencias de entrada presupone modos independientes y no se utiliza como prueba universal para fuentes coincidentes. Las cotas de salida no necesitan esa suposición para encerrar la suma compleja declarada.

UNKNOWN cubre incertidumbre ausente, recorrido incompleto, fuente/rama nueva, orden no demostrado, denominador cercano a cero, cobertura no probada y modo/referencia incompatibles. Tampoco se confunden una muestra dentro del intervalo y la demostración de inclusión: las muestras y mpmath de 90 dígitos son diagnósticos independientes; la garantía procede de las operaciones y condiciones anteriores.
