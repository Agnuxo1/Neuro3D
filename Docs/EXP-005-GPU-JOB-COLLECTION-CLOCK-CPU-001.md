# GPU-JOB-COLLECTION-CLOCK-CPU-001

P1 Codex / capacity_audit-EXP005. Opt-in `gpu-job-collection-clock-CPU-v1`.
Base e78fbd9bc986636ce137aa3c8c6d520ff9e0a67d.
Acuse collector-isolation CPU SHA 8e24696b7b012ec444fdc78c1045295f1b67e2112dcb722a2b0a4f23ccd83aad.

## Contrato

El monitor congelado recibe UTC/monotonic antes de llamar al collector. En un control nuevo, elapsed declarado0 y reloj previo0.9s permiten CONTINUE; al terminar a1s se debería rechazar elapsed0. No se modifica ese monitor ni sus tests/umbrales.

Adaptador nuevo: toma pares de reloj OS secuenciales (time_ns, monotonic_ns), valida rollback/gap antes de collector y al terminar, y pasa la marca POSTERIOR al monitor congelado. No modifica snapshot/elapsed ni presupuestos/deadlines de entrada. STOP del adaptador es terminal antes de volver a leer reloj/callback; KeyboardInterrupt del collector se propaga después de latch STOP. El monitor interior puede conservar CONTROL_READY cuando el adaptador ya está STOP; sólo state del adaptador es válido para este contrato, no inspeccionar frozen_view como permiso.

Acceptance: contraejemplo previo/endpoint contrastado, gap>1s/rollback/error reloj/stale/deadline rechazados; valid control conservado; una observación real de reloj OS con snapshot explícitamente ficticio y un timeout real de worker CPU propio fijo (0.25s + cleanup1s). Evidencia completa retenida. No repetir suite anterior/barridos.

## Límites de evidencia y seguridad

Sólo CPU sintética. Relojes OS no autentican telemetría de recursos ni reservan GPU; lectura secuencial NO par atómico. No reloj externo inyectable en API, pero los controles deterministas usan mocks declarados. Cadencia máxima1s HEREDADA sin relajación; crossing-second usa límite EXACTO1s y no cambia umbral.

Callback arbitrario no tiene timeout en este adaptador: debe usar collector previamente acotado. El control real usa únicamente el worker SHA fijo propio; no ejecuta ningún writer ajeno, Blender, GPU, gpuq ni kill/cancel ajenos. Wrapper suite CPU afinidad1/OMP-BLAS1/timeout60s, I/O de subprocess stdlib puede usar hilos adicionales. No afirmar cobertura para collector hostil/progenie/OSstall ni guard completo de workload GPU. Entre POST y policy sigue existiendo pequeña ventana; no atomicidad/TOCTOU/clock-auth proof.

GPU_job_admission, GPU_executed, live_resource_telemetry, runtime_GPU_guard, reservation_authenticated, clock_pair_atomic_authenticated y arbitrary_callback_timeout_implemented SIEMPRE false. Snapshot ficticio no reetiquetado como live. Nueva fecha del plan del control OS es sólo fixture NUEVO CPU; histórico0337 CLOSED/deadline/fixtures previos intactos. Ningún SDK/DrJit/Kaggle/push/merge. JEV bloqueado: fallback LOCAL sin aval remoto/sin reintento. Sharedboards locales SINstage; sólo propios revisados versionados.

CPU sintética NO Bpyfloat32, GPU ALU digital, RT ni óptica física. Costes completos UNMEASURED_NOT_ZERO; test-time no speedup/eficiencia/ganador. Auditorías RT-AUD001/RT-CAP006 ya cerradas no repetidas. Petición Claude: artifacts YA EXISTENTES de backend/guard/reserva y MISMO ORIGINAL-decoder-ABI-gauges-work/fullcosts con ID/path/SHA/bytes; no cargas de relleno. Prioridad de precisión de escena/auto-intersección/huecos/hi-lo/fuentes/cota fase conserva sus STOPs, no promovida por esta unidad.

Skills cognición extendida y feature-development: reusar fixtures lossless pinneados y corregir frontera temporal mediante adaptador nuevo, no editar contrato congelado.

## Resultado retenido

Suite nueva 7 tests PASS, 16 controles (14 STOP y 2 CONTINUE CPU); contraejemplo frozen-pre CONTINUE frente a endpoint STOP por elapsed_monotonic_mismatch, snapshot intacto y retry idéntico sin collector/reloj. Un hijo CPU propio real TIMEOUT con cleanup confirmado y lectura real OS de reloj con recursos sintéticos. Sin nuevos fallos inesperados; negativos esperados retenidos.
Suite afinidad1/OMP-BLAS1/hijo60s: 0.5829888000153005 s, stdout 26786 bytes SHA a2dfb8622405f99ff53cf0ff24490c559434d9e7936f2db541ab6473acb949bf. Salida completa comprimida en recibo, no truncada. El oráculo independiente verifica hashes y evidencia retenida sin imports de producción ni hijos; se ejecutará antes/después del commit. Estos tiempos no son costes completos de inferencia.
