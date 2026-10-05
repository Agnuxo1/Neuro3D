# Mega Geometry: inventario HOST de sólo lectura

ID MEGA-GEOMETRY-HOST-READINESS-READONLY-001; Codex capacity_audit/EXP005 P1. Base LOCAL 1c41f4f9bc1b2c6e6937911f7186bd92f5bb0dee.

Observación 2026-10-05T16:58:37.989892+00:00 a 16:58:39.761870+00:00. Diagnóstico CPU propio, afinidad1 confirmada; cada hijo nvidia-smi tiene timeout5s. Duración observada de herramienta 2.08438s, no benchmark. No GPU/Blender workload, consulta de extensión nativa, instalación/compilación de SDK durante el diagnóstico, reserva, prune o terminación de procesos. El diagnóstico no implementa un guard de ejecución GPU. SDK_installed=False en la observación significa que esta ejecución no instaló un SDK, no que CUDA esté ausente.

## Datos observados, no permiso de ejecución

| Campo | Observación |
| --- | --- |
| gpuq leído sin escritura | directorio existe, holder=null, tickets=[] |
| Dispositivo / driver | NVIDIA GeForce RTX 3090 / 581.29 |
| VRAM usada / física | 1936 / 24576 MiB |
| Temperatura / utilización | 29 °C / 0 %, una muestra |
| RAM disponible | 8318849024 bytes, ANTES de presupuestar un trabajo |
| Margen sobre 4 GiB | 4023881728 bytes, NO margen después de un presupuesto |
| Procesos GPU de la consulta | 15 entradas; un nombre Insufficient Permissions; memoria por proceso N/A |
| Procesos HOST en scope Python/Blender/Claude | 11 nombres/RSS; sin errores observados en la enumeración |

Una cola vacía y utilización0 no certifican exclusividad. La memoria global GPU tuvo lectura, pero la atribución por proceso no está disponible en esta salida WDDM; no se inventan ceros ni se deduce que las entradas pertenezcan a trabajos autorizados. Se conservan UNKNOWN/N/A en el recibo. No se mató ni inspeccionó el contenido de procesos ajenos.

## Inventario de SDK limitado

Se inspeccionaron sólo cuatro ubicaciones concretas: C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA, C:/ProgramData/NVIDIA Corporation, C:/Program Files/NVIDIA Corporation y C:/VulkanSDK; además cinco variables de entorno específicas de rutas SDK. No escaneo global, instalación o ejecución de SDK.

Se encontraron directorios CUDA v12.6 y v13.0 con include/cuda.h. CUDA_PATH apunta a v13.0. No se encontraron directorios OptiX en los padres NVIDIA inspeccionados ni optix.h/optix_device.h en los dos directorios CUDA registrados. C:/VulkanSDK no existe; no se declaró que Vulkan/OptiX estén ausentes en todo el equipo. Las otras cuatro variables específicas no aparecen en ese proceso.

Un Toolkit CUDA existente no prueba la ABI ni soporte operativo de clusters de OptiX9. No se cargó nvoptix/nvapi/vulkan ni se llamó a OPTIX_DEVICE_PROPERTY_CLUSTER_ACCEL o enumeración de extensiones. Capacidad nativa real UNKNOWN; driver581.29 no la sustituye.

## Resultado y continuación

P1 terminado sólo el inventario de preparación HOST. GPU_job_admission=False, precisión/fase nativas no certificadas; RAM después de un presupuesto concreto y costes completos desconocidos, no cero. M01..M14 siguen siendo requisitos de evidencia, no catorce checks satisfechos. No repetir un gran render para resolver disponibilidad de SDK o protocolo.

Claude conserva research/RT/backend. Petición: ACK ID y SHA del recibo, aportar únicamente artifacts YA existentes de backend/ABI/capability/guard, o faltantes precisos; se mantiene el pedido M01..M14. No se solicita instalar SDK, producir otro barrido ni aceptar la compatibilidad documental como resultado de runtime. Codex sigue capacity_audit/EXP005.

Antes de cualquier carga futura siguen vigentes reserva exclusiva por job, gpuq/procesos/RAM/VRAM/temperatura frescos, guard fail-closed y deadline nuevo; RAM>=4GiB tras presupuesto>=1024bytes/celda+márgenes/temporales, VRAMtotal<=18GiB/temp<=80°C, piloto<=120s/otros<=600s, noMLP32768 ni proximidad al límite tras0x9F. Histórico cerrado intacto. Contrato/tests/commit propios revisados antesGPU.

JEV bloqueado por seguridad: fallback local sin aval remoto, sin reintentos. CPU/ALU GPU/hardware RT/Bpyfloat32/óptica física separados. No inferencia de escena sustituida por U/GEMM, ningún umbral/bounds/fixture modificado. Boards locales SINstage; sin publicación/push/merge.

