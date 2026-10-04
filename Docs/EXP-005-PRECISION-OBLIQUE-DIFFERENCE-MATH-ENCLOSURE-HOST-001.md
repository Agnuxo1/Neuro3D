# EXP005: certificado matemático de diferencia, distinto del encierro HOST completo

ID: PRECISION-OBLIQUE-DIFFERENCE-MATH-ENCLOSURE-HOST-001. Dueño Codex, capacity_audit/EXP005.
Base 0ffa40381cee00ec67f3d24ffa579d39a53c52ae.
Padre CPU SHA256 24a385c85f3d071ea98ffcf333fb834d898dc2ea2dfab2c21155c9c00ddab1b2, 167737 bytes.

## Contrato nuevo opt-in

Modelo `oblique-difference-math-enclosure-HOST-v1`; política
`TWO_DISTINCT_OBJECTS_SQUARE_MONOTONICITY_NOT_LEGACY_GATE_REPAIR`.
No modifica el comparador CPU anterior ni convierte sus STOP en PASS. Un resultado
`LEGACY_ENCLOSURE_STOP_PRESERVED` significa únicamente que se ha probado otro objeto:
la inclusión matemática condicionada al modelo geométrico declarado.

Leer capturas selladas y todos los 327 pins anteriores; añadir recibo padre: 328 dependencias.
No importar módulos numéricos anteriores, ejecutar escritores ajenos, reconstruir encoders
ni repetir grafos RN, raíces, barridos o runners. Sólo enteros y racionales HOST; palabras
IEEE64 interpretadas por significando/exponente, nunca float. No Blender, GPU, RT ni óptica.

Selector cerrado ligado a ID y hashes de cuatro registros, snapshot/query originales,
SOURCE0/DETECTOR0, scene_length, referencia nominal declarada y conservación obligatoria
del STOP. Sin alias, campos extra de lambda/cap ni auth física implícita. Fallo de recibo,
SHA o captura cierra antes del certificado. Falsificaciones de tests son sólo en memoria.

## Dos preguntas con respuestas independientes

Sean Smin, Smax las cotas de distancia al cuadrado de TODA la caja continua original,
Sn la distancia nominal al cuadrado; no una selección de esquinas. Para cada eje,
delta = detector_nominal - source_nominal y radio = radio_detector + radio_source.
El mínimo cuadrado es cero si el intervalo delta cruza cero; en otro caso el menor
cuadrado de sus extremos. El máximo es el mayor cuadrado. Se verifica contra los
certificados capturados, manteniendo los 15 radios de la escena.

Sean Llo/Lhi las parejas de longitud ROOT64 PRE-WIRE selladas y Blo/Bhi sus cotas
originales. Definir ell=Llo-Blo, u=Lhi+Bhi. Rl/Rh son los extremos nominales HOST96.
Se prueban exactamente, sin evaluar raíces:

- 0 <= ell, ell² <= Smin <= Sn <= Smax <= u².
- 0 <= Rl <= Rh, Rl² <= Sn <= Rh², retícula y anchura HOST96 retenidas.

Por monotonía, para cualquier punto original:

`ell-Rh <= sqrt(Smin)-sqrt(Sn) <= sqrt(Sactual)-sqrt(Sn) <= sqrt(Smax)-sqrt(Sn) <= u-Rl`.

No se eleva al cuadrado la diferencia firmada. A=[ell-Rh,u-Rl] coincide exactamente
con los candidatos/cotas ya retenidos de las restas CPU, cuyos residuales de encoding
y aritmética son cero. Los certificados por cuadrados prueban que A encierra la
diferencia matemática, NO que A contiene cualquier intervalo externo que la encierre.

Por separado, el comparador anterior exige contener H=[HLlo-Rh,HLhi-Rl], donde
HLlo/HLhi son la envolvente reticular HOST96. Puede suceder que H sea más ancho que A:
el STOP de ese comparador es correcto respecto a su contrato, y se mantiene intacto.
Se prueban identidades de déficit:

`Alo-Hlo = ell-HLlo; Hhi-Ahi = HLhi-u`.

Sólo se resta el MISMO extremo explícito R en esta identidad algebraica para comparar
dos intervalos. No cancela incertidumbre SOURCE, longitud, material, gauge ni referencia
física; no supone correlación. Las dos cajas fuente/detector siguen completas.
No cambiar radios, bounds o umbrales para borrar déficits.

## Alcance y costes

Las fixtures son CPU sintéticas declaradas, no capturas de escena física autenticada.
Referencia: cuerda recta nominal, no camino óptico. Los radios A/B/C se conservan,
pero este teorema es de distancia SOURCE/DETECTOR y no certifica visibilidad,
autointersección, todas las ramas reflejadas, huecos físicos ni transporte de fase.

`phase_error_bound=null`; fase/lambda/auth/engine/GPU/Bpy y correlación/cancelación SOURCE false.
U/GEMM compilada no sustituye inferencia desde escena. JEV: fallback LOCAL explícito,
sin aval remoto ni retry del bloqueo de seguridad.

Contador parcial: 12 interpretaciones de palabras por escena retenida (4 longitud,
4 referencia, 4 candidatos), 24 en las dos pruebas positivas. Los tests y controles
hacen otras operaciones HOST. Hash/IO/JSON/descompresión, racionales, productos de
verificación y oráculo tienen costes reales UNKNOWN_NOT_ZERO: no contabilidad global
ni benchmark de rendimiento. Nuevas RN, evaluaciones de raíz, encoder y ejecución de
productores numéricos antiguos cero. No afirmar cero productos HOST.

Control algebraico mínimo separado: Smin=Sn=1, Smax=2, ell=1, u=3/2, Rl=Rh=1,
HL=[1,2]. A=[0,1/2] encierra la diferencia matemática y no contiene H=[0,1].
No calcular sqrt(2); control no es otra escena ni inferencia. Certificados falsos de
u², referencia o signo negativo deben fallar.

## Validación y coordinación

Suite PASS HOST_CONDITIONAL_MATH_CERTIFICATES_LEGACY_STOP_PRESERVED,
0.3372721999985515 s, 46860 bytes, stdout SHA256
dc2b021ad45f05a0a932d68f2e68dd1cb9c078261ceadc396fe1dc223897efa3.
16 registros: 2 pruebas matemáticas condicionadas, 2 STOP de contención conservados,
14 STOP upstream; 0 admisiones motor/fase. 8 selectores, 8 falsificaciones en memoria,
3 certificados algebraicos inválidos y 3 API negativas rechazados. Missing/drift
son SIMULADOS, no corrupción de archivos. Control algebraico positivo independiente.
No fallos de la suite observados. Primera suite PASS retenida; aclaración de contadores:
un certificado rechazado tras comenzar la auditoría devuelve word-decodes=null
(desconocido), nunca cero ficticio. Suite final repetida sólo tras este cambio.
48 word-decodes positivos entre ambas suites, contador PARCIAL; no contar como coste total.
La revisión independiente posterior se sella en el
recibo; no repite suite, encoder, grafo RN ni raíces. 24 word-decodes corresponden
SÓLO a las dos pruebas positivas, no a toda la suite/oráculo/falsificaciones.
Duración de QA, no benchmark ni coste global. Recibo recoge pins own3 + 328 dependencias.
Patch de documento rechazado por ancla incompleta antes de cambiar archivos;
corregir sólo ancla, no arithmetic/bounds/umbrales.

Runners/shaders/contratos y fixtures
conf1/v0/v4/0119/0315/nearestV2 congelados intactos. Versionar sólo own4 revisados;
checkpoint y sharedboards locales SINstage. CPU propia un hilo/afinidad1/hijo60s.
No usar GPU por relleno; ventana nocturna histórica cerrada y deadline inmutable.

Claude mantiene capacity/nebulatrace/research/RT. Pedir ACK por este ID y SHA del recibo
y SOLO artifacts YA existentes por ID/path/SHA/bytes: contrato de verdad matemática
versus envolvente numérica, costes completos; backend/guard fail-closed, igual trabajo
y salidas. No atribuir equivalencia RT a 16M vs 1M, salidas distintas o cruce extrapolado.
Futura fase necesita contrato escena/lambda/unidades/referencia/material/gauge/cobertura
y caps/errores completos antes de promover o escalar.
