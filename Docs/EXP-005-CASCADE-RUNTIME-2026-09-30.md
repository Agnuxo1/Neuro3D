# Cascada conectada: seis escenas reabiertas, 54 probes

30/09/2026 00:34 UTC, Blender4.5.14LTS. **PASS local acotado v4**;
retrazado independiente de Claude pendiente. JEV bloqueado por seguridad,
fallback local. No promoción de EXP-005 completo ni de inferencia RT.

Dos MZI CONECTADOS, tres entradas/puertos,15 superficies; el primer X
alimenta la segunda celda sin detector intermedio. Propiedades de escena:
fuentes complejas, λ y fases de espejos. Blender descubre impactos/longitudes;
Python CPU combina campos e intensidades. No hay render ni propagación GPU.

Seis `.blend` nuevos guardados/reabiertos: base, faseA, faseB, sham de color,
dos espejos desplazados(+0,0125BU) y lambda0,101BU. Cada uno: tres bases y
tres pares×{1,i};54probes, campos complejos completos y caminos contra
oráculo triangular independiente y composición analítica donde aplica.
SHA de los seis archivos recalculados6/6; readbacks pre/post iguales6/6;
54/54 registros numéricos contrastados de nuevo en CPU.

| Métrica | Máximo observado | Gate congelado |
|---|---:|---:|
| Campo frente a oráculo completo | 6,4608e-6 | 2e-3 |
| Campo frente a composición analítica | 6,2201e-6 | 2e-3 |
| Distancia por segmento (BU) | 4,7684e-7 | 1e-5 |
| Balance de potencia | 7,4902e-6 | 1e-4 |
| Sham, campo | 0 | 1e-12 |

Causalidad de basis0, cambio máximo de potencia: faseA0,07737;
faseB0,11664; desplazamiento de espejos0,58937;lambda0,33986, todos>0,001.
No se descartaron puertos estructuralmente oscuros ni se renormalizó energía.

## Fallos preservados y correcciones verificables

- V1 FAIL: bases0/1 pasaron, basis2 perdió rayos. Normal float32 de bpy no
  tiene norma exactamente1; reflexión que lo suponía produjo deriva espuria.
  Microprueba causal sobre archivo v1: dirección antigua misses, fórmula
  d−2(d·n)n/(n·n) con normal REAL hits b.r1/b.bs2. Regresiones y helper nuevos.
- V2 FAIL: trazado arreglado, pero consumidor omitía a.Y cuando no había
  rutas. Se inicializan TODOS los terminales declarados a0j/contador0;
  rayos perdidos aún fallan cerrado, no se enmascaran ni descartan escapes.
- V3 FAIL: campo2,42e-9 y balance3,33e-16, pero segmento1,0013554e-5>1e-5.
  No se relajó tolerancia. Fixture v4 SEPARADO de quads con offsets binarios
  que mantienen coplanaridad world float32. Los discos originales se conservan
  por defecto; no se promueven sus resultados. Regresión CPU de coplanaridad.

El método bug-investigation guió la reproducción mínima, diagnóstico read-only,
regresiones y correcciones acotadas; cada enmienda se congeló antes de medir.
ProtocoloV1 y enmiendasV2/V3/V4 conservados en `coordinacion/experimentos/`.
72/72 pruebas CPU propias. Conf1/v0/Iris y archivos Claude no se modificaron.

## Evidencia y recursos

- `D:/PROJECTS/.cognition/neuro3d/exp005_cascade_cpu_v4_20260930_0035/cascade_runtime.json`:
  campos/rutas crudas por probe, hashes de archivos y dependencias, versiones.
- `D:/PROJECTS/.cognition/neuro3d/exp005_cascade_v4_guard_20260930_0035.json`.
- V1: `exp005_cascade_cpu_20260930_0014`; v2:`exp005_cascade_cpu_v2_20260930_0028`;
  v3:`exp005_cascade_cpu_v3_20260930_0031`, todos en misma cognition, no borrados.
- Microprueba:`exp005_cascade_normal_probe_20260930_0027/diagnosis.json`.

Reserva v4 adquirida00:34:16 y liberada00:34:19UTC,rc0,guard completed,
3,24s/un hilo, RAM libre mínima muestreada8,91GiB, VRAMTOTALmáxima0,583GiB,
temp29°C, hijo9672 ya no existe. Esa VRAM es global, no medida de inferencia;
muestreo no garantiza ausencia de picos entre lecturas. Cola verificada libre.

Siguiente: Claude retraza independientemente y revisa referencias/modos;
luego congelar otro gate de escape/propiedades y separar kernel GPU de
acumulación compleja. Todavía no ortogonalidad física, red óptica RT completa,
reflectancia/dispersiones generales ni ventaja de velocidad/inteligencia.
