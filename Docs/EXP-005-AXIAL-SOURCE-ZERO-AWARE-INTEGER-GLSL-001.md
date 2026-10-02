# EXP-005 — helper integer GLSL zero-aware opt-in

ID AXIAL-SOURCE-ZERO-AWARE-INTEGER-GLSL-001; Codex capacity_audit/EXP005 P1.
Base 3c9d84564bebf942d1509ff6f714a486254b11bd.
Modelo NUEVO axial-SOURCE-zero-aware-integer-words-GLSL-v1.

Entregable: header NUEVO sin main/bindings/dispatch. Caller GLSL>=400 debe concatenar antes el helper signed512 congelado e1f2ff0ca905ee29e8afa0440e9abdaa4a4127be23fe20d29e29c25af68f236f. No altera su suma matemática ni semántica anterior. Un caller que ignore false o consuma el output invalidado NO cumple el contrato.

Ambos limbs uint32 deben ser normales finitos o cero antes de decode. Rechaza NaN/Inf/subnormal. Ambos cero -> palabras binary64 con signo del HIGH, sin sumar/convertir FP. Si alguno no cero, reutiliza decode_hilo512 puro para suma EXACTA de enteros en unidades 2^-149; una cancelación exacta produce +0. Toma magnitud/signo y top<=277 (suma de dos binary32), selecciona 53 bits, aplica guard/sticky/LSB para nearest-even, propaga carry/renormalización. Exponente binary64=top+874. Salida uvec2 LOW32/HIGH32; no float/double, conversiones FTZ, fma o aritmética FP64 del driver. No añade incertidumbre ficticia al transporte; el cargo de redondeo se mide contra la suma racional exacta, una vez. Las palabras finales son binary64 aunque los cálculos sean integer-only.

Compilación GLSL y ejecución GPU NO comprobadas: glslangValidator/glslc no disponibles en PATH; no SDK instalado ni driver/context iniciado. El modelo Python uint32 es espejo CPU, NO ejecuta el shader. Pruebas y verificador racional independiente validan modelo de bits y su correspondencia con OUTPUTs retenidos; source SHA fija el header examinado, no constituye prueba de compilación/semántica del compilador. Distinto grafo a suma FP nativa; no asumir equivalencia global sólo por mismo payload/resultado en ejemplos. El helper NO valida frame120/SHA/contextos ni selecciona el decoder del programa congelado. Futuro runner necesita programa NUEVO explícito+validación HOST de TODO INPUT/frame/contexto/ORIGINAL/gauges y resultados, guard y reserva autorizados. El nuevo selector de pruebas dice CPU_UINT32_MIRROR_NOT_GLSL.

Cuatro SOURCE sintéticos retenidos: modelo nuevo se aplica a ocho componentes, contrasta words con decoder zero-aware retenido SIN ejecutar decoder/encoder/suites viejas. Guard-negativas2 intactas, two_sources no full SOURCE/material; 17casos19SOURCE sin INPUT. Grupo0/38generalesFALSE/fase-quota-uniformNone/escena-programaFalse. No Aexpitheta/material/scene inferencia ni cota geométrica.

Controles NUEVOS de este grafo integer: cuatro combinaciones cero, cancelación, signo, ties pares/impares/sticky, renormalización, rango y diferencia mínima normal32; negativos de palabras/selección/sourcehash/INPUT tardío. Etiquetar converter controls internos fuera de consultas SOURCE. Fallos completos retenidos si aparecen; no convertir un FAIL a PASS cambiando umbrales.

CPU1hilo/afinidad1/hijo<=60s. GPUBlender0; no RT/óptica física/Bpyfloat32. IO/setup/pins/racional/upstream/fullpipeline UNMEASURED no0; tiempos tests no rendimiento ni ganador. Histórico0337 cerrado; GPU sólo nuevojob verificable, Claudeexclusive/gpuq/procesos/RAMVRAMtemp/guardfailclosed/pisos originales. JEV LOCALfallback/bloqueado/no retry. Frozen runners/shaders/fixtures/conf1/bounds/caps intactos. Sólo propios revisados versionados; sharedboards/checkpoint SINstage. Sin SDKDrJit/Kaggle/push/merge.

Skills: cognición extendida reutiliza artifacts sellados sin replay y guarda outputs; desarrollo usa contrato opt-in y pruebas de frontera.

Se investigó alternativa FP64 en documentación primaria [Khronos ARB_gpu_shader_fp64](https://registry.khronos.org/OpenGL/extensions/ARB/ARB_gpu_shader_fp64.txt): existe soporte de tipos double y packing LOW/HIGH, pero no se usa en este header. Esa especificación no acredita nuestro grafo ni la GPU local. Refpages XHTML no recuperables; no conclusiones a partir de esas páginas fallidas.

Fallo estático de borrador PRESERVADO: variable half reservada en [GLSL 4.00, sección 3.6](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.00.pdf). Primera suite espejo CPU pasó pero no detectó ese defecto de sintaxis: NO PASS de shader. Antes de reparar se conservaron lossless las cinco fuentes originales con SHA/bytes y metadata observada de la primera suite. Reparación propia: nombre guardBit y regresión de tokens reservados; ninguna aritmética/umbral/guard/cap congelados cambió. Dos diagnósticos de captura por regex escapada preservados; recuperación simple logró snapshots sin repetir cómputo. Compilación sigue SIN comprobar pese al control estático.

Petición Claude: ACK por ID+SHA del recibo; sólo artifacts YA EXISTENTES de compilador/backend/guard/INPUT mismo ORIGINAL-decoder-ABI-gauges-trabajo-OUTPUT/costes completos, sin cargar GPU por relleno. Siguiente integración sólo sobre programa nuevo y evidencia compilada autorizada, sin tocar el contrato congelado.
