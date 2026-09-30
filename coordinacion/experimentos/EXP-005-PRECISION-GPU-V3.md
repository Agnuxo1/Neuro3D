# EXP-005 Precision V3: contrato prospectivo local

Estado: preparado y verificable en CPU; NO compilación/runtime GPU todavía.
Una nueva ventana de carga es necesaria tras el corte nocturno06UTC.
JEV bloqueado: fallbacklocal explícito, no aval remoto.

## Cambio único de variante, históricos preservados

Componer sobre nearestV2 congelado y base sharedV1 con hashes obligatorios.
Solo dos sustituciones: BIAS1e-6→0 y tolerancia de producto escalar terminal
1e-6→1e-9. Mantener mínimo global, normal canónica, banda inclusiva1e-9,
umbral de avance t>1e-9, reflejos/fases/ramificación/ledger ylimits anteriores.
No copiar rayos ni impactosCPU aGPU; entrada escena cruda solamente.

No afirmar que quitar bias resuelve todas las autointersecciones ni escalas.
Datos cercanos a t_min siguen fuera de resolución; GPUlengthledger esfloat32.
No certificación de Maxwell, hardwareRT, BVH, modos físicos ni velocidad.

## 36 dispatches definidos ANTES de medir

- 21 rawcasos de nearestV2 para regresión de mínimos/ambigüedad/normal/miss.
- 8 casos nuevos rawfloat64: direct_gap yreflected_gap con1e-8BU, controles
  direct_far/reflected_far con2BU, mode_match, mode_inside(2e-5rad),
  mode_mismatch(2e-4rad) ymode_reverse(pi). Dosmode inválidos status3/campos0;
  demás válidos con oráculo triangular completo independiente.
- 3 dispatches nearestV2 históricos: direct_gap/reflected_gap deben status1
  ymode_mismatch debe status0: conservar reproducción GPU antes de reparación.
- 4 escenas reales K3/K4basis0/all1 reabiertas desde0315, cambios SOLO fuentes,
  readbackevaluadoexacto/12blendSHA antes/después. Triángulos sintéticosfloat64
  no se presentan como escenasBlenderfloat32 capaces de preservar esos gaps.

Cada válido: campos/ledger≤1e-4, potencia/balance≤2e-4, length≤1e-5BU,
contadores decasts/rutas iguales aloráculo ybalance sin renormalizar.
Para gap, unledger enD ylengtherror≤1e-7BU (límitefloat32: NO medición delgap
a1e-8 enledger de longitud total≈1). La existencia de detección yla escena
cruda son eltest geométrico; no sobreinterpretar precisión de longitud leída.
Específicos inválidos: camposvacíos/statuscorrecto; normaangular fallaprimerquery.

## Operación y criterio de promoción

Runner propio exp005_precision_runtime.py, GPU ALU OpenGL dentroBlender;
export/preflight/pack/transfer/readback/oráculos CPU explícitos. Reporte nuevo,
hashes/36casos/dispositivo/prefsprivadas/fallosretenidos; fijarcommitANTESGPU.
Guardfailclosed≤110s, host1,5GiB/device1GiB, RAMlibre≥4GiB después presupuesto,
VRAMtotal≤18GiB/temp≤80°C/gpuqexclusivo. Deadline nuevo verificable SOLO tras
autorización humana; no modificar/eludir guardnocturno ni reservaClaude.
SinprimeraGPUreal, esta entrega NO tiene gatePASSruntime.

Luego: auditoríaCPU de todaslecturas guardadas ycríticaretenidaClaude;
probarautointersección oblicua, traslaciones/escalas, overflow yerrorfase antes
de extender dominio/tamaños. No promover conf1/RT/generalidad por unfixture.
