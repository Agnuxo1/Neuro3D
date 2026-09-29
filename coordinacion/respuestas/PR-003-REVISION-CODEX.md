# PR #3 — revisión estática y recomputación fresca independiente

Revisión local favorable a las correcciones P1 del PR #1; NO fusiono el PR.
Fran decide la integración. PR: https://github.com/Agnuxo1/Neuro3D/pull/3

Diff respecto a merge-base: ocho archivos Iris únicamente. La comparación directa
contra HEAD mostraba eliminaciones aparentes de mis archivos nuevos porque la
rama era anterior; NO son cambios del PR ni deben integrarse como reemplazo
completo de main. Script del worktree y blob de la rama coinciden:
`0a78c1f3dc50e7e4a9590e3fd7f8a5b40f86ee3a`.

Corrida propia CPU -t1, Blender 4.5.14, sin render/reentrenamiento/escritura en
worktree de Claude, límite 120s vía gpuq, rc=0. Se abrió el `.blend` final, no se
reconstruyó la escena; se ejecutaron las definiciones del texto embebido bajo
nombre de revisión para no activar presentación/timers GUI.

- Escalador guardado coincide EXACTAMENTE con min/max de las 120 filas TRAIN;
  índices train/test disjuntos y coincidentes con el split fijo.
- Texto embebido coincide con fuente y localiza sus datos tras apertura fresca.
  Registro explícito del panel funciona; no se habilitó autoejecución.
- Flor 71: clase correcta 1, 56 855 raycasts; error máximo de ocho campos frente
  al modelo 6,66e-5; error de balance 5,04e-6; escape 0.
- Flor 13 (extremo fuera del mínimo TRAIN): clase correcta 0, 51 284 raycasts;
  error de campos 6,72e-5; balance 4,15e-5; escape 0.
- Flags de exclusión se restauran tras cada traza; sham de color produce delta 0.
- Mover realmente dos espejos c12.r1/r2 +0,003125 BU en MEMORIA cambia el campo
  máximo 0,07388796, sin escape. No se guardó ese tratamiento ni se cambió theta:
  prueba causal de recomputación, no reproducción de un render congelado.
- SHA del `.blend` idéntico antes/después:
  `d444831512ba10e66cd77433cb8130991522252617100ffa7a364511c17f39f0`.

Evidencia: `D:/PROJECTS/.cognition/neuro3d/pr003_review_20260929/`
`pr003_fresh_recompute.json` y log. Script propio reproducible:
`Blender/tests/pr003_fresh_recompute.py`.
Umbrales pre-run campo <=2e-3, balance <=1e-3, sham <=2e-3,
cambio geométrico >1e-4; escape debe ser cero.

## Alcance

La revisión respalda escalador, reapertura/panel y recomputación de dos ejemplos;
no reproduce las 30 flores ni demuestra generalización externa. El 29/30 sigue
siendo el resultado completo comunicado por Claude, con incertidumbre de test
pequeño y una partición fija. Interferencia/abs²/argmax siguen en Python.
`TRACE_INFO.escape` suma intensidades por ruta: cuando es exactamente cero basta
para comprobar ausencia de rutas perdidas, pero NO sirve como balance coherente
general cuando hay escapes. EXP-005 implementa ese tratamiento más estricto.
La animación revela un estado estacionario ya calculado, no dinámica de ondas.
Ninguna ventaja de velocidad/energía ni superioridad general demostrada.

P2 documental: «only trained parameters are positions» debe matizarse, porque
ref y temperatura también se optimizan (temperatura es auxiliar de entrenamiento).
No bloquea estas correcciones; no cambiar mis archivos ni refusionar main completo.
JEV sigue bloqueado: revisión local, sin atribución de aval al servicio.
