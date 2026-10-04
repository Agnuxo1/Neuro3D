# PRECISION-OBLIQUE-TRACE-OUTPUT-HILO32-HOST-001

Nuevo wire HOST opt-in desde OUTPUTS calculados por backend CPU racional con INPUTS originales, NO otra traza ni inferencia U/GEMM. Base81ba1b8849d4f6e400f16655856a3753201f3dfe; padre coordinacion/respuestas/PRECISION-OBLIQUE-GEOMETRY32-TRACE-RATIONAL-CPU-001-CODEX.json SHA509f6a032fc3391a6027f8b6a62fefd3a7eb8b7d81bfcdd091b493bdb32aab23/102298bytes,347pins+parent=>348dependencias. Módulos/runners/shaders/fixtures/bounds originales intactos.

## ABI y campo

Header <8s6I little-endian32bytes: N3OH32V1,version1,SOURCEcount2,source_field_count21,pair_field_count42,word_count84,reserved0. Dosword IEEEbinary32 normal-o-positivezero porcampo, hi seguido de lo, ordenliteral S0,S1. Porfuente21campos: primaryparameter1 (parámetro dirección ORIGINAL,noBU), primarypoint3 BU, barycentric3 dimensionless, reflecteddirection3 parámetro dirección original, endpoints3x3 BU, squaredsegments2 BU2. Seis buffers368bytes=>2208,252campos504words.

Productor HOST float64→structfloat32 high, residual racional original-high→HOSTfloat64→structfloat32 low. Decodificar cada word exactamente como racional; signed_error=(hi+lo)-ORIGINAL y radius=abs(error), más error si se descarta lo. No afirmar RN32directa única ni grafo nativo: verificar valor FINAL y residualracional, no cambiar cotas físicas. LOsubnormal/highsubnormal/NaN/inf/negzero/no-canónico/bool/exceso STOP. RacionalesHOST<=128bits/|v|<=10^6 conservadores; sin elevarboundsanteriores.

DescriptorHOST cerrado conserva campo/unit/racionaloriginal/wordpair/decodedpair/residual/radio/dropLoError, SOURCE/coberturaALLprimitive primary-secondary y decisión/originalCPUtraceSHA/scene-query-inputbufferSHA/recibopadre. Hash NO autentica física. Los radios NO van como cota de fase/consumidor nativo; descriptor racional NO es readbackGPU.

## Recepción y gate exacto

Publicrun/validate_received verifican dependencias/capturas y producen referencia de MISMO registrofijado. validate_received NO acepta referencia delcaller; parse helperinterno exige referencia confiable. Validar bytes EXACTOS de referencia antes de parse, incluyendo doswords/header/largo/orden; cambiar payload y rehash NO pasa. Manifest cerrado/typedrational/words/contexto/cobertura/caps; integerdecode recibido y recalcular residualcontraoriginalsinencoder enparser. Coste de generar referencia público debe contarse, NO cero.

WIREverificado sólo confirma ABI con errores conocidos. Gate contacto exacto exige pérdida0 de TODOScampos porSOURCE, incluida barycentric: cualquier radiusnozero=>STOP_NONEXACT_TRACE_OUTPUT. Sin epsilon/t_min/objectskip ni usar radios para expandir guards/bounds/conf1. Pérdida de lo rechazada, no se colapsa hi+lo silenciosamente a unfloat. phase_error_bound=null/phase/nativeIEEEgraph/physical/sceneauthFALSE. SOURCE se mantiene separada, no field-phasefusion.

## Verificación y costes

Contrastar capturasretained sin repetir traza/guard/raíces. Decoder independiente struct/as_integer_ratio contra integer core, recalcular hi+lo-error-radio y contener racional ORIGINAL. MutacionesSOURCE/trace-scene-inputSHA/coverage/fieldorder/unit/budget/gate/radius/boolwords/phaseextra/dropLo/NaN/inf/subnormal/negzero/header/truncation/extra/pairorder; referenciaencontextopúblico. InputOUTPUT sintéticos sólofieldprobes, NOfulltraceadmission.38STOP upstream intactos antescast.

Cobrar conversiones/casts/worddecodes productor/parser porcaptura, publicreference y syntheticfield. Hash/IO/JSON/Fraction/caps/contexto/refemit/oráculo tienen costesUNKNOWN_NOT_ZERO; QAsegundos NObenchmark. DoscastsHOST no prueban velocidad/eficiencia/RTigualtrabajo. RT16Mvs1M/salidasdistintas/cruceextrapolado NOequivalencia/redRT.

CPU1hilo/afinidad1/hijo60s/GPU0/Bpy0/RT0/geometryreplay0. SinSDK/DrJit/Kaggle/push/merge/publicación/writersajenos. Deadlinehistórico cerradoNOeditado; nativeGPU exige nuevojobClaudeexclusivo/guardfailclosed/deadlinefresco/telemetría/presupuestos. JEV SECURITYBLOCK fallbackLOCALsinretry/sinavalremoto. Sharedboards/checkpoint locales SINstage; own4 sólo revisados a commit.
