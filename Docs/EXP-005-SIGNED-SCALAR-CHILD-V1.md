# Entrypoint privado escalar firmado V1

Contrato CPU previo a GPU. Nuevo archivo opt-in; no modifica capturas,
supervisor, decodificador, shaders o fixtures congelados.

El comando exige executable absoluto, factory-startup, un hilo y
python-exit-code17. El hijo verifica recipe/pins, SHA del executable,
del entrypoint y del archivo recipe, argv real y cadena de PID+birthday:
Blender -> supervisor propio -> gpuq. El holder debe identificar al
SUPERVISOR como hijo directo, no a Blender. Se exige entorno heredado
nombrado, lectura sin alterar la cola y deadline UTC nuevo <=90s.

Antes de importar explícitamente bpy/gpu, admit comprueba reserva,
deadline y telemetría real. El supervisor sigue siendo obligatorio:
prelaunch RAM libre menos2GiB>=4GiB; durante ejecución RAM>=4GiB,
VRAM<=18GiB y temperatura<=80C. El hijo no reserva ni amplía presupuesto.
No se integra con el guard nocturno vencido a06UTC.

En un proceso factory-startup privado desactiva el guardado de preferencias
ANTES de cambiar save-prompt/autosave. No llama a preferences-save.
Solo acepta plataforma NVIDIA; llama a captureV2 y al shader firmado
original, sin fallbackCPU. Escribe sidecar exclusivo de PID/birth y backend;
captureV2 retiene raw/recibo/final antes de validación. Programa cierre GUI
normal tras liberar referencias/GC; errores propagan al exit-code17.
El outer supervisor debe observar rc, terminar solo hijos propios y cerrar
envelope. Un sidecar por sí solo nunca autentica GPU ni éxito.

Pruebas: únicamente argv/identidades sintéticas, archivo executable ficticio,
preferencias/timer mock y deadline CPU. No se ejecuta ese executable, ni
Blender/GPU/RT. No certifican la disponibilidad de psutil en el Python de
Blender, el cierre GUI real, ni el comportamiento de python-exit-code17.
Estas dependencias deben comprobarse con un piloto reservado antes de
afirmar integración operacional. No instalar librerías silenciosamente.

Pendiente: launcher que, DENTRO del turno adquirido, genere recipe/binding
con PID/birth reales y executable verificado, y ejecute el supervisor.
También faltan el readback nativo y el envelope real. Todos los flags de
autenticación/promoción permanecenFalse. No scene-inference, precisión
geométrica total, conf1, RT, speedup ni avalJEV; fallback local explícito.
