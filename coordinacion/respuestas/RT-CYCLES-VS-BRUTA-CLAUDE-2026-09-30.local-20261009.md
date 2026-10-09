# RT (Cycles/OptiX) frente a fuerza bruta en GPU: medición propia (Claude, 2026-09-30)

Fran aprobó medir con Cycles/OptiX de Blender sin instalar nada. Todo por gpuq (tickets rt-smoke..rt-final, rt-brute) en la RTX 3090.
Scripts y JSON: `D:/PROJECTS/.cognition/neuro3d/rt/` (rt_cycles.py, brute_same.py, rt_final.json, brute_same.json).

## Método
- T triángulos aleatorios (mismos para ambos métodos, semilla T), cámara ortográfica, 1024x1024 píxeles x 16 muestras = 16,8 M rayos por render, max_bounces 0, emisión, persistent data, denoiser off. Blender 4.5.14 LTS.
- «RT solo trazado» = mínimo de las renders 2ª-4ª (BVH persistente, semilla distinta) menos la sobrecarga fija de una escena de 2 triángulos. «BVH+1ª» = 1ª render (sincronización + BVH + trazado) menos esa base.
- Fuerza bruta: kernel CuPy/NVRTC fp32, un hilo por rayo, recorre los T triángulos y guarda el z más cercano (no sale antes), 1 M rayos.
- Corrección: con T=1000 la cobertura por píxel coincide con un cálculo numpy de fuerza bruta salvo 961 de 1 048 576 píxeles (0,09 %, bordes): Cycles 896 798 píxeles cubiertos frente a 897 215 (numpy y kernel CuPy coinciden en 897 215).

## Resultados
| T triángulos | RT solo trazado (Mrayos/s) | Fuerza bruta (Mrayos/s) | RT/bruta | RT BVH+1ª render (s) | rayos por BVH para empatar (bruta = RT total) |
|---|---|---|---|---|---|
| 1 000 | 689 | 261 | 2.64x | 0.43 | 1.8e+08 |
| 10 000 | 529 | 24.7 | 21.4x | 0.47 | 1.2e+07 |
| 100 000 | 558 | 2.37 | 235x | 1.17 | 2.8e+06 |
| 300 000 | 516 | 0.761 | 678x | 2.46 | 1.9e+06 |
| 1 000 000 | 482 | 0.228 | 2.12e+03x | 7.87 | 1.8e+06 |

- El trazado de Cycles es casi plano en T (690 -> 480 Mrayos/s entre 1e3 y 1e6), la fuerza bruta cae como 1/T (~2,3-2,6e11 pruebas/s). Cruce de rendimiento por rayo: T ~ 300-1000 (con gpu_micro, T=300 bruta = 587 Mrayos/s).
- El coste de construir/sincronizar: 0,40 s (T=1e3, casi todo sobrecarga fija de la sesión Cycles), 1,1 s (1e5), 7,8 s (1e6); Python `foreach_set` de la malla, 1,3 s a 1e6.
- Con una sola tanda de 1 M de rayos la fuerza bruta gana hasta T~1e6 (7,8 s frente a 4,6 s); RT gana cuando el mismo BVH atiende varias tandas: ~2-3 M rayos a T=1e5-1e6, ~1e7 a T=1e4.

## Límites y lectura honesta
1. Son rayos primarios ortográficos coherentes (el mejor caso para RT), primer impacto, un solo z: no hay rebotes especulares ni longitud de camino/fase por rayo; Cycles no devuelve la cadena espejo->divisor->detector. Cada rebote exigiría una render nueva (0,05 s de sobrecarga fija por render) o un kernel propio.
2. Las redes de Neuro3D actuales tienen T <= ~300 triángulos (conf1: 208): ahí la fuerza bruta paralela iguala o supera a RT y la fusión por estado evita trazar. RT/BVH solo compensa con escenas de >= 1e3-1e4 triángulos estáticos y >= 1e7 rayos.
3. No demuestra coherencia (fase) ni ventaja de nicho; es solo el cruce de trazado de geometría. float32 en Cycles frente a fp64 del oráculo: para fase habría que fijar contrato de precisión antes (ver PRECISION-004/005/006).
4. 1 medición por T (mínimo de 3 renders repetidas), RES 1024, 16 spp; la sobrecarga fija de render (~0,03-0,05 s) podría enmascarar T pequeños.
