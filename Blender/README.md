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

El circuito se verificó mediante el API real de Blender 4.5.14 LTS en modo
background, sin render ni shaders GPU. Se creó, trazó, guardó y reabrió una
escena de tres objetos. También se comprobaron cambios de posición, orientación,
reflectancia RGB y frecuencia. El registro está en
[`../Docs/BLENDER_RUNTIME_REPORT.md`](../Docs/BLENDER_RUNTIME_REPORT.md).
La instalación visual del addon en la interfaz aún no se ha comprobado.
Consulta `../Docs/BLENDER_ARCHITECTURE.md` para ecuaciones y límites del modelo.

Para repetir la prueba en Windows con memoria y CPU limitadas:

```powershell
python Blender/tests/run_blender_smoke.py --blender D:\ruta\a\blender.exe --artifacts D:\ruta\de\resultados
```

## Estado de la ruta GPU

`shaders/nebula_photonic_compute.glsl` es un contrato experimental preparado para
una futura prueba de compute shader. Antes de habilitarlo habrá que validar:

1. compilación GLSL en la versión concreta de Blender;
2. buffers de entrada/salida y sincronización;
3. equivalencia contra el oracle CPU;
4. readback y checksum por frame;
5. estabilidad y coste en la GPU objetivo.

Consulta el plan completo en `../Docs/BLENDER_TEST_PLAN.md`.

## Prototipo experimental de dos caminos (solo CPU)

`core/mz_scene.py` calcula un Mach–Zehnder de siete objetos geométricos con
dos detectores, campos escalares complejos y balance de potencia RGB. Los
canales RGB son etiquetas de potencia con una frecuencia simulada común; aún
no representan tres longitudes de onda físicas. Si los dos rayos no llegan
solapados al combinador, el motor marca la potencia como no resuelta y **no**
afirma que hubo interferencia.

Advertencia actual (DEC-006): si ambos caminos alcanzan puntos distintos del
combinador pero caen dentro de la tolerancia, el prototipo compara fases sin
transportarlas a un frente de onda común. Puede declarar constructiva una
configuración geométricamente destructiva. No usarlo como prueba física ni
promocionar sus resultados hasta corregir y verificar ese caso.

`addon/neuro3d/mz_scene_adapter.py` prepara la creación y lectura de esos
objetos en Blender, pero todavía no se ha ejecutado allí ni se ofrece en el
panel. El circuito estable de tres objetos permanece intacto. Las pruebas
ligeras del nuevo núcleo se ejecutan con
`python -m unittest discover -s Blender/tests -p 'test_*.py' -q` desde la raíz;
no arrancan Blender ni la GPU. El contrato experimental sigue en
`../coordinacion/experimentos/EXP-001-BORRADOR.md`.
