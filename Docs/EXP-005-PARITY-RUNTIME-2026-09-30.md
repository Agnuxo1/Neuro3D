# Paridad de readback real en Blender: diez casos

2026-09-29 23:55 UTC (30/09 01:55 Madrid), Blender4.5.14LTS. Decisión local,
JEV bloqueado por revisión de seguridad. **PASS acotado10/10**; no es inferencia.

Contrato definido antes de medir en
`coordinacion/respuestas/EXP-005-PARIDAD-PLAN-RUNTIME-CODEX.md` y
`Blender/tests/exp005_parity_runtime.py`. Se crearon diez `.blend` nuevos de una
celda y cada uno se guardó/reabrió; no se usaron ni modificaron conf1/v0/Iris.

| Tratamiento | Resultado esperado y observado |
|---|---|
| Base visible | Aceptada, conjunto óptico evaluado coincide |
| Oculto en viewport | Rechazado: óptico ausente del depsgraph |
| Oculto en render | Rechazado: ocultación óptica no soportada |
| Oculto en view layer | Rechazado: óptico ausente del depsgraph |
| Colección excluida | Rechazado: óptico ausente del depsgraph |
| Transformación negativa | Rechazado: orientación no soportada |
| Transformación singular | Rechazado: orientación no soportada |
| Modificador solo en render | Rechazado: malla base potencialmente obsoleta |
| Fase solo en datablock | Rechazado: phase_rad no existe en objeto |
| Dos espejos comparten malla | Aceptados: misma malla, fases de objeto0,2 y0,4 independientes |

Cada rechazo comprobó su motivo predefinido; errores arbitrarios no serían PASS.
Instantáneas aceptadas exportan vértices/caras mundiales y propiedades reales.

Reserva `neuro3d:codex-exp005-parity`, adquirida tras liberarse la de Claude,
inicio23:54:54UTC, fin23:55:06UTC, rc0, guard propio completed/reasons[].
Proceso de un hilo, sin render. Supervisor11,82s, RAM libre mínima muestreada
9,12GiB, VRAM TOTAL máxima muestreada0,69GiB, temperatura32°C. No se atribuye
esa VRAM global a nuestro cálculo ni se garantiza ausencia de picos entre muestras.

Evidencia local:

- `D:/PROJECTS/.cognition/neuro3d/exp005_parity_cpu_20260929_2354/parity_runtime.json`
  con diez desenlaces, SHA256 de cada `.blend`, versión y hash del script.
- Snapshots aceptados y log en el mismo directorio.
- `D:/PROJECTS/.cognition/neuro3d/exp005_parity_guard_20260929_2354.json`.
- 56 pruebas CPU sintéticas/AST pasaron antes del runtime.

Límites: paridad para VIEWPORT/depsgraph de readback, no `scene.ray_cast` en esta
prueba, ni campos/interferencia/RT/render. No cubre redes multicelda ni fuente/
puerto ortogonal. EXP-005 completo sigue **NO GO** hasta fixture congelado,
oráculo completo y campos por puerto/superposiciones. No repetir este smoke
sin cambio relevante; siguiente unidad es el fixture multicelda pequeño y
su contrato, preservando todas las versiones anteriores.
