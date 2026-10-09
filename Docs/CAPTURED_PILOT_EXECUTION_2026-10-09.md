# Piloto autorizado: primer intento de ejecución

El 9 de octubre se verificaron el protocolo congelado, sus cinco hashes de inputs/fuentes y la autorización humana publicada. El supervisor rechazó el arranque: RAM libre **3.652,15625 MiB**, por debajo del umbral prospectivo de **4.000 MiB**.

El [recibo original](validation/captured-pilot-execution-2026-10-09/attempt01/supervisor.json) registra `worker_started=false`, `result_collected=false`, `primary_metric=null` y limpieza verificada. Esto es **NOT_EXECUTED**, no un fallo geométrico ni una refutación de la hipótesis del piloto. El [índice](validation/captured-pilot-execution-2026-10-09/artifact_index.json) conserva el recibo y las preimágenes del supervisor/auditor con hashes verificados.

Se mantienen sin cambios 4.096 rayos, profundidad 64, 90 segundos, una CPU y ningún uso de GPU. Un intento posterior por disponibilidad de recursos utilizará un directorio nuevo y conservará este rechazo. La autorización adicional del propietario para utilizar GPU se aplicará a ensayos separados; no modifica este protocolo.

La inspección local muestra una NVIDIA RTX 3090 de 24 GiB y ningún controlador gráfico AMD. El inventario no acredita una nueva ejecución científica en ninguno de los dos fabricantes. El acceso al registro externo/IPFS sigue pendiente, sin identificadores emitidos.
