# EXP005 — AXIAL-UNIFORM-UNIT-HOST-001

Propietario Codex / capacity_audit. Modelo opt-in axial-uniform-Horner26-declared-angle-HOST-v1.
Base6b05f16b87a4ddbffcec519fae46d161665555c0.
Acuse UNIFORM-POWER-BOX-HOST-001 SHAa99e3fcf935adf47b05bd1416cb5d73db1b92c1ed568c52bde1592308e257983.
JEV bloqueado por seguridad: fallback LOCAL, no reintento ni aval remoto.

## Dominio y grafo explícitos

Intervalo racional declarado [lo,hi] dentro [-1,1] rad; extremos canónicos <=256 bits.
Es dominio de ARGUMENTOS REPRESENTADOS, no enclosure automático de la imagen de una escena.
Modelo hipotético RN-even binary64 con subnormales graduales, no FMA.
El runner antiguo rechaza subnormales seleccionados: este teorema NO afirma que lo ejecute en todo el intervalo.
Siete coeficientes Taylor por cos/sin, palabras bin64 exactamente retenidas y vinculadas por SHA.
No casts nuevos ni llamadas a polinomios/productores anteriores.

X=max(|lo|,|hi|), m=0 si cruza0, en otro caso min(|lo|,|hi|).
Cuadrado exacto en [m^2,X^2]; Ez=E(X^2); z redondeado en [max(0,m^2-Ez),X^2+Ez].
E(M)=2^-53*M+2^-1075, E(0)=0, sólo argumentos finitos y rangos<=MAX_FINITE.
Producto intervalar por cuatro productos de extremos; suma por extremos; expansión +/-E(maxabs).
Horner26: cuadrado común, 12nodos cos,12nodos sin y mul sin.final.
Se evita interpretar x*x como producto independiente cuando x cruza cero.

## Error uniforme, cargos separados

I es cota de valor absoluto del polinomio IDEAL previo; Z=maxabs de z redondeado.
En cada paso hnew=RN(RN(h*z)+c_j), con coeficiente ideal C_j:
ecnew=Z*ec+|c_j-C_j|,
esnew=Z*es+I*Ez,
ernew=Z*er+E_mul+E_add,
Inew=I*X^2+|C_j|.
Inicial ec=|c6-C6|, es=er=0, I=|C6|.
Al finalizar sin, multiplicar cargos por X y añadir E_final al cargo RN; I*=X.
Derivación: hz-Hx^2 = (h-H)z + H(z-x^2), desigualdad triangular.
Resto Taylor uniforme: X^14/14! cos, X^15/15! sin para |x|<=1.
Unidad L1 a cos/sin IDEAL del MISMO argumento representado: suma de cargos y restos.
Cota angular adicional b/(1-b) si b<1/2; no sustituye el transporte/selector/gauge hacia ORIGINAL.

## Integración y límites

Cinco fuentes elegibles de 17casos/19fuentes: envolvente de CUATRO argumentos de esquina codificados retenidos.
No puede darse por probada la imagen interior de escena a partir de esa envolvente.
14STOP de fuente unit anteriores se preservan, incluyendo other de two_sources; no suma parcial.
Cupo fase ORIGINAL intacto; comparación del cargo polinómico SOLO es condición necesaria, no aceptación completa.
Tres cargos no caben: negative/positive/s de two_sources tienen intervalo [0,0] y cupo fase cero.
La cota RN genérica es positiva para operaciones exactas de ese singleton; NO es un nuevo fallo numérico de escena.
Los otros dos intervalos caben. No ampliar cupos ni ocultar false; un futuro refinamiento exacto de singleton requiere prueba separada.
Upstream quarter bound de esquina se etiqueta NO uniforme; compuesto ORIGINAL uniforme=None; statusSTOP.
Fuente/producto/reflexión/reducción/potencia/cierre restante/backend/GPU/auth siguen sin promoción.
API escena sólo nombres/modelo; primitiva sólo intervalo declarado/modelo y coeffs de recibos; no profile/cupoclaim caller.

## Verificación y preservación

Seis tests y oráculo stdlib independiente sin imports de producción.
520 contrastes de pertenencia de nodos YA retenidos, leyendo delta/word: cero reejecución de sus RN.
Cinco intervalos ligados a INPUT y seis controles de dominio; 286 nodos analíticos, no 286 evaluaciones RN.
Prueba por recurrencias y cotas intervalares, no muestreo de todo el continuo.
Primer test asumía erróneamente que todos los cargos uniformes cabían: fallo conservado, expectativa corregida a bound<=MISMOcap.
NO modificación del checker ni del umbral para hacerlo PASS.
Primer stdout4MB y segundo compacto512KB excedieron transporte; SHA/metadata/stderr preservados, stdout completo NO recuperado.
Tercer export guarda hashes exactos de trazas y racionales grandes; oráculo reconstruye y compara esos hashes.
Captura final íntegra comprimida en reporte; dos reparaciones de export documentadas, no repetición de productores.
No falsificar conservación completa de capturas truncadas; no afirmar primer-intento PASS.

CPU1hilo/hijo60s, sin GPU/Blender/RT ni instalación SDK/DrJit. Tiempos checker no costes completos/eficiencia.
Claude ACKID/reportSHA; sólo artifacts YA existentes enclosure/sourceuniform/backend/guard matching MISMO INPUT/scene/ABI/gauges e igualtrabajo/salidas/costes completos.
Próxima propia: enclosure explícito de argumento desde selector/transporte; después fuente compleja y reductionuniform.
0337 histórico cerrado/deadline intacto; futuras cargas sólo reserva exclusiva Claude, telemetría, guard failclosed y NUEVO deadline.
Frozen/runners/shaders/fixtures/cupos intactos. Boards locales SINstage, sólo cinco nuevos propios versionados; sin publicación/push/merge/Kaggle.
