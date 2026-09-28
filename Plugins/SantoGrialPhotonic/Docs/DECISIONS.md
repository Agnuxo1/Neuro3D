# Santo Grial: decisiones de reconstrucción

## Bloqueo de objetivo

El objetivo único de este trabajo es desarrollar **Nebula Santo Grial**: una red neuronal digital ejecutada en GPU, con estados ópticos abstractos y futura visualización 3D en Unreal Engine. Las menciones a Solar Filaments, Kaggle, P2PCLAW u otros proyectos en documentación auxiliar no son objetivos ni destinos de trabajo; no se incorporan al código ni sustituyen a NEBULA.

La documentación auxiliar contiene credenciales y tokens en texto plano. No se usan, no se copian y no se registran en este proyecto. Deben considerarse expuestos y revocarse fuera de este repositorio.

## Estado de la evidencia

- El proyecto local base es `D:\PROJECTS\9_NEBULA_NEW` y declara Unreal Engine 5.6.
- El archivo de Drive `NEBULA_EMERGENT_UE5.h` describe una galaxia neuronal con buffers de neuronas y fotones, Niagara, Lumen y OptiX, pero también contiene partes conceptuales y dependencias que impiden usarlo como núcleo fiable.
- El código legado mezcla el módulo de juego `NEBULA`, un plugin `NEBULA` y un plugin `CUDA`, además de duplicar fuentes. Se conserva como referencia; no es el camino de compilación del corte nuevo.
- No hay una instalación de Unreal Editor local detectable en este equipo. Por tanto, la compilación UE queda pendiente de ejecutarse en una máquina con UE 5.6.

## Consulta JEV

JEV recomendó: reconstrucción como simulación numérica digital en GPU; C++ para ciclo, parámetros y validación; RDG para dependencias y doble buffering; compute shaders para propagación y estado; Niagara para consumir buffers y Lumen solo para iluminación escénica; OptiX/RTX como extensión posterior. Su corte vertical es de 1.024 neuronas y grafo fijo, con comparación CPU/GPU, checksum por frame, error documentado, decaimiento energético, latencia y throughput.

Se intentó un segundo gate JEV después de implementar el plugin, pero el backend agotó el tiempo de espera. No se considera una aprobación; queda como gate pendiente.

El 2026-09-22 se reparó y verificó el conector local canónico de JEV en `E:\Rescate-C-2026-09-21\Documents\JEV-Orchestrator`. `doctor` confirmó la disponibilidad del perfil sin exponer claves y `probe --profile lareliquia` confirmó conexión real con `jev-1.13.0`. La consulta tipada específica de Nebula respondió con confianza 0.99 para `ue_compile_gate` y `evidence_first`; recomendó localizar una instalación válida de UE 5.6 y compilar antes de añadir visualización, escala u OptiX. La política resultante es pedir otra opinión solo ante incertidumbre, fallo o impacto alto, y pasar a otros modelos únicamente un paquete compacto de evidencia.

## Decisión de implementación

La primera entrega usa tres pases GPU deterministas:

1. `EmitSignalsCS`: cada arista emite una señal con intensidad, fase, frecuencia y color.
2. `AccumulateFieldsCS`: cada neurona suma el campo complejo RGB de las señales entrantes.
3. `UpdateNeuronsCS`: actualiza activación, energía, fase, frecuencia, intensidad y color.

El actor incluye ahora un readback periódico opcional (`ReadbackEveryNFrames`) que copia el estado neuronal GPU y registra checksum FNV-1a, neuronas activas y energía total. Esto prepara la comparación CPU/GPU; todavía requiere compilación y ejecución dentro de UE 5.6.

La referencia CPU está en `Tests/photonic_reference.py`. El modelo es digital: usa variables ópticas y propagación coherente como abstracción numérica. No es hardware fotónico ni un solucionador completo de Maxwell.

## Criterios de aceptación del corte

- La referencia CPU es reproducible con semilla fija y su checksum cambia tras inyectar un pulso.
- Un pulso activa al menos un nodo conectado y no activa por sí solo una arista de peso cero.
- Activación y energía permanecen acotadas; la atenuación no aumenta la intensidad de una señal.
- El shader no contiene un cálculo visual independiente: la salida de la simulación es el estado que deberá consumir la capa 3D.
- No se declara equivalencia GPU/CPU hasta ejecutar un readback de una red pequeña y documentar el error máximo por campo.
- No se añade OptiX al primer gate: primero deben pasar compilación UE, readback y comparación.
- El readback debe demostrar que el estado observado procede del buffer calculado, no de una animación CPU paralela.

## Siguiente gate

La búsqueda dirigida del 2026-09-22 no encontró `UnrealEditor.exe` ni una ruta registrada de UE 5.6 en este equipo. Por tanto, el siguiente gate queda bloqueado de forma verificable por la disponibilidad del motor: no se instalará ni modificará software automáticamente. Con UE 5.6 disponible, compilar el plugin, colocar `ASantoGrialPhotonic` en un mapa, capturar el buffer de salida en una red pequeña y conectar una visualización GPU de posiciones/color/intensidad. Niagara no debe volver a calcular la red; solo visualizar el buffer validado.
