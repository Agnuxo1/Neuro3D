# AXIAL-GEOMETRY-WORDS-001 — geometría desde ABI de escena, CPU entero

Opt-in scene-hilo32-axial-geometry-signed512-CPU-v1. Packer escena congelado
y split_double puro: world triangles/source xyz/direction/lambda reales,
owners/sourceIDs ordenados y binding original; NOhits/longitudes suministrados.
El ABI nuevo es un modelo HOST, no el ABI GPU previamente ejecutado:
centros son suma EXACTA limbs32, NO decodefloat64 silencioso. Los radios
HOST ceil a unidades2^-149 cubren error de encoding y extra radius declarado;
no se aumenta ninguna fixture/budget. YZ original debe ser exacto/invariante.
Solo normal/cero32; subnormales/NaN/Inf/bool y overflow512 rechazan, sin FTZ.

Core branches checked signed512, escala2^-149. Barycentría YZ mediante
determinantes enteros: interior estricto, frontera excluida sin snap/epsilon.
PlanoX único compartido porowner, origen derivado de escena. Selección por
intervalos positivos/competidor separado. Reflection unit X exacta ysalida
derivada del MISMO plano aceptado: solo eseowner tiene t=0 exento; otroowner
contact0 rechaza. No caller previousprimitive ni rayorigin suministrados.
Longitud completa correlacionada sign*(2*M-S-D), NO sumas independientes
que pierdan doblecargo del espejo. Perfil exactamente1mirror luego terminal.
Fase HOST referida a fuente original:8*max|Lbox/lambdabox-Loriginal/lambdaoriginal|,
2pi<8 cota conservadora, mirror ORIGINALphase0. No fase espejo general.
Presupuesto original explícito porfuente; topología PASS no implica phasePASS.

CPU entero sintético, NO implementación nativa/shader/GPU ALU/Bpy/RT/física/
campos/auth/fullpipeline o escala. Bounds de encoding HOST no certifican
error shader/geometría nativa. Coste core: nodos enteros trazados+worddecodes;
HOSTpack/originalbound/IO/memoria/energía/guard/fullcost separados NOmedidos.
Contrato y tests nuevos guiados por feature-development, huellas reutilizadas
por codex-extended-cognition. Frozen/runners/shaders/fixtures/FAIL intactos.
JEV bloqueado/fallback local sin aval ni reintento. Un hilo/hijo<=60s.

Claude acuseID/SHA y SOLOartifacts0337 geometry/limbs/bindings/backendguard
YA existentes y contrato igualtrabajo/costescompletos, sin cargas de relleno.
Guardfailclosed/reserva/deadline NUEVO porjob antes GPU; histórico intacto.
Sharedboards/checkpoint locales SINstage. Próximo: validar/native ABI/rango
antes transportar longitud a quotient/selector; no promoción automática.

## Evidencia propia verificada (2026-10-01)

8 tests PASS rc0/0,8827474s: 13 escenas nuevas, 14 fuentes, 1706 nodos
enteros trazados. 9 fuentes aceptan geometría, SOLO7 aceptan presupuesto
de fase; 5 fuentes rechazan topología/contacto/frontera. Gap2^-30 desde.1
resuelve; nextafter(.1) colapsa y RECHAZA. No afirmación de todos los huecos.
Radio declarado1/128: longitud[19/32,21/32] BU, cota fase2rad<=budget2;
no replica conf1 ni sube sus bounds. Escenas noexactas/lambda transportada
pueden conservar geometría y FALLAR fase con budget0. Fuentes separadas.

Validador independiente SINimportar producción: 90pins congelados/93huellas,
1706 operaciones signed512 verificadas, 72 esquinas geométricas +144 esquinas
longitud/lambda y9 referencias desde escena/fuente/lambda ORIGINALES;
rc0/0,1824696s. Geometría de esquinas mueve planos porowner compartido,
no vértices arbitrarios/diámetros-YZ/escenas generales. Evidencia raw completa
705716bytes SHA8087c4d6d1700f5c66f0b6e538aeccb28869cc5939b70e6918637e58d83d62b1.

Fallo inicial8errores preservado con SHA/código/raw/stderr: adaptador HOST
llamaba parser de bound serializado para int/Fraction. Fix SOLOmódulo nuevo
a exact_nonnegative; presupuesto numérico y frozen intactos. Se agregaron
rechazos bool/negativo/Inf/NaN de budget. Captura intermedia truncada NO se
trata como evidencia raw válida; fallo de validación preservado en reporte.
No se repitieron suites congeladas; última ejecución cubre tests propios
cambiados. No campos/origen-relativo/selector desde esta geometría ni motor
nativo; integración con quotient requiere contrato y nuevos cargos antes GPU.
