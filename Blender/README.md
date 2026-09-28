# Neuro3D para Blender

Esta carpeta contiene el primer circuito óptico de Neuro3D. La escena guarda
emisor, reflector y receptor como objetos con posición, orientación y parámetros
ópticos. El operador CPU lee esos objetos, traza un rayo reflejado y guarda la
señal recibida en el receptor. La visualización es secundaria al cálculo.

## Ejecutar sólo las pruebas CPU y estáticas

Desde la raíz del repositorio:

```powershell
python Blender/tests/test_photonic_model.py
python Blender/tests/test_scene_optics.py
python Blender/tests/test_static_contract.py
```

Estos comandos no importan `bpy`, no crean un contexto GPU y no ejecutan Blender.

## Circuito dentro de Blender

En Blender, instala como addon la carpeta `Blender/addon/neuro3d`.
En la barra lateral **Neuro3D**, pulsa **Create Optical Circuit** y después
**Trace Optical Pulse (CPU)**. Lee `received_intensity`, `received_rgb_power`,
`received_phase`, `activation` y `optical_reason` en las propiedades personalizadas del objeto
**Neuro3D Receiver**. Gira el reflector o mueve el receptor y repite el trazado:
el resultado debe cambiar conforme a la geometría. La escena se puede guardar
con los parámetros y resultados.

El operador **Build Legacy Visual Preview** queda conservado, pero no es una
prueba de cómputo óptico. El circuito nuevo usa tres objetos vacíos y no
inicializa render, Cycles, Eevee, CUDA ni shaders GPU.

Este adaptador aún no se ha ejecutado dentro de Blender en esta máquina porque
no se ha localizado `blender.exe`. Su núcleo geométrico sí dispone de pruebas CPU.
Consulta `../Docs/BLENDER_ARCHITECTURE.md` para ecuaciones y límites del modelo.

## Estado de la ruta GPU

`shaders/nebula_photonic_compute.glsl` es un contrato experimental preparado para
una futura prueba de compute shader. Antes de habilitarlo habrá que validar:

1. compilación GLSL en la versión concreta de Blender;
2. buffers de entrada/salida y sincronización;
3. equivalencia contra el oracle CPU;
4. readback y checksum por frame;
5. estabilidad y coste en la GPU objetivo.

Consulta el plan completo en `../Docs/BLENDER_TEST_PLAN.md`.
