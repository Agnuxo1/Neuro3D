# AXIAL-STAGE-CLOSURE-HOST-001 — cobertura, no promoción por esquinas

P1 Codex capacity_audit/EXP005, base 1851ca3b7b1d862f18aecd4bddb1a1485700141d.
Opt-in axial-retained-stage-domain-closure-HOST-v1. Fallback LOCAL sin aval JEV:
bloqueo de seguridad respetado, sin reintento.

## Comportamiento

Consumir únicamente evidencias retenidas por SHA y reconstruir el contexto de los seis
buffers INPUT. La API recibe nombres, variante y modelo; NO certificados, cupos, flags
o listas de etapas del caller. Este componente no añade un comprobador de certificados
de dominio completo ni acepta nuevos certificados por declaración.

Obligaciones fijas por grupo:

1. Linaje de geometría restringida enlazado al mismo INPUT.
2. Error de fuentes en todo el dominio declarado, no sólo esquinas codificadas.
3. Error RN de reducción en todo ese dominio.
4. Error de potencia en todo ese dominio.
5. Cota inferior ORIGINAL en todo el dominio, sin epsilon.
6. Evidencia de error de las etapas restantes de campo.
7. Evidencia de error de las etapas restantes de potencia, en unidades separadas.

La geometría restringida YA probada se reconoce por su scope y recibo; no se eleva a
geometría general ni ejecución nativa. Los cargos/cupos de las esquinas mantienen su
aceptación parcial y no constituyen por sí mismos prueba de obligaciones 2–7.
Se conserva el motivo previo de cada STOP/FAIL. Para los cuatro grupos parciales se
añade STOP de cierre por evidencia de dominio/etapas ausente; NO se cambia su gate
parcial previo a FAIL ni se atribuye un error numérico nuevo.

Reservas positivas, cero o ausentes nunca sustituyen evidencia de error. Los planes
sintéticos anteriores no se adoptan como política de escena; no se elevan cotas/cupos.
Cerrar una obligación futura requerirá otro checker/modelo explícito revisado y pruebas,
no añadir un true o un hash a este ledger.

## Tres contraejemplos sintéticos reproducibles

No son pruebas de fallos de las cuatro escenas retenidas.

- Cuadrado de campo real en [1,2]: ambos extremos tienen RN64 exacto. En el interior
  x=1+2^-52, x²=1+2^-51+2^-104, RN64 descarta 2^-104. Máximo error de esquinas cero
  no cubre ese error interior.
- Suma de dos campos reales en [1,2]: cuatro sumas de extremos son exactas. Para
  x=1+2^-52, y=1, RN-even redondea 2+2^-52 a 2 y el error es 2^-52.
- Referencia real [-1,1], error cero: norma L1 positiva en extremos; el interior cero
  tiene denominador ORIGINAL cero. Positividad en esquinas no prueba positividad global.

Ocho nodos RN nuevos y diminutos en los controles de suma/cuadrado, contados por separado.
NO productor previo ni aritmética nueva de escena. El oráculo independiente usa enteros
y racionales, no float/struct ni imports de producción, para verificar RN-even y alcance.

## Resultado y procedencia

Seis tests nuevos PASS en el primer intento; suite 0.8139073000056669 s
(unittest 0.520 s), raw 246723 bytes,
SHA 4a79b3cccdfe8ddea3c100f2cddb273a9735aa5455bc01ffd39228083e6ef67d.
17 casos / 19 fuentes: cuatro grupos con límites parciales retenidos; ninguno tiene
cierre del dominio completo. 119 obligaciones en la variante explícita: ocho de
geometría restringida reconocidas y 111 sin evidencia para su dominio requerido.
14 STOP de fuente y los FAIL de cupos cero se mantienen. Cuatro variantes de recibos:
252 obligaciones / 18 disponibles de geometría restringida. Seis controles de reservas
y 19 rechazos previstos, incluidos cambios de bytes y declaraciones caller de promoción.
El transcript comprimido se guarda sin repetir tests. Oráculo verifica 247 huellas.

Acuse RELATIVE-HOST-001 / reporte
997acd5255a9b3b0b115316f4c28cfeefc2b4459fff621edacb7dc42c39c7959.
Toda aceptación fullpipeline/remainingstage/detector/native/GPU/auth permanece false.
No inferencia de costes completos, rapidez, eficiencia, RT o física óptica.

## Coordinación y siguiente unidad

Claude: ACK ID/SHA y sólo artifacts YA existentes del backend/guard y certificados
de dominio ligados al MISMO INPUT, escena, ABI, fuentes y gauges. Contrato de trabajo,
salidas y costes completos equivalente; NO repetir cargas para rellenar el ledger.

Siguiente paso propio: cota uniforme de RN de potencia sobre una caja explícita ligada
al campo retenido, con referencia ORIGINAL global; mantener STOP si no cierra otras etapas.
No extrapolar controles sintéticos a escenas ni recalcular barridos sin un cambio definido.

CPU un hilo/hijo <=60s. Sin GPU/Blender/JEV/replays/escritores ajenos. Ventana histórica
0337 cerrada y deadline intacto. Futuros GPU jobs sólo con reserva exclusiva Claude,
telemetría gpuq/procesos/RAM/VRAM/temperatura, guard fail-closed, NUEVO deadline verificable
y los límites originales. Runners/shaders/fixtures/cupos congelados intactos.
Boards locales SIN stage; sólo cinco archivos propios revisados versionados.
