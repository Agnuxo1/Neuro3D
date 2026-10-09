# Punto 2: first-hit nativo validado en las 20 consultas

`native18` pasa las 20 consultas preregistradas (13 casos: 9 consultas reales K3/K4 y 11 adversariales), sin alterar el manifiesto original ni las expectativas. Se conservan 20 dispatches/readbacks y 189952 bytes leídos de GPU. El supervisor pasa, el proceso sale con código 0 y la limpieza queda confirmada.

La auditoría independiente, basada únicamente en biblioteca estándar y `fractions.Fraction`, también pasa las 20 consultas. No importa la implementación ni ejecuta Blender/GPU. Reconstruye paquetes y fracciones, compara echo bit a bit, estados, primitivas, objetos, máscaras de empate, contactos previos excluidos y los cocientes exactos de distancia, y verifica el hash completo de readbacks.

| Recibo | Resultado / SHA-256 |
|---|---|
| Manifiesto original | `1ba451212cc136442ea34a1ec9a7cefd44fdf366211f28813590f21b732ba800` |
| Worker | PASS; `dc22fec1191bbd818e640ebb26a5f8d5e6fcf7c9bd9430eae1338521995071f4` |
| Supervisor | PASS; `a192218bdfe6cb52fafa78bd73f0ffed5d0188676a44a0bd810602d9bc1aed27` |
| Auditor independiente | PASS; `0ff2161190f0899cd8f078ddfb1f7c8a55e15d78234f1ecd9801a5d30421dfb5` |
| Readbacks concatenados | `358be3eff5ec83d5e0ca8f7c0ece219f60bb997d6c6303ede3c020cb6aa858dd` |

Evidencias: [worker](validation/robust-first-hit-native-2026-10-08/native18/worker.json), [supervisor](validation/robust-first-hit-native-2026-10-08/native18/guard.json), [auditor](validation/robust-first-hit-native-2026-10-08/native18/independent_audit.json), [intentos](validation/robust-first-hit-native-2026-10-08/attempt_index.json).

Entorno: RTX3090, OpenGL, Blender 4.5.14 LTS, build `62c1db4208e8`. La ruta validada usa OpenGL core dentro del contexto WGL privado de Blender. `GPUShaderCreateInfo` sigue sin estar validado para este shader. El worker informa la API usada; la CPU sube/lee bytes y verifica resultados, mientras la geometría se calcula íntegramente en GLSL.

La implementación final utiliza un banco de 64 enteros de 512 bits y tres productos de 1024 bits en 4480 bytes de memoria compartida, con una invocación por workgroup. Evita pasar/retornar grandes estructuras a través del compilador. Conserva la precisión entera y los productos cruzados racionales. [Justificación y límites](FIRST_HIT_INTEGER_REPRESENTATION_2026-10-08.md).

El tiempo observado del worker fue 4.692542s; el sobre temporal del supervisor, 9.560617s. Son observaciones de este ensayo, sin comparación de rendimiento o energía. La preparación de la cola y otras etapas no están incluidas en esas cifras.

Se conservan los intentos anteriores, incluidos errores de invocación, reservas RAM, compilación y resultados nativos incorrectos. No son réplicas independientes ni se ocultan para calcular una tasa de éxito. Las variantes vectoriales fallidas permanecen como experimentales; el prototipo original se conserva intacto.

El cierre es finito y está limitado a estos paquetes, implementación, build y dispositivo. No cierra aún propagación multicamino, fase, incertidumbre física, red Iris completa, RT ni ventaja de rendimiento. El siguiente punto es integrar estos estados en la propagación completa.
