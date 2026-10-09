# Protocolo de búsqueda de novedad · P1-6

Fecha de compromiso: 2026-10-09, antes de ejecutar ninguna consulta. Este commit fija preguntas, consultas y criterios; cualquier cambio posterior se registra como enmienda con fecha.

## 1. Hipótesis

El claim de novedad de Neuro3D es la **combinación** de cuatro componentes:

- **C1.** Red óptica coherente: entradas complejas, propagación coherente, detección por potencia y decisión por argmax.
- **C2.** Entrenamiento de la geometría: los parámetros entrenables son posiciones o retardos de elementos de una escena de render o de geometría evaluada.
- **C3.** Certificado de intervalo: cotas numéricas verificadas para la salida de la red.
- **C4.** Escena capturada: la geometría se lee desde una herramienta estándar de escena (p. ej., Blender) y no desde un modelo analítico.

- **H0 (novedad refutada):** existe al menos un trabajo previo que reporta C1+C2+C3, o C1+C2 con cotas de error verificadas.
- **H1 (novedad soportada):** ningún trabajo reporta C1+C2+C3 juntos.

**Criterio de refutación:** un solo trabajo que cumpla C1+C2+C3 refuta H1. Un trabajo que cumpla C1+C2 y mencione cotas o intervalos se analiza a mano.

Se registra también la situación por componente: cuántos trabajos cumplen cada uno por separado.

## 2. Fuentes

- arXiv (API `export.arxiv.org/api/query`).
- OpenAlex (`api.openalex.org/works?search=`). Sin clave.
- Semantic Scholar: solo si responde; si da 429, se anota y no se insiste.
- GitHub: `gh search repos` y `gh search code` (cuenta autenticada, solo lectura).

## 3. Consultas (fijadas aquí)

1. `coherent optical neural network trainable geometry differentiable ray tracing`
2. `photonic neural network inverse design mirror positions gradient`
3. `optical neural network interval arithmetic certified error bounds`
4. `differentiable rendering optical computing neural network`
5. `Mach-Zehnder mesh training geometry parameters neural network`
6. `scene graph optical propagation neural network verification`
7. `rigorous error bounds photonic neural network`
8. `reconfigurable photonic mesh differentiable simulation ray tracing`
9. `inverse design photonic neural network adjoint geometry`
10. `optical neural network GPU ray tracing OptiX`
11. `unitary mesh optical neural network phase shifters training`
12. `Blender optical simulation neural network`

En GitHub: `optical neural network blender`, `photonic neural network ray tracing`, `coherent optical neural network simulation`, `differentiable optics geometry training`.

## 4. Criterio de inclusión

Un registro entra si su título o resumen contiene al menos dos de estos grupos de términos:
- óptico o fotónico, junto con red neuronal;
- coherente, interferómetro, malla, Mach-Zehnder o unitaria;
- trazado de rayos, render, escena o geometría diferenciable;
- intervalo, cota o certificado.

Se incluyen también los 106 registros de `ELIGIBLE_BACKGROUND_NOT_FULL_EXTRACTED` de `Docs/research/literature_review_audit_v1.json`.

## 5. Extracción

Para cada registro incluido: C1, C2, C3, C4 marcados como `sí`, `parcial`, `no` o `no verificable`, con la fuente de la marca (resumen, o texto completo si se lee). Se indica explícitamente cuando la marca viene solo del resumen.

## 6. Resultados que se publican

- Registro de consultas: fecha, fuente, consulta, número de resultados, código HTTP y SHA-256 de la respuesta.
- Tabla de extracción por registro.
- Los métodos más cercanos (hasta 8) con diferencias concretas respecto a Neuro3D.
- Veredicto por componente y para la combinación, con la limitación de que la búsqueda cubre resúmenes y no el texto completo de todos los registros.

## 7. Limitaciones previstas

- Búsqueda no exhaustiva. Registrarla así.
- Muchas marcas vendrán solo del resumen.
- Semantic Scholar puede no responder.
