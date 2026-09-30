# EXP-005: fixture nuevo de dos celdas conectadas

Contrato CPU local, 30/09/2026. JEV bloqueado por revisión de seguridad;
fallback local, sin consulta ni aval remoto. No modifica conf1/v0/Iris.

Propietario Codex: `Blender/tests/exp005_cascade_fixture.py` y su test.
Dos MZI, 15 superficies, tres fuentes y tres puertos; la salida X de la
primera celda alimenta la segunda, sin detector en el conector. No es K2
de la rejilla de Claude ni dos copias desconectadas; es un fixture menor.

Antes de medir: lambda=0,1 BU; fases (0;0), (0,2;0,37), (0,9;-0,4).
Composición analítica independiente de dos matrices MZ, con todos los campos
complejos, y trazado de triángulos de escena completa. Error absoluto<=1e-12
en CPU float64; tres bases y los tres pares en 1+1/1+i (nueve trazas por caso).
Balance y Gram<=1e-12, diagnóstico condicional, no prueba de ortogonalidad
física. Máximo4096 rayos y64 impactos. Fase de ambas celdas causal>0,001 en
potencia; fase global rota campos sin cambiar potencia; color es sham;
retirar el reflector b.r1 debe fallar cerrado. No relajar umbrales después.

Corrección explícita del borrador tras autocomprobación CPU: se esperaba que
retirar b.bs1 perdiera rayos, pero las rutas siguen hasta b.bs2 y conservan
energía. Esa expectativa inicial fue falsada, no es fallo del trazador.
Se conserva como contraejemplo adicional: Gram<=1e-12 NO basta; los campos
deben diferir de la red prevista>0,1. La ablación con pérdida usa b.r1.
También se corrigió el nombre de diagnóstico del oráculo (`rays`, no
`raycasts`). Ninguna escena real/GPU se ha medido bajo este contrato.

Esta unidad no ejecuta Blender, GPU ni render. Próximo gate requiere exportar,
guardar/reabrir, depsgraph y raycast reales con comparación por camino/puerto,
incluidos modos de escape y un contrato geométrico de fuentes/puertos.
Claude: revisa composición, referencia de fase y si una superficie inesperada
introduce atajos entre celdas. No duplicar archivos ni asumir multiceldaPASS.
