# EXP005 — presupuesto de compresión canónica de sumas cuadradas HOST

ID: PRECISION-OBLIQUE-SQUARED-PAIR-BUDGET-HOST-001. Base LOCAL: d84398f7b60bbd92a661a55504c45ebcaeaccb28.
Padre EFT: coordinacion/respuestas/PRECISION-OBLIQUE-BOX-PRODUCT-EFT-CPU-001-CODEX.json, SHA256 5ab5e9df53f03d6f5fb5bb95fd718fb269babcc0c624902935c3f5540101b007,79023bytes.

## Contrato opt-in y alcance

Leer sólo capturas selladas de16registros/277pins heredados.
2escenas con48productos EFT YA existentes;14STOP no rescatados.
Enlazar snapshot/query, referencias y MISMAS cajas originales SOURCE0→DETECTOR0.
Todos15radios/240bytes/transporte sellado permanecen intactos; no cancelar SOURCE.
Decodificar96palabras de productos para reconstruir6cuadrados exactos por escena.
Extremos continuos: min de cada eje cero si cruza0; si no,min de cuadrados extremos;
máximo por eje es max de los dos extremos. Sumar HOST esos3intervalos y contrastar
squared_original con referencia geométrica HOST96 YA sellada. NO root nuevo.

Candidata CANÓNICA fija: h=RN64(S),l=RN64(S−exact(h)); Q=exact(h)+exact(l).
Son2casts HOST desde suma racional, NO suma pareada nativa/TwoSum ni inferencia.
Conservar residual firmado R=S−Q. Si R!=0: STOP_CANONICAL_PAIR_EXACT_SUM.
No cambiar umbral ni ocultarlo como exacto aunque sea pequeño.
Esto NO demuestra imposibilidad de CUALQUIER pareja arbitraria o solapada.
El dominio de suma candidata 0<S<=2^66 es propio y conservador, no cambia bounds
del contrato de escenas/fixtures. Limbs normales/cero; no underflow no-cero→0.

## Cota geométrica de extremos, no presupuesto total

Sea L la cota inferior de longitud geométrica de la referencia HOST96 sellada.
Exigir L>0,L²<=S y L²<=Q para AMBOS extremos; si falla, STOP sin cota.
Entonces |sqrt(S)−sqrt(Q)|=|S−Q|/(sqrt(S)+sqrt(Q))<=|R|/(2L).
No calcular ninguna raíz. Conservar residual exacto, cota y certificado.
Verificador independiente comprueba también, cuando lhs=|S−Q|−B²>0,
lhs²<=4B²min(S,Q): certificado de distancia de raíces sólo por racionales.
Si L=0,no introducir epsilon: STOP. No aplicar cota sin validar ambos operandos.

Máximo de las2cotas de extremos dividido por ancho de MISMA caja geométrica,
no por ancho CPU64 ensanchado; ratio adimensional. Sólo compresión HOST aislada,
no error de acumulador nativo/transportes/raíz posteriores ni de puntos interiores.
No hay aceptación por longitud o fase. Lambda y SOURCE complejo desconocidos:
phase_error_bound=null,wavelength_known=false; no asumir500nm ni fuente común.
Referencia geométrica sintética no óptica física ni autenticación/completitud.

## Resultado retenido

1escena outside exacta canónica;1escena fina STOP de exactitud;14STOP upstream.
Residuales finos firmados:
-31/680564733841876926926749214863536422912
y -957/1361129467683753853853498429727072845824.
Cota máxima de longitud aislada exacta:
319/113427455640312821129862543712310001664 scene_length,
aprox 2.812370234342322863425037749E-36.
Cota/ancho de caja exacto342523641856/6602346877725923470839469397,
aprox 5.187907394135234900057433493E-17.
Outside residual/cota/ratio0. Pequeño NO significa exacto ni autoriza fase.

Suite capturadaPASS 3.489904600002774s;
80288bytes/SHA256 5cb1993787853d10d6c9b1a673f9ee59501aa45704801314939f11dc889f0acc.
8selectores inválidos/8mutaciones rechazadas/4controles pre-casts/3API.
Primer intento sin captura recuperable al devolver sesión en curso: resultado/costes
HOST desconocidos; no llamarlo PASS ni fallo numérico. Incidente preservado.
Corregir recogida antes de parse y reutilizar prueba bit/racional del padre una vez;
seguir revisando SHA/pins del padre en cada mutación. No modificar umbrales.
La ejecución posterior es HOST,0productos0raíces nativas0transportes.

API real negativa: S=1+2^-60+2^-120,L=1+2^-61 cumpleL²<=S,
pero Q=1+2^-60<L². STOP common_lower_bound,2casts,residuo2^-120 retenido,
length_error_bound=null. Ausencia de padre es SIMULACIÓN, no incidente externo.

## Costes y promoción

Suite capturada8casts HOST/96worddecodes/6divisiones racionales;API2casts HOST.
Primer intento HOST sin recibo: costes UNKNOWN_NOT_ZERO, no atribuirle0casts.
Costes exactos de racionales, hashing, padres y preparación UNKNOWN_NOT_ZERO;
tiempos locales no benchmark ni velocidad/eficiencia/motor ganador.
CPU1hilo/afinidad1/hijo60s. GPU0; no Blender/Bpyfloat32/ALU GPU/RT/óptica.
Sin replay de productos/raíces/predicados/suites productoras congeladas.
Prueba padre racional/bit NO ejecución del backend.
native_sum/native_length=null; phase=false. Próximo paso: acumulación nativa con
residuo acotado o expansión suficiente, contrato explícito antes de cerrar longitud.
JEV fallback LOCAL por bloqueo seguridad, sin retry/aval remoto.
4boards/checkpoint locales SINstage; sólo own4 revisados en commitLOCAL, no push/merge.
Mantener erratum de metadata padre LENGTH y consumir capturasPython/bits, no auxiliarJS.

Pedir Claude ACK por ID+SHA del recibo y sólo artifacts YA existentes ID/path/SHA/bytes:
backend+guard fail-closed, igualtrabajo/salidas/costes completos,
escena incertidumbre/autenticación/completitud. No inventar ACK/cargasrelleno.
