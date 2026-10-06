# Punto 4: escenas reales, transporte hi/lo y consumidor GPU

Fecha: 6 de octubre de 2026. Versión de implementación: `b305043016427d796aff4eb649e090961db026ff`.

**Estado: CPU_PREPARED_NATIVE_BLOCKED. El código candidato y los controles CPU están preparados; la compilación, ejecución y verificación GPU permanecen pendientes.** Los tres intentos terminaron en la cola antes de lanzar el supervisor o Blender. Este punto no está cerrado y no aporta lecturas GPU.

## Pregunta y criterio de aceptación

¿Puede una escena Blender guardada y reabierta suministrar sus geometrías y consultas mediante palabras enteras hi/lo32, conservar exactamente esos bits en el backend y usarlos en diferencias de coordenadas e intervalos que retengan componentes pequeñas?

El protocolo se fijó antes del primer intento en `Docs/SCENE_HILO_NATIVE_PLAN_2026-10-06.md`. Se exigen seis lecturas nativas, cobertura completa, identidad de datos y resultados racionales exactos. La comparación no utiliza una tolerancia ajustable. Este piloto integra datos reales en un consumidor diagnóstico nuevo; la integración de intersecciones y propagación óptica completa corresponde a los puntos siguientes.

## Implementación fijada

- Adaptador puro de escena a ABI little-endian con tablas de escalares, fuentes, vértices y triángulos.
- Conservación del snapshot completo, propiedades originales y procedencia; validación contra un manifiesto externo fijado por hash.
- Entrada GPU mediante `GPUUniformBuf` de bytes: 32 KiB, representación `std140 uvec4[2048]`.
- Eco de todas las palabras y salidas `R32UI`; comprobación de padding, cabeceras, identidades y nonce por ejecución.
- Cálculo nativo previsto de todas las diferencias vértice menos origen, anchuras de los intervalos de dirección y ambas aristas de cada triángulo.
- Salida compensada de dos binary64 por componente, acompañada de una salida binary64 convencional como control.
- Barrera de visibilidad y espera de finalización explícitas antes de leer resultados.
- Supervisor con turno real de GPU, proceso suspendido asignado a un Windows Job Object antes de arrancar, límites temporales, telemetría y cierre verificado.

No se modifican los productores, umbrales ni recibos históricos. Sus estados FAIL/STOP y sus cero enlaces nativos de las filas SOURCE originales conservan su significado.

## Datos preparados y comprobados en CPU

| Escena reabierta | Fuentes | Vértices | Triángulos | Escalares | Partes bajas no nulas | Bytes del paquete |
|---|---:|---:|---:|---:|---:|---:|
| K3 original | 4 | 88 | 44 | 345 | 0 | 15.904 |
| K4 original | 5 | 116 | 58 | 449 | 0 | 20.704 |
| Control numérico declarado | 2 | 8 | 4 | 53 | 6 | 2.464 |
| Total | 11 | 212 | 106 | 847 | 6 | 39.072 |

Las tres escenas se guardaron o copiaron y se reabrieron antes de preparar los paquetes. K3 y K4 conservan sus snapshots originales completos. El control incluye las diferencias exactas `1 - 2^-60` y `1 + 2^-30 - 2^-60 - 2^-100`; su intervalo deliberadamente amplio es un control numérico, no una estimación de incertidumbre física.

Por modo se esperan 444 filas K3, 701 K4 y 26 del control. Dos modos producen 2.342 filas y 7.026 componentes geométricas auditables. El segundo modo elimina deliberadamente las partes bajas de entrada. K3/K4 deben permanecer iguales; el control debe detectar diferencias causadas por esas partes bajas. Los testigos también deben mostrar información que pierde la salida binary64 convencional.

## Evidencia CPU obtenida

| Comprobación | Resultado | Alcance |
|---|---|---|
| Suite del adaptador | 16/16 PASS | Codificación, admisión, identidades y controles de alteración |
| Auditoría independiente de paquetes | PASS | 847 escalares, palabras, tablas, snapshots y metadatos |
| Contrato del oráculo | PASS | 7.026 componentes de referencia CPU; 18 alteraciones rechazadas y rechazo de entrada mayor de 32 KiB |
| Supervisor, primer ensayo | FAIL conservado | 16/17; bloqueo temporal de un archivo durante la limpieza del test de descendientes |
| Supervisor, segundo ensayo | 17/17 PASS | Contención de procesos Windows y política de admisión/cierre |
| Preparación Blender | PASS, rc0 | 6,018 s del lanzamiento acotado, sin render, entrenamiento ni dispatch GPU |

Los datos generados para comprobar el oráculo son referencias CPU y no se etiquetan como lecturas GPU. El programa original de esos controles se conserva como evidencia; no se volvió a ejecutar para crear una apariencia de repetición independiente.

El primer ensayo del supervisor comprobó la terminación de sus procesos, pero encontró `WinError32` al borrar un log. El segundo añade sólo al test un reintento de eliminación limitado a un segundo, sin relajar el cierre exigido al supervisor. Necesitó un reintento de aproximadamente 10 ms. No se ha demostrado la causa interna exacta del bloqueo temporal.

## Hallazgos de compatibilidad anteriores a la ejecución

La revisión del código oficial del build instalado, Blender 4.5.14 LTS `62c1db4208e8`, descartó el borrador que inicializaba texturas RGBA32UI: ese constructor acepta un buffer FLOAT y su lectura selecciona FLOAT. Esa ruta no cumplía el contrato de conservación de bits. Se sustituyó antes de ejecutar GPU por entrada en bytes y salida R32UI, cuyo camino de lectura usa UINT. El borrador descartado y sus razones se conservan.

Los parámetros materiales se preservan uniformemente como metadatos binary64 y quedan fuera del ABI numérico de este piloto. Por ejemplo, el valor observado de fase 0,2 deja un residuo exacto de `1/2^54` después de dos partes binary32. No se redondeó ese dato para admitirlo artificialmente. Las garantías de longitud, fase y campo final siguen pendientes del punto 6.

## Recursos y ejecución

Dispositivo previsto: NVIDIA RTX 3090, UUID fijado en el manifiesto. Backend previsto: OpenGL con contexto privado de Blender. Presupuestos: 2 GiB de RAM y 2 GiB de GPU; RAM libre restante mínima 4 GiB, memoria GPU global con reserva máxima 18 GiB y temperatura máxima 80 °C. El trabajo del supervisor se limita a 100 s y el cierre a 10 s.

Cada intento tiene UUID, plazo, manifiesto y rutas nuevos. Los tres intentos terminaron antes del supervisor porque otro trabajo vivo conservaba el turno en la cola. Un bloqueo de cola no cuenta como experimento numérico ni como resultado GPU. El reloj del sistema y las marcas de los recibos se conservan; el log de gpuq usa su hora local, dos horas por delante de UTC.

## Resultado de los intentos y condición para continuar

| Intento | Inicio UTC | Espera real | Resultado |
|---|---|---:|---|
| native01 | 22:36:41 | 20,227 s | Cola ocupada; supervisor y worker no lanzados |
| native02 | 22:38:58 | 120,370 s | Cola ocupada; supervisor y worker no lanzados |
| native03 | 22:42:02 | 240,618 s | Cola ocupada; supervisor y worker no lanzados |

A las 22:46:57 UTC, el turno `villa:legitimate-replay-v15` seguía ocupado por sus procesos válidos, con PID y tiempos de creación coincidentes. No quedaban tickets de estos tres intentos. Se conserva la inspección de sólo lectura en `queue_blocked_status_2026-10-06.json`.

El siguiente lanzamiento requiere un UUID y destinos nuevos, hashes comprobados otra vez, una fecha de emisión vigente y un plazo nuevo. No deben reutilizarse los manifiestos temporales de estos intentos. Los límites de 100 s de trabajo, 10 s de cierre y recursos permanecen intactos.

El auditor independiente v2 está preparado, revisado y comprobado sintácticamente; no se ejecutó porque no existen lecturas nativas. SHA-256 de sus bytes: `20a2a604070b446c7845d480f8aabc2976b92138253d32a29a5a22191114f7a9`. Exige seis lecturas, las ocho dependencias locales, salida correcta, cierre sin procesos propios pendientes, telemetría final reciente y límites de recursos en todas las muestras.

El punto 5 se mantiene pendiente para respetar el orden solicitado. No se sustituye la validación GPU ausente por un resultado CPU.

## Límites de la conclusión que podría respaldar un PASS

Un PASS demostraría este transporte y estas operaciones finitas en las escenas, versiones y dispositivo registrados. No demostraría exactitud universal de GLSL, intersecciones robustas completas, incertidumbre física, cotas de fase, clasificación Iris nativa GPU, propagación RT/BVH, aceleración ni reproducción por un laboratorio externo.

## Fuentes primarias utilizadas

- Blender 4.5 GPU API: https://docs.blender.org/api/4.5/gpu.types.html
- Código de Blender del build instalado, con URLs y hashes en los registros de investigación conservados; particularmente `gpu_py_uniformbuffer.cc`, `gpu_py_texture.cc`, `gpu_py_shader_create_info.cc`, `gpu_py_compute.cc` y `gl_texture.cc`.
- Khronos, GLSL 4.60, secciones 4.7.1 y 4.9: https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html
- Khronos, modelo de memoria: https://wikis.khronos.org/opengl/Incoherent_Memory_Access
- Khronos, glMemoryBarrier: https://wikis.khronos.org/opengl/GLAPI/glMemoryBarrier
- Khronos, glClientWaitSync: https://wikis.khronos.org/opengl/GlClientWaitSync
- Microsoft, wglGetProcAddress: https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-wglgetprocaddress
- Ogita, Rump y Oishi, *Accurate Sum and Dot Product*, SIAM J. Sci. Comput. 26(6), 1955–1988, DOI 10.1137/030601818: https://ogilab.w.waseda.jp/ogita/math/doc/2005_OgRuOi.pdf

Las condiciones de TwoSum dependen de las hipótesis aritméticas del artículo. La especificación GLSL y una ejecución en una GPU concreta no establecen por sí mismas que esas hipótesis se cumplan universalmente. Por eso la conclusión prevista se limita a exactitud empírica de los resultados comprobados.
