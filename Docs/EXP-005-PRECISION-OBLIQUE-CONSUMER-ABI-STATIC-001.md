# PRECISION-OBLIQUE-CONSUMER-ABI-STATIC-001

Auditoría opt-in ESTÁTICA P1 de Codex capacity_audit/EXP005. Base 87abe3af193f0b6ffcbb827b294f3dbf39b5dd26.
Padre coordinacion/respuestas/PRECISION-OBLIQUE-SCALAR32-CONSUMER-GATE-CPU-001-CODEX.json, SHA256 1f14029ecb7520b7ed3597c44828b29c6608a8562285a917855d0e99d5f111b9, 214787 bytes.
No ejecución de fuentes ajenas, Blender/Bpy, shaders, GPU, RT u óptica física. Fallback LOCAL sin aval JEV (bloqueado; sin reintento).

## Contrato cerrado

Sólo 16 registros sellados del gate escalar, mismos snapshots/query, SOURCE0/DETECTOR0, referencias y cajas originales con incertidumbre de fuente intacta. Selector fija backend, política, registro y hashes del padre, wire, referencia, original, snapshot, query y fuentes. Falta/drift rechaza antes de decodificar. Los 14 STOP heredados y la pérdida escalar en las otras dos escenas no se rescatan.

| Ruta leída | Entrada esperada | Operación expresada por código | Gate retenido |
| --- | --- | --- | --- |
| Frontier | Dos texturas float32; no buffer raw de raíz conectado | Convertir cada componente a double y sumar | STOP adaptador/genealogía de escena |
| Probe de fase | Un escalar binary64 por longitud (8 bytes), otro por wavelength | packDouble2x32, NO suma hi32+lo32 | STOP significado de bits |
| Ingress axial | 3 parejas binary64 de 16 bytes más header; expected separado | Copia RAW, NO longitud/fase | STOP ancho/trabajo |
| Guard oblicuo | Header + 2 parejas binary64: 48 bytes in / 32 out | Candidato diferencia EFT, NO longitud/fase | STOP ancho/operación |

Los 8 bytes de nuestro paquete son dos float32 independientes, no un double ni una pareja binary64. Igual número de bytes NO equivale a igual significado.
El host split_double recibe un escalar binary64 y recalcula lo=RN32(value-hi); no recibe directamente nuestra pareja retenida. Se leen AST y líneas de split_double/texture_data/native_shader/dispatch/pack_paths, sin ejecutarlos.
El launcher observado usa por defecto exp005_blender_fields.glsl, NO frontier. No se presume conexión launcher-frontier ni ROOT-scene. El frontier expresa suma double; la pérdida RN64 ya capturada sólo se aplica CONDICIONALMENTE si se ligaran los mismos operandos. No prueba GPU ni consumo de longitud.

## Evidencia verificable

Seis fuentes congeladas selladas por SHA/bytes. Anclas con líneas/texto y cinco funciones Python con SHA de AST; el test reconstruye evidencia desde las fuentes sin importarlas.
Cuatro paquetes de las dos escenas se reinterpretan en CPU como binary64; oráculo independiente IEEE bits/racional verifica el resultado exacto y la desigualdad frente hi32+lo32 exacto. No suma/cast/producto/raíz flotante nueva. La raíz/referencia, transporte y proyección anteriores se reutilizan de capturas, sin barridos.
Paquetes finos: 0000003e0000009f y 0000003e0000001f. Su alias binary64 NO es 1/8. Exterior: 041e004067654225 y e7610040911963a5; también desigual.
Los signos negativos son sólo diagnóstico del alias hipotético; ningún código de status shader fue ejecutado o observado. Wavelength desconocida, fase/cota de fase y longitud nativa null; no promover.

Suite PASS 11.61308519999875s, captura 96372 bytes, SHA256 84dd76e4c30e5d9570ac54f7ce1715d52581cf4a8b75d53ad658b3df4e1642fa.
2 escenas elegibles, 4 alias desiguales, 14 STOP, 0 admitidas; 8 selectores y 8 mutaciones rechazados.
Costes NUEVOS: 4 llamadas CPU de byte decode / 4 escalares; 0 RN64/RN32, productos, sqrt o replay numérico. Oráculos racionales/AST/IO tienen costes reales; costes completos UNKNOWN_NOT_ZERO. CPU 1 hilo/afinidad1/hijo<=60s; tiempos QA NO benchmark equivalente.

Fallo inicial preservado: ancla propia con espacios length < 0.0lf no encontrada; corregida a length<0.0lf, sin modificar shader, umbral o cálculo. Captura falla con 0 stdout/0 decodes; fuente inicial íntegra en recibo.
Un intento de lanzar oráculo con base64 demasiado grande no inició hijo (CreateProcess206); evidencia pasa a recibo propio, sin shell escritor ni ejecución numérica extra.

## Siguiente evidencia solicitada

Claude: ACK por ID y SHA del recibo, y sólo artifacts YA existentes por ID/path/SHA/bytes de backend, guard fail-closed, adaptador REAL ligado a escena/pareja, igual trabajo/salidas y costes completos. No cargas de relleno.
GPU sigue sin admitir hasta reserva exclusiva por job, deadline nuevo verificable y todas las comprobaciones exigidas. Ventana histórica cerrada e intacta; sin instalaciones, push/publicación/merge. Fixtures/runners/shaders/contratos congelados intactos. Tableros/checkpoint locales SINstage.

## Revisión independiente final

Oráculo PASS 11.885589400000754s, captura 4335bytes/SHA256 f39e1d5c09e1eb43fce11d7c6ba92f79f48223e179f9b0599eaa8d4057dccc4e. Revalida el padre por bits/racionales sin repetir sus sumas/casts. API pública: selector inválido, padre ausente SIMULADO y drift de fuente SIMULADO rechazados con 0 byte decodes; archivos intactos. Ocho mutaciones vuelven a rechazarse sin nuevos decodes.
304 pins heredados incluyendo recibo padre/seisfuentes (algunas ya heredadas); añadir sólo tres fuentes propias, sin autorreferencia del recibo. Fuente inicial y fallo de ancla preservados y equivalencia después de corregir sólo espacios demostrada. COSTES TOTAL NUEVOS = cuatro byte decodes CPU, no se duplican al revalidar capturas. Sin admisión de motor.
