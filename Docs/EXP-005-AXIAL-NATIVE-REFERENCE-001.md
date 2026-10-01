# AXIAL-NATIVE-REFERENCE-001 — referencia fija ORIGINAL, cotas CPU

Opt-in de Codex en capacity_audit/EXP005, base fe9d238. No backend GPU.
Consume exclusivamente paquetes INPUT de INGRESS-001 y reevalúa el selector
propio EVENTS-001. Trabajo redundante declarado; no ejecuta productores antiguos,
writers ajenos, suites congeladas ni barridos. JEV bloqueado: fallback LOCAL sin aval.

Perfil limitado: +/-X, YZ exacta, dos owners espejo-terminal y dos eventos.
La precondición exactYZ se contrastó offline en los 13 inputs retenidos;
un SHA arbitrario aportado por caller NO prueba exactitud, autenticidad ni coherencia.
Referencia worldpoint ORIGINAL fija / modo ideal unit-X. Bits binary64 de
punto/dirección originales transportados intactos. La ABI HOST existente de R
se consume sin nuevo encoder; cinco referencias ausentes NO se reconstruyen.

En palabras signed51216limbs, escala BU*2^149, usando radios existentes:

    Lgeom = sigma*(2*M-S-D)
    correction = sigma*(D-R)
    Lref = sigma*(2*M-S-R)

El MISMO D se cancela; Lref se acota directamente. La suma de dos intervalos
independientes se registra sólo como diagnóstico NO usado. R no se sustituye
silenciosamente por D. Lref puede ser firmada o cero; no es longitud física
positiva. Lambda tiene cota inferior estrictamente positiva. Se rechazan
dominios incorrectos y overflow, sin epsilon, caps/radios relajados ni FTZ.

Este componente evalúa enclosures, NO divide Lref/lambda, calcula fase,
error de fase, campo, fuente compleja, reducción, potencia o aceptación de red.
`reference_bounds_evaluated_CPU_only` NO es `accepted_terminal_reference_CPU_only`;
este último permanece false, al igual que fase/fullpipeline/admisión GPU.
Los dos phaseFAIL con geometría válida no se promueven. Gauges/IDs y caps originales
se mantienen ligados al input. Campos originales, cap0 y referencias HOST ausentes
NO se convierten en PASS ni se cambian en silencio.

Falta ABI nativa explícita de geometría/longitud/λ ORIGINAL binary64 para cota
de fase de esta implementación word-only; valores JSON originales no se
reinterpretan como transporte nativo gratuito. Siguiente unidad: contrato de
originales y costes explícitos antes de fase/GLSL/GPU, conservando FAIL.

Tests: lectura de artefactos retenidos y controles sintéticos de R!=D,
cancelación correlacionada, dos signos, referencias negativas/cero, overflow,
tipo/orden, modo/frame inválidos, λ<=0, alias y preservación de flags/caps.
Oráculo independiente stdlib: huellas y todas las operaciones instrumentadas,
inputs enclosures contra ORIGINAL y contraste con nueve respuestas retenidas.
Resultados y código verificable en respuesta por ID, con SHA tras cierre.

Validación: 8tests PASS, rc0/0,4604301s final; primera versión también PASS
rc0/0,5014161s, retenida. Cambio posterior sólo añadió control explícito
HOSTref ausente con geometría válida, sin alterar producción/caps/frozen.
13casos/14fuentes: 8referencias HOST presentes, 5ausentes, 9enclosures
calculadas/contrastadas y 5rechazos upstream preservados. Dos phaseFAIL
siguen sin promoción. Oráculo independiente comprueba 179huellas,
226checks de bits/enclosures contra ORIGINAL y 8controles aritméticos,
además del nuevo control HOSTref ausente con input/receipt propios.
Costes son conteos de llamadas del espejo CPU, incluidos controles,
NO tiempos de hardware nativo, costes completos GPU/RT ni energía.
Oráculo final rc0/0,3750223s; 5423llamadas instrumentadas:
1011add/1499sub/555mul/654compare/1704decode32; 1overflow mul esperado.
No FAIL numérico ni cambio de caps; producción igual en ambas versiones.

Nada aquí confirma GLSL compilado, GPU ALU digital, Bpyfloat32, RT, óptica
física, rendimiento, energía, eficiencia, motor ganador o costes completos.
CPU 1hilo/hijo<=60s. Sin reserva ni carga GPU. Frozen/runners/shaders intactos.
Claude conserva RT; sólo pedir artefactos YA existentes que correspondan a
esta ABI/escena/referencia y protocolo igual trabajo/salidas/costes completos.
Guard0337 histórico cerrado NO admisión nueva. Sharedboards locales SINstage.
