# Contrato congelado: frontier compartido V1

Fecha: 30/09/2026 03:35 UTC, antes de GPU. Borrador anterior conservado.
Shader nuevo `exp005_shared_frontier.glsl`, backend `shared_frontier_gpu.py`,
runner `exp005_shared_runtime.py`. No modificar kernel, ABI ni inputs V1/V2.

## Operación y contadores

Un único dispatch(1,1,1), grupo local1: enumeración DFS de fuentes/rayos y
acumuladores por cinco puertos máximo. No recorridos separados por puerto,
no matriz ni rayos/campos/rutas CPU de entrada. Geometría/óptica vienen de
snapshot evaluado de escena Blender reabierta; el host hace transporte,
preflight/readback y oráculos. GPU ALU exhaustiva, **no RT/BVH**.

Cuarta imagen final work_out: totalcasts, totalterminalpaths, invocaciones1,
status. Cada puerto recibe COPIA del totalcasts como metadata para conservar
ABI, no sumar esas copias como trabajo real. Decoder exige contador finito,
entero, copiesconsistentes, suma de caminos porpuerto y único statusglobal.
Oráculo independiente debe confirmar exactamente totalcasts/totalpaths.
Errores de cualquier rama borran TODOS los campos parciales.

Límites sin expansión:64tri/5sources+portsopt-in(default3protegido),stack33/
depth32/steps4096porfuente/ledger128porpuerto. Bias1e-6+eps1e-9 y distancia
compensada. Primitivasdeintersección/fase idénticas a kernelprevio verificadasCPU.

## Gates congelados

Reabrir SOLOLECTURA12escenasK3/K4de0315. ManifestSHA:
`c101286137e59ceb47918e0913f112c3ca1a0e9733610b662be7d2d63dd961f4`.
SHA12.blend previos y posteriores intactos; snapshot evaluado exacto para
cada entrada. Seis tratamientos y bases/todospares1/i:246probes.

Campo/ledger/suma/analítico/comparaciónGPUprevio<=1e-4;potencia/balance<=2e-4;
longitudledger<=1e-5BU; multiplicidad/source/countsexactos. Sham exacto,
cuatrocontrolescausalesbasis0ΔP>1e-3 en ambos tamaños. Fuera del cono de
fase, puertos definidos por historias independientes deben quedar exactos
(107casos segúnfixtureV2;19dark). No excluirpuertos oscuros.

Diez negativos:missingmirror/overlap/modeaxis/steps1/depth1 en ambos tamaños.
Error específico en todospuertos y camposborrados. Stack/ledgeroverflow/role
siguen defensivos NO runtimeverificados; no inventar evidencia.

No benchmarkdevelocidad en estaunidad. Registrar tiemposdispatch/readback
como diagnóstico, sin comparar con corrida anterior de orden/warmupdistintos.
Reducir recorridosgeométricos no implica aceleración end-to-end ni ventaja
frente a otras redes. Comparación de costes requiere protocolo separado.

Artifacts nuevos porcorrida, FAILconservado, gpuq/guard120s/host1,5/device1,
RAMfloor4GiB/VRAMtotal18GiB/temp80°C/deadline06UTC. No matarajenos, no bajar
reservas para entrar. RT/OptiXClaude. JEVbloqueado/fallbacklocalsinavalremoto.
