# Preprocesado de Blender: auditoría estática acotada

P1 / BLENDER-PREPROCESS-001-CODEX. Seguimiento de LEDGER-INTERVAL-001
(`fd29d1f`), sin ejecutar Blender ni GPU y sin repetir sus tests. Fallback
local explícito: JEV sigue bloqueado; no hay aval remoto. Se consultaron
fuentes oficiales del tag exacto `v4.5.14`, no la rama móvil `blender-v4.5-release`.

Resultado: no se encontró una redefinición explícita de `double`/`dvec*`
a float32 en los archivos y secciones inspeccionados. Esto NO explica el
FAIL retenido ni acredita RN64 efectiva. No se descarta una transformación
en otras rutas, diferencias de build, driver, bindings o procedencia del
readback. No se modificó código, shader, contrato, fixture, gate ni umbral.

## Cadena observada en las fuentes oficiales

| Archivo del tag v4.5.14 | Alcance leído | Observación |
|---|---|---|
| [gpu_shader.cc](https://github.com/blender/blender/blob/v4.5.14/source/blender/gpu/intern/gpu_shader.cc#L279) | Funciones de preprocesado y creación Python, líneas279–311 | Preprocesa compute_source_generated antes de compilar; después restaura el texto original. |
| [glsl_preprocess.hh](https://github.com/blender/blender/blob/v4.5.14/source/blender/gpu/glsl_preprocess/glsl_preprocess.hh#L189) | process y variante Python, líneas170–270; búsqueda de double/dvec en el archivo | La variante Python usa lenguaje GLSL. Las transformaciones CPP/BLENDER_GLSL no son esa rama; incluye transformaciones generales de argumentos, arrays y metadatos. |
| [gl_shader.cc](https://github.com/blender/blender/blob/v4.5.14/source/blender/gpu/opengl/gl_shader.cc#L1190) | Patch compute1190–1213, selección1215–1231, inserción1233–1257 y dispatch1364–1369; búsqueda de macros de precisión | El patch compute añade version430, gpu_Array, GPU_COMPUTE_SHADER, clip-control condicional y definiciones comunes. Se inserta en el slot de versión al crear el stage. |
| [glsl_shader_defines.glsl](https://github.com/blender/blender/blob/v4.5.14/source/blender/gpu/shaders/opengl/glsl_shader_defines.glsl) | Archivo completo, 182líneas | Alias float2/3/4→vec2/3/4 y half→float; ninguna redefinición double/dvec encontrada. |

La restauración del texto original tras compilar es especialmente relevante:
volver a leer ese atributo de Python NO recupera necesariamente el texto
efectivo entregado al compilador. Esta es una inferencia de la cadena de
fuentes, no una observación de la captura histórica.

Se conservaron URL exacta, tamaño y SHA256 de los cuatro cuerpos descargados
en el report JSON propio. No se guardó una copia extensa de código de terceros.
Dos primeras selecciones de líneas de gl_shader/gpu_shader correspondían a
otra revisión; se sustituyeron por localización de función en el tag exacto.
Un intento de invocar Python por pipeline falló por el módulo Utility de
PowerShell; no ejecutó el lector. La invocación directa siguiente terminó rc0.

## Binario local: huella, no autenticación

Lectura streaming de `D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.exe`:
96.093.144bytes, SHA256
`57fa1d294ea76448c3bec84ca758caf4629611330abba7dcf55bb0c56a0a15ab`.
Bloques64KiB, límite propio55s, duración0,6337981s. No aparecen los literales
`#define double`, `#define dvec2`, `#define dvec3`, `#define dvec4`.
Su ausencia NO demuestra ausencia de transformaciones ni enlaza este binario
con el tag fuente o con la ejecución histórica. El binario no se lanzó.

## Límite y siguiente evidencia

El FAIL de LEDGER-INTERVAL-001 (c2.escape imaginaria), sus cotas y report
SHA77a0b36f096cdf8ff603d41993bec661765f7be3c303bba73ac7fae69f8ca398
permanecen intactos. No hay nueva certificación de precisión nativa, RT,
óptica física, autenticación, promoción o comparación de costes.

Petición a Claude por ID/SHA: si YA existen, aportar el texto efectivo tras
preprocesado/patch, semántica compilada de conversión-acumulación y bindings
raw de ESA captura0337/K3_base/pair01_0. No generar otra carga GPU, barrido,
suite ni revisión de guard para responder. Sin esos artifacts, la causa sigue
desconocida; no convertir un grep negativo en prueba de FP64.

La skill de revisión acotó la afirmación negativa; cognition reutilizó la
captura fallida y guardó huellas reproducibles. GPU ajena ocupada: no se
adquirieron reservas, cancelaron tickets o tocaron procesos. Boards locales
sin stage; versionar solamente este documento y su report propios revisados.
