# EXP005 — Cobertura única del ledger de visibilidad (HOST)

Unidad PRECISION-VISIBILITY-LEDGER-COVERAGE-HOST-001, base08e1ad63dc6a769a6e5dca204a6cdbe249c20839. Modelo opt-in
precision-visibility-ledger-coverage-HOST-v1. Nuevo verificador, NO cambia
módulo ni oráculo congelados de VISIBILITY001.

## Contraejemplo retenido, alcance preciso

VISIBILITY001 SHAcaeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5
emitió ledgers correctos en la captura retenida. Su bloque de admisión del
oráculo verificaba numérica por fila, cantidad4*triángulos, cuatro destinos y
dos previous-zero, pero no unicidad/cobertura de SOURCE-segmento-primitiva.
En cada uno de los seis ledgers admitidos, copiar la fila [S0,1,0] sobre
[S1,1,0] deja8 u12 filas,4 destinos y2 previouszero, y todas las filas siguen
numéricamente válidas según row_check del lector congelado. Solo existen7
u11 claves distintas y falta la comprobación de [S1,1,0].
Se preservan seis LEGACY_ADMITTED_ROW_BLOCK_ACCEPTED_COUNTEREXAMPLE:
legacy_sufficiency=FAIL, no se ocultan con el PASS de la nueva suite.
Se ejecuta solo row_check y el bloque de admisión correspondiente, NO main()
del oráculo completo ni override de cap/lectura/identidades/archivos.
NO se afirma un fallo observado del core emisor, del recibo íntegro, de GPU,
de seguridad o de óptica; sí una insuficiencia demostrada de ese bloque
de comprobación para garantizar cobertura frente a mutaciones.

## Contrato nuevo

validate(model, request, ledger) requiere selector cerrado case/receipt_sha256/
intent=HOST_UNATTESTED_VISIBILITY_LEDGER_ONLY. Evidencia e inputs provienen
internamente del recibo sellado y146pins; no override de inputs/escena.
Solo ledger es un candidato externo explícitamente no autenticado.

Los38 resultados parentales STOP bloquean antes de inspeccionar el candidato.
Para los6 admitidos, reconstruye el producto cartesiano en orden
S0/S1 x segmento0/1 x todas las primitivas en orden de escena.
Exige unicidad, conjunto exacto, orden, tipos estrictos (bool no int), esquema
de seis campos, límite16 filas y representación JSON exacta de las filas
numéricas selladas. Comprueba también que el ledger sellado cumple ese grid;
no presupone que un contador certifica la cobertura.
No reejecuta geometría, sqrt, RN, shader/compiler, Blender ni GPU.
Devuelve HOST_UNATTESTED_VISIBILITY_LEDGER_MATCH: mismo ledger numérico
completo, NO provenance/inferencia/certificación de material o física.
Un candidato copiado puede igualar el ledger y sigue no autenticado.
verified_rows=0 en todo STOP; no publica una verificación parcial.

## Verificación y límites

Captura reutilizada44 casos:6matches/38STOP intactos.
Diez mutaciones por ledger admitido: duplicación/omisión SOURCE1, quitar fila,
invertir orden, cambiar primitiva, cambiar t, reescalar denominador a [2,2],
bool en segmento, campo extra, lista vacía y diccionario en lugar de lista:
60STOP. Reescalar [1,1] a [2,2] preserva valor racional, pero este contrato
exige representación serializada sellada exacta; no se inventa normalización.
Cuatro selectores incorrectosSTOP: total104corridas+4selectores.
Suite3gruposPASS conservando seis legacy_sufficiencyFAIL.
Verificación independiente inline, guardada íntegra en recibo, reconstruye
grid y mutaciones sin importar core, comprueba respuestas/contadores/flags,
censos/contraejemplos/capturas/hashes y API pública sin override.
Tiempo QA NO coste de motor ni prueba de eficiencia. No comparación
16Mvs1M ni alteración pareadoV1/RT-AUD001/caps/conf1/bounds/fixtures.

CPU1hilo/afinidad1/hijo<=60s, JEV LOCAL sin aval remoto ni retry,
GPUBlender0/producer0/RN0/compiler0; lectura del row_check anterior solo para
el nuevo contraejemplo dirigido, no barrido científico repetido.
Todos los permisos de promoción/autenticación físicos/GPU siguen False/STOP;
costes UNMEASURED_NOT_ZERO. Runners/shaders/guard/frozen y archivos Claude
intactos. No SDK/DrJit/Kaggle/push/merge. Sharedboards LOCAL SINstage.
Skills de cognición extendida y pruebas enfocadas dirigen reutilización de
captura y mutación contra cobertura, preservando el fallo sin cambiar umbral.
Ningún backend usa silenciosamente el nuevo verificador: integración futura
opt-in requiere su propio contrato/tests y artifacts ya existentes por
ID/path/SHA/bytes, mismo ORIGINAL/literal/overlay/cotas/trabajo/salidas/costes.
