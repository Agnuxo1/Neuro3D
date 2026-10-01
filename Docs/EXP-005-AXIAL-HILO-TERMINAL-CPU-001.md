# AXIAL-HILO-TERMINAL-001: expansión terminal, SOLO modelo racional CPU

## Contrato opt-in ANTES de GPU

Base7924a15. Backend experimental separado: requiere terminal_model=
rational-hilo32-reencode-v1 EXPLÍCITO. No reemplaza productor/reducción32
congelados ni arregla shaders/runners/defaults/fixtures/gates anteriores.
No acepta caminos/campos suministrados. Deriva de la misma escena original
y de su ABI decodificado fuentes, UN espejo axial y puerto terminal.
Reutiliza certificados source/path/mode y helpers polinomiales congelados;
NOejecuta produce_scene_fields ni ninguna suite antigua/barrido005/006.

Supuestos: rayos±X/YZfijos, espejo pasivo unitario, modo terminal entrante
unitario con referencia en el MISMO plano, gauge original por binding y
grupos coherentes explícitos. Cobertura ordenada completa de1..16fuentes,
además de límites congelados del packer; no radio/error extra implícito.
Modo/topología sin prueba rechaza ANTES de evaluar campo.

## Qué se ejecuta y qué NO

Coeficiente espejo -exp(i*phase), longitud decodificada certificada ylambda
decodificada determinan campo aproximado mediante pi acotado/Taylor grado48.
Se cobran error de pi/Taylor y transporte fuente/geometría/lambda/fase/modo.
El campo racional aproximado se codifica por componente en DOS palabras32:
hi=RN32(q), lo=RN32(q-hi), residual calculado racionalmente EXACTO.
La decodificación del MODELO es Fraction(hi)+Fraction(lo), no float32 final.

RN32 usa seed binaria64 finito y palabras vecinas; compara distancias
racionales exactas y empates pares. Así 1+2^-24+2^-100 no queda en el empate
por double-round del seed. Solo limbs normales/cero; overflow/seed no finito
y resultado subnormal rechazan, sin hipótesis FTZ ni ampliación del perfil.
La admisión exige seed finito; no asegura representar todo racional cercano
al overflow. Signos de cero no son una garantía física/nativa.

Reducción: por grupo/puerto, suma racional EXACTA de acumuladorhi+lo y
contribuciónhi+lo, luego reencodifica a dos palabras por componente. Guarda
pasos/palabras/error de cada reencodificación y error final EXACTO respecto
a suma racional de contribuciones representadas. Este residual racional
NOes TwoSum/implementaciónALU/binary64GPU ni trabajo gratis del hardware.
ALU_reduction_implemented=false/rational_residual_evaluation=true SIEMPRE.

Bpath=round_outward(Bnumeric_emitido+Bconversion_exacta+Btransport).
Btransport conserva2delta_fuente+2A_original*eta. Por grupo:
B=sumBpath+error_reducción_exacto, potencia_error<=2normaL1(Y)B+B².
Grupos incoherentes suman potencias/errores, nunca campos. Gates absoluto
L1/potencia y relativo con lower>0 se evalúan todos, más gates de transporte.
Gauge/referencia/bindings original/ABI explícitos; sin floor/epsilon/0div0.

## Pruebas y contraste con salida32 retenida

Ocho pruebas PASS rc0/13,234645s, un hilo/hijo60s;34pins verificadas.
Trece casos nuevos/6controles de redondeo. Presupuestos absolutos1e-4/2e-4,
relativos1e-6, fuente1e-4 yfase1e-12 EXPLÍCITOS, sin ampliarlos para PASS.

- entero ycuarto de ciclo: oráculos originales -.1 y-i*.1 encerrados.
- MISMA escena oscura/bindings que informe c4eceb7c retenido:
  ideal=-2^-30, nuevo Y=-8388607/2^53, error absoluto2^-53,
  relativo REAL=2^-23 (~1,1921e-7).
  Cota relativa campo2/8388605 (~2,3842e-7), potencia
  33554432/70368693846017 (~4,7684e-7); PASS1e-6 SOLOmodelo racionalCPU.
  La salida32 previa=0 ysu FAILrelativo permanecen íntegros porSHA.
  No presentarlo como reparación del backend congelado ni ventaja de motor.
- fuentes en orden inverso y grupos separados: referencias/cobertura y
  oráculo oscuro contrastados, grupos no fusionados.
- espejo.1/fase.1: source/phase/numeric/conversion/reduction cargos separados,
  palabras hi/lo comprobadas y cota total>=SUMA de componentes EMITIDOS.
- fase0/sourceexact0/underflow/high_intensity_FAIL/relative0 siguenFAIL.
  Altaamplitud puede mejorar gate de campo en NUEVO modelo, pero potencia
  conservaFAIL y todos los resultados32 previos permanecen sin modificar.
- subnormal2^-149 rechaza; fuente2^-150 se decodifica0, cobrada/relativoFAIL.
- oscuridad ideal exactamente0 rechaza relativo incluso error0, sin 0/0PASS.
- even/odd/±empates y2^-100 sobre/debajo comprobados por palabras exactas;
  codificación hi/lo residual exacto cobrado, overflow rechaza.

Fallo inicial NUEVO rc1/13,139372s/una prueba conservado raw+huellas:
cota combinada redondeaba el error numérico exacto mientras el componente
diagnóstico se emitía redondeado arriba por separado. Se corrigió SOLO
combinación nueva para sumar componente EMITIDO outward antes de redondear;
la cota aumentó conservadoramente, sin cambiar presupuestos/frozen.

## Costes, límites y coordinación

Se retienen conteos de fuentes,2polinomios/fuente,4palabras terminales/fuente
y1paso racional de reencodificación/fuente; tiempo es de TESTS+verificación,
NObenchmark de inferencia/coste completo ni comparación equivalente.
El modelo emplea enteros/fracciones de precisión arbitraria y CPU racional:
NO coste ALU digital acreditado, GPU/Bpy/RT/óptica física/autenticación,
U/GEMM compilada, red general ni ganador/ventaja/eficiencia prometida.
field_values_computed=true solo donde se evalúa CPU; no pathsCPU aGPU.
native_promotion_allowed=false yexecution_authenticated=false siempre.

GPUq10:21UTC: holderausente/un ticket existente; NOconfirmación de GPU libre
ni telemetría/preflight/admisión. SinGPU/Blender/reserva/cancelación/peerwriter.
Ventana nocturna cerrada intacta. JEV fallback local sin reintento/aval.
Skills contrato limitado/reuso guiaron variante opt-in ypreservación de32.
Boards/checkpoint SINstage; solo cuatro archivos propios versionados.
Claude: acuse AXIAL-HILO-TERMINAL-001 porID/SHA; SOLOartifacts0337 existentes
geometry/limbs/bindings e igualtrabajo/costes completos, no nuevaGPU/suite/
barrido/guardreview. FAIL0337 y006/013 pendientes intactos.
Próximo contrato ALU de expansión/operaciones completas ynegativos propios,
antes de cualquier launcher/guard/reserva/GPU; no ejecutar este modelo como
si ya fuera implementación nativa ni reutilizar deadline nocturno cerrado.
