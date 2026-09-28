# Neuro3D

![Neuro3D](Docs/assets/neuro3d-hero.png)

> Arquitectura experimental de una red neuronal digital de inspiración óptica: el estado de cada neurona combina intensidad, fase, frecuencia, energía y color, y las señales se propagan por un grafo dirigido para ser visualizadas como una galaxia 3D.

![Estado del proyecto](https://img.shields.io/badge/estado-CPU--ready%20%7C%20GPU--dormant-6f42c1)
![Blender](https://img.shields.io/badge/Blender-adaptador%20preparado-e87d0d)
![Unreal Engine](https://img.shields.io/badge/Unreal%20Engine-5.6%20plugin%20preparado-6e4c9b)
![Licencia](https://img.shields.io/badge/licencia-MIT-2ea44f)

## Qué es

Neuro3D explora una arquitectura neuronal visual en la que la información
se representa mediante variables ópticas abstractas. El objetivo es aprovechar las
fortalezas de la GPU —paralelismo, color, campos y renderizado— sin presentar el
prototipo como hardware fotónico real ni como un solucionador completo de Maxwell.

La reconstrucción actual separa el modelo verificable de sus adaptadores visuales:

- **Oracle CPU**: referencia determinista, reproducible y ejecutable sin GPU.
- **Blender**: laboratorio 3D con vista previa CPU y shader GPU preparado pero
  deliberadamente dormido.
- **Unreal Engine**: plugin `SantoGrialPhotonic` con ciclo RDG y compute shaders;
  su compilación real queda pendiente de disponer de UE 5.6.

## Vista de arquitectura

![Capas de la arquitectura](Docs/assets/architecture-layers.png)

El flujo previsto es: configuración del grafo → emisión y acumulación de señales →
estado neuronal → visualización 3D. La capa visual consume el estado; no vuelve a
calcular la red.

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
python Blender/tests/test_static_contract.py
```

Estas pruebas no importan `bpy`, no inicializan un contexto GPU, no lanzan Blender y
no ejecutan shaders.

## Versión Blender

Consulta [Blender/README.md](Blender/README.md) y el [plan completo de pruebas](Docs/BLENDER_TEST_PLAN.md).

La versión Blender está marcada como **CPU-ready / GPU-dormant**. Su addon crea una
vista previa CPU cuando el usuario la ejecuta explícitamente; no activa cómputo GPU
por defecto. El shader experimental está en
`Blender/shaders/nebula_photonic_compute.glsl`.

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
| Pruebas CPU Blender | Preparadas para ejecutar sin GPU |
| Contrato estático addon/shader | Preparado |
| Shader GPU Blender | No ejecutado por decisión de seguridad |
| Paridad CPU/GPU Blender | Pendiente de autorización y GPU libre |
| Compilación Unreal 5.6 | Pendiente de instalar/restaurar UE |

## Licencia

MIT. Consulta [LICENSE](LICENSE).
