# EXP005 — AXIAL-GEOMETRY-DECODE-GUARD-CPU-001
P0 Codex, NUEVO modelo opt-in. Base6b5c611; anterior intacto.

## Problema acotado
El deserializador anterior liga bytes/paths/ORIGINAL y cargos racionales, pero no verifica que decoded_uint64 sea RN64(hi+lo). Un atacante puede cambiar esa palabra y ajustar ambos cargos para que sean coherentes. No invalida el anterior audit de puntos honestos ni su oráculo; falta guard del consumidor de records externos.
Control sintético preservado: viejo deserializador acepta, nuevo guard rechaza. No reejecución del productor/encoder/raycast/Horner anterior.

## Contrato
Antes del PRIMER add nativo se admiten TODOS los records: tipos exactos (bool no es int), paths completos ordenados, words finitos normal-o-cero, SHA/bytes/snapshot ORIGINAL y cadena RN-even.
Cadena comprobada por intervalos de midpoint entre representables adyacentes: high32=RN32(ORIGINAL), residual64=RN64(ORIGINAL-high), low32=RN32(residual), decoded64=RN64(high+low). Ceros IEEE por nodo y empate-even; cargos racionales canónicos completos. No se toma el cargo provisto como prueba de redondeo.
Sólo después se ejecuta RN64(high+low) desde palabras SERIALIZADAS admitidas y se compara su output word. Retorno atómico; ningún snapshot parcial se entrega al fallar.
Modelo CPU de punto; runtime probes locales obligatorias en entrada audit. decode_guarded es primitiva interna; no API GPU/job-guard ni autenticación/coherencia remota.
Conserva misma escena decodificada honesta/76coords2fuentes. Otras17 sin ejecutar/two_sources no parcial; caps/fixtures/FAIL intactos.
No nuevos raycasts/argumento/Horner/SOURCE/material/reducción/potencia/detector ni cotas físicas/uniformes.

## Verificación y costes
4 tests propios, falsificación coherente, mutación del ÚLTIMO record, tipos/ceros/empates/hash/stale/runtimefail. Todas las entradas rechazadas antes de cualquier add nuevo.
Oráculo independiente stdlib usa redondeo IEEE por enteros (no midpoint del guard), reconstruye words/SHA/paths/escenas/salidas y controla preservación de la falsificación y 8FAIL/12signos previos.
Main76adds64 nuevos; encodingcasts/subs/raycast0. Probes6ops64+4casts32, controles extra y racionales/pins/IO/setup no medidos separados; suite wall medido no benchmark igual-trabajo.
CPU1hilo/afinidad1/hijo<=60s; SINGPU/Blender. JEV fallback local sin aval/noretry, histórico0337 cerrado. SinSDKDrJitKagglepushmerge. Boards locales SINstage; sólo cinco archivos propios versionados.
