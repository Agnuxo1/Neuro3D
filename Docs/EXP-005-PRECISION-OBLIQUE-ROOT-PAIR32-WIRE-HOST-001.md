# PRECISION-OBLIQUE-ROOT-PAIR32-WIRE-HOST-001

Unidad P1 propia Codex capacity_audit/EXP005. Opt-in CPU de formato, no Bpy, Blender, shader, GPU ALU, RT ni óptica física.

## Contrato cerrado

Padre sellado PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001, SHA256 6ef5e1e46e9e9f37c4c7051d064598191e76c93737325dc3683e4aeb3e082eef (168330 bytes, 292 pins). Reutilizar sus cuatro parejas nativas y cajas originales; 14 STOP heredados intactos. Leer y probar las capturas no vuelve a ejecutar sus productos, sumas, raíces, runners ni escritores.

Política SEALED_NATIVE_PAIR_INDEPENDENT_COMPONENT_RN32_WIRE_HOST_COMPOSITION: convertir cada componente CPU64 por separado mediante struct.pack('<f', x), little-endian [hi32,lo32], paquete de 8 bytes. No recalcular lo con el residuo del redondeo de hi. No renormalizar ni sustituir esta política por una compresión HOST. Entrada normal/cero, valor absoluto <=2^33, exactamente dos palabras. El cero firmado se conserva. Un destino subnormal o no-cero que redondea a cero provoca STOP; mantener ledger, número de conversiones y bytes parciales, sin paquete aceptado ni cota publicada. No relajar el dominio para aceptar controles.

struct.unpack('<ff', packet) comprueba el formato CPU. Sus dos valores se interpretan como racionales exactos HOST; NO se suman mediante ALU float32. No es una prueba de consumo Bpy/shader ni de transporte real a GPU. La suma exacta de dos float32 no implica que un consumidor escalar float32 conserve lo.

## Composición verificable de cotas

Q64=h64+l64; Q32=h32+l32; E=Q64-Q32, todas sumas racionales exactas HOST. B64 es la cota numérica aislada sellada del padre. B32=B64+|E| por desigualdad triangular. Verificar Q32-B32>0 y (Q32-B32)^2<=S<=(Q32+B32)^2 contra el MISMO S original, sin evaluar sqrt de nuevo. Para extremos inferior/superior usar el límite inferior/superior de las respectivas cotas. Conservar todos los radios SOURCE/DETECTOR y la referencia96 sellada; no tratar el ancho geométrico como error de redondeo ni cancelarlo.

Diagnóstico separado SIMULATED_CONSUMER_DROPS_LO_NOT_BPY_SHADER: Qsingle=h32, pérdida Q32-Qsingle, Bsingle=B32+|Q32-Qsingle|. El intervalo nominal puede colapsar aun cuando la cota conserva incertidumbre. No atribuir este comportamiento a un backend no ejecutado.

La política independiente puede perder precisión por el redondeo de hi32; el antiguo lo64 no compensa necesariamente esa pérdida. El éxito del certificado significa encierro conservador, NO precisión equivalente a CPU64 ni éxito de motor.

## Validación y costes

Oráculo independiente IEEE32 por bits: significando/exponente exactos, vecinos enteros, midpoints y tie-to-even; no usar struct.pack float32 como oráculo. Probar orden/endianness/decodificación, signos de cero, ambos limbs, error firmado, composición de cota y bindings SHA a escena/query/cajas originales. Controles sintéticos aparte: exacto/cero firmado, dos empates par/impar, bajo normal, underflow-a-cero y subnormal, entradas inválidas, selectors cerrados y mutations rechazadas. Los controles no son nuevas escenas.

Cuatro paquetes de escena=8 RN32 y 4 decodificaciones; cuatro controles aceptados=8 RN32 y 4 decodificaciones; dos STOP negativos=4 RN32 sin decodificación. Total suite20 RN32,8 decodificaciones.0productos/0sumas nativas/0sqrt/0replay numérico previo. HOST rational, preparación, provenance, IO y coste completo UNKNOWN_NOT_ZERO, nunca cero inferido. Tiempos de QA no constituyen benchmark ni comparación igualtrabajo.

CPU1hilo/afinidad1/hijo<=60s. Sin GPU, reserva GPU ni afirmación GPU libre. Fixtures conf1/v0/v4/0119/0315/nearestV2, límites, shaders/runners/contratos congelados intactos. No SDK/DrJit/JEV retry/push/merge. Fallback LOCAL explícito, sin aval JEV.

## Límite de aceptación

promotion=STOP_CONSUMER_BPY_SHADER_SCENE_PHASE_PHYSICAL_GPU; native_length=null, phase_error_bound=null, wavelength_known=false, phase_certified=false. Ni inferencia desde escena completa ni autointersección/huecos del motor están certificados por esta unidad. No promover/escalar hasta componer consumo real y error de escena/referencia/fase; U/GEMM no sustituye inferencia desde escena.

Contrato, implementación, pruebas y recibo propios revisados/versionados LOCAL antes de cualquier eventual GPU. Cuatro tableros locales SINstage. Pedir a Claude ACK por ID+SHA y SOLO artifacts YA existentes backend/guard fail-closed e igualtrabajo/salidas/costes completos; no repetir cargas por relleno.

## Evidencia de esta ejecución

SuitePASS8.230896699998993s, captura102886bytes/SHA256 e726e6004ac43c8a9b6152974085cb0eede90870ec2ca7836384a6ed1e0251cb. Oráculo independientePASS7.639472700000624s/SHA256 9c1ee3898cdccf899af46461dd0ec61ef921ab01fc570f0e891145f0027a6791. Estos tiempos son QA, no rendimiento comparable.

Dos escenas/cuatro paquetes aceptados,14STOP retenidos,8selectors y8mutations rechazados,8precontrols. Dos STOP de segundo componente: underflow-a-cero2^-200 y subnormal2^-140; mantener8bytes parciales/2casts y certificado=null. API adicionalPASS1.3611428000003798s: selector público inválido, ausencia de padre SIMULADA sin modificar archivos y STOP en primer componente2^-200 (1cast/4bytes parciales). Total21 RN32/8 decodificaciones,0productos/0sumas nativas/0sqrt/0replay.

Caso fino, paquetes 0000003e0000009f y 0000003e0000001f: hi32=1/8, lo32=-2^-65 y +2^-65. Cota compuesta máxima exacta:
60968923268576921303392636620505089/6901746346790563787434755862277025452451108972170386555162524223799296
scene_length≈8.833840046429490623690115971E-36. Cota/ancho referencia≈1.629555864866302623667183365E-16. Ancho HOST≈5.421010862427523372861858483E-20; ratio/referencia96≈0.9999999997671695782823150272. Referencia96 contiene su propio redondeo; ratio<1 no es raíz exacta ni ganador físico. La incertidumbre geométrica original permanece. Descarta-lo SIMULADO: ancho nominal0, pero cota HOST conserva≈5.421e-20. No afirmar que Blender/shader haya hecho esa operación.

Caso exterior: cota compuesta máxima≈1.145057657581105586114162346E-7, ancho HOST≈0.004143695796211400390909038003 y ratio/referencia≈1.000105863573698041526077512. La conversión independiente de hi pierde precisión; lo sellado NO fue corregido para compensarla. Certificado conservador aprobado, equivalencia de precisión CPU64 NO demostrada. Error firmado y todos racionales exactos quedan en captura.

Fallo inicial de sintaxis del test (0RN/0stdout) preservado en recibo; corregido un paréntesis, sin cambios de contrato/dominio/umbral. Incidentes de creación de recibo por límite de longitud Windows y AddFile denegado preservados como infraestructura; recuperación con apply_patch dividido y permiso de archivo propio, sin evasión ni cambios ajenos.

Aún STOP consumidor Bpy/shader, inferencia completa desde escena, autointersección/huecos del motor y fase/referencia física. Pedir artifacts existentes; no repetir cargas para completar casillas.
