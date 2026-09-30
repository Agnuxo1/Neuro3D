# Precision V3: preparación CPU tras el turno nocturno

Estado: candidato aislado y runner/auditor preparados, NO gate runtimeGPU.
No se ejecutó Blender, render ni CUDA en esta entrega.

## Evidencia nueva

Dos escenas sintéticasfloat64 hacen visible el salto geométrico fijo1e-6:
detector a1e-8BU desdefuente ydetector a1e-8BU después de reflejar en
espejo45°. El emulador de consulta conbias no ve eldetector; sinbias sí.
El oráculo triangular independiente registra respectivamente1y2consultas,
con longitudes1e-8 y1+1e-8BU. Esto es evidencia CPU, no reproducción GPU.

Otra escena llega condesajuste angular2e-4rad: déficit deproducto escalar≈2e-8.
El criterioviejo1e-6 acepta, pero eloráculo1e-9 rechaza. Control2e-5rad válido,
modo alineado válido ymodo inverso rechazado. Sonmodos escalares ideales,
no ortogonalidad física Maxwell.

## Cambio preparado

`Blender/benchmarks/capacity_audit/precision_v3.py` compone sobre fuentes
nearestV2/sharedV1 congeladas, verificando hashes. SOLOBIAS1e-6→0 y
toleranciaterminal1e-6→1e-9. No se cambian los shaders anteriores, API de
dispatch, inputs, geometría, unidades, reflexión, fases, cotas ni ledger.
La variante no se activa en ningún benchmark antiguo ni en códigoClaude.

Runner independiente `Blender/tests/exp005_precision_runtime.py`:36dispatches
prospectivos,29casos sintéticos(21regresiones+8nuevos),3controlesV2 y4probes
realesK3/K4conreadback. Auditor posterior `exp005_precision_audit.py`.
Contrato `coordinacion/experimentos/EXP-005-PRECISION-GPU-V3.md`.

## Verificación y límites

- 182testsCPU PASS8,730s; ocho pruebas específicas nuevas. Primer intento
  de testaislado fallóimportnearest_hit_v2; corregido path explícito antes
  de pruebas final/completa. Nada se instaló ni se modificó en Claude.
- ArtefactoCPU `D:/PROJECTS/.cognition/neuro3d/exp005_precision_cpu_20260930_0652.json`.
- SHA `b22da470375710a7ea3320f0460da14b4b0195c55d949e8de098c555298152c1`.
- t_min sigue1e-9BU: gaps≤1e-9 fuera de resolución. Sinbias puede reaparecer
  autointersección con geometría oblicua/grandescoordenadas; esta entrega no
  demuestra ausencia general. Esos adversarios deben preceder escalado.
- Ledgerfloat32 de longitud≈1 no resuelve gap1e-8; no presentar ese readback
  como certificación de precisión1e-8. Escenasrawfloat64 no equivalen a
  geometríaBlenderfloat32 guardada/reabierta.
- Falta compilar shader, reproducir tresfallos V2 y36gates enGPU, guardrc0,
  reauditar artefactos ycríticaClaude. No ampliar conf1/bounds ni declararRT,
  speedup oventaja general antes de esos resultados.

JEV sigue bloqueado por revisión de seguridad, fallbacklocal sin aval remoto.
GPU pertenece actualmente aotro ticketClaude; la ventana nocturna expiró.
Solicitada nueva ventanaGPU alusuario. El reloj nocturno continúa pausado.
