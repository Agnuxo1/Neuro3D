# AXIAL-UNIT-ROTATION-001: rotación de propagación RN32 modelada

Base845cca7. Opt-in axial-unit-rotation-horner26-CPU-v1; solo argumentos
de paths retenidos por informe SHAfa8ea4f0...a4d72 y53huellas. Sin
repetir quotient, geometría, escena, productores o suites005/006. No campos
aportados por usuario ni matriz compilada sustituyendo escena.

Selector de quarter k=floor(4*r+1/2) en racionalCPU: todo intervalo
centrado retenido en la misma celda o rechazar, sin epsilon. Residual
u=r-k/4 debe tener |u|<=1/8. Codificar x=RN32((PIlo+PIhi)*u)
SOLOCPU; cobrar |x-2PImid*u|+|u|*(PIhi-PIlo) rad. NOimplementación
nativa de selector/longitud/multiplicación de argumento/PI. PI bounds
congelados del productor anterior, importados como constantes, no ejecutar.

z=RN32(x*x). Coeficientes RN32 c_j=(-1)^j/(2j)!, s_j=(-1)^j/(2j+1)!,
j0..6. Horner seis iteraciones cada polinomio: h=RN32(RN32(h*z)+coeff),
sinfinal=RN32(h_s*x), cos=h_c:26operaciones, sinFMA/reasociación.
Resultados SOLO de nodos RN32; Horner racional con coefexactos sirve SOLO
oráculo/cota, nunca terminal reencodificado. Domain |x|<=1 para remainder
alternante: Esin<=|x|^15/15!, Ecos<=|x|^14/14!. Coefhighest charges initial;
por paso Bnew=|z|*Bold+|hideal_previous|*Esquare+|Emul|+|Eadd|+Ecoeff.
Separar coef/square/RN, sincancelación gratis. Sinfinal cobra suEmul.
Permutar cos/sin por k modulo4 mediante signbit/swap, sin coste float nuevo.
Inputs/intermedios normal/0; subnormal seleccionado/overflow rechazan sinFTZ.

Bunit_L1=Bpoly_RN+Bremainder+2*(Bphase_retenido+Eangleencoding).
Exigir Bunit<=2*phasebudget_retenido por sourceID: MISMO presupuesto rad
traducido con |dcos|+|dsin|<=2, NOrelajar threshold para convertirFAIL enPASS.
La cota fase retenida incluye conservadoramente transporte espejo, pero
fase absoluta espejo NOse evalúa: salida es SOLOunidad de propagación.
Flags anteriores/FAIL se mantienen y fullpipeline/auth/promoción=false.
No fuente-a-campo, espejo completo, reducción, detector, Bpy/GPU ALU/RT,
óptica física ni costes completos/ventaja. Un hilo/hijo60s, sin GPU/reserva/
cancelación/peerwriter/SDK/DrJit/push/merge/deadlinealterado. JEVfallback
local explícito sin reintento/aval. Skills contrato/reuso guían evidencia.
Claude acuseID/SHA y SOLOartifacts0337 geometry/limbs/bindings/backendguard
YAexistentes/igualtrabajo-costes; no nuevasGPU/suite/barrido/guardreview.

## Resultado verificado: presupuesto no ampliado

Ocho tests PASS/rc0, hijo0,6771261s (tests internos0,117s), un hilo/límite60s.
18casos retenidos/21paths evaluados/546nodos RN32; tres primitivas/78nodos.
16casos aceptan SOLOunidad de propagación; mode_FAIL no se evalúa y
nonquarter_FAIL no pasa la nueva cota. Ocho flags completos anteriores y
diezFAIL previos intactos; ningún campo/fullpipeline/nativo promovido.

nonquarter_FAIL: cota L1 aproximada1,231621076845902e-7, presupuesto
derivado MISMO=2e-12. RECHAZADO, sin ampliar phasebudget1e-12rad,
sin esconder pérdida tras oracle racional o sustituir cálculo de campo.
Near_quarter_FAIL: residual2^-27ciclos, senoRN32 nozero; cota L1 aproximada
3,70114818210018e-15 <=2e-12 SOLOunidad. Sigue FAIL como caso completo.
Cuatro quarters dan (1,0)/(0,1)/(-1,0)/(0,-1), cota0 en estos casos;
la fase absoluta del espejo sigue sin evaluar, no coeficiente de reflexión.

Coeficientes/square/RN/remainders comprobados como cargos separados, cada
nodo nearest/ties-even; wordsubnormal/bool/intermedio subnormal2^-140/
domain>|1rad|/selector cruce/gauge/budget0/IDsduplicados/SHA/optin/selección
rechazan sobre copias locales. Sin FTZ, sin modificar frozen ni umbrales.
Validador independiente0,0610879s comprueba624nodos/coeficientes/cotas,
bindings/sourceID/phasebudget y21oráculos unitarios de propagación ligados
a longitud ORIGINAL mediante Taylor40 racional+resto/pi, NOcampos físicos.
No usa helper RN ni repite quotient/escena/productor/tests anteriores.

Rawstdout199322bytes SHA
f9372f0744069c657057ff7263a35ef21cb43b1967b01ff319b6f3a2b251753e,
retenido comprimido en informe propio; sin fallo inicial del hijo.
53huellas previas+informe quotient=54pins;57huellas actuales y53previas,
sin huella autorreferente del informe nuevo. ColaGPU sigue desconocida;
NOtelemetría/preflight/admisión/reserva/carga. JEVfallback sin aval remoto.
Pendiente producto fuente-a-campo, fase espejo, longitud/selector/producto
argumento nativo yfullpipeline/guard/deadline nuevo antes cualquier escala.
