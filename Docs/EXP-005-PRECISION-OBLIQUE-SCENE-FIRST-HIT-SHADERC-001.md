# EXP005 — Primer impacto desde geometría original, candidato opt-in

ID PRECISION-OBLIQUE-SCENE-FIRST-HIT-SHADERC-001. Codex capacity_audit/EXP005, base f6d8dd148a7f15532a4f1da1f5527e830c01b41e.
Skills: desarrollo/pruebas Python y cognición extendida, sin agentes. JEV bloqueado por seguridad: fallback LOCAL, no aval/retry.

## Contrato congelable del candidato nuevo

Objetivo acotado: shader GLSL compute que consume directamente INPUT N3DG32V1 ya sellado de escena original, recorre TODAS las primitivas por S0 y S1 y calcula candidatos de primer impacto t/u/v. No recibe impactos/longitudes/normal/fase previamente calculados. No adapters al ABI aritmético anterior, no U/GEMM/lookup ni simulación presentada como GPU.

No es un backend completo: no reflexión, segundo segmento, visibilidad de todo el camino, exclusión robusta de autointersección, transporte hi-lo float32, cota de longitud ni fase. Salida nueva N3FH64V1 NO equivale a N3OH32V1 de 368 bytes; no se pasa a consumidores existentes. TODOS los resultados permanecen NO CERTIFICADOS.

INPUT: cabecera original40bytes little-endian (magic/version/SOURCEcount2/triangle_count/scalar_count/tablecount/rootID/detectorID/reserved0), IDtable y escalares binary32 originales. n=1..64, count=17+9n, words=10+n+count; IDs únicos <2^31/root-det distintos y presentes. Las fuentes conservan posiciones/direcciones sin normalización; no se ignora ninguna primitiva. Todos los words se validan finitos, normal-o-positive-zero y no subnormal/negative-zero ANTES de uintBitsToFloat; luego |v|<=10^6, lambda original>0 y ambas direcciones no nulas. Es el dominio original del ingress, no aumento de bounds/conf1/caps.

OUTPUT: 112bytes/28 uint32 little-endian. Header8words: magic N3FH64V1, version1, SOURCEcount2, SOURCEstride10, UNCERTIFIEDflag1, triangle_count, certified_flags0. Dos records10words: SOURCEordinal0/1, state, chosen_primitive_id o0xffffffff, triangle_tests=n, t/u/v cada uno dos uint32 de binary64 (lowword/highword). Esto NO es hi-lo float32 ni certificado exacto. Orden S0/S1 no fusionado; no SOURCE-field óptico.

State1=hitcandidate,2=nohitcandidate,3=ambiguo(paralelo/degenerado/borde/no finito),4=contacto t==0,5=empate t==best. Ninguno es PASS físico/geométrico. Se recorren todas primitivas incluso ante ambigüedad; sólo t>0 y interior candidato. No epsilon arbitrario ni exclusión por primitive_id. El mismo root/detector declarado se valida pero NO se fuerza a ganar.

Precise GLSL limita contracción solicitada en operaciones explícitas, NO demuestra RNE/fp64 correcto del driver. Möller–Trumbore binary64 candidato puede perder robustez de signos/cancelaciones/empates. El modelo Python FP64 no prueba equivalencia bit a bit shader/driver; el contraste exacto Fraction desde binary32 sólo diagnostica errores, no certifica el backend. Criterio de diagnóstico zero-error explícito, sin tolerancia ni relajación de umbral; cualquier error nozero/clasificación distinta se conserva como PRECISION_STOP.

Guard de fuente: gid distinto de0 o outputextent!=28 retorna sin escribir. HOST futuro debe invalidar salida nueva y rechazar esos casos antesdispatch. Para salida28, se invalidan todos los words antes de validar entrada; todos los STOPinput mantienen magic0. Magic final es publicación lógica, NO fence/atomicidad/runtime proof. No guard GPU se declara probado aquí; permisos, telemetría, reserva/deadline y fence/readback siguen STOP.

## Plan de pruebas propio CPU

Sólo test nuevo, stdlib Python3.13, CPU1hilo/afinidad1/hijo<=60s. Sin import/ejecución de productores o escritores ajenos: leer capturas selladas como DATOS. 394 pins contexto de readiness, GI original SHA f4814286200766db8494df3f99ff7653d7cf038bd1f51cd34491206a0537016b; readiness SHA f0844047f70c2f56856d4b4796c8b840e8e48dfa25231df1c46d02c8b4ada24e.

6 INPUT originales/12 SOURCE, CPU nuevo first-hit vs Fraction independiente de output retenido (se calcula desde INPUT, no se inyecta referencia en shader). Negativos de cabecera/ID/extents/IEEEdominio/lambda/direcciones; API cerrada contra otra escena/bool/unknown; controles de etapa FABRICADOS para t0/degenerado/empate. Conservar fallos y comparación exacta completa.

Compilar sólo NEW shader y syntaxnegative, dos llamadas CPU previstas, DLL ya existente D:/TOOLS/Blender/blender-4.5.14-windows-x64/blender.shared/shaderc_shared.dll SHA d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b. Target Vulkan1.0/compute2/main/optimization0. Versión textual UNKNOWN identidadSHA. No SDK/DrJit/instalación ni cargasGPU. BinarySPIRV completo sellado en recibo, encabezado/instrucciones/Float64 revisados, NO SPIRV-Tools validación/CFG-driver-IEEEcert.

## Estado

Implementación nueva y contraste CPU cerrados; precisión/nativo/contacto/visibilidad/fase STOP. Fuente SHAbe70c31483ddadb6e750741151acd9f4bae26703a0647e314d750fc1af3641b3. Compilación positiva status0/errors0/warnings0; SPIRV18648bytes SHAb00009bb50481212c8caff2bedac475d18774052171dd01f88c8f93a67ef3589,1250instrucciones/Float64; candidato sólo CPUcompile, nunca GPU.

Suite inicial PASS de controles (0.4647510999930091sQA/stdoutSHA5f810d236704a892ea6597aa2c9f2889528e5f0cca7a5976cea5c1620ddcc1d4/93729bytes), pero PRECISION_STOP: 6 INPUT originales/12SOURCE/28pruebasprimaria/16hits contrastados. Todas las 12 selecciones de candidato apuntan al primitive1; clasificación coincide sólo en esos casos, NO certifica robustez universal. 16 filas de hit contienen errores binary64 nozero frente a Fraction (clasificaciones distintas0). Se conservan signos/magnitudes/casos completos, sin cambiar zero-error ni caps. Por ejemplo bary u error -1/54043195528445952 y v -1/216172782113783808; NO error RAD/fase ni test de driver, no elevarlos a cota de presupuesto.

21 negativos INPUT,3 selectores internos y3 controles de etapa fabricados (contacto0→state4,degenerado→3,empate→5) PASS. El helper prepare pertenece al test, acepta su contexto interno: NO API autenticada de un dispatcher real ni permiso GPU. Dos únicas llamadas compiler del turno: NEW positivo y syntaxnegative status2/errors1/SPIRVvacío, diagnóstico preservado. No nueva compilación de fuente unchanged por añadir codec.

Después se añadió codec interno N3FH64V1: seis controles de112bytes procedentes del cálculo CPU NUEVO retenido, NO device-readback ni referencia inyectada en shader. Probe enfocado sólo words/codec (0.11468890000833198sQA/stdoutSHAf3138509df46fe80f9f802b54a5e46e416d76ff8e11b17828a8b86475157e393/6411bytes): 6OUTPUT/13mutaciones magic-version-SOURCEstride-uncertifiedflag-certifiedflags-state-extents-nonfinite STOP. Compiler0/replaygeometría0/aritméticaFP0 en ese probe. Fuente inicial del test y huella c496265f9a36a3e097922c428926c8ab734fd21d9c037d2f74f0497f9d43baae preservadas. Suite completa inicial + codec enfocado de versión final; no afirmar una segunda suite completa compilada.

Oráculo independiente sin importar nuevo core/test/compilador/oldproductores PASS (0.25929180000093766sQA/stdoutSHAd32f86ef9e0cc13bfeeda981f69fd4f133166eb385399c3f8033572078c442ac): plano/normal y bary Gram alternativos28pruebas,16hits/16errores nozero exactos/12selecciones/6codec/21+3+3+13negativos,394contextpins+own3. Binario inspeccionado con int.from_bytes y21IDs aritméticosFloat64 NoContraction estáticos; NO control de redondeo/memoria/CFGdriver ni validez SPIRV-Tools. La huella Doc en ese primer oráculo antecede esta nota; pin final explícito en recibo y verificación final.

Costes de operaciones/hash/parse/IO/compilación/modelos/checker/QA NO instrumentados completos; tiempos anteriores son QA, no velocidad/eficiencia/motor ganador. No fallos de ejecución observados en nueva suite/probe/oráculo; syntaxnegative y16fallos de exactitud permanecen. No se repara el redondeo cambiando tolerancias. Próxima unidad propia útil: presupuestos/cotas de primerimpacto ligados a escena antes de enlazar reflexión/transportehi-lo; contrato y prueba sin promoción.
GPU/Bpy/RT0, phase_error_bound=null/nativeIEEE/contactexact/sceneauth/fase FALSE; costes UNKNOWN_NOT_ZERO, QA no benchmark. Fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/caps/runners/shaders congelados y archivos Claude intactos. Own4 sólo versionar tras revisión; sharedboards/checkpoint locales SINstage.

Claude: aportar SOLO artifacts YAexistentes porID/path/SHA/bytes mismos INPUToriginal/OUTPUTABI/S0S1/scene-query/ALLcoverage/nativeguardruntime/cota material-gauge-lambda-reference/igualtrabajo-salidas-costes completos, o declarar faltantes; no inventar ACK/cargasrelleno. RT16Mvs1M/salidas diferentes/extrapoladoNOequalwork/redRT; CPU sintética/Bpy32/GPU ALU/RT/óptica física separados.

Antes de GPU: contrato/tests/commit propios, reserva exclusiva Claude, guard fail-closed, deadline NUEVO verificable; gpuq/procesos/RAMVRAM/temp actuales, freeRAM>=4GiB tras presupuesto>=1024bytes/celda+márgenes/temporales, VRAMtotal<=18GiB/temp<=80C/pilotos120/hijos600; noMLP32768/límites0x9F. Ventana/deadline/overrides históricos cerrados intactos/no reutilizados. No push/merge/publicación/Kaggle/procesos-tickets ajenos.
