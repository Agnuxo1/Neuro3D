# Informe de ejecución F4 · capacidad y aprendizaje de la familia pasiva

Preregistro: `PREREGISTRO-F4.md` (sin cambios). Resultados: `resultados/RESULTADOS_F4.json`, parciales en `resultados/parciales/`, hashes en `resultados/SHA256SUMS.txt`.
Entorno: Python 3.13.7, numpy 2.2.6, scipy 1.15.1, scikit-learn 1.4.0. Solo CPU, 2 procesos, sin GPU.

**Límite obligatorio:** la familia es la malla de P2-10 (Clements, N modos, N capas), no la geometría capturada de Neuro3D. Ninguna conclusión sobre el dispositivo físico.

## Verificación previa (resultados/verificacion_f4.json): PASA
- (a) Gradiente analítico frente a diferencias finitas, 3 configuraciones (N=8 K=3, N=8 K=2, N=16 K=10): error relativo máximo 1,4e-9 (< 1e-6). La copia de la malla y el gradiente reproduce los valores de `escala-modos/resultados/verificacion_gradiente.json` (N8, N8_K4, N4 coinciden a < 1e-12).
- (b) Unitariedad en 20 configuraciones aleatorias: error máximo 3,6e-15 (N=8) y 6,8e-15 (N=16), < 1e-12. La aplicación por capas coincide con la matriz densa.

## Resultados por hipótesis
- **C1 (control de cordura): cumple.** 400 configuraciones entrenadas (una por reinicio); error de unitariedad máximo 6,7e-15; κ(U) entre 1,0000000000000002 y 1,0000000000000013.
- **C2 (sin criterio).** κ(G) sobre las N entradas, media / mediana: Breast Cancer 29,9 / 29,4; Digits 10,25 / 10,26. Iris y Wine: G singular (cuatro modos de entrada a cero), κ = infinito; sobre las 4 columnas activas: Iris 295,9 / 293,9; Wine 67,7 / 76,1.
- **Control de ruido:** con σ = 0 se reproduce exactamente la exactitud del reinicio elegido en las 40 particiones.
- **H3a: NO CUMPLE** (exige los cuatro conjuntos). Pérdida media en σ = 0,03 [IC95 bootstrap]: Iris 0,040 [0,018; 0,061]; Wine 0,025 [-0,002; 0,051]; Breast Cancer 0,0033 [-0,003; 0,010]; Digits 0,0083 [0,0057; 0,0108]. Cumplen Breast Cancer y Digits; no cumplen Iris y Wine.
- **H3b: CUMPLE** en los cuatro conjuntos (tolerancia 0,005). Único incremento positivo: Breast Cancer, σ 0,01 → 0,03, +0,0030. Exactitud media (σ = 0 / 0,01 / 0,03 / 0,1 / 0,3): Iris 0,823 / 0,818 / 0,783 / 0,727 / 0,591; Wine 0,832 / 0,830 / 0,808 / 0,698 / 0,510; Breast Cancer 0,716 / 0,709 / 0,712 / 0,691 / 0,590; Digits 0,908 / 0,906 / 0,900 / 0,839 / 0,382.
- **H4: CUMPLE** (interpretación 1) en los cuatro conjuntos. Diferencia media (mejor − mediana) con signo, IC95 y Wilcoxon bilateral: Iris +0,0033 [-0,010; 0,020] p=1,0; Wine 0,0000 [0; 0] p=1,0 (todas las diferencias son cero); Breast Cancer +0,0061 [0,0026; 0,0096] p=0,031; Digits +0,0068 [0,0018; 0,0122] p=0,047. En Breast Cancer y Digits la diferencia es positiva y distinta de cero, aunque menor que 0,01. Rango de exactitud de prueba entre reinicios: Iris 0,70-0,90; Wine 0,78-0,92; Breast Cancer 0,65-0,78; Digits 0,86-0,94.

## Tiempo de CPU por entrenamiento (2000 pasos, 100 entrenamientos por conjunto, para P1-9)
| Conjunto | N | K | muestras entrenamiento | media (s) | mediana (s) |
|---|---|---|---|---|---|
| Iris | 8 | 3 | 120 | 3,50 | 3,55 |
| Wine | 8 | 3 | 142 | 3,72 | 3,77 |
| Breast Cancer | 8 | 2 | 455 | 6,11 | 6,09 |
| Digits | 16 | 10 | 1437 | 58,8 | 60,4 |
Estimación previa de la ejecución completa: 1,08 h con 2 procesos (límite 3 h); no se superó.

## Interpretaciones declaradas
1. H4: |media sobre particiones de (mejor − mediana)| < 0,01; se reporta el signo.
2. Mejor reinicio = menor pérdida de entrenamiento tras 2000 pasos (empate: menor semilla). Nunca por prueba.
3. Iris y Wine: particiones y selección de 4 atributos (columnas 1 a 4 de wine.data) de P0-4; 10 particiones cada uno (no hay desviación).
4. Breast Cancer y Digits: StratifiedShuffleSplit 80/20 con semillas 20261009+k, k = 0..9, mismo código que P1-5. Los índices de Digits coinciden en las 10 particiones con `escala-modos/resultados/splits.json` (que usa train_test_split).
5. Preprocesado: min-max y PCA ajustados solo con entrenamiento (N = 8 Breast Cancer, N = 16 Digits); normalización a potencia unitaria. Iris y Wine: las 4 entradas se colocan en los modos 0 a 3 y los modos 4 a 7 quedan a cero (la especificación no fija cuáles).
6. κ(G) de C2 se calcula con G = XᵀX/n sobre las entradas ya normalizadas a potencia unitaria, con la tolerancia λmin > 1e-12·λmax; si no, κ = infinito. El cálculo sobre las 4 columnas activas de Iris y Wine es un dato adicional.
7. C1 se mide sobre las fases entrenadas de cada reinicio; el ruido de C3 se aplica a todas las fases (θ y φ) con semillas deterministas por (conjunto, partición, σ, extracción).
8. Hipótesis H3a/H3b/H4 se evalúan sobre la media de particiones (estimación puntual); los IC95 son informativos.

## Desviaciones y límites
- Sin desviaciones del preregistro. Wilcoxon en Wine: las 10 diferencias son cero. SciPy devuelve estadístico 0 y p = 1,0 y emite un aviso de división no válida (RuntimeWarning). `resultados/RESULTADOS_F4.json` no registra ese aviso (`wilcoxon_nota` está vacío); el aviso se documenta aquí, en el informe. El p = 1,0 es una convención de SciPy cuando todas las diferencias son cero, no evidencia de igualdad: significa que la prueba no tiene información.
- La exactitud absoluta es baja en Iris (0,82) y Breast Cancer (0,72): resultado tal cual, sin ajuste. Esta tarea no la compara con líneas base.
- Con 10 particiones por conjunto los IC95 son anchos (Iris y Wine incluyen valores < 0,01 en la pérdida de σ = 0,03).
- Las comparaciones entre conjuntos de H3a mezclan tamaños de prueba distintos (30 a 360 muestras).
- Resultados de la familia simulada de P2-10; sin conclusión sobre Neuro3D ni hardware.

## Riesgos y limitaciones
- (a) Los p de H4 (Breast Cancer 0,031; Digits 0,047) no sobreviven a una corrección por 4 pruebas (Holm: ninguno). Digits es marginal: el test de signos da 0,109.
- (b) H3a se decide con una estimación puntual sobre solo 10 particiones; los IC95 de Wine y Breast Cancer incluyen valores por debajo y por encima de 0,01, así que "no cumple" no es una refutación firme.
- (c) La exactitud absoluta es baja (Iris 0,82, Breast Cancer 0,72); H3 y H4 describen un clasificador débil y no se extrapolan a modelos bien entrenados.
- (d) Las pruebas de Iris y Wine tienen 30 y 37 muestras; un paso de exactitud (0,033 y 0,027) es mayor que 0,01, y el 0,0000 de Wine no distingue una diferencia real nula de una por debajo de la resolución.
- (e) En Wine, 4 de 10 particiones (k = 0, 2, 5, 8) tienen las 10 exactitudes de prueba idénticas (Iris, 3 de 10: k = 1, 5, 7). Es un hallazgo de resolución gruesa, no un fallo de semillas: las semillas 0 y 3 de Wine k = 0 tienen fases iniciales y finales distintas y pérdidas distintas (0,475558 y 0,475198), pero la misma exactitud (0,8919) y 0 de 37 predicciones de prueba difieren. Las 10 pérdidas de entrenamiento son distintas en las 40 particiones.
