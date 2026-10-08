# Enmienda prospectiva de implementación first-hit

Se conserva el manifiesto de 13 casos/20 consultas del 2026-10-07, sus bytes, hashes, expectativas, perfil OpenGL/RTX3090, aritmética exacta y límites del supervisor. Esta enmienda no modifica ningún criterio de aceptación numérica.

Antes del ensayo `native10`, se declara una segunda forma de compilar/enlazar y ejecutar el mismo shader entero: llamadas OpenGL core documentadas en el contexto WGL privado de Blender. `native09` comprobó que el programa con tipos vectoriales enlaza por esa interfaz, mientras `GPUShaderCreateInfo` continúa fallando. El nuevo worker declara `shader_api=RAW_OPENGL_CORE_IN_BLENDER_WGL` si usa esta ruta. El fallo de `GPUShaderCreateInfo` permanece registrado y no se declara resuelto.

La ruta core sube el paquete de 32KiB a UBO, configura dos imágenes R32UI, ejecuta un único dispatch por consulta, aplica el barrier/fence ya existente, conserva echo y resultado, restaura estado GL y libera recursos propios. No usa el selector CPU, las expectativas del manifiesto ni un resultado precalculado para producir geometría. El CPU admite entradas y compara los resultados después de la lectura GPU.

La representación signed512 cambia de arrays locales a bloques uvec4, conservando todos los limbs y productos 1024. Se declara compilación sin optimización y opciones NVIDIA para controlar crecimiento de temporales; estos ajustes forman parte del código fijado por hash. [Justificación aritmética](FIRST_HIT_INTEGER_REPRESENTATION_2026-10-08.md).

Registro posterior de implementación: los intentos vectoriales fallaron. Antes de `native18`, su job y archivo de fuentes fijaron una implementación con banco compartido de 4480 bytes, IDs escalares, `optimize(on)` y `optionNV(unroll none)`. El archivo `source` de ese ensayo conserva exactamente los bytes utilizados y el recibo job identifica sus hashes. No se modificaron consultas ni respuestas. Esta descripción posterior de resultados no se presenta como una nueva preregistración retroactiva.

Cierre del punto 2: exige 20 dispatches y readbacks ordenados, echo bit a bit, estados/IDs/máscaras/razones exactas coincidentes con las expectativas originales, auditoría independiente Fraction PASS y recibo supervisor PASS con limpieza confirmada. Un fallo conserva datos y mantiene el punto abierto. Un PASS certificará la ruta concreta declarada, sin implicar fase, multicamino completo ni óptica física.
