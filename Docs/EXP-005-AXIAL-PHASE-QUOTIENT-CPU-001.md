# AXIAL-PHASE-QUOTIENT-001: argumento de fase geométrica CPU

Base d20b64e. Opt-in axial-phase-quotient-5rn32-CPU-v1. Unidad acotada:
paths/cotas/sourceID/gauge/bindings retenidos por SHA, sin reconstruir escena
ni ejecutar productor/reducción/detector/suites/barridos. No acepta campos
terminales ni sustituto de escena. Modelo CPU racional, NO GPU/ALU/RT/Bpy.

Longitud L retenida se codifica en dos limbs32 SOLOCPU; cobrar error de
codificación. Esto NOimplementa reconstrucción geométrica nativa desde ABI.
Lambda debe ser singleton positivo del intervalo retenido y representable
exacto normal32; no inferir lambda decodificado de intervalo no singleton.
Inputs/intermedios normal/0; subnormal seleccionado/overflow rechazan sinFTZ.

Cinco nodos RN32 separados, nearest/ties-even, sinFMA/reasociación:
q0=RN(Lhi/lambda); p=RN(q0*lambda); r0=RN(Lhi-p);
r1=RN(r0+Llo); q1=RN(r1/lambda). Q=q0+q1 como expansión, NOcast32 final.
Identidad exacta por grafo Q-(Lhi+Llo)/lambda=(-dp+dr0+dr1)/lambda+dq1.
Defecto dq0 cancela algebraicamente por reutilizar el MISMO q0; error de
producto dp sigue cobrado. Cota sumabs/lambda+abs(dq1), no suponer producto
exacto por magia ni teorema universal de división compensada/hardware.

Selector n=floor(Q+1/2) es SOLO racionalCPU, NOoperación nativa implementada.
El intervalo de L/lambda original/decoded y envolvente numérica deben estar
enteros en la misma celda centrada; cruzar frontera rechaza, sin epsilon.
Residual Q-n se mantiene racional de dos limbs para auditoría: no afirmar
que existe residual/shader/trigonometría/campo nativo.

Bphase_total=Bgeom_retenido+Bmirror_transport_retenido+8*(Eencode/lambda+Bquotient).
8 es la cota conservadora de2pi usada por certificado anterior, no cambio
de presupuesto. Mismo phasebudget por sourceID. Fase absoluta del espejo
NOevaluada: aceptar argumento geométrico parcial NOpromueve caso completo.
FAILprevios quedan con su flagoriginal; fullfield/nativo/auth/promoción=false.
Fuente/amplitud/campos/reducción/detector/trig/fase completa fuera de alcance.

Pruebas nuevas: quotient con oráculos racionales, producto noexact cobrado,
señal de fase perdida por cast32 simple y retenida en low, cruce del selector,
subnormal/overflow/optin/selección/SHA/gauge/cobertura/budget0 negativos.
Un hilo/hijo60s; sinGPU/reserva/cancelación/peerwriter/deadlinealterado.
Tiempo tests y5nodos/path NOcostes completos/benchmark igualtrabajo.
Skills contrato/reuso guían trabajo acotado; JEVfallback sin reintento/aval.
Claude acuseID/SHA ysolo artifacts0337/backendguard YAexistentes/igualtrabajo-
costes completos; no nuevasGPU/suite/barrido/guardreview. 006/013/0337FAIL
intactos; fasegeneral/productor yselector nativo pendientes antes escala.

## Resultado verificado, no promoción

Ocho tests PASS/rc0:0,3581166s, tests internos0,068s. Un hilo/hijo60s.
18casos retenidos/21paths numéricos/105nodos RN32, dos primitivas/10nodos.
17casos aceptan SOLOargumento geométrico parcial; mode_FAIL no lo admite.
Ocho flags completos previos verdaderos y diez FAIL previos conservados;
ningún caso se promueve a pipeline completo. La fase absoluta del espejo
NOse evaluó, incluso si transporte/espejo2^-150 tiene cota pequeña.

En near_quarter_FAIL MISMAescena retenida: Ldecoded=5/8+2^-30,
lambda=1/8. División principal RN32=5 pierde2^-27 ciclos; expansión
q0+q1=5+2^-27 conserva esa diferencia con error exacto0 del grafo en
este caso. No equivale a un campo o fase trigonométrica ejecutados.
Primitiva sintética de2^24+1/8 ciclos retiene1/8 en limb bajo.
Producto noexacto con lengthhi32(.1), low2^-30 ylambda32(.3) produjo
dp nozero: la cota lo cobra; no suponer multiplicación sinerror.

Selector cruza frontera1/2 -> RECHAZADO, sinepsilon; singleton1/2
selecciona n=1/residual=-1/2 SOLOCPU. Normal2^-126/2 selecciona
subnormal yrechaza. Overflow/bool/inputsubnormal/lambda0/lengthnegativo/
budget0/non-singletonlambda/gauge/order/binding/SHA/optin rechazan.
Todos negativos con copias locales, sin modificar fixtures o umbrales.

Validador independiente sin helper RN32:0,0358708s; comprueba115nodos
nearest/ties-even, identidad correlacionada, cargos, encodinglongitud,
referencias/intervalos y mismo phasebudget. No repetir productor/tests.
Rawstdout65108bytes SHA
178e2d5f82b5983b7fa2e8827b33a60be8ab997fb0780359aa043dc99b0757fd,
comprimido en informe propio; no fallo inicial del hijo. 49huellas previas+
informe detector=50pins;53huellas actuales y49previas. Huella del informe
nuevo se registra fuera del propio JSON para evitar autorreferencia.

Lectura de ruta D:/PROJECTS/.gpuq sin salida no verifica estado de cola;
NOpreflight/telemetría/admisión/reserva/GPU/Blender. Diagnóstico rg demasiado
amplio detenido por el propio agente al encontrar accesos denegados, sin
reintentar/bypassear ni modificar datos. No driverfault ni sabotaje inferidos.
Implementación nativa de longitud/selector/trig/fase del espejo/producto
fuente-a-campo sigue pendiente. Sin aval JEV remoto ni costes completos.
