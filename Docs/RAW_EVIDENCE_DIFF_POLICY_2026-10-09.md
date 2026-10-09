# Registros crudos y revisión de cambios

Los registros científicos completos siguen publicados en `Docs/validation/`, con sus bytes originales, hashes y versiones. Algunos contienen millones de filas numéricas. Su vista automática de diff se desactiva mediante `.gitattributes` para reducir el coste de revisar y previsualizar esos datos.

Los índices de evidencia, el código canónico en `Tools/` y `Blender/`, los perfiles de `Docs/research/` y los protocolos conservan diffs de texto normales. La regla no comprime, elimina, sustituye ni altera los registros, ni modifica la aritmética, el protocolo o los límites de un ensayo. `git show <commit>:<ruta>` y la descarga del archivo permiten obtener el contenido original; su SHA256 debe coincidir con el índice de evidencia.

Esta es una medida de presentación y uso de memoria. No identifica por sí sola la causa de ningún fallo de RAM, no demuestra una mejora del motor óptico y no evita que una aplicación cargue manualmente un archivo grande.
