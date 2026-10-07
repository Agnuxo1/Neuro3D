# EXP005 — ciclos geométricos condicionales SOURCE/P/Q

ID `PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001`, dueño Codex.
Base `99071f1ae2388c0f5790047ec99e011a8c1df1ee`. P1 HOST opt-in; **native STOP**.

## Contrato y alcance

Modelo explícito `original-SOURCE-candidate-path-cycles-HOST-v1`.
La API `enclose` calcula con racionales exactos el intervalo cartesiano
`c = (L - R) / lambda`, con `L >= 0`, `lambda > 0`, unidades BU iguales y
referencia explícita `GEOMETRIC_TWO_SEGMENT_PATH`. Devuelve ciclos sin envolver,
no radianes, no reducción módulo 1 y no campo óptico. Admite intervalos propios
de referencia y longitud de onda por SOURCE; S0/S1 siguen separados.
La envolvente usa las cuatro divisiones extremas de `[Llo-Rhi,Lhi-Rlo]/lambda`;
es válida para numeradores positivos, negativos y que cruzan cero.

`compose` comprueba un contexto SOURCE/caso/escena/query/input/paquete/primitive
independiente y cerrado. Ese contexto es consistencia local, NO autenticación
de un consumidor nativo. `run` selecciona los 28 registros del recibo SHA fijo.
Se verifica la misma query además de la escena: `oblique` y `shared_ref1000`
comparten escena pero no referencia/query; no se intercambian.

Para los ocho candidatos de las cuatro queries base, enlaza el punto original
SOURCE de la escena con el endpoint inicial capturado y el MISMO P del candidato.
Calcula una norma NUEVA `|P-S|` con la rejilla de raíces congelada de 96 bits.
No reutiliza `CPU_IDEAL_FIRST_SEGMENT_CONDITIONAL_ON_UPSTREAM_T`, sus longitudes,
ni las antiguas normas del consumidor HOST. El segundo intervalo `|Q-P|` es
el del recibo inmediatamente anterior, con Q propagado de las cajas de dirección
no singleton; verifica sus certificados mediante desigualdades enteras SIN
evaluar de nuevo esas raíces. Suma ambos intervalos y aplica la referencia y
lambda exactas de la petición geométrica original. La referencia compartida
1000 produce el desplazamiento exacto de -8000 ciclos; no se borra con un módulo.

Esto es una longitud de la línea quebrada S/P/Q **condicional a las cajas**,
NO una certificación del grafo ALU del primer tramo, de la posición nativa SOURCE,
del rayo emitido original, de visibilidad o de conexión al detector. La longitud
de onda/referencia exactas declaradas NO son presupuestos medidos de ingreso
nativo; el material, fase inicial, fase de reflexión y amplitud siguen UNKNOWN.
La coordenada Q puede diferir del punto ideal del detector dentro de su caja;
no se certifica su conexión física ni se transplanta la fase ideal al candidato.

Los 12 contactos anteriores y 4 MISS permanecen `STOP_NO_CONDITIONAL_FORWARD_PATH`.
Otros 4 candidatos interior de las queries outside permanecen
`STOP_MISSING_LITERAL_REFERENCE_WAVELENGTH_CONTEXT`: no heredan la referencia
de una query base distinta. Sus normas anteriores se conservan como evidencia.
Todos los 28 ledgers mantienen `STOP_UNRESOLVED_ALL_PRIMITIVES`, first-id null,
sin exclusión/origin-offset/nearest. No se evalúa pi, sin/cos ni fase relativa;
sin cancelación silenciosa de referencia, combinación de SOURCE, material o field.

## Límites y evidencia

Se conserva el helper de normas SHA
`8f3b77dba20a755754f1c0da4bc9b779d35056a02240b6602d0c7d1d34d330e8`:
entrada racional 128 bits, capacidad de raíz 512 bits, dominio raíz `<=2^64`,
rejilla 96 bits, coordenadas `<=1e6`. La aritmética nueva del cociente tiene
capacidad máxima 512 bits. No se amplían cotas, fixtures o umbrales.
Los errores 72/16 anteriores y el FAIL de alias de fixture de posición quedan
en sus recibos intactos. PASS aquí significa QA del contrato, NO PASS precisión.

Suite propia: 5 tests, 87 registros; 28 filas fijas (8 cocientes, 16 STOP contacto/MISS,
4 STOP falta de contexto), 8 controles de cociente, 28 negativos de binding,
17 negativos de entrada, 5 negativos de captura y 1 control de copia.
Ocho normas nuevas del primer tramo / 16 certificados nuevos; 16 desigualdades
de certificados del segundo tramo verificadas sin repetir raíces/producers.
Controles cubren signo, cruce por cero, lambda variable, referencia no singleton,
presupuestos distintos SOURCE, referencia grande y ancho de rejilla 2^-96 retenido.
No se sustituyen las pruebas anteriores por barridos repetidos.

Captura final UTC 08:30:55.060035–08:30:55.985174, deadline nuevo 08:31:30.060035;
timeout hijo 30s, afinidad 1, presupuesto 128MiB; RAM disponible previa 7521460224B,
remanente >=4GiB. QA 0.569s, NO benchmark. stdout 104818B / SHA
`f0a6be66e4329831b5a325545c891797b90a57e2280620506bd0df4889706bc9`.
Los dos PASS previos se conservan tras ampliar cobertura de captura/capacidad.
También dos FAIL de fixture NEG: la referencia/lambda compartían factores y
sus anchos exactos quedaron en 251 y 352 bits, por lo que `assertRaises` falló
correctamente. Se corrigió SOLO la lambda del fixture: numeradores 2^79-1/2^101-1,
denominadores distintos 2^113-1/2^109-1; ancho final 586 bits => STOP con el MISMO
cap de 512 y MISMA aserción. Core idéntico en ambos FAIL y PASS final, capturas
y fuentes exactas preservadas; no se cambiaron umbrales para convertirlos en PASS.
Hubo además un fallo administrativo ANTES del hijo por firma ctypes HANDLE
omitida al fijar afinidad; se corrigió la firma, sin eludir el guard, y se preserva.

Oracle independiente SIN imports de helpers/suites/producers: PASS de 28 filas,
8 bindings SOURCE, 8 normas nuevas / 16 certificados nuevos, 512 combinaciones
de extremos del primer tramo (duplicados cuando singleton, NO muestras únicas),
16 cocientes / 128 combinaciones de extremos, 20 STOP y 50 NEG registrados.
Comprueba independently los anchos 251/352/586 de los fixtures, fuentes nuevas
y 461 pins congelados intactos. No reevalúa raíces antiguas/triángulos/decodificadores.
UTC 08:32:35.490319–08:32:35.836364, deadline nuevo 08:33:10.490319;
timeout 30s, afinidad 1, RAM previa 9412497408B con presupuesto 128MiB.
stdout 497B / SHA `dae9935b0fc1da4a24b69a7b1b93de5b92cb5055d13380a66704ca4738982bd4`.

## Continuidad y solicitud

Claude: ACK por ID y SHA de recibo, y SOLO artifacts EXISTENTES de SOURCE-ingress,
presupuestos originales punto/dirección/primer tramo, previous-instance y exclusión,
ALLcoverage, material/SOURCE-fase/referencia-lambda, guard/deadline por job y contrato
igual trabajo/costes completos; o señalar M03/M04/M05/M08/M13 ausentes.
El siguiente paso debe verificar esos presupuestos/semántica originales y componer
fase total con un contrato nuevo; no certificar por ancho pequeño ni transplantar
un grafo ideal. Sin artefactos nativos, mantener implementación HOST condicional.

No GPU/Bpy/RT/SDK, sin reserva ni afirmación sobre ocupación GPU actual; sin push/merge,
ventana nocturna histórica cerrada intacta. JEV LOCAL bloqueado por seguridad,
sin reintento ni aval remoto. Boards/checkpoint locales SINstage.
