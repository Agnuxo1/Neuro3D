# Neuro3D

## Progreso científico — 8 de octubre de 2026

Los resultados nuevos están publicados en la [rama de investigación](https://github.com/Agnuxo1/Neuro3D/tree/codex/neuro3d-scientific-closure-20261008) y la [PR #6](https://github.com/Agnuxo1/Neuro3D/pull/6). Consulta el [README actualizado con esquemas, gráficas y GIF](https://github.com/Agnuxo1/Neuro3D/blob/codex/neuro3d-scientific-closure-20261008/README.md) y el [estado de cada punto](https://github.com/Agnuxo1/Neuro3D/blob/58fbe579ccc13eca6d014c8b499c6724460a50e6/Docs/SEQUENTIAL_RESEARCH_PROGRESS_2026-10-08.md).

**Objetivo concretado:** [Blender-Lab como laboratorio abierto y accesible](https://github.com/Agnuxo1/Neuro3D/blob/487b18ceedc0bc0bc56daa6a1e7101148ecb7742/Docs/BLENDER_LAB_RESEARCH_INSTRUMENT_2026-10-08.md), con Neuro3D como demostrador de red óptica que calcula desde la escena. Se han definido su arquitectura y criterios de validación; la distribución y el trazador completo siguen pendientes. [Cuatro antecedentes directos en Blender](https://github.com/Agnuxo1/Neuro3D/blob/487b18ceedc0bc0bc56daa6a1e7101148ecb7742/Docs/BLENDER_LAB_ANTECEDENTS_2026-10-08.md) orientan la comparación.

**Mejora implementada:** [captura real y contratos neuronales interoperables](https://github.com/Agnuxo1/Neuro3D/blob/58fbe579ccc13eca6d014c8b499c6724460a50e6/Docs/BLENDER_LAB_REUSE_AND_CAPTURE_2026-10-08.md). Se registran mallas evaluadas y parámetros sin añadir redondeo decimal: once pruebas unitarias PASS, controles de software en Blender y captura de la escena Iris con 462 objetos. Cinco entradas, 32 direcciones geométricas de espejos y tres detectores se vinculan sobre la captura. El adaptador de Blender Optics Simulator es opcional; no se declara validado el addon completo ni un nuevo resultado de entrenamiento o propagación óptica.

- [Aportación falsable formulada](https://github.com/Agnuxo1/Neuro3D/blob/487b18ceedc0bc0bc56daa6a1e7101148ecb7742/Docs/CONTRIBUTION_AND_FALSIFICATION_2026-10-08.md), con criterio de refutación y dominio explícito.
- [Revisión crítica de antecedentes](https://github.com/Agnuxo1/Neuro3D/blob/487b18ceedc0bc0bc56daa6a1e7101148ecb7742/Docs/LITERATURE_AND_NOVELTY_AUDIT_2026-10-08.md): 194 registros brutos, 175 únicos y extracción de 30 fuentes. La novedad sigue sin demostrar.
- [Cotas racionales de los resultados GPU archivados](https://github.com/Agnuxo1/Neuro3D/blob/f10d74dff3525a317aa89504395aa8a120bc8f3f/Docs/IRIS_RETROSPECTIVE_RATIONAL_CERTIFICATE_2026-10-08.md): error de campo ≤1.282e-13 y 450 decisiones certificadas frente al modelo algebraico canónico. Es un análisis retrospectivo CPU de datos existentes, sin nuevo ensayo GPU ni certificado de recorrido de triángulos.

![Cotas racionales de readbacks históricos](https://raw.githubusercontent.com/Agnuxo1/Neuro3D/f10d74dff3525a317aa89504395aa8a120bc8f3f/Docs/assets/iris-retrospective-certificate-2026-10-08.png)

**Blender es la plataforma principal; Unreal queda como referencia histórica.** RT coherente desde geometría real, AMD real y generalización siguen pendientes. La fabricación fotónica es una línea opcional, independiente de validar el instrumento computacional. La formulación y estas cotas no acreditan una ventaja sobre CNN/GPT ni calidad Nobel.

El resto de esta portada conserva la documentación del corte de código de `main`; los avances y límites actuales se consultan en los enlaces anteriores.

![Neuro3D](Docs/assets/neuro3d-hero.png)

> Arquitectura experimental en la que la geometría 3D y las propiedades ópticas de la escena determinan la propagación y transformación de señales entre neuronas. La apariencia visual es secundaria al cómputo.

![Estado del proyecto](https://img.shields.io/badge/estado-experimental%20%7C%20render%20verificado-6f42c1)
![Blender](https://img.shields.io/badge/Blender-4.5%20LTS-e87d0d)
![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.6%20plugin%20preparado-6e4c9b)
![Licencia](https://img.shields.io/badge/licencia-MIT-2ea44f)

## Qué es

Neuro3D explora una red neuronal digital donde posición, orientación y respuesta
óptica de los objetos determinan la información que recibe cada neurona. El
primer circuito usa óptica geométrica simulada en CPU y mide intensidad, color,
frecuencia y fase. La ambición posterior es escalarlo y aprovechar la GPU, sin
confundir este prototipo con hardware fotónico real o un solucionador de Maxwell.

## Demostrador ejecutable dentro de Blender

![Neurona coherente calculada durante el render](Docs/assets/neuro3d-render-network.png)

Abre [Neuro3D_Render_Network.blend](Blender/render_network_demo/Neuro3D_Render_Network.blend)
en Blender 4.5 y pulsa **F12**. Sus nodos de material calculan interferencia,
fotodetección y activación durante el render EEVEE; Python no suma campos durante
esa inferencia. Las posiciones X de los codificadores y las propiedades de escena
controlan fase, longitud de onda, potencia y umbral. Cuatro copias de una neurona
coherente mínima muestran XOR, con una presentación lista para inspeccionar.

Es un **modelo digital ideal de shader con offsets simbólicos**, no una red
entrenada general, trazado geométrico de esos haces ni computación óptica física.
Los drivers suministran parámetros desde CPU y el render sigue haciendo aritmética.
No hay ventaja de velocidad o eficiencia demostrada. Pruebas por readback EXR,
instrucciones y límites en [la guía del demostrador](Blender/render_network_demo/README.md).

## Rutas de implementación

La reconstrucción actual contiene:

- **Oracle CPU**: referencia determinista, reproducible y ejecutable sin GPU.
- **Blender**: gates híbridos de raycast y campos, más el demostrador EEVEE
  ejecutado en GPU. La vista previa CPU y el contrato GPU antiguo se conservan.
- **Unreal Engine**: plugin `SantoGrialPhotonic` con ciclo RDG y compute shaders;
  su compilación real queda pendiente de disponer de UE 5.6.

## Vista de arquitectura

![Capas de la arquitectura](Docs/assets/architecture-layers.png)

En el nuevo circuito Blender, los objetos de la escena son la fuente de verdad:
sus transformaciones y propiedades ópticas alimentan el trazado, y el resultado
se escribe en el receptor. Lee [la arquitectura óptica](Docs/BLENDER_ARCHITECTURE.md)
para las ecuaciones, el alcance físico y los límites actuales.

## Cómo viaja una señal

![Propagación de señales ópticas](Docs/assets/optical-signal-propagation.png)

Cada arista tiene origen, destino, peso y retardo. La señal conserva una fase y una
frecuencia, transporta color RGB y pierde amplitud mediante atenuación. La
acumulación coherente modifica la activación, energía, fase y color del nodo destino.

## Validación

![Bucle de validación CPU y GPU](Docs/assets/validation-loop.png)

La GPU no se considera validada por compilar un shader: debe producir un readback
comparable con el oracle CPU, con error por campo, checksum y métricas de latencia.

## Inicio rápido sin ocupar la GPU

Desde la raíz del repositorio:

```powershell
python Blender/tests/test_photonic_model.py
python Blender/tests/test_scene_optics.py
python Blender/tests/test_static_contract.py
```

Estas pruebas no importan `bpy`, no inicializan un contexto GPU, no lanzan Blender y
no ejecutan shaders.

## Versión Blender

Consulta [Blender/README.md](Blender/README.md) y el [plan completo de pruebas](Docs/BLENDER_TEST_PLAN.md).

El addon original sigue siendo un circuito CPU; la demo EEVEE anterior es una
ruta separada, ahora ejecutada y verificada. El addon crea
un circuito de tres objetos y calcula un pulso óptico con un rayo reflejado en
CPU. El circuito se ejecutó realmente en Blender 4.5.14 LTS en background, se
guardó y se reabrió con el mismo estado. Consulta el
[informe de ejecución](Docs/BLENDER_RUNTIME_REPORT.md). La antigua vista previa
visual se conserva aparte. El shader experimental está en
`Blender/shaders/nebula_photonic_compute.glsl`.

Las validaciones posteriores de una celda y una malla de 16 interferómetros
(8 modos) superaron gates locales híbridos: Blender determina geometría y
longitudes por raycast, mientras Python suma los campos complejos. El fallo
histórico de referencia de fase y el primer fixture multicelda fallido se
conservan en el historial, sin convertirlos retrospectivamente en éxitos.
Consulta [la auditoría independiente de EXP-004 conf1](Docs/EXP-004-CONF1-INDEPENDENT-AUDIT-2026-09-29.md).
Estos gates no validan óptica física ni el transporte geométrico del nuevo shader.

## Versión Unreal Engine

El plugin está en `Plugins/SantoGrialPhotonic`. Implementa una primera rebanada
vertical con:

1. `EmitSignalsCS`.
2. `AccumulateFieldsCS`.
3. `UpdateNeuronsCS`.
4. Readback periódico para checksum y energía.

Lee [las decisiones de reconstrucción](Plugins/SantoGrialPhotonic/Docs/DECISIONS.md)
antes de modificar el pipeline. No se debe añadir OptiX ni convertir Niagara en el
núcleo computacional antes de pasar compilación UE, readback y paridad.

## Versiones antiguas y compatibilidad

Las fuentes y documentos previos se conservan en el árbol existente para mantener
trazabilidad. No se borran ni se presentan como parte validada del nuevo corte. Los
artefactos generados —`Binaries`, `Intermediate`, `Saved`, cachés, binarios y
credenciales— permanecen fuera del release mediante `.gitignore`.

## Estado histórico de este corte

Esta tabla corresponde al código conservado en este corte. El estado actualizado de investigación se encuentra en los enlaces de progreso anteriores.

| Compuerta | Estado |
|---|---|
| Oracle CPU y checksums | Validado |
| Pruebas CPU y estáticas Blender | 28/28; incluye 10 del prototipo MZ, sin prueba Blender del MZ |
| Circuito guardado/reabierto en Blender | Verificado en 4.5.14 LTS, background CPU |
| Panel interactivo del addon | Pendiente de comprobación visual |
| Contrato estático addon/shader | Verificado sin Blender |
| Shader GPU Blender | No ejecutado por decisión de seguridad |
| Paridad CPU/GPU Blender | Pendiente de autorización y GPU libre |
| Compilación Unreal 5.6 | Pendiente de instalar/restaurar UE |

## Investigación y continuidad

La colaboración Codex–Claude–JEV y la agenda actual están documentadas en
[`coordinacion/PROTOCOLO.md`](coordinacion/PROTOCOLO.md) y
[`coordinacion/CHECKPOINT.md`](coordinacion/CHECKPOINT.md).

## Licencia

MIT. Consulta [LICENSE](LICENSE).
