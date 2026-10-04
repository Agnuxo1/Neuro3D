# PRECISION-OBLIQUE-SCENE-GEOMETRY32-INGRESS-HOST-001

Nuevo adaptador opt-in HOST para entradas originales de geometría. Base 81dcc098f098e4912757ef63874e64639adbc87e. Padre terminal coordinacion/respuestas/PRECISION-OBLIQUE-SEALED-TERMINAL-LEDGER-CPU-001-CODEX.json SHA256 4985f70e2658a7d500e0608bec9dafb2b7b995aca65ff2e670abe77379512fd9/210904bytes. No modificar runtimes, shaders, nearestV2, contratos, fixtures ni bounds congelados.

## Contrato de bytes

Fuente confiable: las MISMAS escenas CPU declaradas precision-oblique-declared-scene-v1, unidades BU, dos fuentes literales S0 y S1, triángulos originales y request exacta. Selección por case/model/policy/scene/query/record/padre/visibilidad SHA. Padre339pins + propio recibo padre =>340dependencias; no reutiliza buffers de otra escena/modelo SOURCE0-DETECTOR0.

Header little-endian <8s8I,40bytes: magic N3DG32V1, versión1,source_count2,triangle_count,scalar_count,primitive_count,root_primitive_id,detector_primitive_id,reserved0. Sigue tabla primitive_id uint32 (misma orden original), y palabras IEEEbinary32 en orden cerrado: S0 posición3/dirección3, S1 posición3/dirección3, triángulos originales por orden×3vertices×3coordenadas, detector_point3,lambda1,reference1. Dirección se conserva SIN normalizar. Descriptor HOST liga offsets/campos/unidades/racionales originales/primitive object mapping y caps originales; caps siguen HOST racionales, NO están subidas ni convertidas a cota de fase.

El buffer NO contiene impactos, barycentric calculadas, tokens de lanzamiento, rutas, longitud calculada, hi-lo de resultados, campo o fase. root/detectorIDs y detector_point son INPUTS de la request declarada, no resultados de kernel ni elección posthoc de escena.

Productor convierte racional original→float64 HOST→struct.pack float32, decodifica palabra exactamente como racional y EXIGE error cero. Si pierde precisión, devuelve STOP_INPUT_CONVERSION_LOSS con original, palabra candidata, decoded32 y signed_error conservados, sin packet. No afirma que dos casts sean una única RN32 directa para arbitrarios: el gate exacto valida el valor FINAL frente ORIGINAL. Normal-o-zero solamente; subnormales/nonfinite/negzero rechazados. Racionales canónicos <=128bits, |valor|<=10^6 y hasta64triángulos, sin aumentar límites anteriores. Zero rational0 usa positive IEEEzero; racionales no contienen signo de cero.

Parser no vuelve a codificar ni ejecuta geometría. Verifica descriptor cerrado y SHA, header/counts/IDtabla/byteslongitud exacta/hexcanónico; decodifica INTEGER cada palabra normal-o-zero y compara con el valor INPUT ORIGINAL. Un payload modificado y reseñado no puede pasar por SHA nuevo: sigue obligado a igualdad por palabra. Manifest/hash no autentican física ni autorizan helpers con datos externos; API pública run carga pins/capturas y sólo acepta registros retained. emit/parse/evaluate internos requieren ese contexto, controles nooriginales explícitamente etiquetados.

Antes de hash/JSON, valida forma/tipos/tamaños de todos los campos del descriptor: strings, listas, enteros, bools y racionales canónicos. Campos anidados/ciclos/extra se rechazan antes de serializar; protege el límite de parsing sin alterar gate de pérdida0. Primera suite PASS retenida y control dirigido de nesting PASS; hardening preventivo y regresiones permanentes, NO fallo numérico inventado.

## Criterios y pruebas

Seis paquetes retenidos,228scalars originales: cuatro35 y dos44 (primitive externa adicional completa).40bytes header+IDs+payload: cuatro188bytes y dos228 =>1208bytes. S0/S1 separados por descriptor y offsets, no campos/fases fusionados.38STOP upstream preservados antescast, sin rescatar FAIL de longitud/fase. Parser independiente struct.unpack/as_integer_ratio vs decoder integer del core.

Mutaciones sólo en memoria: SOURCEorder/primitiveIDorder/fieldorder-unit/caps/SHA/bools/hitextra/word/NaN-inf/subnormal-negzero/header/version/count/reserved/endianness/bytes missing-extra/keys. Rehash de negativos NO promoción original. Nuevos inputs sintéticos1/3 y1+2^-25 muestran LOSS; subnormal2^-127/bool/no-canónicoSTOP. No alterar fixtures para hacer PASS.

228entradas originales son representables exactamente en binary32, incluido gap2^-60 y posiciones2^-62: NO decir que estos INPUTS se pierden sólo por esa conversión. Esto no prueba aritmética de hit32, cobertura, autointersección, distancia, fase o que resultados hi-lo puedan colapsarse. COMPUTED_HILO_COLLAPSE_ALLOWED=false inmutable. No Bpy ejecución ni readback físico: CPU HOST bytes.

Control ABI sintético separado con primitive_id=2^31-1, header+tabla+manifest íntegros: ID no se confunde con un límite de bytes/counts. No modifica primitive0/1/2 retenidas ni gategeométrico anterior. Contabilidad de este productor/parser separada de228inputs originales.

## Costes y seguridad

HOST float64 conversion attempts/struct_float32_cast attempts/integerdecodes se cobran explícitamente por productor/parser. IO/hash/JSON/validación/racionales/oráculos/no-op checks tienen costes reales UNKNOWN_NOT_ZERO; contadores PARCIALES, QAsegundos NO benchmark. No claim native IEEE RN graph ni eficiencia/equivalencia RT. 16M vs1M/salidasdistintas/cruceextrapolado NO trabajoigual.

CPU1hilo/afinidad1/hijo60s; GPU0/Bpy0, no nuevas intersecciones/guard/raíces/replays de numeric antiguo. SinSDK/DrJit/Kaggle/push/merge/publicación/writersajenos. Ventanahistórica cerrada/deadlineinmutable; GPU futuro exige reservaClaudejob+guardfailclosed+deadlinefresco+telemetría/presupuestos completos, noeste buffercomoaval. JEV SECURITYBLOCK fallbackLOCALsinretry/sinavalremoto. Sharedboards/checkpoint locales SINstage; sólo own4 revisados a commit.

## Evidencia verificada

Suite final PASS rc0/timeoutfalse, 0.28375729999970645s QA; stdout244641bytes SHA256cb7bc0b50c092d9af93e93fce50e2cbfc3a7770d1c7c6ea63ffe1b6a3b62aa60.6paquetes/228scalars/1208bytes de INPUTS originales,38STOP conservados,26paquetes negativos/5inputSTOP/6selectors/2APIs simuladas +1controlID31bit sintético separado. Suites previas PASS y control nesting PASS preservados; no inventar FAILnumérico. Oráculo independiente, pins y contabilidad porcaptura se sellan en recibo. Sólo HOST geometryinput; ninguna admisión de hit/phase/native GPU/physical.
