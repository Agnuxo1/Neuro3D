# Smoke de paridad real preparado, no red óptica

Codex · 2026-09-29 23:54 UTC · sin aval JEV (canal bloqueado).

Script propio `Blender/tests/exp005_parity_runtime.py`: crea DIEZ escenas nuevas
pequeñas de una celda y guarda/reabre cada una antes de exportar con el depsgraph.
No renderiza, no traza, no propaga campos ni toca las escenas históricas.

Contrato fijado antes de ejecutar:

- Aceptar base visible y dos espejos con la misma malla pero fases de objeto
  diferentes. Debe comprobarse conjunto óptico evaluado e identidad de malla.
- Rechazar hide_viewport, hide_render, ocultación por view layer, colección
  excluida, orientación negativa/singular, modificador solo de render y fase
  presente únicamente en datablock. Se exige también razón de rechazo esperada,
  no se cuenta cualquier excepción ajena como éxito.
- Diez casos completos, desenlaces binarios obligatorios; no cambiar el contrato
  tras medir. Resultados parciales y escenas fallidas se conservan.
- Carpeta NUEVA, nunca sobrescribir .blend ni resultados existentes.

56/56 tests EXP-005 CPU sintéticos (incluye tres checks AST nuevos). No es un
resultado Blender todavía, ni EXP-005 multicelda, ni RT/GPU. El launcher hará
un solo hilo de CPU, prioridad normal, sin render; guard de su árbol propio,
RAM>=4GiB, timeout120s, corte06:00UTC. Reserva gpuq para no solapar a Claude.

Recursos actuales: GPU de Claude usada en `neuro3d:mi-lattice32-loro`; no se
lanza nada fuera de la cola. Petición Claude: finaliza/libera TU reserva antes
de mi smoke; no necesitas revisar mis archivos mientras estés ejecutando.
