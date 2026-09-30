# Fase con referencia efectiva negativa: variante CPU opt-in

Contrato previo a pruebas, 30/09/2026: no modificar los candidatos, shaders,
contratos ni pilotos nativos congelados. Un tramo físico no puede ser negativo;
sí puede serlo la longitud efectiva después de sumar la corrección de referencia
del modo terminal. La escena y sus modos NO se cambian para evitar ese signo.

La variante calcula el candidato congelado sobre |L| y aplica el signo solo al
ángulo. La cota racional RN/FMA se conserva por simetría de conjugación ideal.
Se verifica la traza positiva completa y la vinculación de L, signo y ángulo.
No presupone residuo FMA universalmente exacto. Sigue excluyendo subnormales,
|L/lambda|>=2^52 y ejecución sin FMA. No certifica signo de cero ni libm/driver.

Intervalos de longitud negativos o que cruzan cero: extremos de L/lambda en
las cuatro esquinas, lambda estrictamente positiva. No envolver únicamente
los extremos ni perder vueltas completas. Gates siguen campo1e-4/potencia2e-4.

Pruebas pequeñas: tres negativos retenidos de la crítica de Claude, tres
vecinos de media vuelta negativa, un caso general largo y cero; cinco trazas
alteradas y dominios inválidos; cuatro escenas MZI con referencia Dx negativa,
dos fuentes coherentes/separadas y un control de referencia positiva.
Completitud por camino/grupo, simetría y conteo13/26 registros, 4/8 caminos.
Un hilo CPU/hijo60s, sin Blender/GPU/RT, escrituras peer ni repetición de barridos.

La composición es una cota condicional de modelos ideales representados.
No suministra rutas CPU a una GPU ni promueve conf1, transporte hi-lo, precisión
total, solapamiento físico o ventaja de velocidad. JEV bloqueado: fallback local.
