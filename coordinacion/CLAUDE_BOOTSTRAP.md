# Arranque manual de Claude para OPT-001

Si la CLI automática no entrega una respuesta, abrir Claude Code en
`D:\PROJECTS\9_NEBULA_NEW` con Sonnet y pegar:

> Eres el revisor independiente de Neuro3D. Lee `coordinacion/PROTOCOLO.md`,
> `coordinacion/CHECKPOINT.md`, `coordinacion/COLA-DE-TRABAJO.md`,
> `coordinacion/tareas/OPT-001.md` y los archivos permitidos en esa tarea.
> Haz solo una auditoría de lectura; no ejecutes Blender, GPU, render,
> entrenamiento ni pruebas pesadas y no modifiques código. Devuelve JSON
> conforme a `coordinacion/response-schema.json` y guárdalo en
> `coordinacion/respuestas/OPT-001.json`. Cita rutas y líneas aproximadas.
> Si no puedes escribir el archivo, devuelve el JSON en el chat para que
> Codex lo valide. Indica `OPT-001 READY` solo al terminar.

Codex valida la respuesta antes de usarla; no basta una opinión sin evidencia.
