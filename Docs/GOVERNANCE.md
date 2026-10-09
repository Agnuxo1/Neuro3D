# Gobernanza de Neuro3D

Vigente desde el 2026-10-09. Cambios: commit explícito y anotación en `coordinacion/TABLON.md`.

## 1. Fuentes y su autoridad

| Qué | Fuente canónica | Autoridad | Reglas |
|---|---|---|---|
| Estado de los objetivos | `Docs/research/optic_neuro_blender_acceptance_v1.json` | Canónica | Es el único lugar donde cambia un estado. Cada cambio cita evidencia (recibo y SHA-256). |
| Cifras y afirmaciones públicas | `README.md` y `Docs/paper/optic_neuro_blender_reproducible_draft_2026-10-09.md` | Derivadas | Las cifras del README deben aparecer en el JSON o en el artículo. Lo comprueba `Blender/tests/test_governance_consistency.py`. |
| Evidencia | Recibos JSON, protocolos y scripts congelados (SHA-256) | Inmutable | No se edita. Un cambio exige un protocolo nuevo con su recibo. |
| Registro de trabajo | `coordinacion/` (TABLON, CHECKPOINT, COLA, THINKTANK, respuestas) | Registro append-only | No es evidencia. Nunca se cita como resultado. |
| Espacio de trabajo y rutas | `Docs/WORKSPACE.md`, `Docs/PATH_MAP.md` | Canónica | Mapa de rutas y procedimiento de reproducción. |
| Cadena EXP-005 | `Docs/EXP-005-CIERRE.md` e índice `Docs/EXP-005-INDICE.md` | Canónica | Estado de cierre e índice generado por `Tools/exp005_index.py`. |

## 2. Vocabulario de estados

Los estados de cada objetivo empiezan por una de estas etiquetas: `OPEN`, `PARTIAL_`, `CAPTURED_`, `OWN_`. Un estado `COMPLETE_` solo puede asignarse si el campo `remaining` está vacío. La prueba automática rechaza cualquier otro valor.

## 3. Regla de afirmaciones

El campo `claim_policy` del JSON limita lo que el texto puede afirmar. Mientras `novelty_demonstrated` sea `false`, ningún texto puede presentar la novedad como demostrada. Lo mismo para `physical_device_claim`, `full_project_complete` y cualquier otro campo de la política.

## 4. Criterio de parada para la cadena EXP-005

Regla vigente desde el 2026-10-09 (decisión JEV, procedencia `jev`).

4.1. Un **ciclo de auditoría** es una unidad de trabajo que crea o modifica un documento `EXP-005-*`. Su tiempo máximo es de 2 horas de trabajo efectivo.

4.2. Un ciclo nuevo solo puede abrirse si se cumplen las dos condiciones:
- (a) apunta a un criterio de aceptación en estado `OPEN` o `PARTIAL_` del JSON;
- (b) su predicción falsable está escrita en un documento de preregistro comprometido en git **antes** de ejecutar.

4.3. Si tres ciclos consecutivos no cambian ningún estado del JSON ni añaden evidencia nueva a un criterio, la cadena se detiene y se informa en `coordinacion/TABLON.md`.

4.4. La cadena queda **cerrada** con `Docs/EXP-005-CIERRE.md`. Tras el cierre, los documentos `EXP-005-*` son inmutables. Un trabajo nuevo sobre la geometría axial necesita un identificador nuevo y cumplir 4.2.

4.5. El índice `Docs/EXP-005-INDICE.md` se regenera con `python Tools/exp005_index.py`. Su estado derivado es orientativo: nunca sustituye la lectura del documento.

## 5. Procedimiento de cambio

- **Cambiar un estado del JSON:** commit con la evidencia citada y anotación en `coordinacion/TABLON.md`.
- **Añadir un documento EXP-005:** solo si se cumple 4.2; regenerar el índice.
- **Cambiar esta gobernanza:** commit, anotación en TABLON y registro de la decisión JEV en `coordinacion/jev/`.

## 6. Verificación automática

`python -m unittest Blender/tests/test_governance_consistency.py` comprueba que:
- el JSON tiene los 10 objetivos con estados válidos;
- las cifras clave del README aparecen en el JSON o en el artículo;
- el índice EXP-005 tiene una fila por documento;
- este documento, el README y el cierre enlazan las fuentes canónicas.
