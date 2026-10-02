# EXP005 — AXIAL-GEOMETRY-HILO-CPU-001
P1 Codex; opt-in. Predecesor edd1d911bd46bb79236fa625d013931bf9d25664.
Contrato anterior, runners, shaders, fixtures y umbrales intactos.

## Contrato y alcance
Dos fuentes elegibles por receipt ORIGINAL-SOURCE; otras 17 siguen STOP, sin ejecución parcial de two_sources.
38 escalares por escena: vértices M/D, posición/dirección de la fuente seleccionada, origen/dirección de referencia, longitud de onda y fase de espejo nula. No amplitud SOURCE.
Cada escalar: hi=RN32(x), residual=RN64(x-hi), lo=RN32(residual), decoded=RN64(hi+lo). Sólo normal-o-cero; fail-closed para no finitos, overflow y subnormales seleccionados. Signos IEEE, sin canonicalización.
304 bytes LE por escena, paths ordenados, SHA y binding a bits ORIGINAL. Transporte propio experimental, NO reemplaza ABI congelada.
Intersecciones, barycentrías y selector son racionales exactos sobre coordenadas decodificadas; NO intersección nativa RN64 ni Bpy/GPU/RT. Las claves ORIGINAL del adaptador de trace nombran aquí entradas decodificadas, identificadas explícitamente.
Mismos primitive/owner y quarter index; contactos, bordes, ties o cambio de rama producen STOP. Hueco fino debe seguir positivo sin epsilon.
Referencia fija: receipt ORIGINAL previo; no se vuelve a ejecutar su productor, Horner o SOURCE.

## Cargos por punto (BU y rad)
Lgeo = sign(2M-S-D); Lref = sign(D-R); Leff = sign(2M-S-R).
Egeo = 2eM+eS+eD; Eref=eD+eR. Se conservan ambos cargos y su suma no correlacionada.
D se cancela sólo bajo identidad compartida verificada; Eeff=2eM+eS+eR.
Eq <= Eeff/|lambda_dec| + |Leff_original| eLambda/(|lambda_dec| |lambda_original|).
Ephase <= 2 pi_upper Eq + Eargument_RN64_decoded.
Cap ORIGINAL 1e-12 rad inmutable; fits por punto NO aceptación uniforme o de pipeline.

## Verificación y costes
4 tests propios y oráculo independiente stdlib con redondeo IEEE entero, reconstrucción de transporte/escena/roots y cargos; pins heredados, fallos SOURCE 8/12 retenidos.
CPU 1 hilo/afinidad1/hijo <=60s. Principal: 152 casts32, 76 sub64, 76 add64; 2 casts64 y 2 mul64 de argumento, 16 root records. Probes: 6 ops64 +4 casts32; controles/negativos separados.
Tiempo total de suite se mide, NO rendimiento backend ni comparación igual-trabajo. IO/pins/setup/racionales/costes restantes no medidos, no cero.
GPU/Blender/RT/óptica física 0. JEV bloqueado: fallback local explícito sin aval remoto.
