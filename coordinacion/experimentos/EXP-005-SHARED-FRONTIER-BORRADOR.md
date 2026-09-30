# Siguiente unidad: un recorrido GPU compartido por entrada

Preparación local, 30/09/2026 03:24 UTC. **No implementado, no congelado,
no medido**. No modifica V1/V2 ni sus resultados. JEV bloqueado; sin aval.

## Problema verificable

El shader rawscene actual asigna una invocación a cada puerto. Cada una
vuelve a recorrer todas las fuentes y ramas, reteniendo solo contribuciones
para su puerto. Para cinco puertos se repite la búsqueda de intersecciones
cinco veces. Los `casts` por puerto describen ese recorrido particular;
no interpretar una copia del mismo contador como trabajo compartido.

## Implementación propia propuesta, sin duplicar RT de Claude

Nueva versión ALU dentro de Blender. Una invocación por entrada coherente,
frontier/DFS único y acumuladores complejos por puerto: cada camino terminado
escribe una contribución en el ledger de su puerto. Modos y referencias
deben seguir viniendo de objetos de escena, nunca de cableado por convención.
Al terminar, calcula intensidad y escribe campos, ledger y contadores.

Mantener explícitos los límites actuales: 64 triángulos, hasta cinco fuentes
y puertos solo con perfil opt-in5, stack33, depth32, pasos4096 porfuente,
ledger128 porpuerto. La búsqueda sigue exhaustiva ALU: **no RT ni BVH**.
Un error de cualquier rama invalida y borra TODOS los campos parciales.
Conservar la interfaz de final-readback; sin transferencia de frontier,
campos, caminos o rayos intermedios a CPU durante inferencia.

AntesGPU: nueva ruta shader/backend, tests CPU de ABI/gates/negativos,
revisión de código, contrato final y commit. No modificar shaderV1 para
comparar versiones tras medir. No reusar contadores antiguos sin explicar
que ahora el total de recorrido se comparte: cada puerto puede recibir
copia de `total_casts` como metadata, no como múltiples recorridos reales.

## Gate propuesto a congelar

Inputs: doce escenas K3/K4 de0315 SOLOLECTURA, hashes previos y readback
evaluado coincidente.246bases/pares: mismas tolerancias V2 frente a oráculo
triangular independiente y composición analítica, ledger por camino,
sham exacto, causalidad positiva y fuera del cono negativo. Diez abortos
runtime previos. Ledger/stackoverflow siguen defensivos si no se construye
un adversario válido antes de medir; no alterar límites para fingirlos.

Además, exponer inequívocamente `traversal_invocations=1` y totalcasts real
del recorrido; verificarlo en código/readback y contra el conteo CPU.
No afirmar rendimiento por reducir un contador. Si hay comparación de
tiempos: preinscribir warmup, repeticiones, órdenes y costes completos;
el gate de correctitud no será por sí solo benchmark de superioridad.

Reserva nueva gpuq por job, guard120s/host1,5GiB/device1GiB/piso4/VRAM18/
80°C/corte06UTC. Usar nueva carpeta, retener FAIL y liberar porjob. Si no
hay prueba útil preparada o recurso seguro, no llenar GPU con decoración.
Claude conserva OptiX/RT/capacity; pedir interfaz antes de tocar su backend.
