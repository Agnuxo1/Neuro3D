# Punto 7: preparación verificada; compilación, readback y RT coherente abiertos

**Actualización posterior por decisión expresa del propietario, 2026-10-08:** Unreal Engine deja de ser requisito; Blender será la plataforma principal. Este informe y los recibos/fuentes se conservan como preparación histórica. Ya no es necesario localizar/compilar Unreal. El punto 7 continúa abierto para RT coherente en Blender, según el [nuevo plan](BLENDER_SCIENTIFIC_ROADMAP_2026-10-08.md); no se declara compilación Unreal ni equivalencia RT. Las condiciones UE descritas debajo pertenecen al alcance anterior.

**Estado en la preparación original:** el punto 7 no estaba cerrado. La ejecución Iris OpenGL del punto 6 no acredita Unreal ni RT. Se preservaron las rutas y fuentes mientras se investigaba el acceso a un motor utilizable.

## Disponibilidad actual

El preflight de sólo lectura verifica los ejecutables de editor, commandlet, shader compiler, UnrealBuildTool, scripts de compilación/automatización y `Build.version`. El registro de Epic contiene **Quixel Bridge 5.6** con ruta `E:\NEBULA_SYSTEM\Engine\UE_5.6`; no es prueba de que el motor esté instalado. Esa ruta no existe actualmente. Tampoco hay motor utilizable en los otros dos candidatos habituales comprobados. Visual Studio con herramientas C++ sí figura en el inventario.

La búsqueda dirigida adicional no encontró ejecutables del motor en los directorios examinados; tuvo accesos denegados y se interrumpió después de no producir candidatos. No se presenta como un inventario exhaustivo de todos los discos. Se solicitó al propietario la ubicación actual de UE 5.6. No hubo compilación, lanzamiento del editor ni uso de GPU en este punto.

El primer preflight falló por la codificación de la salida de `vswhere`, antes de producir recibo. Se conserva su fuente/nota. El segundo y tercero producen `BLOCKED_NO_USABLE_ENGINE`; el inventario solicita ahora explícitamente UTF8. Admitir un candidato requiere archivos reales y versión 5.6, no sólo una entrada de registro.

## Defecto de preparación corregido

El plugin registra tres global shaders. Se cambia su `LoadingPhase` de `Default` a `PostConfigInit`, siguiendo la [configuración oficial de Epic para plugins con global shaders](https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-a-new-global-shader-as-a-plugin-in-unreal-engine). Se conserva el descriptor anterior. La corrección de configuración está preparada; sólo una compilación y carga reales verificarán su aceptación por UE 5.6.

## Referencia de paridad: discrepancia reproducida y referencia versionada

La referencia CPU anterior no implementa exactamente los tres pases HLSL actuales. Un contraejemplo aislado usa una fuente con color `(2,0,0)`, amplitud digital denominada intensidad 1, activación 1, una arista de peso 1 y fase cero. Con `dt=1/8`, la referencia anterior devuelve intensidad 2 en el destino. El shader normaliza el color antes de acumular: el resultado algebraico es 1. Es un contraejemplo CPU/algebraico, sin observación GPU.

Además difieren la mezcla de color, la regla de frecuencia y el término de energía basado en la intensidad interpolada. Un checksum distinto no basta para determinar el error por campo. La inicialización CPU anterior omite el desplazamiento de ángulo por semilla del actor C++, por lo que los datos de entrada del ensayo deben provenir de buffers capturados y fijados.

Se añade `photonic_shader_reference_v1.py` sin sobrescribir la referencia histórica. Consume explícitamente los tres registros `float4` por neurona y un registro por arista, así como los parámetros del paso. Conserva la semántica de normalización, campo complejo, frecuencia, respuesta, intensidad, energía y color de HLSL. Devuelve señales, acumuladores y estado final para permitir una comparación completa.

Cinco pruebas CPU PASS cubren el contraejemplo, interferencia constructiva/cuadratura/destructiva con señales no nulas, peso cero/pérdida, frecuencia/energía y entradas malformadas o no finitas. Esto comprueba controles analíticos y la referencia; no acredita paridad con el shader compilado ni una cota rigurosa de aritmética binary32.

## RT no equivale a este plugin

`Source/OptiXRayTracing.cu` genera rayos de cámara, acumula luminosidad/RGB y usa `tmin`/desplazamiento de origen fijos de 0.01. No transporta la fase compleja y referencia de los caminos del circuito Iris; contiene dependencias conceptuales como `params`/`NeuronData` que este archivo no declara. Los antiguos diagnósticos Cycles ID/Position/Z no demuestran campos complejos ni equivalencia de red. Las fuentes se conservan y no se promueven a motor RT coherente.

El plugin Unreal es otro modelo digital abstracto de grafo, con tres pases compute; no es un trazador RTX, una implementación de los 16 MZI aprendidos ni hardware fotónico. El número de neuronas de ese modelo no se intercambia con modos/caminos/triángulos de Iris.

## Condición concreta de cierre

1. Localizar UE 5.6 utilizable y compilar realmente el plugin y un host mínimo, conservando logs, versión, dependencias y códigos de salida.
2. Ejecutar un ensayo pequeño acotado, con inputs y parámetros congelados; capturar los buffers reales de entrada, señales, acumuladores y salida, identidad de frame/paso y bytes completos.
3. Auditar todas las componentes frente a la referencia versionada, con presupuesto de error fijado antes de ejecutar y controles de fase/peso cero. El actor actual conserva internamente estado pero sólo registra checksum/contadores: aún debe exportar evidencia completa.
4. Si se mantiene una tesis RT: implementar y ejecutar transporte coherente con referencias y reglas geométricas justificadas, contrastarlo con el oráculo y documentar el uso efectivo de la ruta RT. La mera elección `OPTIX` o presencia de RTX no basta.

Las restricciones de proceso privado, cola exclusiva, fuentes fijadas, deadline y reserva RAM no se eliminan para desbloquear el motor. No se retiran rutas ni se declara este punto terminado por ausencia de instalación. Los puntos 8–26 permanecen abiertos siguiendo la secuencia solicitada.

Recibos: [disponibilidad](validation/unreal-readiness-2026-10-08/preflight03/receipt.json), [contraejemplo](validation/unreal-readiness-2026-10-08/oracle_scope01/receipt.json) y [pruebas de referencia](validation/unreal-readiness-2026-10-08/shader_reference01/receipt.json).
