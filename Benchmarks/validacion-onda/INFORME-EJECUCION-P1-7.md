# Informe de ejecución P1-7 (protocolo con Enmiendas 1 y 2)

## Decisión
**H0 REFUTADA para w = 8λ** (MZI con divisores a 45°, brazos de 30λ, solver FDTD, modelo escalar sin difracción de camino).
E_max = **0,0269 a λ/16** y **0,0275 a λ/24**, ambos por encima del umbral 0,02. La diferencia de E_max entre mallas es **0,0006** (< 0,005: converge). Por la sección 6 y la Enmienda 2, el modelo escalar sin difracción de camino no se usa en este régimen.
Hallazgo explicativo (diagnóstico exploratorio, no preregistrado): el error es difracción libre del haz. Con el mismo modelo más la propagación gaussiana libre, E_max baja a 0,0051 (λ/16) y 0,0046 (λ/24). Con w = 8λ el recorrido total de ~95λ desde la cintura supone ζ = 2z/(kw²) ≈ 0,47, es decir, un solapamiento 1/√(1+ζ²/4) ≈ 0,973 (pérdida de 2,7 %), que el modelo preregistrado no incluye. El solver y la fórmula coinciden: pérdida medida en k = 0 de 2,7 %.

## Historia
1. **Protocolo original**: incidencia ±10°, brazos 30–40λ, w ≥ 8λ, solver directo de Helmholtz. Se implementó el solver (`solver2d.py`), la prueba PML en vacío (reflexión 2,8e-12 / 6,7e-12) y la calibración a incidencia normal (conservada en `calibracion_incidencia_normal.json`).
2. **Enmienda 1**: esa geometría era imposible (los haces reflejados a incidencia casi normal no se separan en brazos de 30–40λ; hacen falta ~95λ). Pasamos a MZI estándar con divisores a 45° (TM); mallas λ/16 y λ/24; λ/32 declarada no viable.
3. **Coste del solver directo** (`resultados/medicion_coste.json`, 9,5 GB libres, SuperLU monohilo): 62 500 incógnitas en 19 s y 0,34 GB; 160 000 en 161 s y 1,3 GB; 255 195 en 148 s y 1,4 GB. El dominio con w = 8λ tiene 2,1 M (λ/16) y 4,7 M (λ/24) de incógnitas: 6–37 GB y 1–14 h por factorización (λ/16), 14–133 GB y 3–90 h (λ/24), con 21 factorizaciones por malla.
4. **Enmienda 2**: FDTD escalar 2D (TM) en CPU con numpy, solo w = 8λ, barrido con espejo móvil y modelo con el desplazamiento del haz.
5. Ejecución con el FDTD (este informe).

## Implementación
- `fdtd2d.py`: malla de Yee (Ez, Hx, Hy; float32), CPML (m = 3, 3λ de grosor), dt = 1/N_p con N_p = 24 (λ/16) y 36 (λ/24) pasos por periodo (Courant 0,67), fuente de haz gaussiano inyectada en una columna con la técnica campo total/disperso (unidireccional; el campo H sale de la relación de dispersión FDTD), onda continua con encendido de coseno elevado (6 periodos), fasor por acumulación de DFT en ventanas de 10 periodos enteros (la ventana anterior sirve de control de régimen).
- `mzi_fdtd.py`: geometría con todos los elementos verticales (haces a 45° → sin escalones), divisores = película de d = 0,25λ y 40λ de longitud, espejos PEC de 2 columnas, brazos de 30λ (tramo divisor–espejo), cintura del haz de entrada en S1, puertos en las líneas verticales x = ±25λ del centro de S2, potencia por solapamiento P = |⟨E,g⟩|²/⟨g,g⟩² con g el modo gaussiano (misma función en solver y modelo).
- Modelo: r y t complejos de la calibración FDTD (referidos al plano medio de la película), espejos −1, exp(i2πL/λ), haz gaussiano de anchura w constante evaluado con el desplazamiento real del haz B, sin difracción de camino.

## Pruebas previas
- **Dominio vacío FDTD** (haz w = 8λ; `resultados/pml_vacio_fdtd_16.json`, `_24.json`): reflexión en potencia 3,3e-10 (45°) y 1,9e-14 (0°) a λ/16; 3,8e-10 y 2,3e-14 a λ/24; criterio 1e-3 cumplido. Solapamiento aguas abajo del haz 0,9987 (15λ).
- **Calibración a 45° con FDTD** (`calibracion_fdtd_45.json`; punto de partida `calibracion_45.json`): a λ/16 el n de Helmholtz (2,4220) daba una diferencia de |r|² de −0,008, se ajustó a **n = 2,4270** (R = 0,49975, T = 0,50030); a λ/24 **n = 2,4850** sin ajuste (R = 0,49702, T = 0,50303). Diferencias < 0,005 en ambos casos. La película difiere entre mallas por el ajuste, y el modelo usa los coeficientes de cada malla.

## Resultados del barrido (`resultados/RESULTADOS_VALIDACION.json/.md`)
| Malla | Simulaciones | E_max | Peor punto | Pérdida del solver | Dif. de régimen | CPU por simulación | Memoria pico |
|---|---|---|---|---|---|---|---|
| λ/16 | 12 | 0,0269 | ΔL = 0, P1 | 2,4–3,0 % | ≤ 1,2e-5 | 323 s | 0,13 GB |
| λ/24 | 18 | 0,0275 | ΔL = 0, P1 | 2,5–3,0 % | ≤ 1,6e-5 | 1096 s | 0,26 GB |

- Dominio: 2,33 M celdas (λ/16, 4560 pasos) y 5,24 M (λ/24, 6840 pasos), 190 periodos. Con 3 procesos en paralelo, 71 ms/paso (λ/16) y 160 ms/paso (λ/24). En una sola simulación (prueba de vacío) cuesta ~20 ns por celda y paso.
- El error es sistemático: el modelo sobrestima la potencia en el puerto dominante (el solver pierde ~2,7 % por difracción). El error por punto va de 0,0129 a 0,0275.
- Convergencia de malla: |E_max(λ/16) − E_max(λ/24)| = 0,0006 < 0,005.

## Desviaciones y puntos a declarar
- **Barrido de ΔL**: el espejo móvil solo ocupa posiciones de la malla (δ = k h). La diferencia de camino efectiva es √2·δ (0,0884λ por celda a λ/16; 0,0589λ a λ/24), así que no se pueden obtener 21 puntos equiespaciados exactos. Se simularon los desplazamientos necesarios para cubrir los 21 objetivos jλ/20: k = 0…11 (12 simulaciones) a λ/16 y k = 0…17 (18) a λ/24. El modelo se evalúa en la geometría real de cada simulación. La cobertura de [0, λ] llega a 0,972λ (λ/16) y 1,002λ (λ/24).
- La cintura del haz de entrada está en S1 (la entrada se inyecta 8λ antes con la curvatura correspondiente). Es una decisión de implementación: con la cintura en la fuente la pérdida teórica sería ~3,1 % en vez de 2,7 %; en ambos casos la decisión es la misma.
- Ventana de DFT de 10 periodos sobre 190 en total; un primer ensayo con 150 periodos dejó una diferencia de régimen de 1,3e-3 y se descartó (`resultados/_descartados/`); con 190 la diferencia es ≤ 1,6e-5.
- Elementos de 40λ de longitud (semilongitud 20λ ≈ 1,8·√2·w proyectado): el truncamiento (amplitud 4,7 % en el borde) forma parte de la geometría finita y no explica el error, que el diagnóstico con difracción reproduce.
- No se ejecutaron w = 4λ ni 16λ (descartados por la Enmienda 2).

## Limitaciones
Solver 2D escalar; espejos PEC; película dieléctrica sin pérdidas; el modelo se valida solo para w = 8λ, divisores a 45° y brazos de 30λ. La refutación se refiere al modelo **sin difracción de camino**; no refuta el modelo con propagación gaussiana libre, que da E_max ≈ 0,005 en este régimen (resultado exploratorio, sin preregistro, que requeriría una nueva prueba para confirmarse).

## Integridad
Hashes SHA-256 de código, calibraciones y resultados en `resultados/SHA256SUMS.txt` (saltos LF).
