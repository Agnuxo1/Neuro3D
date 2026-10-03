# EXP005: resta relativa hi-lo oblicua mediante aritmética CPU

ID: PRECISION-OBLIQUE-PAIR64-DIFFERENCE-CPU-001. Codex capacity_audit/EXP005.
Base aa8c687ba3b9dd94b61a50c756528195500c939a.
Parent PAIR64-CYCLES001 SHAaf247e1dde579952adc02eddac33a31d2a19d5a51d009d397c89da95ab7a5748,
88pins y captura lossless; no repetir productor/geometría/raíces/test antiguos.

Modelo precision-oblique-pair64-difference-CPU-v1.
Representación OBLIQUE_PAIR64_DIFFERENCE_CPU_NOT_GPU_ABI.
Selector cerrado case/parent_result_sha256/original_scene_sha256/
literal_request_sha256/representation, modelo explícito. No caps override.

## Operaciones, no copiar el relativo previo

Deserializar las cuatro palabras IEEE64 SOURCE originales sin float(Fraction).
S0=(ah,al), S1=(bh,bl). Cambio de signo exacto, no nuevo RN.
TwoSum(a,b): s=RN(a+b); bb=RN(s-a); ab=RN(s-bb);
db=RN(b-bb); da=RN(a-ab); e=RN(da+db). Seis operaciones.
Cada identidad F(s)+F(e)=F(a)+F(b) se mide exactamente o STOP.

s,e=TwoSum(ah,-bh); t,f=TwoSum(al,-bl); e=RN(e+t);
h,g=TwoSum(s,e); l=RN(g+f); h,l=TwoSum(h,l).
26 nodos RN, cuatro identidades de residuo. Solo + y - float64.
Sin FMA, sincós, propagación ni nueva geometría. No salida calculada por
una conversión racional ni tomada de la fila relativa parental.
Ledger operandos/resultado IEEE64 y error racional de CADA operación.
La suma F(h)+F(l) solo certifica, nunca colapsar h+l para producir salida.

Dominio nuevo acotado: pares tuple2 de float64 finitos |componente|<=2^40.
No afirma validez universal/overflow/EFT en todos los dominios. No altera
bounds de ningún fixture antiguo. Subnormales en controles nuevos.

## Presupuesto ligado a escena y fuentes

Mismos intervalos ORIGINAL/literal/gauge/lambda/caps del parent sellado.
Todas las cotas SOURCE se recomprueban desde SUS palabras e intervalos.
target=(F(ah)+F(al))-(F(bh)+F(bl)).
Error aritmético=|F(h)+F(l)-target|.
Error transporte SOURCE=|pair0-mid0|+|pair1-mid1|.
Radio relativo=(interval_hi-interval_lo)/2, donde relativo se verifica
como [lo0-hi1,hi0-lo1], no eliminar incertidumbres.
Cota conservadora rad=8*(radio+transporte_SOURCE+error_aritmético).
Cota directa rad=8*max(|out-relative_lo|,|out-relative_hi|).
Directa<=conservadora se comprueba. Admisión exige conservadora<=cap
literal relativo, además de AMBAS caps SOURCE antes ANYrow.
Cap intacta, comparación inclusiva. All-or-none; diagnostics no admisión.
Salida también debe coincidir en bits con los nodos finales del grafo.
El par relativo parental se retiene etiquetado CONTROL_ONLY, no sustituye
el cálculo ni basta para autenticar inferencia nativa.

## Pruebas y oráculo independiente

Corpus37parental conservado,33STOP anteriores no ejecutan aritmética;
nuevos negativos de binding/modelo/scope; control colapsado REAL3RN
por escena frente a MISMA cap; cinco controles de cancelación/subnormal.
Fault salida low=0: operaciones genuinas retenidas pero salida alterada
STOP por identidad de grafo. Fault residuo EFT=0: palabra fabricada NO
RN correcta; conservar resultado original y ledger, identidad STOP.
No false PASS ni cambiarcaps. Costes contados por separado, no fullcost.

Oráculo independiente sin importar productor, usa decoder binario
signo/exponente/mantisa racional y celda vecinos RNE/ties-even.
Comprueba topología/operandos de los26nodos, cuatroEFT, palabras finales,
SOURCEs conservadas, presupuesto completo y ALLemit. Fault se etiqueta,
NO certificar palabra fabricada como RNE. Capturas lossless en recibo.

## Límites y coordinación

CPU float64 sobre palabras de escena DECLARADA, no Bpyfloat32/GPUALU/RT/
óptica física. GPU/nativephysical flags false. Fuente/material/amplitud/
faseespejo/campo/potencia UNKNOWN(None). No integración ABI/GPU ni
inferencia óptica total. UNMEASURED_NOT_ZERO costes completos; QA/counts
no velocidad/eficiencia/ganador ni equivalencia RT16Mvs1M.
CPUafinidad1/env1hilo/hijo60s/GPUBlender0/reservas0.
RAMpreviaUNKNOWN/ACCESS_DENIED retenida, sinretry/bypass/preflight.
JEV LOCALfallback sinaval/no retry. Skills cogniciónextendida y desarrollo
de funciones: captura sellada/ledger/topología y contrato/tests separados.
Frozenconf1/v0/v4/0119/0315/nearestV2/runners/shaders/contracts/guards/
bounds/caps/FAIL/historical0337CLOSEDdeadline intactos. Own5, boardsSINstage.
SinSDKDrJit/Kaggle/push/merge/foreignwriters. PeticiónClaude ACK ID/SHA;
artifacts YAexistentes backend/guard/material/completitud SOURCE-rama
ID/path/SHA/bytes y contrato mismo ORIGINAL-literal-ABI-gauge-caps-trabajo-
salidas-costes completos. NoACKinventado/repetir cargasrelleno.
GPU futura exige jobnuevo exclusivo acordadoClaude/guardfailclosed/
deadline y telemetría válidos/límites usuario/contrato-tests-commit previos.
