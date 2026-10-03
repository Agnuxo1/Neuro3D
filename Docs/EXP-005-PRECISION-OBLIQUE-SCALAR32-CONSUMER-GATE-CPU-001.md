# PRECISION-OBLIQUE-SCALAR32-CONSUMER-GATE-CPU-001

P1 propio Codex capacity_audit/EXP005. Contrato opt-in nuevo; no modificar los contratos congelados ni ejecutar escritores previos.

## Modelo y regla fija

Padre PRECISION-OBLIQUE-ROOT-PAIR32-WIRE-HOST-001, SHA256 580b012d7921d0130852fa082de6e5cc8bdd066340c790d9849fb381355fc111,159924bytes/296pins. Reutilizar cuatro paquetes hi32/lo32 y sus cotas; no regenerar ni repetir transporte/productos/sumas/raíces previos.

Política EMULATED_RN64_ADD_THEN_RN32_PRESERVE_SEALED_PAIR_SUM_EXACTLY. Ejecutar a+b en Pythonbinary64 y convertir el resultado por struct.pack('<f',v); registrar intermedio64 y candidato32. Esto es EMULACIÓN CPU, no ALU32 nativa, Bpy, Blender, shader ni GPU. No afirmar equivalencia universal entre dos redondeos y RN32 de suma exacta: el oráculo independiente demuestra ambas propiedades para CADA captura probada. Sólo se verifican sumas de estos operandos, no un grafo completo de escena.

Gate FIJO nuevo: preservar EXACTAMENTE Qwire=h32+l32. Si T32!=Qwire, STOP_PROJECTION_LOSS; scalar_word32=null aunque se conservan candidato, ledger, error firmado y cota. Este gate de información no es una tolerancia física ni una certificación de precisión CPU64; aceptar exactitud de proyección sólo preserva la pareja ya degradada por transporte. No cambiar el gate para convertir resultados en PASS.

Input: paquete canónico little-endian8bytes, dos componentes normales/cero, |componente|<=2^33; Qwire positivo<=2^33, Soriginal positivo<=2^66, cota Bwire canónica y encierro heredado positivo verificado. Rechazar entrada subnormal/infinita antes decodificación. Destino subnormal/cero→STOP sin certificado, con ledger y candidato preservados. No subir dominio tras fallo.

## Cota y vínculo a escena

Qwire racional exacto HOST, V64 el intermedio real y T32 el candidato. Registrar Qwire-V64 y Qwire-T32 por separado; no ocultar pérdida previa al cast. Bscalar=Bwire+|Qwire-T32|. Verificar T32-Bscalar>0 y (T32-Bscalar)^2<=Soriginal<=(T32+Bscalar)^2, sin nueva sqrt. El certificado es diagnóstico conservador incluso cuando el gate rechaza la proyección; NO habilita scalar_word32 ni motor.

Por escena, comparar intervalo NOMINAL de candidatos y encierro HOST de extremos. Conservar cajas SOURCE0/DETECTOR0 originales, todos los radios y referencia96 sellada. Incertidumbre de fuente no cancelada. SHA de cada selector ligado a recibo/record/original snapshot/query/reference.14STOP anteriores retenidos, ninguno rescatado. STOP canónico de políticas anteriores permanece como antecedente, no cambiar etiquetas.

La diferencia entre ancho nominal y certificado no prueba que un motor haya perdido una colisión: no ejecutar ni afirmar autointersección, huecos finos del trazador, inferencia completa desde escena ni fase física. Es un bloqueo concreto a sustituir una pareja por escalar sin contrato de precisión.

## Pruebas y costes

Oráculo IEEE64/IEEE32 bit/racional independiente: vecinos/midpoints/tie-to-even para intermedio y candidato, también candidato frente suma exacta de palabras32; bindings a capturas originales. Controles sellados de formato se usan como inputs sin repetir sus casts. Dos NUEVOS controles sintéticos de suma tie-even/tie-odd y un caso de cancelación normal→subnormal.8precontrols/8selectors/8mutations; todos los candidatos/parciales STOP conservados.

Contar RN64_add y RN32_cast separados, llamadas decode y componentes. Ninguna ALU32 nativa medida. Preparación de controles, HOST rational, provenance, IO y coste completo UNKNOWN_NOT_ZERO. Tiempos de QA no son benchmark, igualtrabajo, eficiencia ni velocidad. Capturas grandes en recibo, sin convertir racionales a números JS.

CPU1hilo/afinidad1/hijo<=60s/GPU0. No SDK/DrJit/JEV retry/push/merge. JEV fallback LOCAL explícito sin aval remoto. Sólo cuatro archivos propios revisados/versionados LOCAL; cuatro tableros/checkpoint SINstage. Frozen fixtures conf1/v0/v4/0119/0315/nearestV2, límites/runners/shaders/contratos intactos.

promotion=STOP_SCALAR_LOSS_REAL_CONSUMER_SCENE_PHASE_PHYSICAL_GPU; native_length=null, phase_error_bound=null, wavelength_known=false, phase_certified=false, physical_reference_certified=false. Aun con proyección exacta sintética no hay promoción de motor. Solicitar a Claude ACK ID+SHA y artifacts YA existentes backend/guard/consumo REAL hi-lo e igualtrabajo/salidas/costes completos; no repetir cargas por relleno.

## Evidencia y rechazo preservado

Suite finalPASS9.772327699996822s, captura102454bytes/SHA da7ad8e7117fdf780ddbaf21c94111fff5c677ef2ae04d9d50aed5b9418836f9. Oráculo bit/racionalPASS8.986521599996195s/SHA02b471415221137f4ede29e1750ea4062b3c57c69031b819e60dc054d7bd26f5. APInegativaPASS1.5257659000053536s/SHA c3bee21159ef0992b0488add96761f9edb3e6d59d5ea590033f8973eca422aee: selector que pretende permitir pérdida rechazado y padre ausente SIMULADO,0aritmética adicional.

Dos escenas elegibles, CUATRO proyecciones STOP_PROJECTION_LOSS;0escenas admitidas,14STOP heredados intactos.3controles sintéticos exactos,3controles sintéticos con pérdida (incluye2empates RN32),1STOP normal-input→subnormal-output por cancelación; candidato01000000/parcial preservado, scalar_word32/cert=null.8selectors/8precontrols/8mutations rechazados.

Fino: candidatos ambos0000003e, T32=1/8; pérdidas firmadas ±1/36893488147419103232=±2^-65. Ya el intermedio binary64 pierde esos términos; el oráculo demuestra para estas capturas que también son los redondeos RN32 de la suma exacta. No confundir esta observación con GPU ALU32. Cota compuesta máxima exacta
187072209578355634498994927164605529908595986006017/6901746346790563787434755862277025452451108972170386555162524223799296
scene_length≈2.710505431213761968402636645E-20, aproximadamente0.4999999998835848411557567265 del ancho de referencia. Ancho NOMINAL0 frente encierroHOST≈5.421010862427523372861858483E-20; TODOS radios originales conservados. El certificado diagnóstico no rescata el gate de pérdida.

Exterior: cota compuesta máxima≈1.145057659267223002855067475E-7, ancho nominal0.0041434764862060546875 frente anchoHOST0.004143695796212131569866140412, ratio/ref≈1.000105863573874515958150545. Pérdidas firmadas por sumar la pareja:12739943/75557863725914323419136 y -14883217/75557863725914323419136. Ambos rechazos conservados, sin tolerancia nueva para PASS.

Costes: suite final11sumas RN64+11casts RN32,14decodificaciones de input+10deoutput/38componentes. La ejecución provisional también realizó11+11 y24decodificaciones; su capturaPASS102366bytes/SHA14067ff99793f23c75977ce1afc897eaf8d5af2fa3cc5485e7456f836a74407f y fuentes propias iniciales están preservadas en recibo. Antes del sellado se corrigió etiqueta ambigua new_native_sums=0 a native_ALU32_sums=0; el oráculo prueba igualdad de TODO payload salvo ese renombrado. Ningún resultado/umbral/operación cambiado. Total REAL de ambas ejecuciones22RN64+22RN32/48decodificaciones/76componentes,0ALU32nativa/0productos/0sqrt/0replay de unidades anteriores. HOST/provenance/IO/costes completos UNKNOWN_NOT_ZERO, no equivalencia de rendimiento.

El próximo consumidor útil debe mantener dos palabras (o justificar explícitamente otro presupuesto) y probar aritmética REAL ligada a escena. No escalar ni ejecutar GPU sin guard/deadline/telemetría/reservaClaude exclusivos verificables; pedir artifacts existentes en lugar de cargas de relleno.
