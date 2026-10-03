# PRECISION-POSITION-HILO-RECONSTRUCT-CPU-001

Consumidor nuevo opt-in `precision-position-hilo-reconstruct-CPU-v1`,
API `audit(model,request)`. CPU analítica racional: no hardware/Blender/GPU/RT.

## Contrato

Padre INGRESS-HOST-001, recibo
`coordinacion/respuestas/PRECISION-POSITION-HILO-INGRESS-HOST-001-CODEX.json`,
SHA `03dbb47ddec84ffec2ffbbac02f4f0467a9cefd8063b787a727bdfed8ebe7ec9`.
Todas las capturas, oráculos y pins son verificados. No reproducir encoder,
traversal/clip/ingress/shader/compilación previos; se leen resultados sellados.

Selector seis strings: record_id, consumer, parent_receipt_sha256,
parent_record_sha256, geometry_sha256, intent.
Intent `ROUNDED_POSITION_CONSUMER_ERROR_ONLY`.
Consumer explícito ANALYTICAL_RNE32 o ANALYTICAL_RNE64, nunca autodetectado
ni sustituto silencioso de la suma EXACTA HOST del receptor previo.

La geometría recibida debe coincidir exactamente, incluido contexto, con
ORIGINAL cuyo SHA está sellado. En los 120 frames admitidos actuales
el error de encoding era cero. Se redondea cada centro exacto hi+lo a
binary32 o binary64 mediante RNE entero-racional con ties-to-even.
Se deriva el radio abs(rounded-original) en las 15 coordenadas.
No error relativo al hi aislado ni solo al segundo cast.
Mantener normal/cero, rango normal explícito, overflow/subnormal STOP;
+0 canónico racional, sin claim de signed-zero original ni FTZ/FMA nativos.

El padre STOP siempre permanece STOP antes de operaciones nuevas.
Si los centros siguen idénticos y todos los radios son cero, se verifica
y reutiliza certificado sellado del ancestro encoding por SHA exacto.
Si cambian, aplicar biblioteca pura clearance congelada SOLO a la nueva
geometría consumidor y sus radios DERIVADOS, nunca repetir cotas originales.
No aumentar 128bits/bounds/fixtures/conf1 ni cambiar umbrales.

Admisión limitada CPU_ROUNDED_POSITION_SEPARATION_ONLY con gap > 0.
No phase/field/fullvisibility/scene/uncertainty/GPU autenticados. Promoción STOP.
Errores/diagnósticos de STOP se conservan, pero rows/rounded_geometry/radii/
consumer_words vacíos o None. Los contactos no se rescatan con precisión mayor.

## Resultado verificable

330 principales = 160 registros/modos padre x 2 consumidores + 10 negativos.
192 separaciones CPU; 138 STOP = 80 padres bloqueados, 48 pérdidas NUEVAS
de hueco consumidor (24 RN32 y 24 RN64), 10 selector/modelo.
16 helpers con 0, signos, ties-even, 1/10 y mínimo normal; 9 negativos
(subnormal, overflow de dominio, carry de redondeo a overflow, tipo/consumer).
API pública y recibo ausente aparte. No claim de exhaustividad IEEE754.

Los 120 frames coincidían byte-a-byte, pero en las 24 geometrías hi-lo
outside_2m60, ambas sumas RN32 y RN64 pierden el desplazamiento 2^-60
alrededor de 1: los radios derivados consumen el separador (gap=0).
No es un fallo del encoder/receiver ni evidencia de ejecución GPU defectuosa.
Binary64 sola no sustituye una representación hi-lo preservada en ese caso.
No se concluye contacto real ni equivalencia de costes ni motor ganador.

Todos los admitidos son controles CPU SINTÉTICOS. S0/S1 de las escenas
declaradas previas permanecen STOP. Contexto/hash de source_position_BU
no constituye escena física/Bpyfloat32 autenticada ni inferencia neuronal.

Oráculo independiente sin importar core: vecino IEEE, midpoints/tie-parity
para 3600 palabras redondeadas y helpers; radios contra ORIGINAL; 48 cotas
NUEVAS por 13440 proyecciones de ocho esquinas/punto/axis;
192 reuses por certificado idéntico, censo, pins, API y flags.
No replay de 72 geometrías originales ni de suites congeladas.

Captura propia acotada a 2MiB, schema ROWS_AND_PINNED_CERTIFICATE_DEDUP_V1:
rows=diagnostics o vacío; certificados cache se referencian por SHA/record
y se reconstruyen del ancestro sellado. Resultado reconstruido se verifica
con result_sha256. Las 48 cotas nuevas se guardan completas. No pérdida de
evidencia ni aumento del límite. Fuente de restauración/oráculo en recibo.

Ledger PARCIAL principal: 3600 redondeos RNE, 3600 diferencias absolutas
ORIGINAL, 48 separadores nuevos y 192 cachés verificadas.
Internos racionales, validación, SHA, I/O/setup/serialización/upstream/
memoria/auxiliares UNKNOWN_NOT_ZERO. Tiempo de prueba no es benchmark.
No costes completos/energía/eficiencia/velocidad/RT equivalentes inferidos.

Fallback LOCAL: JEV bloqueado por seguridad sin retry/aval remoto.
Own4 revisados/versionados; checkpoint/sharedboards locales SINstage.
Fixtures/runners/shaders/contratos congelados intactos, sin GPU.
Pedir Claude solo artifacts YA existentes con ID/path/SHA/bytes del consumidor
posicional, backend/guard y mismo trabajo/salidas/costes completos.
Continuar únicamente con representación que conserve los limbs y sus errores,
sin asumir que sumar en binary64 satisface la escena o la fase.
