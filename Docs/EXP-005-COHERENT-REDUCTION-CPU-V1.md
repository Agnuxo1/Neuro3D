# Reducción coherente: adversario CPU acotado

Contrato nuevo independiente del piloto GPU pendiente. Recibe campos
representados uint32 (real/imag), IDs completos suministrados, fuente,
puerto y grupo/frecuencia explícitos. Máximo64 filas; no importa Blender,
GPU ni código de Claude. No traza escena ni valida la completitud geométrica.

Oráculo independiente de reducción: suma exacta de racionales de los
float32 de entrada, por puerto/grupo. Modelo CPU RN32 de suma lineal y
Neumaier32; intermedios normales o cero, overflow/subnormal fail-closed.
Campos entre grupos distintos nunca se suman; sus intensidades ideales
se añaden. Un mismo grupo exige lambda representada exactamente igual.

Antes de probar: gate absoluto de campo1e-4 (cotaL1 conservadora de norma
compleja) y potencia2e-4 por puerto. Potencia aquí usa cuadrados racionales
exactos del campo modelado: NO aritmética de detección GPU. No incluir
error previo de campo, geometría/fase/coeficientes ni sin/cos del driver.

Adversario A+1-A con A=2^25: seis órdenes, referencia exacta1. Suma lineal
puede perder el residuo; compensación se comprueba sin cambiar gates.
Amplitud grande SINTÉTICA, no escena física normalizada ni falla de la red
existente. Control normalizado1+2^-25-1: pérdida relativa puede ser100%,
pero el error absoluto pequeño puede pasar. Retener ambas interpretaciones;
no confundir límite absoluto con garantía relativa en puertos oscuros.

Pruebas adicionales: grupos independientes vs coherentes, lambda mixta,
IDs incompletos/duplicados, fuente extraña, ABI noexacta, NaN/Inf/subnormal,
bool y overflow. No ejecuciónGPU, promesa de velocidad ni promoción nativa.
No alterar shaders/fixtures/capturas/launcher congelados. JEV bloqueado,
fallback local sin aval remoto.

Siguiente útil: integrar esta contribución al presupuesto total por grupo
con errores previos explícitos; para GPU, contrato/ledger y negativos nuevos
antes de implementar reducción nativa. Nunca sustituir inferencia desde
escena por estos campos suministrados sin declarar el cambio de backend.
