# Motor a medida: fusión por estado en CPU y GPU, escala medida y qué dice sobre RT/BVH (Claude, sesión 99ac67, 30/09)

Código en `D:/PROJECTS/.cognition/neuro3d/nebulatrace/` (`statefuse.py` CPU numpy; `gpu_states.py` torch float64 por lotes de escenas; `bench_scale.py`; `bench_scale_cuda.json`). Todo por gpuq (job de 14 s, 5 GB VRAM). Etiquetas: HECHO / INFERENCIA / PROPUESTA.

## 1. Qué es

Un **estado** es (punto de salida, dirección). El futuro de un rayo depende solo de su estado, no de su historia. Los rayos que llegan al mismo estado desde historias distintas (la interferencia de un Mach-Zehnder en cada divisor) se suman con su amplitud compleja y se sigue con **uno**. El trazado pasa de «un cast por camino» (×~15 por cada paso de K) a «un cast por estado único» (~lineal en el número de celdas), y la amplitud se propaga por el grafo (DAG) con una suma dispersa. Sigue siendo trazado real y sigue siendo óptica escalar digital, coherente y de una sola longitud de onda; no es RT, ni física de fotones.

## 2. Validación (HECHO)

| Contra | Resultado |
|---|---|
| Oráculo B (matrices) en conf1 | 5,5e-13; pytracer 3,8e-12; unitariedad 2e-15 |
| 246 sondas de la GPU de Codex (`exp005_shared_native_20260930_0337`) | diferencia máxima de campo 4,49e-7; 28 estados (K3) y 37 (K4) frente a 142 y 302 casts |
| `lattice_U` de PyTorch con 32 retardos aleatorios (chicanes) | 7e-13 |
| Escenas de Blender reabiertas con `scene.ray_cast` | U a 2,6e-4 … 6,4e-4 (float32 de `ray_cast`), predicciones idénticas (ver MI-EN-ESCENA) |
| Versión GPU por lotes frente a la CPU | 5,5e-13 … 7,5e-12 (todas las cargas) |

## 3. Escala medida en la RTX 3090 (torch float64, `bench_scale_cuda.json`)

| Carga | Triáng./escena | Estados/escena | GPU total | GPU por escena | numpy CPU por escena | Aceleración |
|---|---:|---:|---:|---:|---:|---:|
| conf1 (16 MZI), 1 escena | 208 | 136 | 112,2 ms | 112,2 ms | 23,3 ms | 0,21× (CPU gana) |
| Motor Imagery, 12 escenas | 336 | 200 | 141,4 ms | 11,8 ms | 31,0 ms | 2,6× |
| **Motor Imagery, 204 escenas (12 bandas × 17 sujetos)** | 336 | 200 | **162,2 ms** | **0,79 ms** | 30,7 ms | **38,6×** |
| Rejilla K = 8 (64 celdas) | 1312 | 784 | 245,9 ms | 245,9 ms | 159,1 ms | 0,65× (CPU gana) |
| Rejilla K = 16 (256 celdas) | 5184 | 3104 | 508,8 ms | 508,8 ms | 1186 ms | 2,3× |
| Rejilla K = 32 (1024 celdas) | 20 608 | 12 352 | 1307,4 ms | 1307,4 ms | ~18 100 ms (medida aparte con la misma CPU) | ~13,8× |

Cifras del código **corregido** (longitud de onda por escena y clave cuantizada exacta, tras la auditoría de Codex del trazador por lotes); una primera pasada con el código anterior dio los mismos órdenes de magnitud (204 escenas: 0,75 ms/escena y 41,6×; K = 32: 1,23 s). Ambas están en los registros `bench_scale_cuda*.log`; el JSON contiene la última.

Comparación con enumerar caminos (HECHO hasta K = 6, INFERENCIA más allá): conf1 K = 4 son 58 288 casts (17 492 caminos); K = 5, 824 790; K = 6, 11 950 332 (`s3/conf1/states.json`); extrapolando ×~14,5 por paso de K, K = 8 serían ~2,5·10⁹ y K = 16 inabordable. Con estados: 136, 210, 300, 784 (K = 8), 3104 (K = 16), 12 352 (K = 32).

Lectura honesta:
- Con una escena pequeña la CPU es más rápida (22 ms frente a 100 ms): la GPU se pierde en lanzamientos y sincronizaciones de mi implementación en Python, que no está optimizada (bucle por niveles, 14 a 101 niveles, propagación iterativa de 36 a 444 pasos). Un kernel persistente o CUDA Graphs recortarían esto; no lo he medido.
- La GPU gana cuando hay **muchas escenas** (38,6× con 204: es la carga natural de Motor Imagery, y la de un entrenamiento con candidatos de geometría) o escenas **grandes** (2,3× a K = 16, ~14× a K = 32).
- Todas las escenas se trazan en 0,16 s en la GPU frente a 6,3 s en CPU. Ningún resultado de esta tabla es una ventaja frente a una red convencional: comparan dos implementaciones mías del mismo trazador.

## 4. Qué implica para RT, BVH y el motor (INFERENCIA con esas cifras)

- **Los «millones de rayos» son un artefacto de enumerar caminos.** Con fusión por estado, una escena necesita 10² a 10⁴ lanzamientos (conf1: 136; Motor Imagery: 200; K = 32: 12 352).
- **Fuerza bruta paralela basta hasta K = 32**: 12 352 casts × 20 608 triángulos = 2,5·10⁸ pruebas en ≤ 1,31 s con todo el sobrecoste. Un BVH (y los núcleos RT, que aceleran justo eso) reduce las pruebas por rayo de ~2·10⁴ a ~10². Extrapolando linealmente en (estados × triángulos), K = 64 (4096 celdas, ~82 000 triángulos, ~50 000 estados) serían ~4·10⁹ pruebas (~20 s por fuerza bruta): **ahí, no antes, empezaría a compensar un BVH.** Para rejillas regulares, además, la matriz de transferencia por capas (torch) ya da K = 256 sin trazar.
- **Dónde sí importaría RT/BVH**: escenas con ≥ 10⁵ a 10⁶ primitivas (geometría libre, no una rejilla), operaciones intrínsecamente geométricas (búsqueda de vecinos, memoria asociativa sobre una escena) o renderizado diferenciable con topología cambiante. Esa prueba (RT frente a fuerza bruta paralela con el mismo tamaño de escena) es lo único que falta para cerrar la pregunta con datos; requiere instalar `drjit` (4,3 MB, PyPI, BSD) y el OK de Fran. No se ha instalado nada.
- **Motor a medida (PROPUESTA)**: exportador de Blender (escena → arrays planos) → trazador por estados (CPU para escenas sueltas, GPU por lotes para muchas) → grafo (aristas con longitud y coeficiente) → U por escena → inferencia por lotes con GEMM (0,22 ns por muestra) → resultados de vuelta a Blender. Blender queda como editor y visor; no hace falta Unreal ni un motor de juego. Quitamos sombreado, materiales, luces, cámaras y UI; añadimos poda/fusión de estados, contadores de trabajo y verificación contra oráculos.
- **Diferenciabilidad (PROPUESTA)**: con topología del grafo fija, las longitudes son funciones lineales a trozos de las posiciones de los discos; recalcularlas en torch permite entrenar las posiciones directamente por gradiente en la GPU. No implementado.

### Método de la extrapolación a K = 64 (para poder rehacerla o refutarla)
Medido en K = 32: 12 352 estados × 20 608 triángulos = 2,55·10⁸ pruebas triángulo-rayo en 1,307 s (todo incluido) = 5,1 ns por prueba (torch float64, fuerza bruta, sin BVH). Supuestos: estados y triángulos crecen ∝ nº de celdas (×4 de K = 32 a K = 64), luego las pruebas ×16 (4,1·10⁹); tiempo por prueba constante. Resultado: ~21 s por fuerza bruta. Un BVH reduciría las pruebas por rayo de ~10⁵ a ~10² solo si la escena mantuviera coherencia espacial; no se ha medido ningún BVH ni núcleo RT. Los «39×» de la tabla comparan mi trazador GPU con mi trazador CPU (numpy), no con redes convencionales ni con el kernel de Codex. La fusión suma amplitudes complejas por estado: es válida con coherencia total y una sola longitud de onda escalar (la fase y la suma coherente se conservan); la clave cuantizada (escena, posición, dirección) define qué estados se consideran iguales.
### Lo que este motor NO es
Es un backend compilado (escena → grafo de estados → U → GEMM), distinto del objetivo de recorrer la escena óptica en cada inferencia. Debe etiquetarse siempre como tal. SER y ReSTIR: se marcaron «no aplican» por el tipo de cálculo (no reordenan ni remuestrean nada que el trazado por estados necesite); no hay prueba propia que las excluya, así que son variantes que exigirían contrato.

## 5. Riesgos y límites

- La fusión exige coincidencia exacta de estado dentro de tolerancia (1e-9 BU en doble; 1e-4 con `ray_cast` float32). En geometrías sin simetría no hay ahorro (el resultado sigue siendo correcto).
- Vale solo para el modelo actual: escalar, coherente, una longitud de onda, sin pérdidas ni absorción.
- La fusión compara la clave cuantizada exacta (escena, posición a 1e-9 BU, dirección a 1e-9): dos estados a menos de esa tolerancia SE FUSIONAN (es la tolerancia declarada, no una colisión); el hash solo indexa y una colisión aborta. Tras la auditoría de Codex: la longitud de onda es por escena (antes se tomaba la de la primera escena del lote).
- Los tiempos son de una sola sesión, sin control de reloj de GPU (mismo defecto que critiqué en el coste V1); tratarlos como órdenes de magnitud, no como constantes.
