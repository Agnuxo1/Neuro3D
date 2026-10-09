# Auditoría independiente de vecindades interiores

Se añade una comprobación secundaria del grafo ya recogido, conservando su
auditor original y sus recibos. La comprobación anterior verificaba cada primer
hit cerrado y las ramas, pero no la vecindad interior de la unión de triángulos.
El nuevo auditor exige ambas cosas antes de admitir cada estado.

El método independiente proyecta el plano óptico de forma inyectiva a dos
coordenadas. Para cada desigualdad triangular con holgura positiva `s` escoge
un radio racional `r ≤ s/(2(|a|+|b|))`. Así ninguna desigualdad inactiva cambia
de signo dentro del cuadrado centrado en el punto. Las activas conservan las
restricciones locales. Recorta exactamente cada uno de los cuatro lados del
cuadrado contra cada triángulo, mediante desigualdades lineales racionales.
La unión de intervalos cerrados debe cubrir `[0,1]` en los cuatro lados.

Cada triángulo contiene el centro y es convexo. Todo segmento del centro a un
punto cubierto del perímetro pertenece a algún triángulo. Por ello la cobertura
del perímetro prueba la cobertura de todo el cuadrado, y una vecindad abierta
en el plano. El radio fijado por las holguras también hace que un sector local
faltante alcance el perímetro: no puede ocultarse aumentando una tolerancia.
No se importa el selector ni el clasificador angular del productor.

Seis controles verifican abanicos completos, caras invertidas/duplicadas,
un sector ausente de pendiente `2^-120`, bordes exteriores, uniones en T,
geometría de tamaño `2^-150` y rechazo de un resultado cerrado falsamente
declarado interior. Los controles pasan. El código y este método se publican
antes de aplicarlos al resultado capturado.

El certificado se refiere a la geometría plana **representada**, con coordenadas
racionales de la captura. El radio es el de un cuadrado en las dos coordenadas
retenidas; no una tolerancia de fabricación ni una cota de incertidumbre de
las transformaciones Blender. Las otras cotas de error siguen separadas.

[Auditor independiente](../Tools/audit_graph_neighborhood_v1.py) y
[controles](../Blender/tests/test_graph_neighborhood_audit_v1.py).
