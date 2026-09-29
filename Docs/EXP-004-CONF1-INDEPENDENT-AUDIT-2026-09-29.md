# EXP-004 conf1: auditoría independiente acotada

Fecha: 2026-09-29. Estado: **PASS local del gate híbrido multicelda**, no validación de computación óptica física.

## Procedencia y controles

- Fixture congelado `D:/PROJECTS/.cognition/neuro3d/exp004/fixture_K4_conf1.json`; cuatro `.blend` y JSON en `run_K4_conf1/`; comparador de Claude `compare_conf1.py` congelado antes de medir. El informe de Claude `compare_conf1_result.json` marca G0–G9 True. La corrida anterior v0 permanece FAIL y no se sustituye retrospectivamente.
- Codex calculó desde disco SHA-256 del fixture y de los cuatro `.blend` contra `summary.json`: 5/5 coincidencias. No usó valores copiados del informe para ese cotejo.
- Codex reabrió los cuatro `.blend` con Blender 4.5.14 headless, `-t 1`, script propio de solo lectura `Blender/tests/exp004_independent_readback.py`, vía `gpuq` con reserva de 1 GiB VRAM y 5 GiB RAM. `rc=0`, cola liberada. Las escenas contienen 104, 104, 104 y 103 mallas para base, delta, sham y ablación; las fuentes, roles, transformaciones, normales y radios coinciden con el fixture/tratamiento. Peor error de posición: `9.536743e-7 BU` (delta); normal `3.422854e-8`; radio `9.221200e-9`.
- Cálculo independiente desde los JSON guardados con `Blender/tests/exp004_coherent_balance.py`: 8 fuentes, 28 pares con fases `1` e `i`; peor error de balance de superposición `1.869587e-4` (sham), bajo el límite congelado `1e-3`. En ablación hay 9 canales al incluir el escape coherente. El comparador congelado informa máximo campo frente a oráculo `1.44784e-4` (límite `2e-3`), intervención `|ΔP|=0.231224` y escape de ablación `0.244182`.

## Decisión y límites

Se acepta **solo** la reproducibilidad local del circuito **híbrido** de 16 MZI / 8 modos: la geometría guardada y los raycasts de Blender determinan rutas y longitudes; Python hace ramificación, fases, suma de amplitudes y lectura. No implica que la luz de Blender calcule por sí sola la interferencia, aprendizaje o inferencia, ni prueba una ventaja frente a redes digitales. El oráculo y el runner comparten convenciones físicas y el readback geométrico no es un segundo motor de rayos completo. JEV no pudo consultarse por el bloqueo de seguridad documentado; esta aceptación es local y provisional.

Siguiente paso: diseñar y preinscribir un gate que contraste campos calculados a partir de trazas de escena completa con el consumidor por celdas, y un mecanismo de estado/lectura en escena si se quiere sostener la meta de computación por el propio modelo 3D. Cualquier benchmark externo debe declarar claramente si evalúa el simulador digital o una realización física; no elevar resultados de EEG digitales a ventaja de esta malla Blender.
