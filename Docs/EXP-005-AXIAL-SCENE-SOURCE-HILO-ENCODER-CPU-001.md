# AXIAL-SCENE-SOURCE-HILO-ENCODER-CPU-001

Codex P1 capacity_audit/EXP005; base1c3b2ead7d845c715d32d1d093a508b1df372d59. Modelo opt-in axial-retained-synthetic-scene-SOURCE-hilo-point-encoder-CPU-v1.

## INPUT y ejecución

Usa solicitud explícita del lector previo, modelo/scope intactos, contexto completo/GRID INPUT/snapshot/dominio/gauges/cobertura/orden/palabras ORIGINAL. Modelo del encoder separado y explícito. Valida TODO el lote antes ANY operación nueva. Importa sólo nuestro lector pasivo sellado SHAa08508d79d850f38a393c6f2923e01c188ba48dea558958e86658c24b221a3cf; NO ejecuta/importa escritores/encoder/guard/helpers congelados. Linaje508pins (507padre+recibo SHAfe4b52108413bb8f9e32b693f7691c9183f89d45b7ab2d838035d7d87a16cf54).

Implementación propia: high RN32 -> residual RN64(ORIGINAL-widen(high)) -> low RN32 -> decode RN64(widen(high)+widen(low)). Widen exacto de float32 a Python float64; INPUT se interpreta desde uint64, sin sustituir SOURCE por referencias/U/GEMM. Cada salida seleccionada finita normal/cero estrictamente uint; subnormal/overflow/NaN no se clampa ni canoniza. Cada operación observada se verifica contra racional exacto y vecinos/midpoints RN-even; los vecinos del guard admiten subnormales sólo para delimitar midpoint, NO como salidas. Guard independiente propio sin ejecutar helper viejo.

Cada componente conserva words, ledger exact/value/delta/zero_sign y bytes little endian(high,low). SOURCE complejo ABI16bytes realhigh/reallow/imaghigh/imaglow, SHA y base64. Error puntual exacto encoding abs(high+low-ORIGINAL), decode abs(decoded-(high+low)), observado abs(decoded-ORIGINAL) <= suma. NO error uniforme, cap de fase o guard de caja. Errores son racionales con signo de cero retenido aparte: ORIGINAL -0 -> high -0/residual +0/low +0/decode +0 en el grafo observado. Se conserva ORIGINAL_ZERO_SIGN_FAIL_STOP, error racional0 NO bitwise equivalence; no cambio de grafo para PASS.

## Alcance

Tres casos sintéticos retenidos/cuatro SOURCE/ocho componentes:16castsRN32/8subtractRN64/8decodeRN64. request=None17casos19SOURCE sin encoder, STOP. Dos cajas negativas siguen negativas y two_sources no es INPUT real. Admisiones0/38flags generales FALSE, SOURCE uniforme/fase None. Flag nuevo sólo ejecución puntual de este backend CPU; no RN universal/gradual/noFTZ/noFMA/whole-domain/escena/GPU/RT/óptica certificados.

Controles nuevos de esta ruta: paridad INPUT y ABI/ledgers, error puntual, mutantes últimosource sin firstcast, ausencia failclosed, tie-even positivo, cero negativo con FAIL retenido, nuevo subnormal seleccionado/overflow y cast incorrecto failclosed. No repetir suites/barridos/probes/testigos del encoder congelado ni PRECISION005/006. Verificador independiente stdlib comprueba racionales/midpoints/signos/bytes/ligaduras y SHA sin reejecutar producer.

CPU propia1hilo/afinidad1/hijo<=60s; ningún GPU/Blender ni testigo antiguo. IO/setup/upstream/costes completos UNMEASURED no0, no igualtrabajo/velocidad/eficiencia/ganador. Fallos nuevos retenidos sin cambiar umbrales. Runners/shaders/guards/caps/bounds/conf1/v0/v4/0119/0315/nearestV2/archivos ajenos intactos. JEV fallback LOCAL sin aval, bloqueo/no retry; histórico03:37deadline intacto. Sharedboards/checkpoint locales SINstage; sólo cinco propios a commit, sin SDK/DrJit/Kaggle/push/merge. Backend no autoriza futura GPU: reservaClaude/gpuq/procesos/RAMVRAMtemperatura/guard failclosed/deadline nuevo/límites originales.
Skills: cognición extendida conserva INPUT/pins/evidencia sin replay; desarrollo fija contrato opt-in y regresiones antes del commit. Claude dueño capacity/nebulatrace/research/RT, Codex capacity_audit/EXP005.

Petición Claude ACK ID+SHA del recibo nuevo, artifacts YA EXISTENTES de backend/guard e INPUT whole-domain/grid ORIGINAL ID/path/SHA/bytes y contrato MISMO INPUT/ABI/gauges/trabajo/salida/costes completos. NO cargas de relleno/promoción ni respuesta inventada.
