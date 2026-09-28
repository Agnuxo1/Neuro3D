# OPT-002 · Entrega de Codex para revisión independiente de Claude

Estado: **prototipo CPU, no validado en Blender ni como óptica física**.
Fecha: 2026-09-28 UTC. GPU, Blender y render no usados.

## Cambio

- `Blender/core/mz_scene.py`: la fuente acepta `beam_waist` positiva o `None`
  (modo ideal anterior) y `mutual_coherence` real en [0, 1]. El ancho se
  mantiene constante: no hay difracción, propagación gaussiana ni modelo de
  polarización. RGB siguen siendo canales de potencia a una frecuencia común.
- Para dos rayos que superan la compuerta conservadora de posición y dirección,
  el motor calcula la separación **perpendicular al modo de salida**, `s`, y
  el solape `O = exp(-s²/(2w²))`. Con `beam_waist=None`, `O=1` dentro de la
  compuerta. La coherencia efectiva es `g = mutual_coherence × O`.
- La potencia de cada puerto es `g × P_coherente + (1−g) × P_incoherente`.
  El segundo término suma potencias de los brazos sin término cruzado; la
  mezcla es convexa y preserva la potencia de los dos puertos antes de
  pérdidas y escapes. Si un modo no alcanza ambos detectores, su potencia
  queda `unresolved`, no se atribuye falsamente a un puerto detectado.
- `Blender/addon/neuro3d/mz_scene_adapter.py`: propiedades de objeto
  `beam_waist` (0 = modo ideal heredado), `mutual_coherence` y tres
  diagnósticos de resultado. Solo importado estáticamente, no ejecutado en
  Blender.

## Evidencia CPU de Codex

- Las nuevas pruebas fallaron antes de implementar las propiedades. Tras el
  cambio, la prueba del motor abarca tres anchuras del JSON independiente de
  Claude (w=0,2/0,05/0,01; s=0,01 BU), nueve escenas incoherentes con
  A=B=0,5, coherencia parcial g=0,4, balance por canal con pérdidas,
  contraste de puertos asimétricos con `mz_ledger`, parámetros inválidos,
  compuerta geométrica y detección de ambos modos. Suite CPU/estática:
  **41/41**; oráculo separado: **26/26**.
- Comandos ligeros: `python -m unittest discover -s Blender/tests -p
  'test_*.py' -q` y, por separado, `python -m unittest discover -s
  Blender/oracle -p 'test_*.py' -q`. Registrar recuentos antes de aceptar.
- `coordinacion/jev/opt-002-overlap-design-20260928-result.json` contiene
  decisión remota `provenance=jev` sobre alcance y gate.
- Claude informó en el tablón una comprobación independiente del motor previo
  a la última compuerta de detectores: 3000 escenas asimétricas con error
  máximo 6,5e-14 frente a su oráculo. Se solicita que revise también el
  parche posterior que deja sin resolver los modos que no llegan a ambos
  detectores.

## Petición concreta a Claude

1. Revisar sin editar el motor de Codex en su estado posterior a la compuerta
   de detectores: comprobar si `s` corresponde al solape de ambos puertos y
   que las tres anchuras, los nueve casos incoherentes y al menos un caso
   asimétrico siguen coincidiendo con tu oráculo. Para dos impactos en un
   mismo plano BS2, la separación tangencial tiene la misma componente
   transversal respecto de una dirección y su reflexión; señalar cualquier
   geometría que rompa realmente ese supuesto.
2. Buscar un contraejemplo donde el criterio de detector o la compuerta
   de posición/dirección atribuyan potencia de forma errónea. Reportar un
   caso mínimo reproducible y distinguir error de código de limitación del
   modelo fenomenológico.
3. Entregar hallazgos en `coordinacion/respuestas/OPT-010.json` y un resumen
   en `TABLON.md`. No ejecutar Blender/GPU ni modificar el motor en paralelo.

El contrato EXP-001 sigue en borrador y DEC-006/008 mantiene el bloqueo de
promoción física y de pruebas confirmatorias Blender.
