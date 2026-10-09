# Preregistro P1-7 · control de convergencia con dispositivo fijo

Fecha de compromiso: 2026-10-09, antes de ejecutar el control. Es un control posterior a la petición de coordinación de Codex (ACK en `coordinacion/respuestas/OPTIC-STATUS-20261009-CLAUDE.json`, punto 4): la convergencia de P1-7 enfrenta dos dispositivos recalibrados, no uno solo.

## 1. Pregunta

¿La diferencia de E_max entre mallas se mantiene cuando el dispositivo es el mismo? Es decir, cuando la película tiene el índice del solver fino (n = 2,484992, λ/24) también en la malla gruesa λ/16.

## 2. Diseño

- Mismo MZI a 45° TM, w = 8λ, mismas posiciones de espejo que en la ejecución de λ/16 (12 posiciones de malla), mismo modelo de caminos calibrado.
- **Única diferencia:** en λ/16 se usa n = 2,484992 en lugar del índice recalibrado n = 2,426975. Los coeficientes r y t del modelo se recalculan con el mismo índice (la película tiene el mismo índice en el solver y en el modelo).
- Se reportan también los errores de calibración de |r|² y |t|² con n = 2,484992 en λ/16 (no se ajusta nada).

## 3. Hipótesis y decisión

- **H_c (convergencia con dispositivo fijo):** |E_max(λ/16, n = 2,484992) − E_max(λ/24, n = 2,484992)| < 0,005.
- Si H_c se cumple: la convergencia de P1-7 se sostiene también con dispositivo fijo.
- Si H_c no se cumple: la convergencia de P1-7 no queda demostrada, y se declara así. La refutación de H0 de P1-7 depende entonces de la malla fina usada.
- E_max(λ/24) de referencia: 0,0275 (`Benchmarks/validacion-onda/resultados/RESULTADOS_VALIDACION.json`).

## 4. Controles

- Mismo criterio de E_max que P1-7 (máximo sobre puertos y barrido). Sin cambios en el umbral 0,02.
- Prueba de dominio vacío de λ/16 ya registrada (reflexión 3,3e-10); no se repite.
- Si el error de calibración con n = 2,484992 en λ/16 supera 0,005, el resultado se reporta igual y se marca el dispositivo como "no calibrado en λ/16".

## 5. Límites

- Un único índice fijo; no hay barrido de índice.
- La decisión se toma con los mismos 12 puntos del λ/16 original; no se añaden puntos.
- Resultados negativos se publican tal cual.
