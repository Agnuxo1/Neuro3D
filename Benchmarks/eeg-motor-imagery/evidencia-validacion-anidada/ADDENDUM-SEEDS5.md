# Anexo POST-HOC a la preinscripción (declarado 2026-09-30 ~06:45 UTC, antes de ejecutar)

Estatus: **exploratorio**. La rejilla de 36 configuraciones y sus resultados (results_full.json) quedan intactos. Este anexo evalúa con LORO
externo lo que se enviaría a Kaggle: **promedio de 5 semillas** (los envíos usan 5; el LORO de la rejilla usó 1) de las tres configuraciones
finalistas elegidas por el resultado anterior (12 bandas x 3 ventanas, decaimiento 1e-2, 90 épocas): polar, lattice32, free, más los conjuntos
de logits polar+lattice32 y polar+lattice32+free. Sin bucle interno (`--no-inner`).
Hipótesis H1: promediar 5 semillas mejora el LORO de cada finalista en >= 0,005 respecto de su valor de 1 semilla (0,7188; 0,6953; 0,7285).
Refutación de H1: la mejora pareada por sujeto tiene IC95 que incluye 0 o es < 0,005.
Hipótesis H2: el conjunto polar+lattice32+free no supera al mejor finalista individual con 5 semillas (IC95 de la diferencia incluye 0).
Advertencia: las tres configuraciones finalistas se eligieron mirando el LORO de 1 semilla; cualquier ganancia observada aquí está sujeta a ese sesgo
de selección (pequeño: optimismo MAX-N2 = +0,001) y NO es una estimación limpia del test oculto. Ninguna decisión sobre Kaggle depende solo de este anexo.
Comando: nested_bench.py --grid finalists --tag seeds5 --seeds 5 --no-inner --dev cuda --subjects <S###> (un ticket gpuq por sujeto).
