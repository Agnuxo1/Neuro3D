# EXP005 — contrato offline de evidencia efectiva nativa equivalente

ID AXIAL-NATIVE-EVIDENCE-CONTRACT-001; Codex capacity_audit/EXP005.
Base d07a269; cadena CLOSURE SHA5875def25bf8a3cf3454bef1751dee7573e884fd2f3ccd96cc97de10d325597b.
Opt-in; no cambia runners/shaders/contracts/fixtures congelados.

## Qué exige

13 escenas y 14 IDs, misma ABI geométrica hi-lo, snapshot/binding original,
referencia al plano ORIGINAL, caps/gauges/sourceOrder, grupo/rebase0,
predecesores de ocho etapas, gates y salidas completas por fuente/grupo/puerto.
No centros/salidas distintos, ni 16M vs1M, ni U/GEMM/lookup sustituyendo
traversal desde escena. Política bit-exact de modelos retenidos; una distinta
política numérica exigiría otro contrato explícito, no relajar éste.

Backend+readback+guard+ledger enlazados al MISMO job/contrato y fingerprints.
Readback exige inputs EFECTIVOS y salidas; no sólo passed/metadatos de modelo.
API/dispositivo/runner/codeSHA explícitos; GPU ALU digital no se confunde con
Bpyfloat32, RT ni óptica física. CodeSHA/metadatos/bytes NO prueban ejecución:
matching sólo candidato documental pendiente de autenticación y evidencia de
precisión desde escena. Agrupación todavía hipótesis CPU, no coherencia física.

Guard exige linaje backend/readback, terminación propia registrada, deadline
UTC por job y timeout piloto<=120s/otro<=600s; política fail-closed con los
límites autorizados intactos. Inspección HISTÓRICA offline: nunca admite GPU,
no telemetría fresca/reserva/prueba de actuación efectiva del guard.
Deadline nocturno cerrado no se modifica ni se reutiliza para un nuevo hijo.

## Costes completos, sin atribuir eficiencia

Ledger con queue/export/inputvalidation/compile/build/upload/geometry/
reference-phase/source/groupdetector/readback/outputvalidation/guardoverhead.
Reloj monotónico común y spans dentro de wall TOTAL: pueden solaparse,
NO sumar como tiempo total. Cada N/A requiere cero explícito y motivo; coste
faltante rechaza. Cold/warm y amortización explícitas/cold sólo1run.
Transferbytes y máximos de sampler RAM/VRAM declarados NOpicos globales.
Energía medida microjoules+método o unavailable/null: desconocido NOcero.
Validar cobertura del ledger NO autentica costes/velocidad/energía.

## Tests y frontera de evidencia

Fixtures positivos SINTÉTICOS, etiquetados siempre: fabrican relaciones de
JSON para probar el contrato, NO simulan ejecución de GPU ni tiempos reales.
Todo auth/coherencia física/fullpipeline/native/admisión/runtime-equivalent/
efficiencycomparison false incluso con matching positivo.
0337 existente y guard se rechazan como ESTA evidencia: legacy ALU K3/K4,
sin ESTA referencia/ABI; no repetir cargas para generar relleno.

CPU1hilo/hijo60s, sin producer import/replay/nueva aritmética geom-phase-field.
151 pins heredados (CLOSURE+150inputs), tests acotados y verificador stdlib
independiente de estructura/procedencia. No escritor ajeno ni RTClaude.
Sólo cuatro propios al commit; checkpoint/boards SINstage.
JEV bloqueado/no retry/bypass; fallback LOCAL identificado sin aval remoto.

Claude: acuse ID/SHA y sólo artifacts efectivos YAexistentes que llenen este
contrato; incluido protocolo igualtrabajo/salidas/costescompletos. No autorización
de ejecución por un JSON válido; cualquier futurojob sigue guard-live/reserva/
telemetría/deadline nuevos y contrato/tests/commit antes GPU.

## Evidencia local cerrada

9testsPASS rc0/0,9133303s, CPU1hilo/timeout60s.
Raw211195bytes/SHAaf70bb5c0400e6683a355f098a693810ba0dbe2cbe6f051f70abe1d80902b2d2.
151huellas heredadas154finales; plan de trabajo fijo
SHA472ac95b0a30c1bd1674223fc3ab563323cd14590bc4091af494d1d1e412fdb1.

Verificador independiente inicial rc0/0,2427991s;13bindings14IDs/104SHA de
casos-etapas/6outputs fuente/5puertos referenciados/4receipts/13costes.
No nuevo oráculo/RN/geometry replay. Positivo SÓLO fixture JSON sintético:
duración1s/ledger nanosegundos/bytes0 son datos FABRICADOS de contrato,
NO observaciones de dispositivo ni mediciones. Origen native es únicamente
declaración del artifact, nunca existencia/ejecución probada por el flag.

Tipos bool/int/float no equivalentes; NaN/duplicates rechazan. Whole-plan
SHA prohíbe cambiar contrato vía caller; tests bytes por lectura mock sin
crearfiles cubren rawhash corruption. Native0337/guardhistorical rechazan;
caps/gates/quarter/contactos/lower0FAIL/deadlinefrozen inalterados.
NoFAIL numérico; desarrollo previo retenido. Documento factual posterior
a tests, hashes al ejecutar y finales distinguidos en reporte.

Native matching real sigue PENDIENTE. Ningún JSON activa GPU, reserva o
autentica guard/costes. No publicación/push/merge ni archivos de Claude.
