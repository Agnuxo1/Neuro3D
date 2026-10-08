# Punto 6: precisión de almacenamiento nativo

El primer ensayo `native01` produjo tres readbacks completos y recibo de supervisión PASS, pero la referencia independiente rechazó el resultado numérico antes de aceptar ninguna muestra. Se conservan ambos recibos: PASS del supervisor significa transporte y proceso correctos, no exactitud de inferencia.

El diagnóstico de la muestra0 encuentra normalización escalar `norm2=0.8483258978288235`, `norm=0.9210460888733112`, próximas a su referencia 90 dps. Las amplitudes guardadas en arrays y todos los componentes de campo devueltos son representables exactamente en binary32; el error de amplitud de referencia alcanza 4.25e-8 y el de campo L1 del puerto 0 alcanza 1.06e-5. Esto identifica una pérdida de precisión observable, sin atribuir todavía una causa definitiva al compilador/controlador.

Antes del siguiente ensayo se cambia exclusivamente el almacenamiento de los arrays X/Y/amplitudes/ax/ay/out_field a `shared double`/`shared dvec2`. El grupo tiene una sola invocación; cada estado se inicializa antes de usarlo y se reinicializa para cada muestra. No hay lectores/escritores concurrentes ni necesidad de sincronización entre invocaciones. La reserva explícita es768 bytes:16 escalares*8 +40 vectores*16.

Se mantienen entradas, circuito, algoritmos, umbrales y auditor. El cambio sólo se aceptará si los tres casos completos superan la auditoría. El ensayo fallido y sus fuentes previas quedan conservados. La [especificación GLSL oficial](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html) permite arrays y almacenamiento shared; el nombre double no sustituye la comprobación de sus resultados reales.
