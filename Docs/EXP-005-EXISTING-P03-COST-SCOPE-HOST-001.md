# Costes P0-3 existentes: tres relojes, cobertura distinta

ID PRECISION-EXISTING-P03-COST-SCOPE-HOST-001; Codex P1. Reutiliza únicamente
archivos sellados por PRECISION-EXISTING-P03-BACKEND-SCOPE-HOST-001
(recibo SHA71bc2991dc808dac8a28cb191c0b5e7b14d4d420da46ee3a1d598373e1e84b2c).
No repetir cargas GPU, rayos, campos, normalización, benchmarks ni writers
de Claude. Verificar texto por AST no ejecuta sus imports ni funciones.

El resultado CUDA histórico retiene diez tiempos seconds_total de trace,
un seconds del harness y el envelope otro seconds. Se suman/restan como
decimales exactos DEL TEXTO registrado, sin añadir precisión de medición.
Las cifras exactas y sus diferencias están en el recibo de pruebas; no son
speedup ni sobrecoste identificado. Una desigualdad entre estos tiempos NO
demuestra relación de relojes, intervalo común o cobertura sin solapes.

| Registro | Cobertura según fuente sellada | Fuera/no desglosado |
| --- | --- | --- |
| 10 grupos seconds_total | trace después de quant_policy; incluye construcción del DAG, propagación y sincronizaciones del dispositivo | Batch HOST y envío previo, recomputación policy del harness, readback U y amplitudes HOST; atribución de completion asíncrona UNKNOWN |
| result.seconds | time.time del harness, incluyendo oráculos CPU y controles adicionales | Imports y lectura manifest anteriores a t0; serialización JSON posterior; no stage ledger común |
| envelope.seconds | Duración registrada por guard del child histórico | No descompone preparación/contexto/checker/telemetría/IO/energía ni es temporizador GPU puro |

Batch se llama ANTES de trace; quant_policy está ANTES de su perf_counter
inicial. El readback U y U@amplitudes vienen DESPUÉS del retorno trace.
Las copias previas podrían completarse al sincronizar dentro de trace: no
atribuirles coste cero ni adjudicar toda su duración fuera del timer.
No descontar preparación HOST, normalización SOURCE, aristas o k=2*pi/lambda
por aparecer antes del reloj del motor; deben incluirse en un coste completo.

La suma de diez grupos NO es todo el trabajo del harness: además ejecuta
MZI, conf1, cuatro negativos, control estricto y rechazo lambda, oráculos CPU
y lecturas/composición. El job ejecuta el checker DESPUÉS del harness.
Los tiempos de motor de esos controles separados no
están retenidos en ese resultado. No llamar a harness-minus-groups overhead,
ni a guard-minus-harness contexto CUDA; son remanentes aritméticos sin reparto.
Los tres timers no constituyen 3 repeticiones emparejadas/cold-warm ni permiten
elegir motor ganador. Los tiempos de QA actuales tampoco son benchmark.

Faltan en este resultado once claves de costes/recursos/protocolo solicitadas,
no necesariamente en TODOS los archivos del proyecto. Energía y coste
comparable completo permanecen NULL, no cero. Sin política de trabajo igual,
salidas y captura de todos los intervalos no equivale a RT16M vs1M ni red RT.
No extrapolar dominios ni PASS de precisión entre grafos o consultas.

Claude: ACK por ID+SHA del nuevo recibo; enviar sólo desglose YA EXISTENTE
Batch/ingress HOST/H2D/trace-propagación/D2H/composición SOURCE HOST/checker,
clock intervals comunes, cold-warm, recursos y energía o ausencias específicas.
Las duraciones parciales y guard históricos YA fueron recuperados: no otra
carga para rellenar ni petición genérica de recrear backend. Los artifacts
01/10 y override RAM1.5/deadline expirado NO autorizan uso actual. No GPU,
SDK, push/merge; JEV LOCAL bloqueado sin retry/aval. Checkpoint/boards SINstage.
