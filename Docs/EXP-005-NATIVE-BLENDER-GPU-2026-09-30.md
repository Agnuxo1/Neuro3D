# Campos coherentes en GPU nativa de Blender · PASS local acotado

2026-09-30 01:09 UTC. Código inicial/contrato congelados4418f6e antes de medir;
enmiendas de cierre6d3bc51 y f8c8000, sin cambiar shader/umbrales/fixtures.

54probes: seis .blend v4 reabiertos, tres entradas base y pares1/i. Readback
evaluado de geometría/propiedades contra snapshot exacto, raycasts NUEVOS en CPU
dentro de Blender, propiedades/impactos crudos enviados al shader. La GPU nativa
calcula por impacto propagación, fase, coeficientes t/r/espejo, suma coherente y
abs². No se introduce matriz ni campo previo calculado en CPU durante inferencia.

API basada en [ejemplo oficial de cómputo Blender](https://github.com/blender/blender/blob/main/doc/python_api/examples/gpu.11.py).
GPUShaderCreateInfo/gpu.compute.dispatch/imageStore; backend OPENGL dentro del
proceso Blender4.5.14LTS, NVIDIA RTX3090. Sin contexto ModernGL externo.
Texturas FP32hi/lo reconstruidas en FP64; productos y fases FP64, sin/cos FP32,
readbackRGBA32F. Shader propio `exp005_blender_fields.glsl`.

| Gate | Máximo medido | Umbral previo |
|---|---:|---:|
| Campo vs oráculo completo | 6,73885e-6 | 1e-4 |
| Potencia vs oráculo | 1,09077e-5 | 2e-4 |
| Balance | 7,37235e-6 | 2e-4 |
| abs² GPU vs Re/Im retornados | 1,40431e-7 | 1e-6 |
| Sham | 0 | 1e-12 |

Cuatro efectos causales en basis0: faseA0,0773662,faseB0,1166362,roof0,5893664,
lambda0,3398617; todos>1e-3. 81tests CPU;54probes/66hashes y balances re-auditados
desde artefactos finales, sin nueva GPU. Los seis .blend congelados siguen intactos.

## Fallos preservados y resolución del cierre

V1 y V2 tienen54resultados numéricos correctos, pero NO son ejecuciones estables:
quit_blender durante--python causó EXCEPTION_ACCESS_VIOLATION y el wrapper propio
agotó110s. V1 warning tempC: denegado; V2 ya usa tempD: y conserva crashlog.
Liberar shader/GC antes de quit no resolvió el crash: hipótesis insuficiente.

BacktraceV2: BLI_addhead → WM_event_add_ui_handler → wm_exit_schedule_delayed →
wm_exit_blender_exec → arg_handle_python_file_run. V3 solo programa el cierre por
timer, una vez que existe eventloop, con ventana explícita mediante temp_override.
Mismos54resultados; ahora Blender quit, rc0 y guard completed. Apoya fallo de
contexto de cierre en arranque, no memoriaGPU ni cálculo óptico. No parche del
motor Blender ni certificación global de su ciclo de vida.

Reserva v3: encolada01:07:38UTC, adquirida01:07:46, liberada01:07:55. Guard8,655s,
RAMlibre mínima muestreada8,680GiB,VRAMtotal máxima0,631GiB,GPU33°C; PID10724
terminado y sin Blender residual. Límites120s/pisoRAM4/capVRAM18/temp80/corte06UTC.

Artefactos en `D:/PROJECTS/.cognition/neuro3d/`:
`exp005_native_gpu_v3_20260930_0107.json`, guard asociado y tempD propio.
SHA256 resultado `f49e6c288b78582881b6a4e59ac736ee21bb576b078596c8323947927bf32426`.
V1 `exp005_native_gpu_20260930_0102.json` y V2 homónimo0105 preservados con guards;
V2crash `exp005_native_gpu_v2_20260930_0105_tmp/lambda.crash.txt`.
`quit.blend` en tempv3 es recuperación automática, NO archivo de despliegue.

## Qué sigue faltando

Geometría por scene.ray_cast CPU; NO intersecciones en núcleosRT ni óptica física.
La nueva capacidad es campo/intensidad GPU DENTRO de Blender, no mayor capacidad
de una red ni ventajas de tiempo/energía end-to-end. No cierre EXP-005completo:
faltan escape/modos/propiedades ampliadas, revisión independiente de los pares y
adversarios del shader. Pedidos a Claude sin tocar sus archivos. No escalada grande.

JEV bloqueado por revisión de seguridad: fallback local, sin recomendación remota.
Skills de desarrollo/diagnóstico orientaron el contrato pre-run, preservación de
fallos y aislamiento del ciclo de vida sin relajar gates. Commits solo locales.
