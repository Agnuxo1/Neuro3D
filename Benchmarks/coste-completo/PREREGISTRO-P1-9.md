# Preregistro P1-9 · coste completo y energía de las comparaciones

Fecha de compromiso: 2026-10-09, antes de compilar la tabla. Es un análisis descriptivo: no hay decisión de superioridad.

## 1. Medidas disponibles y lo que NO se mide

- **Energía medida directamente: no.** La máquina (Intel Core i9-7900X, 10 núcleos físicos y 20 hilos, TDP nominal 140 W) no expone contadores de potencia de CPU a Windows (`Get-Counter` sin categoría de potencia). Sin medidor externo, la energía de CPU no se mide.
- **Potencia de GPU:** `nvidia-smi` (RTX 3090) da potencia instantánea. Las comparaciones de esta fase no tienen registro de potencia de GPU, así que no se estima energía de GPU para ellas.

## 2. Cotas de energía (declaradas)

- Cota superior de energía de CPU por ejecución: E_UB = t_CPU × P_núcleo, con P_núcleo = 140 W / 10 núcleos = 14 W. Es una cota superior por construcción: el TDP nominal no se alcanza en carga parcial de un solo núcleo, pero tampoco se mide.
- Tiempo de CPU: tomado de los archivos de resultados (`process_cpu_seconds`, `cpu_seconds`, `cpu` o equivalente). Si una comparación no lo registra, se marca como no registrado.

## 3. Tabla de coste (una fila por comparación)

Para cada comparación de Neuro3D: método, conjunto, unidad de cómputo (entrenamiento, partición, simulación), número de unidades, tiempo de CPU por unidad, tiempo total, memoria pico (si se registró), parámetros nominales e identificables, actualizaciones o pasos, cota superior de energía E_UB y fuente del dato (archivo y campo).

Comparaciones incluidas:
- P0-4: óptico Iris (4 reinicios × 500 pasos por partición) y óptico Wine (entrenamientos completos, 1 y 3 semillas); líneas base lineal y cuadrática.
- P1-5: líneas base B1 a B6 en Iris, Wine, Breast Cancer y Digits.
- P1-7: simulaciones FDTD λ/16 y λ/24 (memoria pico registrada) y medición del solver directo (`medicion_coste.json`).
- P1-8: experimento sintético (generación, QDA, óptico).
- EEG: validación anidada con GPU y CPU, según lo registrado en `Benchmarks/eeg-motor-imagery/evidencia-validacion-anidada/`.

## 4. Lo que se publica

- La tabla, con las cotas de energía marcadas como cotas superiores.
- Un párrafo que diga explícitamente que la energía no se midió.
- Los campos no registrados, marcados como tales. No se rellenan con estimaciones.

## 5. Integridad

- Cada fila cita el archivo y el campo de origen. El script que compila la tabla se publica con sus hashes.
- No se re-ejecuta ninguna simulación ni entrenamiento para esta tabla.
