# Control ondulatorio coherente: familia gaussiana declarada

El ensayo produce un **resultado negativo válido**, con los 36 casos recogidos: la ventana 16 BU falla el presupuesto de campo para λ=0,1 BU y z=4 BU. Se conserva métrica 0, sin interrupción ni modificación de tolerancias. El [perfil fijado](research/gaussian_wave_profile_2026-10-09.json) y la [autorización humana GitHub](research/gaussian_wave_registration_2026-10-09.json) se publicaron antes de ejecutar, en `faa9b788a93b22e64963a079f1fac5c5cbc38d33`, SHA256 de perfil `6c138f2ab91c9ca01942d5113efcef4abdf38ef0ac75d8f09d56f1a27575ad6e`. Se mantiene la vía externa/IPFS sin identificadores emitidos. [Supervisor](validation/gaussian-wave-reference-2026-10-09/attempt01/supervisor.json), [resultado completo](validation/gaussian-wave-reference-2026-10-09/attempt01/worker/result.json), [índice de evidencia](validation/gaussian-wave-reference-2026-10-09/attempt01/evidence_index.json).

Se añade una implementación propia de propagación escalar coherente por espectro angular, como componente del laboratorio. La entrada es un campo gaussiano `E(x,y,0)=exp(−(x²+y²)/w₀²)`, con `w₀=0,1 BU`, longitudes de onda `0,1 / 0,025 / 0,00625 BU`, distancias `1 / 2 / 4 BU`, índice 1 y apertura circular de lectura de radio `0,15 BU`. Estas son **hipótesis nuevas explícitas**; la captura neuronal anterior no especifica ese perfil espacial. El ensayo no modifica su detector modal ni aplica factores gaussianos a sus potencias.

Para frecuencia transversal `f`, la transferencia saliente es `H=exp(ikz·sqrt(1−λ²|f|²))`, con raíz real positiva para propagación y raíz imaginaria positiva para evanescencia. La convención temporal es `exp(−iωt)`. Se conserva el campo complejo y se elimina únicamente la portadora longitudinal común para comparar referencias, con cálculo estable de `sqrt(1−s)−1=−s/(sqrt(1−s)+1)`. Los componentes evanescentes decaen, no se sustituyen arbitrariamente por intensidades. La FFT representa una ventana periódica muestreada: no es por sí sola una referencia continua ni un certificado físico.

La referencia independiente usa la transformada radial gaussiana analítica y una integral Fourier–Bessel de Helmholtz. No importa el productor FFT. Incluye la rama evanescente, cambio de variable angular en el borde de propagación y cuadratura Gauss–Legendre: órdenes 512/128 frente a 1024/256 en frecuencia/radio. El truncamiento espectral tiene cota analítica de amplitud `exp(−36)` por `|J₀|≤1`, `|H|≤1`; la diferencia entre refinamientos de cuadratura es una estimación numérica de convergencia, **no una cota rigurosa total de cuadratura y redondeo**.

La segunda referencia es el gaussiano paraxial analítico: `z_R=πw₀²/λ`, `w(z)=w₀ sqrt(1+(z/z_R)²)`, fase de Gouy y fracción circular `1−exp(−2a²/w(z)²)`. La lectura relevante de [Steck, capítulo 6](https://atomoptics.uoregon.edu/~dsteck/teaching/optics/optics-notes.pdf) fundamenta las convenciones. No se fuerza un pequeño desacuerdo paraxial cuando `λ/w₀=1`.

Se ejecutan cuatro mallas por cada caso: 512², 1024² y 2048² con ventana 16 BU; 2048² con ventana 32 BU. El contraste 1024²/16 frente a 2048²/32 mantiene el mismo paso espacial para aislar el efecto de ventana. Se comparan 65 posiciones radiales alineadas, el campo axial, la norma transversal total y la integral circular de `|E|²`, normalizada por `πw₀²/2`. La integración de apertura usa intensidad constante por píxel y cobertura circular con 8×8 subpíxeles. La norma transversal es un readout escalar; no equivale automáticamente a flujo vectorial de Poynting.

Los umbrales se fijan antes de datos: diferencia compleja radial ≤`2×10⁻⁶` para las dos mallas finas; error absoluto de fracción de apertura ≤`5×10⁻⁴` en 2048²/16 y ≤`2,2×10⁻³` en 2048²/32; refinamiento de apertura 1024²→2048² ≤`2×10⁻³`; refinamiento de cuadratura ≤`10⁻⁹`; contraste de ventana al mismo paso, campo y fracción ≤`2×10⁻⁶`. Norma de entrada relativa ≤`5×10⁻¹²`, con margen de redondeo de norma `10⁻¹⁰` y pérdida evanescente acotada por la cola espectral gaussiana. Todos los 36 casos finitos se conservan si falla algún presupuesto: resultado válido con métrica 0. Una interrupción o salida no válida se distingue como inconclusa.

Pasaron tres controles de física declarada/software: ondas planas propagantes y evanescentes; linealidad y cancelación coherente, rechazo de NaN y retropropagación no admitida; campo gaussiano inicial, límite paraxial y apertura. El primer control de apertura con 256² falló por `1,12296×10⁻⁴ >10⁻⁴`; con 512² pasó **sin cambiar el umbral ni el código de producción**. Se conserva el fallo de desarrollo. Dos controles adicionales verifican perfil/recibo y rechazo de cambios de fuentes, mallas y recursos. Estos controles no son medidas físicas.

Presupuesto: 240 s, un núcleo CPU, ≥4.000 MiB RAM libre inicial / ≥2.500 MiB durante ejecución, RSS ≤1.500 MiB y evidencia ≤64 MiB. La ejecución NVIDIA del grafo neuronal sigue siendo un ensayo separado; este control usa FFT CPU complex128 y referencias independientes.

La [actualización primaria de alcance](research/wave_and_certification_primary_scope_2026-10-09.json) conserva acceso, versiones y limitaciones de lectura. [Ho et al., 2025](https://arxiv.org/html/2412.09774v2) ya combina rayos, difracción y optimización, e incluye aplicaciones coherentes. Su readout de imagen por PSF incoherente no reemplaza nuestra suma de cinco entradas coherentes. La bibliografía de espectro angular y los antecedentes de certificación neuronal impiden reivindicar esos ingredientes como nuevos. Los 106 antecedentes históricos pendientes de extracción siguen pendientes.

Un pase del ensayo caracterizará **esta familia escalar libre**. Para la red completa siguen faltando perfiles espaciales/modos, aperturas de cada superficie, solapamiento, polarización, pérdidas, dispersión y validación conjunta ondulatoria. La geometría capturada y sus cotas aritméticas no proporcionan esas magnitudes. No se afirmará fidelidad de Maxwell, procesador físico o novedad excepcional.

## Resultado y fallo de ventana

El worker terminó en **32,915 s**, RSS máximo **510,734 MiB**, sin interrupción. Todos los controles de norma y apertura pasan en los 36 casos. Ocho de las nueve combinaciones físicas pasan todos sus controles; λ=0,1 BU / z=4 BU falla dos controles de campo. La referencia continua refinada difiere `3,475×10⁻¹⁵` entre órdenes de cuadratura en ese caso; es convergencia numérica, no cota rigurosa total.

| Malla y ventana, λ=0,1 / z=4 BU | Diferencia máxima compleja en 65 puntos | Fracción en apertura | Diferencia absoluta frente a referencia continua |
|---|---:|---:|---:|
| 512² / 16 BU | 2,23119×10⁻⁶ | 0,0271111 | 3,06369×10⁻⁵ |
| 1024² / 16 BU | 2,23119×10⁻⁶ | 0,0271611 | 1,93992×10⁻⁵ |
| 2048² / 16 BU | 2,23119×10⁻⁶ | 0,0271401 | 1,62756×10⁻⁶ |
| 2048² / 32 BU | 4,08665×10⁻⁷ | 0,0271611 | 1,93461×10⁻⁵ |

Refinar la malla a ventana fija no reduce ese error de campo. Aumentar la ventana reduce el error y cambia el espaciado de frecuencias; el contraste al mismo paso espacial también supera el umbral. Es evidencia de una limitación de ventana/muestreo espectral en este caso, sin reivindicar una prueba universal de su causa. La precisión de la integral de apertura y la precisión del campo espacial son criterios distintos: no se sustituye el campo fallido por un detector que pasó.

![Campos y aperturas frente a referencias independientes](assets/gaussian-wave-reference-2026-10-09.png)

La aproximación paraxial y la referencia de Helmholtz tampoco se equiparan. Para λ=0,1 BU y z=1 BU, la referencia continua de fracción circular es aproximadamente 0,32419, frente a 0,33251 paraxial. Es una diferencia bajo el perfil gaussiano declarado, no una medición de la red ni una cota de su readout modal. En las longitudes de onda menores las diferencias complejas FFT/referencia son del orden de `10⁻¹⁴` en los puntos evaluados; la integración de apertura conserva su error de discretización mayor.

El resultado negativo queda publicado antes de preparar el ensayo de reparación con ventanas mayores y los mismos presupuestos de campo/apertura. El nuevo ensayo tendrá identificador y límites de recursos propios; no sustituirá este perfil ni convertirá su métrica 0 en éxito.
