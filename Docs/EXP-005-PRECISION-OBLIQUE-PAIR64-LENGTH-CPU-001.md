# PRECISION-OBLIQUE-PAIR64-LENGTH-CPU-001

Contrato opt-in P1 propio Codex capacity_audit/EXP005. Base 51f1c9b1d628efee633b7118cf57eee1c3549f84.
Padre sellado: `coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-INTERVAL-CPU-001-CODEX.json`, SHA256 bf34de7e81a004bf602437ab260e88060f7d36f899c5862bcd3c1d652f1bd354, 124987 bytes.

## Alcance fijado antes de las pruebas

CPU binary64 digital, no GPU/RT/Bpyfloat32/óptica física. Consumir capturas YA existentes de 16 registros; no ejecutar transporte, predicado ni suites antiguos. Sólo los dos `CPU64_DECLARED_BOX_DISJOINT` reciben una cota de longitud del segmento recto SOURCE0→DETECTOR0 en unidades `scene_length`. El cruce interior, tres contactos y diez rechazos upstream conservan STOP antes de decodificar o calcular longitud. Disjoint sólo frente al primitivo declarado; no certifica escena completa ni camino físico sin obstáculos.

Selector cerrado: backend/policy/record_id/recibo y hash del registro/query upstream/frame/ALL240bytes. Los 15 pares conservan BOTH limbs por decodificación HOST exacta y todos sus radios, incluido SOURCE0 después del recentrado nominal constante. No atribuir esa decodificación a aritmética nativa de pares. No introducir SOURCE1 ni fuente compleja, material, longitud óptica, referencia física o fase. Los costes de transporte y predicado previos son no nulos retenidos; costes completos end-to-end UNKNOWN_NOT_ZERO.

## Operaciones y prueba

Convertir outward sólo los seis componentes SOURCE/detector a 12 extremos CPU64; el resto de geometría/radios permanece enlazado al frame sellado. Restar los intervalos con operaciones nativas separadas. Para cada delta, calcular productos reales de ambos extremos con direcciones lo/hi (4 productos por eje). Mínimo de cuadrados cero exclusivamente si el intervalo cruza cero: teorema analítico de x², no EPS ni reparación de un producto negativo. En otro caso mínimo de los productos lower y máximo de los upper. Dos sumas intervalares dan una cota del cuadrado de la longitud.

Ejecutar math.sqrt real en cada extremo no negativo y verificar su nearest-even mediante los cuadrados exactos de los puntos medios con sus dos vecinos binary64. No usar sqrt racional como sustituto del resultado nativo. Si RN² queda del lado incorrecto, nextafter único outward, con prueba final salida² <= radicando para lower y >= para upper. El auditor independiente no usa sqrt ni operadores float para demostrar estas desigualdades: sólo bits y Fraction. Conserva todos los bitpatterns, pruebas, dirección, widening y costes.

Dominio fijo: finitos normales/cero; operandos subnormales, negativos de sqrt, overflow, RN0 con exacto no cero, vecinos fuera de dominio y fallo nearest-even causan STOP. No reducir radios, cambiar dominio/caps, ni convertir fallos en PASS. El esquema HOST original y sus bounds siguen intactos. No hay umbral de calidad relajable; una cota válida puede ser ancha y sigue sin resolver fase física.

Por cada escena admisible se esperan 22 productos/restas/sumas CPU, 12 casts y 2 sqrt nativas; 34 pruebas de redondeo escalar más 2 de raíz y nextafter contabilizados. Verificar analíticamente toda la caja continua, y adicionalmente 64 esquinas de SOURCE/detector por escena. No confundir muestras de esquinas con la prueba de inclusión continua.

## Controles y recursos

Ocho selectores inválidos antes de operaciones. Diez controles nuevos de sqrt, expresamente NO escenas: seis normales/cero, tres input STOP y una respuesta RN incorrecta SIMULADA mediante mock (no fallo del sistema). Ocho capturas mutadas deben rechazarse: radio SOURCE, prueba midpoint, RN raíz, cota longitud, omisión de coste, rescate upstream, falsa fase y selector/frame.

CPU ligera stdlib, 1 hilo y afinidad1, hijo <=60s; ningún Blender/GPU ni instalación. La autorización GPU general no se consume ni modifica la ventana histórica cerrada. JEV bloqueado por seguridad: fallback local explícito sin retry ni aval remoto. Cuatro archivos propios revisados para commit LOCAL; cuatro boards locales SINstage. Solicitar a Claude sólo artifacts YA existentes por ID/path/SHA/bytes (backend+guard fail-closed, igual trabajo/salidas/costes, escena incertidumbre/autenticación/completitud); no ACK inventado ni cargas de relleno.

## Evidencia

Resultado y capturas inmutables en el recibo propio. El checkpoint llevará el commit LOCAL y las comprobaciones POST para evitar hash circular en el recibo. Las skills de cognición extendida y desarrollo guiaron reutilización sellada, alcance no duplicado y pruebas antes de integrar.

## Resultado local retenido

Primera suite PASS, 2 cotas nativas/14STOP heredados/8selectores inválidos/8capturas mutadas rechazadas. Prueba analítica de toda la caja +128 esquinas. Nuevas operaciones reales:44 aritméticas,24 casts,4sqrt en escenas y6sqrt reales adicionales en controles; además1 invocación interceptada mock SIMULADA (contador de intentos de raíz=7 en controles, NO7sqrt reales).154nextafter en escenas +14 en controles.0transporte/predicado/replays/GPU. Tres pruebas API sin aritmética verifican STOP público, sello incorrecto simulado y ausencia del padre simulada.

Anchura observada del segmento thin_beyond_end: 11/72057594037927936 = 11·2^-56 ≈1.5265566588595902e-16 scene_length. Radio SOURCE por eje=2^-66; cociente anchura/radio=11264 (diagnóstico, no umbral ni mejora prometida). Los casts/operaciones CPU64 outward pueden ensanchar mucho más que los radios nominales: una inclusión válida NO demuestra fase suficientemente precisa. Anchura outside≈0.004143257176200343 scene_length. No longitud óptica, referencia física, material ni fuente compleja autenticada; promoción STOP intacta.

Recibo con primera captura y oráculo independiente; no barrido antiguo repetido. Incidente administrativo de lectura de metadatos KeyError por wrapper evidence conservado; sin escrituras ni ejecución numérica y corregido al leer la estructura cerrada. Sin fallo numérico real; los fallos mock son controles, no incidentes del sistema.
