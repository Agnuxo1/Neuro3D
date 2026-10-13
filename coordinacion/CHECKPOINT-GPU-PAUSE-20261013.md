# Pausa temporal GPU para voces de Villa Anzuelo

Autorización humana explícita; proyecto conservado, no cancelado. Entrenador MNIST y lanzadores Neuro3D suspendidos, sin terminar procesos de Villa. Modelo, Adam, RNG e historia permanecen en los procesos vivos: no hay checkpoint de pesos en disco porque el ejecutor no dispone de guardado intermedio. No reiniciar ni terminar estos procesos si se quiere reanudación exacta. Se retiene su VRAM; la ejecución GPU y el turno se han cedido.

Recibo y artefactos: `D:\PROJECTS\.cognition\neuro3d-gpu-pause-20261013-villa\checkpoint.json`. La cola bloquea nuevos nombres Neuro3D mediante `D:\PROJECTS\.cognition\gpu_queue\pause_registry.json`. Reanudación exclusivamente después de terminar las voces, con el helper documentado en esta carpeta y admisión FIFO; no ejecutar el shard desde cero ni consumir TEST de nuevo.
