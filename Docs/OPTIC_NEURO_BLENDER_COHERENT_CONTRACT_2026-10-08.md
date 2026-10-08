# Contrato coherente de OpticNeuroBlender

Se incorpora un contrato ejecutable propio para unidades, entradas coherentes, fase, direcciones de parámetros y detectores. Se comprobó su admisión dentro de Blender sobre la escena Iris real, además de una fixture que se guarda y reabre. Es un cierre de esta pieza de software; el recorrido óptico completo, el presupuesto nativo y el entrenamiento desde la captura siguen pendientes.

## Convenciones aplicadas

| Magnitud | Convención admitida | Lo que acredita |
|---|---|---|
| Coordenadas y desplazamientos | BU, transformaciones afines racionales de los números capturados | Modelo representado; no recuperación de geometría previa a cuantización |
| Longitud de onda | Valor hexadecimal positivo en BU, igual al contrato del motor escalar | Coherencia dimensional entre longitud y fase |
| Escala de escena | Valor capturado `metres_per_BU`; inicialmente `SCENE_DISPLAY_SCALE_ONLY` | Conversión declarada de interfaz, sin calibración física |
| Fase de campo | Tiempo `exp(-i omega t)`, propagación `exp(+i 2 pi L/lambda)`, n=1 | Una convención común; no aproximación silenciosa de un índice material |
| Espejo y divisor | `-exp(i phi)`; transmisión `sqrt(tau)` y reflexión `i sqrt(1-tau)` | Compatibilidad explícita con el motor propio |
| Entradas | Cinco campos complejos explícitos, una portadora/grupo coherente y referencia de lanzamiento común; sin normalización implícita | Conservación de términos cruzados entre entradas |
| Parámetros | Las 32 direcciones capturadas son coordenadas de traslación en BU | No se declaran 32 grados físicos independientes; el acoplamiento entre espejos y las fases entrenables siguen necesitando su parametrización |
| Detector | Potencia modal normalizada `q=|E|²` en la referencia común; sin renormalizar | Puerto escalar ideal con origen/dirección declarados, no potencia espacial integrada de un haz físico |
| Vatios | `P_ref q` sólo con `P_ref` positiva explícita y convención SI declarada | Conversión de modelo; nunca una calibración medida por defecto |

La captura Iris declara escala de escena 1 m/BU y lambda representada aproximadamente 0,1 BU. Su producto es una conversión de visualización, no la demostración de un láser de 0,1 m ni de fidelidad física. El render, el color de una fuente y la fluencia no fijan la fase compleja.

Las coordenadas de una matriz de rotación son adimensionales; no se aceptan como parámetros de traslación en BU. Tampoco se admiten fuentes independientes, otra referencia/signo de fase, un detector de intercepción, la renormalización de su potencia o parámetros escondidos. Cualquier extensión a polarización, haces finitos, modos guiados o materiales necesita otro contrato y validación.

## Implementación y pruebas

- [Contrato y wrapper de admisión](../Blender/blender_lab/coherent_contract_v1.py): añade metadatos explícitos sin modificar el motor o el protocolo v1 congelados.
- [CLI](../Tools/admit_coherent_capture_v1.py): archivos acotados, claves JSON únicas, rechazo de no finitos, huellas de inputs y salida nueva obligatoria.
- [Controles CPU](../Blender/tests/test_coherent_contract_v1.py): 18 controles del nuevo contrato; con las regresiones de captura, ingreso y abanicos, 50 tests pasan.
- [Fixture bpy](../Blender/tests/test_coherent_contract_blender_v1.py): misma identidad tras guardar/reabrir; cuatro negativas rechazadas.
- [Admisión del `.blend` Iris abierto](../Tools/check_coherent_contract_in_blender_v1.py): captura viva, 104 objetos ópticos, 6.656 triángulos, cinco fuentes, 32 bindings y tres detectores. Blender 4.5.14 LTS, build `62c1db4208e8`.

La captura viva conserva `state_sha256=8624d661252f143653f5b32c744cb7e6b23f71119253d7ad64510bbf1aa1a943`. La CLI independiente conserva todos los valores del paquete v1 anterior después de retirar únicamente el nuevo bloque de contrato. No se ha llamado a `trace_scene()` en estas comprobaciones.

Los controles de lectura calculan exactamente campos `1+1`, `1-1` y `1+i`: potencias normalizadas 4, 0 y 2. El baseline de fuentes independientes da 2 en los tres casos. Otros controles conservan un residuo de amplitud `2^-100`, prueban invariancia bajo fase común, cambio equivalente de escala y el medio ciclo producido por un desplazamiento de espejo `lambda/4` en doble paso. Son identidades analíticas conocidas y comprobaciones del código, no salidas propagadas de Iris.

![Controles de coherencia](assets/coherent-contract-controls-2026-10-08.png)

Se conservaron dos fallos de desarrollo: la primera fixture bpy usaba límites textuales donde la captura espera números; el primer check de equivalencia de la CLI detectó que faltaba el bloque de huellas legacy. Los intentos posteriores corrigen esos errores sin modificar los recibos anteriores. Los negativos y sus fuentes están en [el índice de artefactos](validation/coherent-contract-2026-10-08/artifact_index.json).

## Reproducción del control de admisión

```text
python -m unittest Blender.tests.test_coherent_contract_v1 Blender.tests.test_scalar_scene_ingress_v1 Blender.tests.test_surface_union_interior_v1 Blender.tests.test_blender_lab_capture_v1 -v

python Tools/admit_coherent_capture_v1.py --capture Docs/validation/blender-lab-capture-2026-10-08/resume01/iris/capture.json --semantics Docs/validation/captured-scalar-ingress-2026-10-08/semantics.json --fields Docs/validation/captured-scalar-ingress-2026-10-08/fields_admission_only.json --contract Docs/research/iris_coherent_contract_v1.json --out NUEVO_PAQUETE.json
```

Los intentos bpy se ejecutaron ocultos, en un hilo CPU y prioridad baja, con preflight de 4.000 MiB libres, suelo de 2.500 MiB, límite RSS de 1.500 MiB y 90 segundos. La fixture final usó pico aproximado de 133 MiB y la admisión Iris 236 MiB. Estos tiempos y recursos son de controles supervisados de software, no coste completo de inferencia ni comparación de rendimiento.

El protocolo del piloto conserva SHA256 `5d0cf372f2f66f043c2a219ba6a60f0182ced8a60039348d486ec163be736226` y estado preparado/no ejecutado. La skill exige preregId/IPFS externo; la excepción GitHub solicitada aún necesita una respuesta humana explícita. Este contrato no cambia los inputs o los criterios de ese piloto.

## Alcance del cierre

Se admite la semántica de la prioridad 2 para el modelo escalar actual y se prepara un wrapper opt-in para consumirla. Todavía hay que demostrar que todos los backends y el entrenamiento preservan esa semántica durante el forward completo. Por ello la prioridad global queda `PARTIAL_SEMANTIC_CONTRACT_VERIFIED`, sin certificación de campos, vatios medidos, aprendizaje, GPU nueva ni óptica física.
