# AXIAL-SELECTOR-INT256-001: ABI de selección CPU, no backend nativo

Entrada explícita: dos uint32 binary32 normales/cero (cociente hi-lo retenido),
radio no negativo little-endian uint32[8] en ciclos * 2^149. Salida signed256
little-endian uint32[8] para residual, en unidades 2^-149 ciclos. Código CPU
con enteros acotados signed256, no operación GPU/ALU ni autenticación nativa.
No usa Fraction/división/floor racional para decidir turn o quarter.

Cada palabra se decodifica exactamente con mantisa << (exponente-1), después
se aplica signo. Sum/shift/add/sub controlan [-2^255,2^255-1]; cualquier
desbordamiento, subnormal, NaN/Inf, bool o ABI mal formado RECHAZA.
El radio se transporta explícitamente: ceil(max(|lo-X|,|hi-X|)*2^149).
Adaptación HOST racional separada, inflación outward registrada; nunca se
confunde con aritmética GPU ni reduce la incertidumbre anterior.

Turn n=(X+2^148)>>149, en X-radio, X y X+radio; deben coincidir. Después
quarter k=(X-n*2^149+2^146)>>147, mismos endpoints; deben coincidir.
Tie exacto se asigna a rama derecha, como floor(x+1/2), no nearest-even.
Residual X-n*2^149-k*2^147 se devuelve EXACTO en signed256, abs<=2^146.
Los shifts a derecha tienen semántica aritmética signed; cualquier futuro
port deberá probarla. No se hace cast a float ni producto por pi.

Los datos vienen de informes congelados por SHA, no de ejecutar productores:
IDs/gauge/bindings/cobertura y elecciones antiguas deben coincidir. Mantener
flags anteriores, NOpromoción full-field/selector nativo/argumento/geometryABI.
Dieciocho casos retenidos; la rama mode ya rechazada no hace aritmética.
No sustituye inferencia desde escena por outputs suministrados/U-GEMM.
Coste de modelo entero/decodificación separado; NOcoste hardware/fullcost.
Frozen/fixtures/budgets intactos. JEV fallback local sin aval/reintento.
Skills contrato/reuso; un hilo/hijo<=60s; boards/checkpoint locales SINstage.

## Resultado verificado

Ocho tests PASS rc0/1,1016028s, un hilo/hijo60s. 18 casos retenidos;
21 paths evaluados/17 gates parciales de selector, mode upstream no evalúa.
Validador independiente: 441 nodos enteros retenidos +222 primitivas =663;
12 primitivas, 96 contrastes con oracle racional independiente en tests,
69 huellas congeladas verificadas. Fuente/gauge/bindings/turn/quarter/
residual concuerdan con registros anteriores. No replay productores.

Tie exacto ±1/2 y ±1/8 selecciona rama derecha; radio de UNAunidad 2^-149
cruzando límite RECHAZA. Limb bajo ±2^-40 cerca de 1/2 cambia turn sin
perderse. Radio de 1/(3*2^149) se codifica hacia arriba a 2^-149 y cobra
inflación 2/(3*2^149). Enclosure asimétrico que toca límite por la derecha
puede admitir en contrato viejo; simetrizarlo aquí RECHAZA conservadoramente.
Ese nuevo rechazo se preserva, sin relajar límites ni epsilon.

Dominio mínimo observado -2^106 ciclos (scaled=-2^255) se admite con
radio cero; radio positivo desborda y rechaza. +2^106 queda fuera del dominio
signed256. Pack/unpack de extremos se verifica, pero no amplía dominio de
binary32 aceptado. Subnormales/NaN/Inf/booleanos rechazados sin FTZ.

Los 8 flags completos/10 FAIL antiguos intactos, incluso noquarter con
unidad RN32 anterior rechazada. TODOSfullpipelinefalse; no campo calculado,
producto por pi ni ABI geométrico/selector GPU. Solo primitivas integer CPU
acotadas/21ops por path admitido más decode/host adapter excluidos del conteo.
No equivale a costes completos ni rendimiento de shader/hardware.

Claude: acuseID/SHA y SOLO artifacts0337 geometry/
limbs/bindings ybackend/guard YAexistentes, contrato igualtrabajo/costes
completos; sin nuevas cargas ni guardreview. AntesGPU guard fail-closed,
reserva exclusiva/deadline nuevo, no cambiar histórico cerrado.
