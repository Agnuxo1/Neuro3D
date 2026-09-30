# EXP-005: menos recorridos no basta para acelerar la inferencia

Contrato previo a GPU: `c6aeb58`, EXP-005-SHARED-COST-V1. RTX 3090,
Blender nativo; ambos kernels ALU inmutables en el mismo proceso.
Auditoría posterior: 184 readbacks completos (160 mediciones, 24 warmups).
Cada entrada tiene 20 pares AB/BA alternados; no se descartan muestras.

| Escena/entrada | Repetido, mediana ms | Compartido, mediana ms | Mediana ratio pareado A/B |
|---|---:|---:|---:|
| K3, basis0 | 29.010 | 28.120 | 0.993 |
| K3, todas=1 | 26.151 | 26.362 | 0.990 |
| K4, basis0 | 26.580 | 27.367 | 0.980 |
| K4, todas=1 | 87.951 | 86.852 | 1.000 |

Ratio >1 favorece compartido. El cociente de medianas no es la mediana
de los cocientes pareados. No hay aceleración clara en esta frontera caliente.
No se ha realizado un test de significación ni una prueba de equivalencia.
Las consultas geométricas ejecutadas bajan de 77 000 a 16 420 en las
160 mediciones. Este menor trabajo NO demuestra mayor velocidad.

El reloj incluye actualizar fuentes, exportar estado evaluado, preflight,
packing, asignaciones/transferencias, dispatch, sincronización, readback y
decodificación. Apertura/compilación y oráculos/serialización se separan.
El tiempo interno incluye readback: no es tiempo puro por eventos GPU.
No se descompuso aún el resto del reloj en fases, por tanto no se atribuye
causalmente la falta de aceleración a una sola de ellas.

Todos los campos/ledgers/conteos/oráculos y hashes pasan sin modificar gates:
error de campo máximo 2.855e-7; balance 1.252e-6; ledger 9.410e-8.
La inferencia sigue recorriendo geometría y calculando interferencia en GPU;
no es RT, hardware óptico ni ventaja frente a una red convencional.

Evidencia local en `D:/PROJECTS/.cognition/neuro3d/`:

- `exp005_cost_native_20260930_0357.json` y sus cuatro readbacks.
- SHA256: `e737c0fc49cb644c4610286e4d99c89c39e98b79436d4bbe27731719befcc529`.
- `exp005_cost_audit_20260930_0401.json`: auditoría CPU 184/184.
- `exp005_cost_guard_20260930_0357.json`: rc0, 43.997s, RAM libre mínima
  7.584GiB, VRAM total máxima .873GiB, temperatura máxima36°C.

gpuq liberó03:58:51UTC. No Blender observado tras la prueba. La existencia
posterior del mismo número de PID no certifica que sea el proceso original.
Próxima hipótesis: mantener escena/recursos residentes, medir preparación y
caliente por separado y conservar invalidación estricta ante cambios de escena.
