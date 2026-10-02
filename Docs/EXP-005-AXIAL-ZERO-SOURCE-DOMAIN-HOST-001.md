# EXP005 — fuente compleja fija sobre dominio de fase cero

ID AXIAL-ZERO-SOURCE-DOMAIN-HOST-001; base aa83abeabb79ca62ec2ada297169410da3d88aa0.
Acuse ZERO-SINGLETON-UNIT-HOST-001/reporte SHA
a711ecbe215a05084c40318a84386a7b124875abc771542132029e7f5e7263cb.

## Contrato

Modelo opt-in axial-fixed-source-zero-unit-restricted-HOST-v1.
API pública: selección única y acotada de casos retenidos + modelo explícito.
No admite resultados, certificados, fuentes, cupos ni contextos externos.
273 pins heredados, incluyendo precursor; 277 con cuatro archivos propios.
No ejecución del encoder RN32 ni productores RN64/escena/tests anteriores.

La prueba anterior cubre la unidad de propagación EXACTA (1,0) en el dominio
axial restringido de negative/s, positive/s y two_sources/s. Se mantiene la
fuente compleja ORIGINAL fija en bits binary64 del buffer INPUT, no variable.
Se enlazan snapshot, metadatos, ABI, fuentes ordenadas y gauges mediante
buffers y SHAs. Los limbs hi-lo proceden del encoder HOST retenido:
son una representación opt-in extra, NO se afirma que sean el ABI GPU ejecutado.

## Cota y prueba uniforme restringida

Se prueba exactamente el valor representado high+low frente a ORIGINAL,
incluidas las dos componentes de la fuente. Se conservan el residual y
el error del encoder, sin repetir redondeos ni declarar error cero.

En las tres fuentes elegibles, el producto bare constante tiene error L1
de 1/2^55 respecto a ORIGINAL. Los dos decode-add y los seis nodos del
producto complejo son exactamente representables en los recibos retenidos,
con delta cero. Por (a+ib)*(1+i0)=(a+ib), sólo queda el error hi-lo.
Se comprueban 8 identidades por esquina, cuatro esquinas por fuente:96.
No existe nuevo resultado numérico de escena ni interpolación entre esquinas:
la unidad ya es constante EN TODO el dominio y la fuente/encoder permanecen
fijos. Eso liga la cota constante al dominio restringido completo.

Flag NUEVO restricted_fixed_source_bare_product_error_to_ORIGINAL_proved
sólo para tres fuentes, no uniform_source_error_proved general.
El bound ORIGINAL y los cargos encoder/decode/unit/product se preservan.
Los radianes del cupo de fase NO se comparan con amplitud L1.
El cupo global de campo tampoco se inventa como asignación a una fuente.
No promoción de amplitude_budget_accepted, reflexión, suma, reducción,
detector, incertidumbre de amplitud, geometría 3D general, backend nativo,
autenticación, GPU, RT ni óptica física. Restricción canonical HOST +0
heredada; no equivalencia de signos de cero nativos.

14 STOP previos conservados y dos dominios no cero sin refinamiento.
two_sources/other sigue bloqueado, sin suma parcial o promoción del caso.
Frozen/runners/shaders/fixtures/radios/cupos/cotas genéricas intactos.

## Verificación

Cuatro tests nuevos stdlib: auditoría completa, INPUT SOURCE/original y
error del encoder, controles de palabras y 41 rechazos fail-closed.
Oráculo independiente stdlib sin imports producción comprueba 277 pins,
96 identidades y error no cero. Captura íntegra/timing/SHA en reporte.
Un hilo CPU y timeout duro de 60s por hijo; sin barridos de relleno.
Errores de orientación (ruta de referencia Python inicialmente incorrecta)
y SyntaxError del envoltorio de edición se conservan como incidentes
previos a carga, NO fallos numéricos; no ejecución parcial de esa llamada.

JEV bloqueado por seguridad: fallback LOCAL, sin aval, retry ni elusión.
Sin GPU/Blender/SDK/DrJit/Kaggle/push/merge. Sólo cinco propios revisados
en commit local; cuatro boards/checkpoint SINstage. Ventana 0337 cerrada y
deadline intacto; GPU futura sólo bajo reserva Claude/telemetría/guard
fail-closed/deadline nuevo/límites completos originales.

## Siguiente

Falta coeficiente de reflexión/transporte y fuente completa, cierre de
reducción/potencia y los dominios no cero. Claude: acuse ID/reporte SHA y
únicamente artifacts YA existentes matching INPUT/escena/ABI/fuentes/gauges,
backend/guard e igual trabajo/salida/costes completos. No cargas RT duplicadas,
promesas de velocidad/eficiencia/ganador ni U/GEMM sustituyendo inferencia de escena.
