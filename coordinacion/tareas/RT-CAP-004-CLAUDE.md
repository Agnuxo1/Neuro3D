# RT-CAP-004 — finalizar protección temporal y cleanup del piloto

003 recibida/6SHA: validación pura parcialmente confirmada. Gracias por
restaurar pisoRAM4 y copiaoriginal. Cuatro NaNchecker+cinco guardinvalids ahora
rechazados; 7tests propiosPASS0,021s. Doce EXR002 decodificados propios y256
píxeles exactoscontraJSON, ID/Z/P gates cumplen. No descartar esas capturas ni
relanzarlas porrelleno; operaciónhistórica002 permaneceprovisional.

DocEXP-005-RT-READBACK-REVIEW-CPU-2026-09-30/report1132
SHA33fa40ac7f2148794341baa574da3459b2e25e73f486b8136ecde50076ea8d53.
Todavía no aprobarun guard completo solo porpruebas devalidación:

1. guard_v2:93–112, querynvidia puede bloquear10s ysleep1. Si el hijo termina
   tarde dentro dequery, pollsale delwhile yOKsin revisar elapsed/deadline.
   Relojmonotónico, consulta/espera acotadasal restante, cierre tardío noOK,
   margen explícito para terminarpropio dentro del máximo120. Conserva test
   CPUtelemetría lenta e hijo que acaba después del timeout, sinGPU/Blender.
2. guard_v2:120–123, errorfuera deltrytelemetría trasPopen produceERRORsin
   cleanup, KeyboardInterrupt tampoco. Handlepropio inicializado ycleanup
   garantizado enerror/interrupción; verificarfin. Test callbacknow_fn roto
   despuésspawn y caso interrupt propio; NOmatarajenos ni cancelarqueue.

Entregar VARIANTE NUEVA+testCPU+logs/resultados/SHA; preserve002/003/EXR yfallos.
Los 23tests originales no los ejecutaré porcontener writers/hijos; el contraste
propio será por funcionesinspeccionadas/evidenciaretenida. No otra instalación
ni nueva GPU hasta reparación/revisión/preflightnuevo+gpuq. Tras cerrar estos
dos casos, preparar UN piloto útil pequeño conmanifest/deadline nuevo, no
repetir cuatrocapturas sin cambio ni subirbounds/conf1. Acusa004 en respuesta
conID ySHA. JEVfallbacklocal; C1C2readback NOredRT/coherencia/speedup/C3.
