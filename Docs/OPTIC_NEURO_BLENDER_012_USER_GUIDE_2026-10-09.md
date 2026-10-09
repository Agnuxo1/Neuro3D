# Uso de OpticNeuroBlender 0.1.2

La versión distribuida ejecuta nuestra red óptica escalar desde la geometría evaluada de Blender. Permite inferir, entrenar el ejemplo Iris, cancelar un trabajo propio, recuperar un entrenamiento **terminado** y guardar una copia. Las entradas comparten una referencia coherente. Las potencias son valores modales normalizados, sin calibración en vatios.

## Instalar y abrir el ejemplo

1. Usa Blender **4.5.14 LTS**, la versión realmente comprobada en Windows y Linux. El paquete usa Python y NumPy incluidos en Blender; no requiere instalar Torch ni un entorno Python externo.
2. Descarga [optic-neuro-blender-0.1.2.zip](../Blender/releases/optic-neuro-blender-0.1.2.zip). Su SHA256 es `7b1b747ea6148f6f924a55d7b24a5d065db696295297563f5309904962d9f65f`. Conserva el ZIP cerrado para instalarlo.
3. En Blender abre **Edit → Preferences → Add-ons → Install from Disk**, selecciona el ZIP y activa **OpticNeuroBlender**. Esta ruta para complementos se documenta en el [manual oficial de Blender 4.5](https://docs.blender.org/manual/fi/4.5/editors/preferences/addons.html).
4. Guarda tu escena si tienes cambios antes de pulsar **Abrir ejemplo entrenado propio**: ese botón abre otro archivo. En la vista 3D, abre la barra lateral con **N** y entra en **OpticNeuro**.
5. Selecciona una **Carpeta de evidencia** existente, por ejemplo `D:/PROJECTS/OpticNeuro-runs`. Cada trabajo crea una subcarpeta nueva y conserva sus archivos.

## Inferir con entradas coherentes

Las cinco posiciones de los controles corresponden, en este orden, a **r0, r1, c0, c1, c2**. Para cada entrada define una amplitud no negativa A y una fase φ en radianes: el campo es A·exp(iφ). La fase π permite representar un valor real negativo.

Como primer ensayo usa amplitudes `(0, 0, 0, 0, 1)` y fases `(0, 0, 0, 0, 0)`, y pulsa **Inferir desde la escena**. El panel muestra el estado y las potencias de los detectores **det.R0, det.R1, det.R2**. La carpeta del trabajo contiene el campo complejo y las potencias de los ocho puertos, la captura, el grafo y el resultado completo.

Estos controles **no normalizan automáticamente** las amplitudes: la potencia de entrada del modelo es la suma de sus cuadrados. Cambiar todas las fases por el mismo ángulo cambia la fase global, conservando las potencias del modelo. Cambiar fases relativas puede cambiar las decisiones por interferencia. Cinco entradas nulas producen una decisión indeterminada.

La decisión del panel es el argmax numérico observado. Una decisión certificada requiere un protocolo independiente con intervalos y margen positivo; el panel no presenta ese certificado automáticamente. Los ensayos interactivos son exploratorios.

## Entrenar y conservar la geometría

**Entrenar geometría propia con Iris** usa el dataset incluido y la división fijada 120/30, 60 actualizaciones y 16 traslaciones de pares de espejos. El entrenamiento restablece el centro absoluto no entrenado declarado. Las fases manuales del panel se usan para la inferencia individual del trabajo; no sustituyen la codificación coherente fijada del dataset de entrenamiento.

El worker se ejecuta en otro proceso Blender y conserva 61 auditorías geométricas. En los ensayos publicados se obtienen 110/120 aciertos de entrenamiento y 27/30 reservados. Ese resultado pertenece al ejemplo y al protocolo concreto; no es una garantía para una escena modificada ni una demostración de superioridad sobre otros modelos.

Al terminar, elige su carpeta en **Trabajo que recuperar** y pulsa **Aplicar entrenamiento / recuperar**. La operación comprueba la versión del paquete, la petición, el resultado, el recibo, la escena y las entradas. Si alguna identidad cambió, rechaza el resultado obsoleto. Para aplicar un trabajo anterior, abre su `snapshot.blend` con la misma versión del complemento y restablece las entradas de su `request.json`.

Introduce una ruta de archivo **nueva** en **Nueva copia .blend** y pulsa **Guardar nueva copia**. El complemento rechaza rutas existentes. Conserva también la carpeta de evidencia: el `.blend` por sí solo no contiene todos los registros científicos.

## Cancelación y errores

**Cancelar trabajo propio** detiene solamente el proceso que inició el complemento y conserva sus archivos. La versión 0.1.2 no reanuda el optimizador de un entrenamiento incompleto tras un cierre forzado del host. No aplica resultados parciales como si fueran trabajos completos. Desactivar el complemento cancela su trabajo activo.

El inicio exige 4.000 MiB de RAM disponible. Durante la ejecución se comprueban el límite de tiempo, un suelo de RAM de 2.500 MiB, RSS propio de 1.500 MiB y evidencia de 128 MiB. Si se alcanza un límite, revisa `supervision.json` y `worker.stdout`; un fallo o cancelación no equivale a una potencia óptica cero. Para repetir, inicia otro trabajo conservando el anterior.

El ejemplo admite el contrato de objetos, fuentes y detectores incluido. Modificarlo puede producir una escena no admitida o un recorrido incompleto. La longitud de onda es **0,1 BU**; cambiar la escala visual no establece una calibración física.

## Evidencia de esta versión

- [Nueve controles nativos de instalación, inferencia, entrenamiento y recuperación](OWN_BLENDER_ADDON_PROTOCOL_2026-10-09.md), con el fallo histórico de cierre registrado.
- [Corrección de ciclo de vida 0.1.2: cinco controles y log de salida limpio](OWN_ADDON_LIFECYCLE_PROTOCOL_2026-10-09.md).
- [Reproducción nativa Linux externa: nueve controles y log limpio](EXTERNAL_NATIVE_BLENDER_PROTOCOL_2026-10-09.md).

Estos ensayos ejercitan operadores reales de Blender en modo background. La usabilidad con personas, AMD, recuperación del host tras una caída y la fidelidad de una red óptica física requieren pruebas adicionales. El entrenamiento CUDA propio publicado se ejecuta mediante otro worker de investigación; el complemento 0.1.2 usa CPU.
