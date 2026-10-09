# Piloto autorizado: ejecución y desenlace inconcluso

**Resultado actual:** el segundo intento inició el worker con 4.877,727 MiB de RAM libre. Agotó el presupuesto original de 90 segundos sin escribir resultado; el supervisor detuvo únicamente ese proceso y verificó su limpieza. Duración supervisada 90,040895 s, pico de RSS propio 23,742188 MiB. El [recibo completo](validation/captured-pilot-execution-2026-10-09/attempt02/supervisor.json) registra `WORKER_DEADLINE`, `result_collected=false`, `primary_metric=null`.

El piloto se ejecutó una vez; el primer intento previo no arrancó. La hipótesis de viabilidad permanece **inconclusa bajo este perfil**, no confirmada ni refutada por una métrica geométrica. No existe un campo que auditar: se auditaron hashes de inputs/fuentes, autorización, límite temporal y limpieza. El log del worker está vacío y se conserva como tal. No se conoce cuántos caminos había completado al ser interrumpido.

Se preservan todos los bytes y fuentes previos al cálculo, y se verificaron los once hashes del manifiesto del supervisor. No se extiende el presupuesto ni se sustituye el trazador dentro del mismo protocolo. La selección espacial exacta en desarrollo y cualquier nuevo recorrido serán ensayos separados con alcance explícito.

## Primer intento conservado

El 9 de octubre se verificaron el protocolo congelado, sus cinco hashes de inputs/fuentes y la autorización humana publicada. El supervisor rechazó el arranque: RAM libre **3.652,15625 MiB**, por debajo del umbral prospectivo de **4.000 MiB**.

El [recibo original](validation/captured-pilot-execution-2026-10-09/attempt01/supervisor.json) registra `worker_started=false`, `result_collected=false`, `primary_metric=null` y limpieza verificada. Esto es **NOT_EXECUTED**, no un fallo geométrico ni una refutación de la hipótesis del piloto. El [índice](validation/captured-pilot-execution-2026-10-09/artifact_index.json) conserva el recibo y las preimágenes del supervisor/auditor con hashes verificados.

Se mantienen sin cambios 4.096 rayos, profundidad 64, 90 segundos, una CPU y ningún uso de GPU. Un intento posterior por disponibilidad de recursos utilizará un directorio nuevo y conservará este rechazo. La autorización adicional del propietario para utilizar GPU se aplicará a ensayos separados; no modifica este protocolo.

La inspección local muestra una NVIDIA RTX 3090 de 24 GiB y ningún controlador gráfico AMD. El inventario no acredita una nueva ejecución científica en ninguno de los dos fabricantes. El acceso al registro externo/IPFS sigue pendiente, sin identificadores emitidos.
