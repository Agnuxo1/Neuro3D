# Captura retenida: la hipótesis de almacenamiento RN no queda acreditada

P1/LEDGER-INTERVAL-001-CODEX. SOLO lectura CPU de una sonda histórica
`K3_base/pair01_0`: cuatro puertos, 44 rutas de dos fuentes activas.
No se ejecuta GPU, Blender, tracer/oráculo ni writers ajenos; no se repiten
las246 sondas ni PRECISION005/006. Shader/contratos/fixtures/gates intactos.

Manifest nativo0337 SHAca23f606...c7d5b3 coincide con la evidencia anterior;
declara OPENGL y shader914bf296...dfcd1. Readback K3_base SHA
6f65faf5b53307103aafdc37f48e9fa96330ff0500fd0e45c18e4363308da418
es fingerprint ACTUAL: el manifest original NO incluyó SHA de ese readback. No
confundir esta relación histórica/lectura con autenticación de ejecución.

Comprobación condicional independiente: cada valor normal float32 retenido
define su celda cerrada de redondeo al más cercano, con midpoints racionales
de sus vecinos (ties sobreaproximados). Se suman celdas del ledger y se
ensancha SOLO por gamma_n de sumas IEEE RN64: u=2^-53,
gamma_n=n*u/(1-n*u), multiplicado por suma de máximos absolutos de celdas.
La celda del campo final debe intersectar ese intervalo si se cumple tal
hipótesis. Esto no certifica RN/FTZ/FMA real, ni fase, geometría o física.

| Puerto | Distancia L1 entre suma EXACTA del ledger y campo capturado | Celdas compatibles real/imag |
|---|---:|---|
| c0.Y | 1/2^26 | sí/sí |
| c1.Y | 5/2^27 | sí/sí |
| c2.Y | 7/2^27 | sí/sí |
| c2.escape | 15/2^27 | sí/NO |

FAIL conservado: componente imaginaria de c2.escape no cabe bajo la
hipótesis RN32 de almacenamiento + RN64 de acumulación. NO se aumenta
la celda a una ULP ni se cambia el gamma/umbral para convertirlo en PASS.
Tres tests: dosPASS y unoFAIL/rc1, repetido solo tras añadir evidencia de
intervalos separados y fold32; fallo inicial y final conservados.

La suma secuencial CPU RN32 de ese ledger coincide exactamente con ambos
componentes capturados de c2.escape. Es una pista, NO prueba de que el
compilador/driver acumulara float32: varias causas pueden dar el mismo dato,
incluidas hipótesis de conversión distintas o inconsistencias del artefacto.
No atribuir causa ni declarar incorrecto el shader por este contraste.
El gate óptico histórico1e-4/2e-4 NO ha sido reevaluado ni invalidado aquí.

También se conserva canal de potencia frente al cuadrado exacto del campo
capturado, separado por puerto y con rutas por fuente. No inferir coherencia
física de esa suma ni sustituir intensidad por reconstrucción desde ledger.

Claude: acusaID/SHA. SOLOsiYAexisten, aporta evidencia del compilado efectivo,
semántica de conversión/acumulación y raw/binding de ESA captura/sonda;
no otraGPU/barrido/suite/guardreview. Hasta entonces RN64 nativo NOacreditado
por el tipo dvec2 en fuente. Skillsreview/cognition separaron evidencia real
retenida de modelo condicional; fallbacklocal sin aval/reintentoJEV.
