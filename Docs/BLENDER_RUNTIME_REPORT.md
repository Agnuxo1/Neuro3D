# Verificación real de Neuro3D en Blender

Fecha: 2026-09-28. Versión: Blender 4.5.14 LTS portátil para Windows x64,
obtenida del servidor oficial de Blender y validada con el SHA-256 oficial.
Instalación local: `D:\TOOLS\Blender\blender-4.5.14-windows-x64`.

La prueba se ejecutó en background, con un hilo y prioridad de proceso baja.
El runner impuso 45 segundos por fase, 1,5 GiB de memoria máxima del proceso y
un mínimo de 2,5 GiB de RAM libre del sistema. No se solicitó render, Cycles,
Eevee, CUDA ni shader de cómputo. Se verificó que no quedara ningún proceso
Blender después de la prueba.

## Resultado observado

| Comprobación | Resultado |
|---|---:|
| Objetos ópticos de la escena | 3 |
| Intensidad recibida alineada | 0,7053474966 |
| Activación del receptor | 0,3657724623 |
| Mover receptor fuera del rayo | Señal cero |
| Reflector con filtro azul | Solo potencia azul |
| Guardar/reabrir `.blend` | Estado y nuevo trazado coinciden |
| Girar reflector tras reapertura | Señal cero |
| Cambiar frecuencia del emisor | Cambia la fase recibida |
| Pico de RAM observado, creación | 128,3 MiB |
| Pico de RAM observado, reapertura | 128,7 MiB |

Artefacto local de la segunda ejecución:
`D:\PROJECTS\.artifacts\neuro3d-blender-smoke-v2\neuro3d-optical-circuit.blend`.
Los registros de ambas fases están en la misma carpeta. No se incluyen en Git
porque son resultados específicos de esta máquina.

Se usó `Blender/tests/run_blender_smoke.py`, que llama
`Blender/tests/blender_runtime_smoke.py`. Las 18 pruebas unitarias y estáticas
también pasaron en Python CPU antes de esta ejecución.

## Alcance

Esto demuestra que el estado del circuito depende de la geometría y de las
propiedades ópticas guardadas en una escena Blender real. El cálculo del rayo
lo realiza Python en CPU sobre esos datos de escena. No demuestra todavía una
red grande, interferencia entre múltiples caminos, aprendizaje de pesos,
simulación electromagnética completa ni cómputo de la luz por el renderer/GPU.
El panel interactivo del addon también queda por comprobar.
