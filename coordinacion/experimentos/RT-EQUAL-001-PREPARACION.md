# RT-EQUAL-001: comparación geométrica de igual trabajo y salida

Preparación propia 2026-09-30. NO contrato congelado de ejecución. BackendRT
e implementación siguen Claude; Codex hace contrato/oráculo y auditoría.
Fallback local sin JEV. No instalar SDK ni alterar informeRT ni conf1.

Se aprueba preparar el diseño propuesto por Claude: mismos rayos y salida
ID/t, no atribuir al rango1,2–2,6 una incertidumbre experimental. Son dos
estadísticas distintas sobre cargas no equivalentes, no intervalo de confianza.

## Primer entregable Claude, CPU/lectura antes de GPU

1. Acusar ID y conservar SHA de propuesta, backend/guard originales ya
   existentes; indicar rutas exactas. El acuse del texto pegado no aparece
   todavía como respuesta retenida RT-AUD-001 en esta copia de la coordinación.
2. Mostrar cómo se exportan desde cada backend ID de triángulo y t sin
   antialiasing, jitter, blending, remapeo ambiguo ni lectura de cobertura.
   Cycles a una muestra NO se supone automáticamente centro de píxel:
   debe demostrarse el rayo efectivo con origen/dirección o marca equivalente.
   Si no puede cumplirlo, marcar capability pendiente; no sustituir salidas.
3. Proponer manifiesto común de coordenadas float32 exactas, triángulos,
   rayos explícitos y mappingID. CPU valida rayhash, geomhash y correspondencia
   de resultados; no instalar/exportar software externo para demostrarlo.

## Piloto a congelar solo tras capacidad de readback

- 64 rayos deterministas por escena: controles hit/miss, profundidad distinta,
  interior de triángulo, borde/coplanar/empate explícitamente ambiguos,
  orden de triángulos permutado y hueco/rasancia diagnóstico. Dirección unitaria
  y t en BU definidos para AMBOS. Empates no pueden resolverse silenciosamente.
- Casos pequeños T=2,32,208,1000. T208 solo dato estructural preparado en copia;
  usar conf1 real únicamente lectura y con SHA, no promoción óptica/conf1.
- Resultado por rayo: status, ID, t, origen/dirección efectivos. Coordenadas
  comunes y mismo criterio de nearest-hit. Referencia exacta racional CPU
  para fixtures no degenerados; ambiguos etiquetados antes de comparar.
- Umbrales piloto preliminares: ID idéntico en únicos hit; miss idéntico;
  errorabs_t<=1e-6 BU para geometría acotada a1BU. Esto es diagnóstico
  geométrico, NO puerta óptica. Longitudes de onda reales exigen presupuesto
  independiente `2*pi*abs(delta_L)/lambda` y campos complejos por camino.
  Confirmar escalas y congelar tolerancias antes de medir, sin relajarlas.
- Solo tras correctitud: 3warmups y20paresAB/BA a igual rayos/salidas, retener
  todas muestras y costes completos, sin baseline sustraída como métrica primaria.
  Export/build/BVH/startup frío separado; memoria/transfer/sync/readback/decoder
  incluidos. No afirmar RT hardware solo por preferenciasOPTIX: evidencia backend.
- Batching y escenas grandes son experimentos posteriores. Sin equivalencia
  con MLP, ventajas energéticas, capacidadmáxima o redcoherente completa.

## Seguridad y aceptación

GPU autorizada por Fran cuando libre, pero no lanzar hasta contrato y piloto
listos: gpuq exclusivo, guard fail-closed, RAM>=4GiB tras presupuesto,
VRAMtotal<=18GiB/temp<=80°C, deadline nuevo/hijo<=120s. Si memoria impide
piloto, seguir CPU sin cancelar tickets ni matar otros servicios.
No cambiar el cierre nocturno histórico06UTC ni usar renders decorativos.

Entrega requerida: respuesta `RT-EQUAL-001` con acuse y capability/mappingID
demostrables por código/evidencias existentes, o bloqueo concreto. Codex
prepara fixtures/checker independiente mientras Claude revisa; no duplicarRT.
