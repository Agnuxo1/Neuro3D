# Reproducción de Blender nativo en Linux: protocolo prospectivo

Estado al congelar: **preparado, todavía no ejecutado**. La autorización humana de continuidad cubre este protocolo publicado antes del ensayo; la vía externa/IPFS permanece pendiente, sin identificadores emitidos.

Se repetirá en un runner Linux x86_64 de GitHub la instalación aislada del complemento propio 0.1.2 y los mismos nueve controles científicos y operativos de la ejecución Windows: inferencia de 150 entradas, rechazo de resultados con entradas o geometría cambiadas, cancelación del proceso propio, entrenamiento nativo de 60 actualizaciones con 61 auditorías geométricas, recuperación y aplicación atómica, guardado de una copia nueva y reapertura, y rechazo de un resultado modificado. También se revisará el log completo después de salir para detectar excepciones de ciclo de vida. Los bytes del núcleo científico del paquete son idénticos a 0.1.1.

El archivo oficial [Blender 4.5.14 Linux](https://download.blender.org/release/Blender4.5/blender-4.5.14-linux-x64.tar.xz) se descargó con TLS verificado y coincide con el [checksum oficial](https://download.blender.org/release/Blender4.5/blender-4.5.14.sha256). La inspección local no ejecutó ese binario. El runner volverá a descargarlo y verificará tanto el archivo como el ejecutable antes del ensayo.

| Artefacto | SHA-256 |
| --- | --- |
| Archivo oficial, 378.045.212 bytes | `9ba871ff2ecd36526b77432745980b7e6664ecd0c7ca11c48849073dcfe06da3` |
| Ejecutable Linux, 163.613.240 bytes | `050c02562f81fe80ba616a80198fa02d381e60f8b61b8d39add881f4bca0d7d8` |
| Complemento 0.1.2 | `7b1b747ea6148f6f924a55d7b24a5d065db696295297563f5309904962d9f65f` |

El workflow fija acciones por commit, Python supervisor 3.12.12 y ruedas Linux verificadas por hash. Blender usará su Python y NumPy propios; se registrarán las versiones medidas. La primera etapa comprueba todos los blobs publicados, el perfil y la autorización antes de descargar o ejecutar Blender. El checkout contiene únicamente la dependencia necesaria. No se requieren Torch, SciPy ni GPU para este ensayo.

Límites fijados: 600 segundos de preparación, 1.500 de controles nativos y 2.200 del controlador completo; un núcleo CPU; 4.000 MiB libres al empezar, suelo de 2.500 MiB, RSS agregado propio máximo de 2.000 MiB y evidencia de 256 MiB. Solo se cancelarán procesos descendientes propios. Preparación, descarga, controles nativos y tiempo total quedarán separados; checkout, instalación del supervisor y subida del artefacto se conservarán como etapas del job.

Se exige diferencia de potencia ≤10⁻¹¹ entre el resultado entrenado y su reconstrucción geométrica nativa final. Las diferencias de trayectoria respecto a Windows se informarán, sin imponer igualdad bit a bit entre runtimes. Un fallo de entorno o una ejecución incompleta tendrá métrica nula y conservará sus logs. Superar los nueve controles y la revisión del log tendrá métrica 1.

Perfil: [JSON congelado](research/external_native_blender_profile_2026-10-09.json); [autorización](research/external_native_blender_registration_2026-10-09.json); [recibo oficial](research/external_native_blender_official_receipt_2026-10-09.json); [workflow](../.github/workflows/external-native-blender-20261009.yml).

Este ensayo prueba una ejecución nativa en otro entorno. No constituye interpretación de investigadores independientes, prueba de usabilidad humana, calibración física, ejecución AMD, registro externo ni validación de un procesador fotónico.

## Intento 01: fallo de descarga, resultado científico nulo

Perfil `845cf2135b36ee8516daa654ea182f8f963f1063c24cf6e65097ffca1dc28792`, publicado en `09ff4861ff398de1ee8b9f7d135db98ff64f639d`. El [run37890682207](https://github.com/Agnuxo1/Neuro3D/actions/runs/37890682207) verificó los42blobs antes de preparar Blender. El host respondió HTTP403 a la descarga mediante urllib; el controlador terminó en0,428s, sin iniciar Blender nativo, con métrica nula y limpieza propia confirmada. El artefacto y sus42archivos internos presentes se verificaron por hash; el workflow oculto omitido por la subida se recuperó aparte del commit publicado y también se verificó y se conservaron en [attempt01](validation/external-native-blender-2026-10-09/attempt01/evidence_index.json). No se cuenta como fallo científico del modelo ni como reproducción Blender. Se preparará un protocolo de transporte separado manteniendo los mismos hashes y controles.

## Transporte v2: preparado antes de ejecutar

Se conservan hashes de archivo oficial, ejecutable y complemento, nueve controles, tolerancias y límites. La única reparación de ejecución es fijar el User-Agent y tres fuentes TLS en orden: servidor Blender, NLUUG y RWTH Aachen. Los mirrors sirven únicamente como transporte; su contenido no se confía sin coincidir con el checksum oficial fijado. Se registrará cada fallo y el transporte utilizado. También se incluirá el workflow oculto en el artefacto. [Perfilv2](research/external_native_blender_profile_v2_2026-10-09.json), [autorizaciónv2](research/external_native_blender_registration_v2_2026-10-09.json). Aún no ejecutado al escribir esta sección.
