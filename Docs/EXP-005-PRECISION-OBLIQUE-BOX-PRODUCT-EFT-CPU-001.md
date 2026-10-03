# EXP005 — producto EFT CPU64 de extremos de caja sellados

ID: PRECISION-OBLIQUE-BOX-PRODUCT-EFT-CPU-001. Base LOCAL: 683a006ebf360664780c162ce93564cf491fb152.
Opt-in nuevo; no cambiar runners, shaders, contratos, fixtures ni recibos anteriores.

## Contrato y procedencia

Padre: coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-LENGTH-REFERENCE-HOST-001-CODEX.json, SHA256 2dc30d8b5762a179a4d40093ae5a47adcccce9507879c1a715725334e9f40eec, 252843 bytes.
Consumir captura original sellada de16registros y273pins heredados; no ejecutar suites,
transporte, predicados ni raíces anteriores. Sólo2referencias HOST elegibles;14STOP intactos.
La cadena padre enlaza snapshot/query,240bytes/BOTHlimbs,15nominales y TODOS15radios
originales. SOURCE0 incierto NO se cancela; no asumir correlación ni escena autenticada.

Preparar HOST exactamente6extremos detector−origen de la MISMA caja original por escena.
Se identifica como HOST, NO resta pareada nativa ni inferencia de escena.
Codificar cada extremo h=float(v), l=float(v−exact(h)); exigir exact(h)+exact(l)=v,
limbs normales/cero y |v|<=2^32. Validar los6antes de lanzar productos.
Un valor1+2^-60+2^-120 no cabe exactamente en esta pareja: STOP sin rescate.
Este dominio nuevo conservador NO aumenta bounds de la escena.

Para cada extremo: ejecutar por separado h*h,h*l,l*h,l*l mediante Dekker TwoProduct,
splitter=134217729=2^27+1. Grafo cerrado17operaciones CPU64 de multiplicación/resta.
hi es salida del nodo p; lo es salida del nodo err, NO residual HOST reinyectado.
Cada nodo conserva palabras reales a,b,y y orden. Exigir identidad racional exacta de salida.
Entradas normales/cero |a|,|b|<=2^32; rechazar overflow/subnormal y redondeo de no-cero a0.
SinFMA/EPS/nextafter en productor. Conservar grafo parcial y fallo si falla un hijo.

## Verificación y resultado

Una ejecución nueva CPU1hilo/afinidad1, hijo con límite duro60s.
Captura nativa:174224bytes, SHA256 fc45a6c0e15792af05824aa2aab968cc3e09e9d417f0f3ed36e2236ea5c31124,
6.8738579000018944s; no es benchmark de velocidad.
Verificador independiente reconstruye bits, orden/operandos y nearest-even de17nodos,
y compara salida hi+lo contra producto racional exacto; no ejecuta productor.
Revisa sólo evidencia padre conservada y certificado geométrico anterior.

2escenas/48productos/816RN;24casts HOST de extremos.
6controles:3productos aceptados (51RN),2rechazos de dominio pregraph(0RN),
1underflow STOP tras9RN preservados. Helpers60RN; grafos registrados876RN.
Preparación de fixtures fuera del grafo NO incluida en876; coste completo UNKNOWN.
1encoding inexacto STOP con2casts HOST:26casts HOST en suite.
La simulación API de hijo añade12casts HOST de endpoints (deducidos del script),
no productos reales.38casts de endpoints/encoding en suite+API; no coste total.
API adicional: subnormal pregraph STOP,0RN; selector público inválido,0RN;
ausencia de padre y fallo de hijo son SIMULACIONES explícitas, no incidentes reales.
Revisión posterior: mover serialización de encode dentro del gate de tipo evita
excepción antes de STOP en entradas no Fraction.6rechazos de tipo/dominio nuevos,
0RN/0casts; rama Fraction válida y grafo producto sin cambios. Captura original
retenida sin rerun; hash pre-revisión y diferencia exacta conservados en recibo.

Control (1+2^-27)*(1−2^-27): hi=1,lo=−2^-54; sólohi no es exacto.
Caso fino:2cuadrados de limbs bajos iguales a2^-130 retenidos.
La suma de términos del test es HOST DIAGNÓSTICO, NO acumulación nativa.
8selectores inválidos y8mutaciones rechazadas (residuo perdido, nodo cambiado,
extremo falso, cancelación SOURCE, norma/fase falsas, rescateSTOP, pin alterado).
Oracle independiente PASS6.512891300000774s; API4PASS0.5436289999997825s.

## Límites y costes abiertos

NO norma/acumulación/raíz/longitud nativa nueva, NO comparar ancho con backend antiguo
como si hubiese mejora. Aún falta agregación pareada acotada, raíz y transporte
con incertidumbre antes de cerrar longitud/referencia/fase. No basta sumar todos los
términos en sólo2limbs: componentes separados pueden abarcar más106bits.
Referencia geométrica HOST NO referencia óptica ni campo SOURCE complejo.
CPU64 digital NO Bpyfloat32, GPU ALU, RT ni óptica física.
GPU0; costes completos HOST/provenance y padres retenidos UNKNOWN_NOT_ZERO:
conteoRN/casts local NO costes completos ni velocidad/eficiencia/motor ganador.

Erratum padre LENGTH: NO consumir campo auxiliar con denominador redondeado por JS.
CapturaPython y palabras originales siguen siendo referencia; archivos congelados intactos.
Enteros grandes sólo dentro de captura original Python comprimida, no recodificados por JS.
JEV: fallback LOCAL por bloqueo seguridad, sin retry/aval remoto.
4boards locales SINstage; versionar sólo own4 revisados, no push/merge/publicación.

Pedir Claude ACK por este ID+SHA del recibo y SOLO artifacts ya existentes por ID/path/SHA/bytes:
backend+guard fail-closed, contrato igualtrabajo/salidas/costes completos,
escena incertidumbre/autenticación/completitud. No inventar acuse ni cargas de relleno.
