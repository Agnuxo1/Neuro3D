# Cascada real nueva: protocolo congelado antes de ejecutar

30/09/2026, propietario Codex. JEV bloqueado; fallback local explícito.
Fuente: `exp005_cascade_fixture.py` (42153cd), no conf1/v0/Iris.
Dos MZI conectados, tres fuentes/puertos,15 superficies; no réplica de K2.

Seis tratamientos NUEVOS: base (0,2;0,37), faseA0,6, faseB0,8,
sham color, roof de a.r1/a.r2 +0,0125BU en x, lambda0,101BU (base0,1).
Guardar y reabrir cada .blend exacto. Exigir readback pre/post idéntico y
conjunto óptico evaluado; sin render. Cada tratamiento:3bases y3pares×{1,i},
54probes totales. Fuentes/λ/fases están en propiedades de escena.

Gates antes de medir: mismas secuencias de impactos con multiplicidad,
distancia por segmento<=1e-5BU, campo complejo TODOS los puertos<=2e-3
frente a oráculo independiente de triángulos y balance<=1e-4. Composición
analítica independiente a λ0,1 (roof añade fase2π·2d/λ=π/2) error<=2e-3.
Lambda0,101 se contrasta con oráculo completo, no fórmula de longitudes enteras.
Sham campo<=1e-12; fasesA/B,roof,lambda deben cambiar potencia de basis0>1e-3.
Máximo4096raycasts/64impactos por probe. No relajar tras resultados.

Recursos: cola gpuq, reserva1GiBVRAM/5GiBRAM para exclusión, un hilo CPU,
guard con estimación host0,75GiB+geometría diminuta, device0 (no render),
RAM libre>=4GiB, VRAMtotal<=18GiB,temp<=80°C, hijo<=120s,cierre06UTC.
Carpeta nueva `D:/PROJECTS/.cognition/neuro3d/exp005_cascade_cpu_20260930_0014`;
si ya existe resultado/.blend no sobrescribir, conservar intento fallido.

Alcance: raycast real Blender y suma/interferencia CPU Python, no núcleos RT
ni cómputo óptico físico. NO cierra EXP-005 ni ortogonalidad modal de haces,
no añade reflectancia/dispersiones espectrales generales ni demuestra ventaja.
Claude puede auditar antes/después independientemente; no duplicar runner.
