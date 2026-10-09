# Informe P1-9 · coste completo y energía (cota superior)

Análisis descriptivo, sin decisión de superioridad. Compilado por `compilar_coste.py` solo con lectura de resultados existentes (ningún entrenamiento ni simulación se re-ejecutó).

## Qué se incluye
- 45 filas en `TABLA-COSTE.json` / `TABLA-COSTE.md` (formato del preregistro §3), cada una con archivo y campo de origen.
- P0-4: óptico Iris (4 reinicios x 500 pasos), óptico Wine (semilla 1049, semillas 1050-1051 y suma de 3 semillas), lineal + cuadrático.
- P1-5: B1 a B6 en Iris y Wine; B1 a B4 en Breast Cancer y Digits.
- P1-7: FDTD λ/16 y λ/24 (memoria pico registrada), solver directo (`medicion_coste.json`, solo las medidas) y pruebas PML en vacío.
- P1-8: experimento sintético (cuadrática y control lineal). EEG: validación anidada en GPU, sonda en CPU y una cifra citada.

## Advertencia: la energía NO se mide
No hay medidor externo ni contadores de potencia de CPU accesibles, y las comparaciones de esta fase no tienen registro de potencia de GPU. `E_UB` = t_CPU x 14 W (140 W / 10 núcleos) es una cota superior por construcción, no una medida ni una estimación de consumo. No se calcula energía de GPU.
- `E_UB` se calcula en 34 filas (las que tienen tiempo de CPU de proceso) y queda "no registrado" en 11.

## Campos no registrados
- Memoria pico: solo registrada en P1-7 (FDTD, solver, PML); no registrada en óptico, líneas base ni EEG (37 filas).
- Parámetros identificables: solo donde el preregistro P0-4 los declara (lineal 10, cuadrático 30); del óptico, B2-B4, P1-8 y EEG: no registrados.
- P1-8 (2 filas): solo tiempo de pared (`time.time`), sin CPU, sin separar generación/QDA/óptico: sin E_UB.
- EEG (9 filas): GPU con tiempo de pared (4118 s en 1368 entrenamientos; 2625 s en 750), sin CPU, sin potencia de GPU, sin VRAM; la sonda CPU y la cifra de 335 s tampoco tienen CPU de proceso. Nada se rellena con estimaciones.
- La sección `proyeccion` de `medicion_coste.json` es una proyección y se excluye; las extrapolaciones de INFORME-NESTED.md también.

## Coste relativo: óptico frente a líneas base (CPU por ajuste)
Óptico Iris: 34.55 s por partición (4 reinicios x 500 pasos; total 345.531 s en 10). Óptico Wine: 358.4 s por entrenamiento (semilla 1049; total 3584.05 s en 10); 376.9 s de media en 30 entrenamientos (total 11305.9 s).

Razón = t CPU por ajuste del óptico / t CPU por partición de la línea base (P1-5, mismas particiones):

| Óptico frente a | B1 lineal | B5 lineal P0-4 | B6 cuadrático | B2 SVM | B3 RF | B4 MLP |
|---|---:|---:|---:|---:|---:|---:|
| Iris | 4.42e+03 | 7.37e+03 | 2.21e+04 | no definida (0 s registrado) | 174 | 284 |
| Wine (semilla 1049) | 7.65e+04 | 7.65e+04 | 1.15e+05 | 1.15e+05 | 1.88e+03 | 2.94e+03 |
| Wine (3 semillas) | 8.04e+04 | 8.04e+04 | 1.21e+05 | 1.21e+05 | 1.98e+03 | 3.09e+03 |

Con el tiempo conjunto lineal + cuadrático de P0-4: Iris 3.69e+03x; Wine 5.46e+03x (semilla 1049), 5.74e+03x (3 semillas). Como el lineal solo es una parte de ese tiempo, la razón frente al lineal solo es mayor o igual.
Cautela: las líneas base suman <=0.08 s en 10 particiones (pocos ticks de 0.015625 s); las razones valen como orden de magnitud. Descriptivo: el coste óptico es de varios órdenes de magnitud mayor que el de las líneas base en estas tareas pequeñas.

## Integridad
`SHA256SUMS.txt` lista los hashes de script, salidas y preregistro. Ejecutar `python compilar_coste.py` regenera las salidas byte a byte.
