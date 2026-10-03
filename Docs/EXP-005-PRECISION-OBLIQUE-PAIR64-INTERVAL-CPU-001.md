# EXP005 — PRECISION-OBLIQUE-PAIR64-INTERVAL-CPU-001

Consumidor opt-in CPU sintético, NO GPU/RT/Bpy/óptica física/visibilidad completa.
Base d72c4f554e9508f58d2a42a35164ae813df43a13. Downstream físico/fase STOP.

## Contrato de enlace cerrado

Padre SCENE-PAIR64-CPU001:
813fd728006a90adb40f99d1eb49aa3523f8f63bf61edca7775e332dc57106ea /84149bytes.
Sólo sus 6 escenas y 10 STOP (nativo inexacto +9 entradas) son seleccionables.
Selector enlaza receipt/record/original snapshot/query/request y ALL240bytes de
salida por SHA, política y backend. No override de radios, referencia o fase.
Leer recibo/capturas con límite2MiB, hash/tamaño/EOF completo, PASS de oráculo
y todos los pins heredados; no usar productor de transporte ni suite retenida.
Artefacto local auditado NO autenticación/atestación de escena física.

Antes de predicado: cualquier upstream distinto de CPU_NATIVE_PAIR64_RECENTER_ONLY
devuelve STOP_UPSTREAM, sin decodes/casts/predicado. STOP previo nunca se rescata.

Para ALL15 coordenadas, decodificar AMBAS palabras binary64 normal/zero
little-endian por bits a racional exacto; sumarlas EXACTAMENTE en HOST.
No realizar hi+lo RN nativo previo; no usar solamente hi. Nominal se obtiene
de los bytes recibidos, no sustituyendo por diferencia racional original.
La resta HOST original-SOURCE0 es sólo auditoría de marco geométrico común.
Comprobar nominal contra frame sellado y radio contra el original, incluyendo
origen0±radioSOURCE. Referencia elegida constante NO referencia óptica/fase.
Domain128bits/magnitud2^32 y radios congelados intactos.

Llamar al predicado intervalCPU64 existente sobre nominal decodificado±radio:
30 casts de extremos outward +154 operaciones reales binary64 +280 pruebas
por escena. Cada error RN/outward/nextafter está en ledger/costes; no asumir
colapso exacto ni reducir radio para hacer PASS. Envolver resultado, conservar
STOP aritmético/frontera/det0 y ledgers. No tocar núcleo ni umbrales congelados.

## Verificación y límites

6 llamadas NUEVAS al núcleo de predicado para este enlace explícito cambiado;
0 nuevas llamadas al grafo de transporte,0 suites retenidas repetidas.
No afirmar núcleo0 ni atribuir el coste del transporte almacenado a0:
sus operaciones están en el padre; total end-to-end NO medido.
Oráculo independiente sólo captura/bitpatterns/racionales: validar el grafo
nativo previo sin ejecutarlo, bytes/radios/diferencia común e invariancia exacta
de D/U/V/W/T/end_slack; reconstruir casts/154RN por escena y demostrar inclusión
de TODOS los intervalos originales. Clases1cruce+2disjuntos+3STOP geométricos
condicionados al contrato de cajas; NO visibilidad física completa.

Controles NUEVOS de bytes (NO escena NI salida producida por nuevo grafo nativo):
(+1,+2^-60),(-1,-2^-60),(1,0), radio2^-66 en los dos primeros y0 en el control.
6 casts reales de extremos; demostrar pérdida hi-only2^-60 y ensanchamiento
outward explícito. No extrapolar estos helpers a escenas/RT/fase.
8 selectores alterados STOP antes del predicado;8 mutaciones de captura rechazadas.
10 STOP upstream conservados; fallos directos del abuelo inmutables en sellos.

Costes: decodeHOST180palabras/90pares/1440bytes,924operaciones nativas de predicado,
180casts de escena+6helpers,1680proofs, nextafter/signflips detallados.
Lectura/pins/oráculos/auditoría exacta/preparación/temporales UNKNOWN_NOT_ZERO.
Tiempos de proceso/captura NO velocidad de motor ni comparación equivalente.
No afirmar eficiencia, ganador, redRT o óptica física.
CPU1hilo/afinidad1/hijo<=60s; GPU/Blender0, JEVLOCAL bloqueado sinretry/avalremoto.
Sharedboards locales SINstage; sólo own4 revisados en commit LOCAL.
Skills cognición extendida+feature-development: reutilización de evidencia
sellada y separación explícita entre transporte previo y trabajo del consumidor.
