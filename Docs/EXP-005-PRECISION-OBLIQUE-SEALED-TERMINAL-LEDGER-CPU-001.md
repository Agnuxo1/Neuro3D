# PRECISION-OBLIQUE-SEALED-TERMINAL-LEDGER-CPU-001

Estado: contrato nuevo opt-in CPU. Primera suite PASS provisional/incompleta en tipado del token capturado. Prueba dirigida REAL falló rc1: helper interno con paquete alterado y reseñado permitió True==1 en token result. API pública pinned capture intacta rechaza alteración por SHA; fallo NO equivale a bypass del recibo público. Corregida identidad estricta por digest serializado de token y selector guard; regresión permanente. Sin cambiar geometría, epsilon, límites, umbrales o fixtures. Recibo/oráculo/commit pendientes.
Base fbb5ac69d2fbb4242e08e6863a1e39176e383bed. Padre guard coordinacion/respuestas/PRECISION-OBLIQUE-LAUNCH-CONTACT-GUARD-CPU-001-CODEX.json, SHA256 9f8a54dc298e7765ff22d8485de2be9ff213948b83674e99b74ede53ca9d7d88, 121289 bytes. Congelados anteriores intactos.

## Objeto y límite

Consumir todas las filas selladas del guard para el segmento terminal 1, por separado para S0 y S1, de las seis escenas CPU declaradas retenidas. No volver a calcular intersecciones, guard, raíces, hi-lo, fase ni kernels anteriores. Conservar los 38 STOP upstream; este consumidor no rescata la admisión fallida de longitud o fase de otros modelos SOURCE0/DETECTOR0. BU y parámetro t son objetos distintos.

La API pública run(case, selector) carga recibos sellados, verifica 335 pins y devuelve decisión conjunta sólo si AMBAS fuentes pasan sus ledgers completos. El selector cerrado incluye escena/query/registro/padre/visibilidad por SHA, fuentes literales S0,S1 y segmento entero1. Las funciones packet/evaluate/consume son internas: reciben contexto confiable derivado de esas capturas; digest no constituye autenticación física ni permiso para aceptar datos caller-controlled. Un uso runtime distinto necesita contrato/productor/autenticación propios.

## Contrato de aceptación inmutable

1. MISMA escena/query/path, salida continua original, detector y fuentes/orden originales.
2. Credencial version1/segment1/primitive anterior/punto/barycentric racionales estrictamente tipados; bool no es int. Coordenadas BU<=10^6, racionales canónicos<=128bits; lista de triángulos<=64. Estos límites son los del NUEVO consumidor, no aumento de bounds anteriores.
3. EXACTAMENTE una fila por cada primitive original, sin omisiones/duplicados. SHA del paquete incluye fila/request/result/triángulos/token; un cambio de payload pierde el sello.
4. Sólo la primitive previa, en t=0, punto y barycentric originales puede excluirse. No epsilon, t_min, bias de origen, ni skip por objeto.
5. Todo contacto KEEP se mantiene. Punto sobre segmento y sobre primitive por combinación barycentric exacta. No reejecución de intersección ni afirmación nueva de ausencia geométrica: NO_CONTACT se consume de la captura sellada.
6. Un STOP/coplanar no se excluye; bloquea decisión. Target debe ser contacto único con primitive detector, t=1 y punto terminal exacto. Cualquier otro contacto cerrado 0<=t<=1, incluso vecino t=0 o empate t=1 del mismo objeto, bloquea.
7. Una fuente ausente/incompatible bloquea el resultado conjunto, sin combinar campos, amplitudes o fases.

Resultado positivo CPU_DECLARED_BOTH_SOURCE_TERMINAL_CLEAR_ONLY significa sólo que estos DOS segmentos terminales declarados, según sus capturas completas, tienen detector único tras excluir el autocontacto puntual. NO full-path visibility, hitcoverage nativa, escena física autenticada, fase válida, motor GPU/RT u óptica física. phase_error_bound=null y esas admisiones=false. No U/GEMM como reemplazo silencioso de inferencia desde escena.

## Pruebas y controles

Se consumen 28 resultados guard anteriores sin ejecutarlo. 12 SOURCE packets sobre6 casos originales;38 STOP intactos. Oráculo independiente toma el conjunto de contactos restantes, sin ranking, y exige que sea exactamente el target1.
Controles de decisión NUEVOS usando resultados sintéticos YA capturados por LC: cara vecina mismoobjeto t0, contacto t2^-60, previous-ID positivo y coplanar. Los escenarios de prueba completos se etiquetan NEW_SYNTHETIC_DECISION_CONTROL_ONLY; no son modificación ni promoción de escena original. Para positivo con ID previo, punto no pertenece a primitive original: STOP_INPUT, no sustituir triángulo ni identidad de lanzamiento. Coplanar alimenta el verdict no resuelto ya capturado, no recertifica su segmento alternativo.
Empate terminal distinct primitive202: NUEVO control de decisión por copia explícita del contacto/triángulo target, no nueva intersección. Booleanos, racional no canónico, target omitido, SOURCE replay, cambio de sello y cobertura cerrada se prueban por mutaciones sólo en memoria.

La integridad SHA de recibos/capturas/pins fija evidencia, no autentica escena física. NO_CONTACT es trusted captured verdict; alterar un payload y reseñalarlo externamente no da derecho a invocar helpers internos como API válida.

## Costes y seguridad

CPU propia un hilo/afinidad1; cada hijo timeout duro60s. Nuevas intersecciones/guard/raíces/RN/replays antiguos=0; verificación racional barycentric, hash, JSON, IO y validación/capturas/oráculos tienen costes reales UNKNOWN_NOT_ZERO. ledger_rows_audited es contador PARCIAL, no tiempo ni coste completo del motor; segundos QA no benchmark. No comparar RT16M vs1M ni cruce extrapolado como trabajo equivalente.
Sin GPU/Blender/SDK/DrJit/Kaggle/push/merge/publicación/writers ajenos; JEV SECURITYBLOCK fallback local explícito sin aval/retry. Histórico deadline cerrado/inmutable. Sharedboards y checkpoint locales SINstage; own4 revisados antes commit.

## Resultado verificado CPU

Suite final PASS rc0/timeoutfalse, 0.28607999999803724s QA, stdout 424922bytes SHA256 7bd92ef653ce05b4436724771a4a792c581047f12295c54d55e54c147ba71cdd. 44registros:6escenas/12SOURCE packets/28filas originales;38STOP preservados.17controles de decisión sintéticos,24negativos de paquete,6selectores,1S1 ausente y2dependencias simuladas. Error dirigido REAL rc1 stdoutSHA6f0a118579bf7c0c532e5c8a604cdf772bc5613bd52d6fd7edd4b769973bf26d conservado con fuentes iniciales como datos (no reejecutadas). Dos suites PASS anteriores preservadas como provisionales/incompletas; final también liga record_sha256 original, sin autodigest de registro suministrado. Costes de todas las suites/fallo se reportan por captura como ledger_rows_audited PARCIAL; totales completos UNKNOWN_NOT_ZERO. Oráculo independiente PASS stdoutSHA3922c1a63be356f93a4f9d6a186df83da6c4b698a52feff76424df5b95faf6d1, 0.2611981000009109s QA:339pins,12SOURCE/28filas/38STOP,9BLOCKED/4UNRESOLVED/4INPUT en17controles. Regresión token antesfilas, recordSHA original ligado. Coste PARCIAL242ledger filas auditadas entre3suites80cadauna+2fallo dirigido; hash/IO/validación/racionales/oráculo UNKNOWN_NOT_ZERO. No equivale a promoción física/fase/nativa.
