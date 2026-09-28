# Neuro3D para Blender

Esta carpeta contiene el adaptador Blender de Neuro3D. La versión queda
deliberadamente en estado **CPU-ready / GPU-dormant**: se puede validar el modelo,
la geometría de datos y el contrato de shaders sin ocupar la GPU.

## Ejecutar sólo las pruebas CPU y estáticas

Desde la raíz del repositorio:

```powershell
python Blender/tests/test_photonic_model.py
python Blender/tests/test_static_contract.py
```

Estos comandos no importan `bpy`, no crean un contexto GPU y no ejecutan Blender.

## Instalar el addon más adelante

En Blender, instala como addon la carpeta `Blender/addon/neuro3d`.
El panel sólo ofrece una vista previa generada por CPU. No existe activación GPU
automática.

## Estado de la ruta GPU

`shaders/nebula_photonic_compute.glsl` es un contrato experimental preparado para
una futura prueba de compute shader. Antes de habilitarlo habrá que validar:

1. compilación GLSL en la versión concreta de Blender;
2. buffers de entrada/salida y sincronización;
3. equivalencia contra el oracle CPU;
4. readback y checksum por frame;
5. estabilidad y coste en la GPU objetivo.

Consulta el plan completo en `../Docs/BLENDER_TEST_PLAN.md`.
