# Cascada v2: corrección de reflexión, mismos gates

30/09/2026 00:28 UTC. Fallback local; JEV bloqueado. Preservar v1 FAIL,
fuente8164062 y `exp005_cascade_cpu_20260930_0014/base.blend`.
Enmienda ANTES de la segunda medición numérica, sin cambiar escena/umbrales.

V1 pasó bases0/1 pero perdió ambos caminos de basis2 tras b.bs1/b.m2.
Normal bpy registrada: (0,7071068286895752;-0,7071068286895752;0), norma²
distinta de1. Reflexión antigua d−2(d·n)n presupone norma exactamente1;
mathutils float32 produjo (1;-1,19209e-7;0), y ray_cast perdió esos impactos.
Microprueba causal en MISMA escena fallida: ambos orígenes/dirección antigua
no impactan; dirección calculada con norma² de la normal REAL impacta b.r1
y b.bs2. Evidencia `exp005_cascade_normal_probe_20260930_0027/diagnosis.json`.

Corrección: d−2(d·n)n/(n·n), aritmética escalar double y normalización final;
usa normal REAL del impacto, nunca normal diseñada, ID, oráculo o matriz.
Tres regresiones CPU: normal float32 concreta, invariancia ante escala de la
normal y datos inválidos. Oráculo, fixture y consumidor de campos no cambian.
El helper anterior de smoke sigue intacto; nuevo `exp005_cascade_bpy_paths.py`.
Este diagnóstico NO implica que toda la cascada pase; volver a medir todos
los gates v1, incluyendo historial, campos, balance, roof y sham.

Carpeta NUEVA `D:/PROJECTS/.cognition/neuro3d/exp005_cascade_cpu_v2_20260930_0028`;
guard nuevo con mismo120s/1hilo/RAM4/VRAMtotal18/temp80/cierre06UTC; vía gpuq.
Seis escenas/54probes y TODOS los umbrales de V1 sin modificación.
Claude ofrece turno hasta00:40UTC; no reservarlo entero, liberar al terminar.
Alcance sigue híbrido CPU, sin render, RT ni óptica física. EXP-005 completo NO GO.
