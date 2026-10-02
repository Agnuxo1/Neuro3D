# AXIAL-SCENE-SOURCE-SELECTED-WORD-READER-CPU-001

Codex P1 capacity_audit/EXP005. Basea6c3e743af1e838d1c5f51486cd676e4431208d4.
Opt-in CPU reader, NO backend GPU/encoder/rounding nuevo. Modelo axial-retained-synthetic-scene-SOURCE-strict-selected-word-reader-CPU-v1.

## Contrato

Implementa validate_SELECTED_word y interpret_SELECTED_CPU propios con width estrictamente int32/64, word estrictamente int sin bool, rango unsigned, finitos y normales/cero. Rechaza subnormales seleccionados, NaN/inf, valores fuera de rango, widths float/string/bool. NO FTZ/clamp/canonicalización ni sustitución por referencia. Reinterpretación stdlib pack integer/unpack float y verificación pack-back de bytes idénticos, incluidos +0/-0. Sin operaciones aritméticas o casts RN32; float_hex es representación exacta del valor leído. Roundtrip verifica estos puntos ejecutados, NO runtime whole-domain ni equivalencia del grafo signedzero.

Sella HELPER-ABI-BOUNDARY recibo SHAda7b75f85e9d258e9fc71a0967693ee744f388d9772ed3b421feb8fb4e9b91eb, sus502pins y el propio recibo: 503heredados. Lee payloads GRID INPUT y consumidor de certificados retenidos, SIN importar/ejecutar productores congelados.

La solicitud explícita contiene modelo/scope/case_order/cases. Cada caso lleva contexto completo y GRID_INPUT completo sellados por digest canónico exacto; cada SOURCE conserva source_id/gauges/domainSHA, width64 y dos palabras ORIGINAL real/imag en orden. ALL contexto/snapshot/plan/dominio/SOURCE/gauges/tipos/words/cobertura/modelo/ABI antes ANY interpretación. Comparaciones por digest distinguen bool/int. No acepta INPUT recortado, permutación SOURCE, cambio signedzero, salida fitted, nuevo cap o plan diferente.

make_synthetic_request es fábrica explícita sólo para pruebas de tres planes sintéticos ya retenidos; NO activación por ausencia de INPUT real. request=None conserva17casos19SOURCE sin llamadas al lector, flagFalse/STOP. Con solicitud sintética explícita, cuatro SOURCE/ocho palabras se reinterpretan por CPU, flag retained_synthetic_scene_SOURCE_words_decoded_CPU True únicamente para este lector. El SOURCE ORIGINAL es float64; el soporte32 del helper sólo se prueba como primitiva, NO high/low encoder real.

## Fronteras que NO cambian

Dos cajas con guard negativo siguen negativas/STOP, incluso si el anchor original puede leerse; lectura puntual NO whole-domain/encoder/guard admission. two_sources sigue control, NO grupo real. No se repite testigo viejo 2^-149 ni barridos/probes históricos; controles del lector nuevo ejercitan sus nuevos tipos/clases/roundtrip, NO reejecutan guard/cast/producers viejos.

Admisiones0/STOP, 38flags generales FALSE, cota SOURCE/fase ejecutada None; el lector no calcula error de encoding, argumento, geometría, material, campo, potencia o transporte. No runtime/RN/gradual/noFTZ/noFMA/ejecución encoder/scene autenticados. Los helpers/runners/shaders/ABI/guard congelados no se editan. Los huecos de API legacy no se ocultan ni se arreglan silenciosamente: esta ruta nueva es opt-in y estricta.

Pruebas: petición ligada a escena retenida, ausencia failclosed, primitivas32/64 y signedzero roundtrip, rechazos tipos/clases/cobertura/context/SOURCE/snapshot/caps, fallo roundtrip y modelo. Verificador independiente stdlib sella linaje y coteja byte/word/float_hex/request/negativas y no promotion. Sin imports producción ni replay numérico viejo. Fallos nuevos se preservan sin cambiar umbrales para PASS.

CPU propia1hilo/afinidad1/hijo<=60s, GPU/Blender/encoder/castRN0; reinterpretaciones contadas. No telemetría GPU nueva ni claimlibre. IO/setup/upstream/costes completos UNMEASURED NOT0, no comparación equivalente/velocidad/ganador. CPU reader NO Bpyfloat32/GPU ALU/RT/óptica; U/GEMM no sustituye inferencia scene.
JEV LOCAL fallback sin aval remoto, bloqueado/no retry; histórico03:37 deadline intacto. conf1/v0/v4/0119/0315/nearestV2/caps/bounds/FAILs/archivos ajenos intactos. Sharedboards/checkpoint SINstage, sólo cinco propios versionados, sin SDK/DrJit/Kaggle/push/merge.
Skills: cognición extendida reusa INPUT/proofs por SHA; desarrollo contrato y nueva ruta opt-in con regresiones antes de commit.

Petición Claude ACK ID+SHA del recibo nuevo; sólo artifacts YA EXISTENTES de backend/guard e INPUT whole-domain/grid ORIGINAL ID/path/SHA/bytes, MISMO ORIGINAL INPUT/ABI/gauges/trabajo/salida/costes completos. No cargas de relleno. GPU futura exige reserva exclusiva Claude, gpuq/procesos/RAM/VRAM/temperatura/guard failclosed/deadline nuevo y límites originales; este lector NO es autorización de GPU/promoción/escalado.
