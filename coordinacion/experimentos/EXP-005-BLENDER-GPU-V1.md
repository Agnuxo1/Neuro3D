# Consumidor GPU nativo Blender · contrato v1 previo a medición

2026-09-30 01:02 UTC. Codex; fallback local, JEV bloqueado por seguridad.

Extiende consumidor OpenGL externo sin sustituir su resultado. API pública
GPUShaderCreateInfo/gpu.compute.dispatch, texturas de entrada y imageStore.
Referencia primaria: [ejemplo oficial Blender](https://github.com/blender/blender/blob/main/doc/python_api/examples/gpu.11.py).

Seis .blend v4 reabiertos SIN guardar/cambiar archivos. Readback evaluado exacto
frente a snapshots congelados. Nueve entradas por escena: tres bases y pares1/i.
Cada entrada retraza con scene.ray_cast CPU y transmite impactos crudos; fase y
coeficientes/suma compleja/abs² exclusivamente en shader nativo dentro de Blender.
No matrices ni campos precalculados en inputs. Oráculo CPU solo valida.

ABI textura: FP32 hi/lo conserva distancias/fases FP64, reconstrucción y
productos/reducciones FP64, sin/cos FP32 explícito; outputRGBA32F. Lambda también
hi/lo reconstruida en FP64. Un trabajo por puerto, sin atómicos, todos los puertos.
512caminos/64impactos máximo;64texeles de ancho y filas acotadas. Sin capacidad.

Antes de medir:54probes, abscomplejo<=1e-4 contra oráculo completo y CPU retenido,
potencia/balance<=2e-4,abs²vsRe/Im<=1e-6 por outputFP32,sham<=1e-12,
efectos phaseA/B/roof/lambda>1e-3. No relajación después. Hashes inputs/code
retenidos y archivos v4 invariantes después; fallo se conserva como fallo.

Modo gráfico con ventana OCULTA para disponer de contexto GPU (sin interacción
ni render); wrapper hijo propio, timeout110s/guard120s,1hilo,host1,5GiB/device1GiB,
RAMlibre>=4GiB,VRAMtotal<=18GiB,temp<=80°C,deadline06UTC y gpuq exclusivo.
Si API no compila/no hay contexto, registrar fracaso, NO fallback externo secreto.

Sigue simulación digital híbrida, NO intersecciones RT ni óptica física. La nueva
capacidad es ejecutar el cálculo del campo en la GPU nativa de Blender, no una
ventaja comparativa. Tiempos kernel+lectura no incluyen trazado/carga/contexto.
