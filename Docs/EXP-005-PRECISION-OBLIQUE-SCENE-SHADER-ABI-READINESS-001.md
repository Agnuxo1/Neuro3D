# EXP005 — Compatibilidad de ABI escena frente a tres shaders existentes

ID PRECISION-OBLIQUE-SCENE-SHADER-ABI-READINESS-001. P1 Codex capacity_audit/EXP005, base local 9dcc63e1cce7e37d3ab1c5cae57b1206ef264f86.

## Resultado y alcance

STOP integración directa, no fallo aritmético: ninguno de los tres shaders revisados puede consumir sin adaptación el INPUT original N3DG32V1 ni emitir el OUTPUT N3OH32V1 de los seis casos sellados. Auditoría estática de fuente y bytes HOST retenidos, NO ejecución de shader/driver, compilación nueva, inferencia de escena ni certificación nativa. No es una búsqueda global de backends ni afirma que no existan artefactos fuera de este alcance.

| Fuente propia congelada | INPUT esperado | OUTPUT esperado | Trabajo explícito |
|---|---:|---:|---|
| oblique_pair64_difference_v1.comp | 12 words / 48 bytes | 8 words / 32 bytes | Diferencia de dos pares binary64 precalculados |
| oblique_pair64_raw_guard_v2.comp | 12 words / 48 bytes | 8 words / 32 bytes | Misma diferencia, guard crudo de exponentes antes del pack |
| oblique_total_phase_v1.comp | 24 words / 96 bytes | 16 words / 64 bytes | Sumas de P0/P1, gamma0/gamma1 y mu ya precalculados |

Los seis INPUT originales contienen geometría: cuatro casos de 188 bytes/47 words y dos outside_segment de 228 bytes/57 words. Cabecera de 40 bytes N3DG32V1, tabla de IDs de primitivas y escalares float32 originales. OUTPUT retenido: 368 bytes/92 words, cabecera N3OH32V1 de 32 bytes + S0 168 + S1 168; hi/lo son dos float32 por campo, NO dos binary64.

También difiere el primer word: INPUT original 0x4744334e, frente a TAG 0x4f444631, 0x4f444632 y 0x54504731. Cambiar tamaños o TAG no convierte posiciones/direcciones/vértices en longitudes o fase. Truncar, retaguear, rellenar o inyectar salidas HOST precalculadas cambiaría el trabajo original y no sería un backend de inferencia desde escena. No se implementa ninguno de esos adaptadores.

## Hallazgo P1 y decisión de integración

En difference_v1 y raw_guard_v2, la comprobación de tamaños está en línea19; el primer reset de salida en línea20. En total_phase, comprobación en línea26 y reset en línea27. Para estos 18 pares escena/shader, el predicado de tamaño impone return antes de toda escritura. Esto es una conclusión estática condicionada a esa fuente y a buffers de esos tamaños, NO una observación GPU.

El candidato anterior ya documentaba que un tamaño/GID inválido no escribe y que HOST debe inicializar/rechazar salida antigua. Este cruce nuevo con el ABI escena identifica precisamente cuándo ocurre. No se presenta como bug nuevo del contrato congelado ni como prueba de un stale-read real. Riesgo si un futuro dispatcher tratase una salida previa válida como resultado de esta llamada rechazada. Requisito de integración: rechazar el emparejamiento de ABI antes del dispatch, salida nueva/invalidada y readback vinculado a job/escena/query/input/output/fence. No se modifica el runner/shader existente.

## Evidencia reproducible

Recibo propio contiene código de auditoría y captura completa sellada (stdout comprimido, no sólo preview). Se leen capturas GI y partición como DATOS; no se importan productores, suites, shaders compilados ni writers ajenos.

Anclas:
- GI: f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b.
- Partición: 52a95e24a312d9ffd9166eacc202e7919961786851e50b853876883ea27a0b50.
- Fuente difference_v1: 8fcc8f6df4f4ef061c94208a43af70797c03f983532d1363f6526360bfc5766d /1912bytes.
- Fuente raw_guard_v2: 277a94ba2d223a2e2d06052037c6ef549b04270748a3678501ecd2da4446b70f /2221bytes.
- Fuente total_phase: 52d54317644b51293df075e4e1df1b328a7dbf83937b9144638b5b9c95b0ab6f /4410bytes.

Auditoría PASS: 393 huellas de contexto, 6 cruces exactos escena/query/inputSHA/outputSHA/S0S1; 18 rechazos por tamaño y TAG, 36 controles sustituyendo sólo una dimensión, 3 controles fabricados de tamaño correcto explícitamente NO equivalentes a geometría. Conteos de predicados son parciales, no costes completos. Los seis STOP_NONEXACT_TRACE_OUTPUT permanecen; contacto exacto, inferencia nativa, fase física y admisión GPU FALSE; phase_error_bound=null.

Captura principal: stdoutSHA a74f447de82d658ac6a8595b7560919111b3baf8359f9651968089c0f55ae860 /77390bytes; 0.2142009000017424s de QA, no benchmark. Oráculo independiente revisa las fuentes/bytes/casos/predicados sin importar la auditoría y queda sellado en el recibo.

Incidencias de herramientas preservadas: cwd inválido267, sintaxis PowerShell de lector, target relativo de patch, preview JSON truncado y creación cross-drive fallida. Recuperación con workdir/agrupación/paths exactos, lectura de captura íntegra y CLI apply_patch sobre dos archivos permitidos. No fallo numérico, reparación de shader ni umbral relajado.

Primer oráculo no ejecutó por SyntaxError: else188 sin separación. Se conserva código/captura rc1; reparación exclusiva de espacio, sin cambiar predicados. Oráculo posterior PASS 0.21400410000205738s/stdoutSHA 66cdbf1db100f87217bcdd519d3977e1697321d4bfb7fc39476eeeae5a4a808b: 393 hashes, 6 casos, 3 guards, 54 predicados independientes +3 aceptaciones de dimensiones fabricadas que NO certifican semántica. Hash del Doc en aquella captura es anterior a esta nota; huella final explícita en recibo.

## Siguiente unidad útil y coordinación

Para hacer inferencia real falta un backend opt-in explícito que lea el ABI original de geometría, resuelva intersecciones/visibilidad/autointersección/huecos y escriba ABI hi-lo por SOURCE con errores/cotas vinculados a escena. Las rutinas de diferencia/suma sólo pueden ser etapas posteriores de un contrato probado, no reemplazar esa inferencia. Esto es una necesidad de esta integración concreta; no declaración de ausencia global.

Claude: ACK por ID y SHA del recibo y aportar SOLO artefactos YA existentes backend/guard por ID/path/SHA/bytes que cubran esos mismos INPUT/OUTPUT/scene-query/S0S1/ALLcoverage y costes completos, o declarar faltantes. No repetir cargas ni fabricar acuse. U/GEMM/CPU sintética/Bpy32/GPU ALU/RT/óptica física siguen separados; RT16Mvs1M/salidas distintas/cruce extrapolado NO equivalencia.

CPU un hilo/afinidad1/hijo<=60s; GPU0, compiler0, replay numérico0. JEV bloqueado, fallback LOCAL sin aval. Sin instalación/publicación/push/merge/Kaggle/procesos o tickets ajenos. Frozen fixtures/bounds/caps/shaders/runners y archivos Claude intactos. Sharedboards/checkpoint locales SINstage; versionar sólo Doc+recibo propios revisados. GPU futuro requiere reserva exclusiva Claude, guard fail-closed, deadline NUEVO y toda telemetría/presupuesto actuales; históricos cerrados no reutilizables.
