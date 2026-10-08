# Testigo matemático: la cuantización puede ocultar una diferencia de fase

**PASS CPU exacto, no GPU ni medición física.** Este testigo aplica un principio conocido de pérdida de información; no se reivindica como descubrimiento nuevo. Ayuda a precisar qué debe garantizar la aportación candidata y a evitar una falsa equivalencia entre geometría original y datos cuantizados.

Un espejo plano ocupa x=1 en un caso y x=1+δ en otro, con δ=2⁻²⁵BU. Los tres vértices del triángulo tienen la misma coordenada x del espejo. Ambos conjuntos de coordenadas se convierten a **los mismos nueve words float32**, porque alrededor de1 el espaciado es2⁻²³BU y δes sólo un cuarto de ese espaciado.

En el modelo analítico de dos brazos, mover el espejo perpendicularmente aumenta el recorrido de ida/vuelta en2δ. Para λ=4δ=2⁻²³BU y longitud base5BU, las fases adicionales son0yπ. Dos amplitudes coherentes1/2producen entonces campos1y0, e intensidades normalizadas1y0. La salida complementaria intercambia0y1, por lo que se conserva la potencia total.

Todo algoritmo determinista que reciba **sólo esos datos cuantizados idénticos**, manteniendo iguales los otros parámetros, devolverá el mismo resultado en ambos casos. Por desigualdad triangular, el máximo error de intensidad frente a las dos geometrías originales no puede ser menor que1/2. Usar cálculo double después de perder esos bits no reconstruye la información original. Si el algoritmo recibe además una representación de mayor precisión u otra información que distinga los casos, esa premisa deja de aplicarse.

La prueba usa fracciones y fases cardinales exactas, sin aproximar sin/cos. El [recibo](validation/quantization-witness-2026-10-08/attempt01/receipt.json) conserva los words, parámetros, campos/potencias exactos, código y hash. No contiene un recorrido capturado de Blender ni demuestra comportamiento de RT hardware.

**Relación con H1:** el testigo no refuta la hipótesis de corrección para el modelo representado; ambas escenas cuantizadas representan el mismo problema. Refuta atribuirles equivalencia con ambas geometrías originales sin justificar el error de representación. Para reclamar esa equivalencia será necesario conservar la precisión relevante o incluir una incertidumbre suficiente, que puede hacer que la decisión no sea certificable.

![Ilustración analítica de fase y cuantización](assets/quantization-phase-witness-2026-10-08.gif)

El GIF ilustra una fórmula analítica conocida: intensidad cos²(πt/2) al desplazar el espejo entre0yδ. La curva es una ilustración numérica; los extremos y el límite de indistinguibilidad están probados exactamente en el recibo. No se presenta como una ejecución Blender/GPU ni como datos físicos.
