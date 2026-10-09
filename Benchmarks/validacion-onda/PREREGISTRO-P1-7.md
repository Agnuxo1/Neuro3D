# Preregistro P1-7 · validación del modelo escalar de interferómetro frente a un solver de ondas

Fecha de compromiso: 2026-10-09, antes de implementar el solver de referencia y antes de ejecutar ninguna simulación. Decisiones de régimen, umbral y divisor tomadas con JEV (procedencia `jev`).

## 1. Pregunta

¿El modelo escalar ideal de Neuro3D (propagación de caminos sin difracción, sin pérdidas y sin polarización) predice las potencias de salida de un interferómetro Mach–Zehnder simulado con ondas, dentro de un régimen declarado?

## 2. Modelo bajo prueba

- Escalar, monocromático, sin pérdidas. Propagación `exp(+i 2π L / λ)` a lo largo de cada brazo. Sin difracción.
- Divisores: S-matriz calibrada (ver sección 4). Espejos: reflexión −1, sin fase adicional.
- Potencia de salida = |amplitud de salida|² normalizada por la potencia de entrada.

**Hipótesis nula H0:** en el régimen declarado, el error absoluto máximo de las potencias de salida frente al solver es ≤ 0,02.
**H1:** el error supera 0,02 en el régimen declarado. En ese caso el modelo queda **refutado en ese régimen**.

## 3. Régimen declarado

- Anchura del haz gaussiano `w ≥ 8λ` (régimen primario). Se reportan también `w/λ = 4` y `w/λ = 16` como curva de convergencia; `w/λ = 4` queda fuera del régimen declarado.
- Incidencia de los haces sobre los divisores dentro de ±10°.
- Recorrido de los brazos: 30λ a 40λ.

## 4. Solver de referencia y calibración

- **Solver:** Helmholtz escalar 2D (modo TM), diferencias finitas, capas absorbentes perfectamente acopladas (PML), resolución directa dispersa en CPU. Sin GPU.
- **Malla:** paso h = λ/16 y h = λ/32. La convergencia se acepta solo si la diferencia de error entre ambas mallas es < 0,005.
- **Vacío con PML:** reflexión < 10⁻³ con un haz incidente; si no se cumple, no se continúa.
- **Divisor:** película dieléctrica de índice y espesor elegidos para que |r|² = |t|² = 0,5 con su solución 1D (matriz de transferencia). La calibración se verifica en el solver 2D con una onda plana en incidencia normal: diferencias en |r|² y |t|² menores que 0,005. Si no se cumple, la película se ajusta y se repite la calibración; el ajuste queda registrado.
- **Modelo con el mismo divisor:** el modelo usa los coeficientes r y t calibrados (complejos), no los ideales. Así el ensayo aísla la hipótesis del camino (difracción, geometría finita), y la discrepancia del divisor ideal se reporta por separado.

## 5. Geometría y barrido

- Interferómetro Mach–Zehnder: entrada en un puerto, dos divisores, brazos de longitud L₁ y L₂ con diferencia ΔL = L₁ − L₂ variable.
- Barrido de fase: ΔL en 21 valores equiespaciados en [0; λ] (paso λ/20).
- Entrada: haz gaussiano de anchura w, centrado en el eje del puerto.
- Potencias de salida: solapamiento del campo con el modo gaussiano de cada puerto de salida.

## 6. Métrica y decisión

- **Error por punto:** |P_solver − P_modelo| en cada puerto y cada ΔL.
- **Error máximo:** E_max = máximo sobre puertos y barrido. Es el estadístico principal.
- **Decisión en el régimen declarado** (w ≥ 8λ, ±10°, ambas mallas):
  - Si E_max ≤ 0,02 en ambas mallas y la diferencia entre mallas es < 0,005 → **H0 no refutada en el régimen**.
  - Si E_max > 0,02 en ambas mallas → **H0 refutada**; el modelo no se usa en ese régimen.
  - Cualquier otro caso → **no concluyente**.
- Se reporta la curva E_max frente a w/λ ∈ {4, 8, 16}.

## 7. Integridad

- Se registran los hashes del código del solver, de la calibración y de cada resultado.
- Los resultados negativos se publican tal cual.
- Se registra el tiempo de CPU por simulación (para P1-9).

## 8. Limitaciones conocidas (antes de ejecutar)

- Solver 2D escalar (TM): no modela polarización, dispersión 3D ni pérdidas.
- Espejos de reflexión −1 (conductor perfecto en la referencia). No se modelan fabricación ni tolerancias.
- La decisión solo vale para el régimen declarado. No generaliza a interferómetros con haces estrechos ni a incidencias oblicuas mayores.
- El modelo con divisor ideal no se evalúa en el solver porque el divisor ideal no existe en él. Su discrepancia se reporta aparte.

## 9. Registro externo

Pendiente de autorización. Este commit es la marca temporal interna.

## Enmienda 1 (2026-10-09, antes de cualquier simulación del interferómetro)

**Motivo.** La sección 3 fijaba incidencia de ±10° y brazos de 30 a 40λ. La ejecución de la fase de calibración mostró que esa geometría es imposible: con w ≥ 8λ, los haces reflejados en divisores a incidencia casi normal no se separan dentro de brazos de esa longitud (la separación angular es ≤ 20°, y separar haces de ancho ±2w exige unos 95λ). La especificación original era, por tanto, inconsistente. Ninguna simulación del interferómetro se ejecutó con ella. La calibración a incidencia normal y la prueba PML en vacío se conservan como historial.

**Cambios.**
1. **Geometría:** Mach–Zehnder estándar, con divisores a **45°** (modo TM). El régimen declarado pasa a ser: w ≥ 8λ, divisores a 45°, brazos de unos 30λ.
2. **Calibración:** la película se recalibra a 45° (TM) con su solución 1D y se verifica en el solver 2D con onda plana a 45°. El criterio no cambia: diferencias en |r|² y |t|² < 0,005. El ajuste de índice por malla se registra.
3. **Mallas:** gruesa λ/16 y fina **λ/24**. La malla λ/32 se declara no viable (coste medido: ~3,8 M incógnitas, ~2,4 h y más de 30 GB por factorización). El criterio de convergencia (diferencia de E_max entre mallas < 0,005) se mantiene. Si no se cumple, el resultado es no concluyente.
4. **Decisión:** sin cambios respecto a la sección 6, aplicada al régimen de esta enmienda.

**Alcance declarado.** La validación cubre el interferómetro con divisores a 45° y w ≥ 8λ. No cubre incidencias ±10°, haces estrechos ni otras geometrías. Esta enmienda se decidió con JEV (procedencia `jev`; confianza 1,0 en ambas decisiones).
