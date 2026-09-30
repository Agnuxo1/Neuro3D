# Enmienda v3 · ventana y bucle de eventos al cerrar

2026-09-30 01:06 UTC. V2 volvió a fallar al mismo address tras54probes correctos;
liberar shader no arregló el fallo. Hipótesis de su destructor refutada como
explicación suficiente. Registro real conservado en cognition:
`exp005_native_gpu_v2_20260930_0105_tmp/lambda.crash.txt`.

Backtrace: BLI_addhead → WM_event_add_ui_handler → wm_exit_schedule_delayed →
wm_exit_blender_exec → pyop_call → arg_handle_python_file_run → main.
Evidencia apunta a cierre con contexto de ventana inválido en argumento--python
ANTES del bucle de eventos, no a GPU OOM ni al cálculo del campo.

Cambio único funcional: programar cierre por bpy.app.timers y ejecutar operador
con temp_override(window=primera ventana propia). Si no hay ventana, falla; guard
acota el proceso. Mantener destrucción shader antes. Kernel,ABI,fixtures,tolerancias
idénticos. Nuevo artefacto, mismos54probes y retorno0 requerido; V1/V2 intactos.
