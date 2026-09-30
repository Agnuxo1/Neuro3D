# EXP-005: comprobar datos retenidos no autentica su ejecución

## Auditor propio de solo lectura

`exp005_history_artifact_data.py` recibe el report del runner95358ee y un
deadline UTC común explícito. Exige esquema/scope congelado, exactamente
base/switch/referencia en orden y rutas absolutas a los tres hijos directos
del folder. Recalcula SHA de bytes; detecta archivos cambiados durante la
auditoría. `audit_folder` además conserva/recomprueba bytes de export.json.
No modifica/repara archivos, lanza Blender ni ejecuta scripts del report.

Rehace las historias desde CADA snapshot after, no desde historias del
fixture o del report; descarta esas rutas declaradas como entrada al tracer.
Compara exactamente el nuevo resultado CPU (rutas/campos/metadatos) con el
report. La fórmula <=1e-13 de los helpers congelados sigue sin cambios.
El orden global de objetos debe coincidir before/after además de los gates
congelados; no confundir igualdad de diccionarios con orden de IDs globales.
Fingerprint de report conserva ese orden, no lo elimina con sort_keys.

Este perfil exige igualdad exacta del resultado CPU retenido, NO certifica
portabilidad binaria entre Python/Blender/libm distintos. Cualquier diferencia
en ejecución real será un rechazo retenido, no se relajará retrospectivamente.

## Evidencia CPU sintética

Auditor ejecutado15:01:57 UTC (1503 es etiqueta del archivo): dos tests
PASS0,487s, un hilo/hijo<=60s. Tres controles, 13registros
por caso/errorfórmula2,22e-16; quince negativos rechazan: cobertura faltante/
duplicada/reordenada, scope o deadline incorrecto, ruta ajena/hash incorrecto,
readback cambiado/orden before cambiado, terminal omitido, campo complejo o
error declarado alterado, procedenciaGPU falsa, NaN, bytes cambiados durante
la auditoría. Entradas inmutables. Tests y report usan la MISMA ejecución.

Report local `D:/PROJECTS/.cognition/neuro3d/exp005_artifact_data_cpu_20260930_1503.json`
SHA `e4c4db1d66dd897643df3e14abc32121322764edba2e2b9835c05f9bc80c303a`.
Veintidós codeSHA verificados (18baseline/policy+plan+3nuevos). Snapshots y
lecturas de bytes son doubles: NO se creó/leyó un .blend real, abrió Bpy,
probó audit_folder con archivos reales ni ejecutó GPU/gpuq.

## Límite y siguiente paso

Los bytes arbitrarios «CPU DOUBLE NOT BLEND» pasan los controles positivos:
es evidencia de consistencia de datos, NO de formato o ejecución Blender.
El auditor SIEMPRE devuelve bpy_execution_certifiedFalse,
operational_gate_passedFalse y blend_format_checkedFalse. Texto de versión,
flags y SHA solos no autentican un proceso ni que esos bytes codifiquen la escena.
No convertir este control en redGPU/RT/óptica física/conf1/ventaja de inferencia.

Integrar gates de datos con adaptador operacional propio de admisión/pins/
logs/envelope/cierre y procedencia real. GPU de otro proyecto/006Claude sigue
pendiente; no nueva guardreview/barrido/render solicitado ni tickets cancelados.
Mientras tanto, integración CPU propia o audit006retenido si llega; no esperar
otra ventana humana si libre con recursos/márgenes reales. Contratos/runners/
shaders/fixtures anteriores intactos; JEVfallback local sin aval remoto.
Skills de desarrollo/continuidad guiaron pruebas focalizadas y límites claros.
