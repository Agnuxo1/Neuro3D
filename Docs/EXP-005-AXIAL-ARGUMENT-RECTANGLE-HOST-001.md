# EXP-005 — AXIAL-ARGUMENT-RECTANGLE-HOST-001

Unidad P1 Codex capacity_audit; backend/checker HOST opt-in, no dispositivo.
Base c369a40d3e6d716eb1aec714940fa8c8429388c6.
Predecesor AXIAL-UNIFORM-UNIT-HOST-001, recibo SHA
0ab0e6d7236cc215f53034b35bb4d89d9dce37cfe133e0287e66f8dc2ed17eac.

## Contrato y resultado admisible

Modelo explícito axial-parameter-rectangle-quarter-RN-monotone-HOST-v1.
API de escena: nombres únicos de casos retenidos + modelo; no admite caja,
cupo, palabras RN ni certificados de escena aportados por el llamador.
La primitiva racional es un teorema sobre un dominio declarado, no un aval
de que la geometría continua produzca exactamente ese dominio.

Se reconstruyen seis buffers INPUT, snapshot ORIGINAL, ABI, orden completo
de fuentes y referencias separadas a partir de recibos ligados por SHA.
Longitud efectiva correlacionada y wavelength proceden del contrato de referencia
retenido; no se sustituye por suma independiente de bounds de geometría y X.
Las cuatro esquinas deben ser el producto cartesiano EXACTO de sus dos intervalos.
La referencia ORIGINAL sigue separada de los parámetros codificados.

Para wavelength estrictamente positiva, los extremos de L/w están entre sus cuatro
esquinas, incluso con L negativo. Se verifican j=floor(q+1/2) y k=floor(4(q-j)+1/2)
en ambos extremos y en la referencia ORIGINAL. Si cambia alguna rama, STOP.
Empates exactos conservan la convención semiabierta: residual centrado [-1/2,1/2)
y residual de cuarto de vuelta [-1/8,1/8). Sin epsilon, clipping ni snapping.

Con rama fija, se prueba la imagen del grafo RN64(T) seguido por RN64(P*cast),
P=palabra positiva retenida de 2pi. RN-even es monótono; las palabras de los endpoints
se verifican por pertenencia a sus celdas racionales entre vecinos, incluyendo
empates par/impar y signo de cero. No se repiten casts/productos ni productores.
Se rechazan no finitos y celdas del máximo finito; no se usa este teorema para overflow.

La cota uniforme de fase a referencia fija es
8*max(|qlo-qOriginal|,|qhi-qOriginal|), usando el bound conservador 2pi<8.
Cargos de cast, constante 2pi y multiply se mantienen separados:
P*E(max|T|), max|T|*B2pi, E(P*max|cast_endpoints|);
E(M)=2^-53*M+2^-1075 para M>0 y E(0)=0.
Las constantes y su bound son los de los recibos previos; no son nueva metrología.

La hipótesis RN gradual no habilita FTZ/FMA. La compatibilidad con el runner antiguo,
que rechaza subnormales seleccionados, sólo es cierta si TODOS los resultados cast
y argumento son normales del mismo signo o exactamente cero. El checker lo prueba
para estas cinco cajas; no autentica ejecución de hardware.

## Verificación y límites

17 casos, 19 fuentes: cinco imágenes de rectángulos declarados y 14 STOP de unidad
conservados. 40 pertenencias a celdas RN retenidas; cero casts/productos RN nuevos.
Ocho controles de ramas racionales y seis controles de celdas RN; 23 rechazos.
El intervalo de argumento previo de Horner contiene estas cinco imágenes.

Se conservan las tres cotas polinómicas genéricas que no cabían en cupos fase cero
(negative/s, positive/s, two_sources/s). No son fallos nuevos de escena y no se
ensancha ningún cupo para rescatarlas. No se compone silenciosamente una cota de
esquinas con una cota uniforme. No se suma una fuente aceptada si su compañera STOP.

Los seis tests originales se ejecutaron UNA vez y pasaron. Su captura temporal
se perdió al interrumpirse la sesión; se recuperó íntegra del evento de herramienta
del historial local, verificando 111338 bytes y SHA
9e4c5ac50ff67db4614dcf2301fd8641a24e505c2b7d9d509d2a16a088c9810a.
No se repitió la suite para recuperar el recibo. El reporte conserva stdout
comprimido, stderr, duración y procedencia de recuperación.
El verificador independiente usa únicamente stdlib/racionales y recibos; no
importa checker ni productores. Reconstruye ramas, celdas, cargos, linaje y cupos.
Las verificaciones del propio verificador pueden repetirse al cerrar pins/commit;
no son nuevas cargas numéricas del backend.

Permanece STOP para escena completa: whole_scene_parameter_enclosure_proved,
scene_argument_enclosed, uniform_unit_error_to_ORIGINAL_proved,
uniform_source_error_proved, full pipeline, ejecución/coherencia autenticadas,
native/GPU/RT y admisión de GPU son false. Este teorema de parámetros NO certifica
autointersecciones, huecos finos ni el selector/transporte completo de geometría.
Siguiente obligación: certificado verificable de dominio desde escena ORIGINAL,
después fuente compleja y cierre uniforme de reducción/potencia.

CPU propia un hilo, hijo <=60s; sin GPU, Blender, RT, SDK/DrJit, Kaggle ni push/merge.
JEV bloqueado por seguridad; fallback LOCAL explícito sin aval remoto ni reintento.
0337 histórico permanece cerrado, deadline intacto. Cualquier futuro job GPU
necesita reserva exclusiva Claude, telemetría previa, guard fail-closed, NUEVO
deadline y todos los límites originales. Frozen/fixtures/umbral/cupos intactos.
Cuatro tablones locales sin stage. Tiempos de checker no son costes completos,
eficiencia ni evidencia de motor ganador; ALU digital/RT/óptica física se distinguen.

Claude: ACK por este ID/SHA y sólo artifacts YA existentes de dominio/backend/guard
del MISMO INPUT/escena/ABI/fuentes/gauges y contrato de igual trabajo, salida y
costes completos; sin repetir RT ni cargar por relleno.
