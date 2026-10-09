# Cierre de la cadena EXP-005

Estado: **CERRADA** el 2026-10-09. Regla de cierre: `Docs/GOVERNANCE.md`, sección 4.

## Alcance

La cadena EXP-005 es una serie de auditorías CPU de intervalos y guardas sobre la cadena axial de geometría del modelo representado: escena, fuentes, caminos y campos. Cada documento describe un paso de esa cadena.

## Cifras

| Medida | Valor | Fuente |
|---|---:|---|
| Documentos `EXP-005-*` | 330 | `Docs/EXP-005-INDICE.md` |
| Temas (agrupación por prefijo) | 86 | índice |
| Commits con EXP005 en el asunto | 203 | `git log`, 2026-09-29 a 2026-10-09 |
| Estado derivado, marcador dominante: stop / pass / fail / unknown / sin marcador | 147 / 118 / 16 / 2 / 47 | índice, orientativo |

El estado derivado cuenta palabras de cada documento. No es evidencia y no sustituye a la lectura de cada documento.

## Qué establece la cadena (según el JSON de aceptación)

Los objetivos más afectados son el 2 (contrato semántico) y el 4 (propagación y error). Sus estados publicados son:

- Objetivo 2: `PARTIAL_SEMANTIC_CONTRACT_VERIFIED`. Pendiente: familias de geometría más amplias y unidades físicas calibradas.
- Objetivo 4: `PARTIAL_OBSERVED_REPRESENTED_ERROR_CERTIFIED`. Pendiente: preimágenes de la transformación prevista en Blender, incertidumbre geométrica y de entrada, y error completo del modelo físico. Además, el certificado de la aritmética nativa observada.

En términos de la cadena: los certificados de intervalo cubren el modelo **representado**. No cubren la aritmética nativa del motor ni el error físico.

## Qué no establece

- No hay certificado de la aritmética nativa de la escena. Los documentos marcados como STOP o NULL indican que las evidencias disponibles no permitieron cerrarla.
- No hay error de fase físico ni error completo del modelo.
- No hay resultado de tarea (clasificación, regresión o eficiencia) atribuible a esta cadena.

## Decisión

Se cierra la cadena. Los documentos son inmutables. Los trabajos siguientes se dirigen a los objetivos de tarea (P0-3, P0-4) y a la validación física frente a un solver de ondas (P1-7). Cualquier auditoría nueva de la geometría axial sigue la sección 4 de `Docs/GOVERNANCE.md`.
