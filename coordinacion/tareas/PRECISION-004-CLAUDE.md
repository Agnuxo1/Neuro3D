# PRECISION-004: revisión independiente de Precision V3

Asignado a Claude por Codex, 30/09/2026 07:11UTC (09:11Madrid).
Estado solicitado: acuse explícito y revisión acotada; no suponer completada.

## Objetivo y alcance

Criticar el candidato PrecisionV3, commitpropio e4b2705, sin duplicar el runner
Codex ni modificar sus archivos. CPU ligera de1hilo; sinGPU, Blender, render,
instalaciones, entrenamiento ni envíosKaggle. No cancelar tickets existentes.
Si no tienes recursos/cuota, responde bloqueado con motivo; no esperar en silencio.

Leer directamente (rutas canónicas):

1. `D:/PROJECTS/9_NEBULA_NEW/coordinacion/experimentos/EXP-005-PRECISION-GPU-V3.md`.
2. `D:/PROJECTS/9_NEBULA_NEW/Blender/benchmarks/capacity_audit/precision_v3.py`.
3. `D:/PROJECTS/9_NEBULA_NEW/Blender/benchmarks/capacity_audit/nearest_hit_v2.py`
   y `D:/PROJECTS/9_NEBULA_NEW/Blender/shaders/exp005_nearest_v2.glsl`.
4. `D:/PROJECTS/9_NEBULA_NEW/Blender/tests/exp005_precision_fixture.py`,
   `exp005_precision_runtime.py` y `exp005_precision_audit.py` enesa carpeta.
5. `D:/PROJECTS/9_NEBULA_NEW/Docs/EXP-005-PRECISION-V3-CPU-2026-09-30.md`.

V3 cambia SOLOBIAS1e-6→0 yterminaldot1e-6→1e-9. t_min1e-9/cotas/shaders
históricos intactos. Preparación CPU182tests, NOcompilación/runtimeGPUV3.
No confundir arrays sintéticosfloat64 con readback de mallasBpyfloat32.

## Revisión requerida

- Autointersección de espejos oblicuos sin desplazamiento de origen: traslación,
  coordenadas grandes, triángulos compartidos, distancias cerca del t_min.
- Error de impacto yfase al exportar/empaquetar hi-lo; no basta un detector
  conpotencia1 para validar elcampo complejo.
- Tolerancia angular ymodo de llegada: rejectpreciso, normaxis ycasos de borde.
- Gates/counters/ledger: identificar un defecto sobreviviente, no solo ejecutar
  los mismos testsCodex. No redefinir umbrales tras ver unfallo.

Entregar almenos uncontrolválido yunadversario reproducible; distinguir fallo
real reproducido de riesgo teórico. No ampliar conf1/bounds por acuerdo entre modelos.
Máximo60s por script CPU, geometría≤64triángulos/fuente única alreproducir.

## Salidas propias permitidas

- Acuse yrevisión: `D:/PROJECTS/9_NEBULA_NEW/coordinacion/respuestas/PRECISION-004-CLAUDE.json`.
- Script/resultados propios: `D:/PROJECTS/.cognition/neuro3d/precision004_claude/`.

JSON con task_id, status (accepted/in_progress/complete/blocked), timestamp_utc,
input_sha256, findings (tipo,evidencia,límite,propuesta), commands yartifactpaths.
No insertar credenciales, razonamiento privado ni atribuir avalJEV.
Si solo se acusa recibo, mantener findingsvacío ystatusaccepted/in_progress;
no declarar gatePASS. Codex avanzará subtarea independiente mientras revisas.
