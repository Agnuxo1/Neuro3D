# PRECISION-OBLIQUE-TRACE-ENDPOINT-LENGTH-ENCLOSURE-HOST-001

Nuevo consumidor HOST opt-in, base e5ae544057955c46770e4633639cf95d3df636e0. Padre output hi-lo, recibo SHA b62ddeca67ae4c9c8f37d50db1fbe9d53ca62e1fcae3bf0fc6e7a015aa092bfd/112485 bytes: 351 pins + recibo = 352 dependencias. Sólo cuatro archivos propios nuevos. Fixtures, runners, shaders, contratos y umbrales congelados intactos.

## Entradas y frontera de aceptación

Seis paquetes capturados del transporte HOST, misma escena original S0/S1 y cobertura ALLprimitive, 38 STOP previos antes de calcular. Datos YA calculados, no ejecutar producer/encoder/traza/guard/root antiguos. API run carga hashes y capturas; selector cerrado fija modelo/caso/orden SOURCE/resultSHA/reciboSHA. Helper evaluate usa contexto confiable interno; ningún caller público proporciona una referencia. Un paquete recibido distinto del sellado STOP antes de decode/raíces, aun rehasheado. Verificar header, dos palabras, originales racionales, residuales, radios y unidades.

Se decodifican 84 words por caso, hi y lo preservados separados en descriptores. Centro hi+lo es una suma RACIONAL HOST exacta para intervalos, NO colapso a float en consumidor nativo. Para cada endpoint BU, caja por coordenada [centro-radio,centro+radio]. Radio es descriptor HOST del transporte de ESTA traza, no incertidumbre de una nueva intersección ni cota del backend ALU32. Los otros campos, incluidos cuadrados transmitidos, se verifican; cuadrados originales son contraste, NO inputs de las nuevas normas. Contacto exacto sigue STOP para todos los casos por residuales barycentric: la cota de longitud NO revoca ese STOP.

## Cota matemática nueva

Por segmento A a B: diferencia por eje [Bmin-Amax,Bmax-Amin]. Cuadrado intervalar: mínimo cero si cruza cero, si no mínimo de extremos al cuadrado; máximo de extremos al cuadrado. Sumar tres intervalos BU2. Esto incluye TODOS los radios de ambos extremos y no asume cancelación entre fuentes o segmentos. Puede ser conservador, no es una nueva cota física.

Raíz HOST certificada por enteros, resolución FIJA 96 bits fraccionarios BU. Para q>=0 racional, k=isqrt(floor(q*2^192)); comprobar k²*den <= num*2^192 < (k+1)²*den. Límite inferior k/2^96; superior igual si cuadrado exacto, si no (k+1)/2^96. Para q intervalo, tomar lower de certificado qmin y upper de qmax. Nueva capacidad de certificados: racional interno <=512 bits y q<=2^64; entradas racionales recibidas canónicas <=128 bits, bounds originales no se amplían. No adaptar precisión, truncar negativos, usar sqrt float ni cambiar capacidad para convertir fallo en PASS.

Dos segmentos sumados por SOURCE con intervalo [L1min+L2min,L1max+L2max], anchura BU, endpoints/coverage/SHA. Ninguna fusión de SOURCE. 4 normas/8 certificados enteros por escena; 24 normas/48 certificados en seis casos. Oráculo externo independiente reconstruye extremos originales y comprueba cada cota; controles sintéticos sólo stage intervalar, NO nuevas escenas admitidas ni modificación de radios originales.

## Lo que NO entrega

HOST_length_enclosure_verified sólo certifica matemática de longitudes de dos segmentos DECLARADOS con cajas recibidas. length_accuracy_budget_admitted=false: no nuevo umbral de precisión ni reinterpretación de phasewidth/caps. exact_contact_allowed=false; phase_error_bound=null. Sin λ/referencia/gauge/material/autenticación física nueva, sin native IEEE RN graph, GPU/Bpy/RT/óptica/campo/launch/full visibility. No usar esta cota para epsilon/t_min/bias/conf1 ni sustituir inferencia escena por U/GEMM.

## Pruebas y costes

Pruebas de intervalos firmados/cruce0/caja no binaria/longitud exacta/tiny gap2^-60 BU; corners independientes. Rechazar cambio words/radius/unit/SOURCE/coverage/scene/query/ref/extraPhase/contactPromotion/campos, selector y capacidad raíz. Casos sintéticos explícitos y fallos reales preservados, no barridos viejos ni cargas de relleno.

CPU 1 hilo/afinidad1/hijo<=60s, GPU0. Medir nuevos worddecodes/normas/certificados; hashes/IO/JSON/Fraction/validación/isqrt/oráculo tienen costes completos UNKNOWN_NOT_ZERO. Segundos QA NO benchmark ni motor ganador. RT16M vs1M y salidas distintas/cruce extrapolado NO comparación equivalente.

JEV bloqueado por seguridad: fallback LOCAL explícito sin retry ni aval remoto. Sharedboards/checkpoint locales SIN stage; versionar sólo propios revisados. Sin SDK/DrJit/Kaggle/push/merge/publicación ni escritores ajenos. Deadline histórico cerrado/no editado. GPU futuro sólo job reservado con Claude, guard fail-closed/deadline nuevo verificable/telemetría/presupuesto conservador autorizados; no MLP32768 ni cargas cercanas al límite tras0x9F. Pedir artifacts existentes por ID/path/SHA de backend/guard/ABI/igualtrabajo-costes completos, no repetir cargas.
