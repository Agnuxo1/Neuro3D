# Neuro3D

![Neuro3D](Docs/assets/neuro3d-hero.png)

> Arquitectura experimental en la que la geometría 3D y las propiedades ópticas de la escena determinan la propagación y transformación de señales entre neuronas. La apariencia visual es secundaria al cómputo.

![Estado del proyecto](https://img.shields.io/badge/estado-CPU--ready%20%7C%20GPU--dormant-6f42c1)
![Blender](https://img.shields.io/badge/Blender-adaptador%20preparado-e87d0d)
![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.6%20plugin%20preparado-6e4c9b)
![Licencia](https://img.shields.io/badge/licencia-MIT-2ea44f)

## Qué es

Neuro3D explora una red neuronal digital donde posición, orientación y respuesta
óptica de los objetos determinan la información que recibe cada neurona. El
primer circuito usa óptica geométrica simulada en CPU y mide intensidad, color,
frecuencia y fase. La ambición posterior es escalarlo y aprovechar la GPU, sin
confundir este prototipo con hardware fotónico real o un solucionador de Maxwell.

La reconstrucción actual contiene:

- **Oracle CPU**: referencia determinista, reproducible y ejecutable sin GPU.
- **Blender**: circuito escena → rayo reflejado → estado receptor, más la antigua
  vista previa CPU y un contrato de shader GPU inactivo.
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

La versión Blender está marcada como **CPU-ready / GPU-dormant**. El addon crea
un circuito de tres objetos y calcula un pulso óptico con un rayo reflejado en
CPU. El circuito se ejecutó realmente en Blender 4.5.14 LTS en background, se
guardó y se reabrió con el mismo estado. Consulta el
[informe de ejecución](Docs/BLENDER_RUNTIME_REPORT.md). La antigua vista previa
visual se conserva aparte. El shader experimental está en
`Blender/shaders/nebula_photonic_compute.glsl`.

Existe además un **prototipo experimental CPU de dos caminos** con dos salidas,
campos complejos y balance de potencia por canal. Sus pruebas CPU pasan, pero
el adaptador de siete objetos todavía no se ha ejecutado dentro de Blender;
no sustituye al circuito de tres objetos ya verificado ni demuestra todavía
interferencia controlada por geometría. Detalles y límites en
[`Blender/README.md`](Blender/README.md).

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

## Estado de verificación

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
