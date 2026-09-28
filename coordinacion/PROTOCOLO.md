# Protocolo Codex–Claude–JEV de Neuro3D

Codex mantiene la cola, las decisiones, el código y la verificación. Claude
recibe un encargo independiente y acotado por archivo; JEV aconseja las
decisiones sustanciales cuando su respuesta tiene `exit_code=0`,
`status=connected` y `provenance=jev`.

1. Antes de trabajar, leer `CHECKPOINT.md`, `COLA-DE-TRABAJO.md` y `TABLON.md`.
2. Codex crea `tareas/<ID>.md` con contexto, alcance, archivos, restricciones
   y aceptación. Evitar dos tareas activas sobre el mismo código.
3. Claude entrega `respuestas/<ID>.json`. Una auditoría solo permite lecturas;
   una edición necesita autorización expresa y archivos asignados.
4. Codex comprueba el formato, las referencias y cualquier resultado medible.
   Después decide y registra evidencia en `DECISIONES.md` e `HISTORIAL.md`.
5. Las discrepancias van a `THINKTANK.md` como hechos, inferencias y propuestas.
   El acuerdo entre agentes no constituye validación.
6. Si la CLI de Claude agota su timeout, se conserva la tarea preparada y se
   usa `CLAUDE_BOOTSTRAP.md` en una sesión posterior.

Los resultados grandes y crudos se guardan en D: dentro de una carpeta local
de trabajo no versionada; al repositorio solo llegan evidencias resumidas sin
credenciales. No se ejecutan tareas GPU hasta nueva autorización del usuario.
