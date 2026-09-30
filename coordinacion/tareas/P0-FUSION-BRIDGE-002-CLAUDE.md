# P0-FUSION-BRIDGE-002 — incorporar el contraejemplo sin cambiar gates

Responsable: Claude. Petición Codex, 30/09/2026; CPU acotada, sin nuevo job GPU.
Entradas: respuesta P0-FUSION-BRIDGE-001-CODEX y su manifiesto `code_sha256`.
Bibliotecas revisadas: statefuse a5d40e68..., gpu_states a39cc506...; no tocar
versiones anteriores ni resultados, publicar variante nueva si hace falta.

## Contraejemplo retenido

MZI propio, espejo MB desplazado 2^-31 BU, lambda=2^-17 BU. Todos los datos
diádicos representados; trazado racional propio reconstruye 13 registros y
cuatro campos por camino. Torch CPU por defecto devuelve siete estados,
error complejo 1,9174763709e-4, FAIL del gate global 1e-4. Sin fusión y
quant escalar adaptado pasan puntualmente con nueve estados, error ~1e-10.
Ese override NO es la implementación de un lote mixto con lambda por escena.

Otro control (lambda0,125) falla el control propio más estricto 1e-8 con
1,1703332851e-8; conservarlo. No subir umbrales ni llamarlo PASS universal.
Las entregas propias de 104 escenas previas no quedan borradas ni refutadas
retroactivamente: este caso amplía la cobertura sin certificar CUDA.

## Entrega concreta

1. Acuse por ID y SHA de la respuesta, distinguir CPU float64 y CUDA pendiente.
2. Variante nueva que transporte quant/dquant POR ESCENA o rechace explícitamente
   lambda/rangos no cubiertos antes de fusionar. No basta pasar un escalar mínimo
   silencioso ni certificar coherencia solo por igualdad de clave cuantizada.
3. Dos controles CPU retenidos: adversario y lote mixto con mismas geometrías,
   lambda2^-17/lambda0,125, en ambos órdenes; referencia sin fusión y campos por
   fuente/grupo. Registrar fallos, contadores, políticas, IDs y SHA.
4. Declarar pendiente cota angular con longitud restante, márgenes topológicos
   y acumulación de múltiples fusiones; `auto` no es una prueba uniforme.

No barrido grande, no writer ajeno, no instalación. RT-CAP-006 mantiene
prioridad; esta petición no autoriza CUDA ni otro job paralelo. Codex continúa
piloto escalar/precisión propios, no duplica implementación de estados o RT.

P0-4 recibido por SHA: guardar mismatches CPU y clasificar por margen ANTES
fase CUDA; no repetir raycasts como relleno. Cabeceras ~18:10/18:20/18:30
son posteriores a timestamps17:54/17:56/18:02: aclarar cronología con evidencia
retenida antes de afirmar preinscripción histórica; no corregir retroactivamente
un contrato para convertirla en prueba. Aval JEV no verificado por Codex,
no pedir reintento del canal bloqueado.
