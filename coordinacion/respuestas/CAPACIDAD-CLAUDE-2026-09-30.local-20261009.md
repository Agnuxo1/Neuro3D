# Capacidad en la RTX 3090: red convencional frente a nuestra arquitectura (Claude, noche 29-30/09) · v2

v2 (00:00 UTC) incorpora la revisión de Codex `CAPACIDAD-CONTEO-REVISION-CODEX-2026-09-30.md`; la v1 se conserva como `INFORME-CAPACIDAD-CLAUDE-2026-09-30-v1.md` en la carpeta capacity.

Datos: `D:/PROJECTS/.cognition/neuro3d/capacity/claude_*.jsonl`. GPU RTX 3090 (24 GB), todo vía gpuq, con
límites de 18 GiB de VRAM y 600 s por job; RAM: en las corridas de esta noche la guarda previa estimaba 300-400 B por celda y el supervisor mataba el proceso por debajo de 3 GiB disponibles (así cortó 3072², 6144² y 8192²); desde las 00:15 UTC la política es ≥ 1024 B por celda + 1 GiB de margen y suelo de 4 GiB. Auditoría independiente de Codex
sobre Iris y los lotes: `codex_capacity_post_restart_audit.json`.

## Resumen

| Qué se ejecuta | Mayor tamaño correcto medido | Qué lo limita | Tiempo |
|---|---|---|---|
| **Red convencional**, torch: producto matriz-vector | 49 152² = **2,4·10⁹ pesos** (9 GB) | memoria (no se probó más allá, por seguridad) | 2048²: 0,044 ms (lote 1) |
| **Red convencional**, torch: MLP de 4 capas con ReLU (no lineal; distinto del matvec) | anchura 24 576 = **98 304 neuronas y 2,4·10⁹ parámetros** (4w² + 4w contando sesgos; 9,1 GB) | la de 32 768 (~17 GB) no se repitió tras el reinicio | 69 ms por lote de 256 |
| **Nuestra rejilla coherente**, matriz de transferencia calculada por torch (backend matemático; no es una ejecución física ni un trazado de escena) | K = 256: **512 modos y 65 536 celdas MZI** (0,52 GB) | tiempo de construcción en un bucle de Python (17 s), no la memoria | aplicar a 4096 entradas: 2,3 ms |
| **Nuestra rejilla coherente**, cada camino de rayo por separado en torch (solo la fuente r0, la esquina más cargada) | K = 7: 14 modos y 49 celdas, 2·10⁷ caminos | exponencial (~×15 por paso de K). Conteos exactos, verificados por Codex: K = 8, 297 402 880 caminos en r0 (2,2 GB solo de amplitudes; no se probó); K = 9, 4 466 millones en r0 (≈ 33 GB solo de amplitudes: **no cabe en 24 GB si se materializan todas las amplitudes a la vez**; un algoritmo por flujo o con reducción sería otra implementación) | 61 ms (K = 7). Por puerto frente a la matriz, error ≤ 2,7e-7 (K = 2-5); los K ≤ 7 del JSONL solo comparaban la potencia total |
| **Render que calcula** (Cycles + OptiX, núcleos RT; multiplicador incoherente, pesos como geometría) | 2048² = **4,2·10⁶ pesos**, error 1,1e-6 | **RAM del host al construir la escena en Blender** (~600-860 B por peso); 3072² cortado por la guarda | 2,6-3,6 s por render |
| **Render que calcula, pesos en TEXTURA** (misma escena; la máscara es una imagen EXR, como en un videojuego) | 4096² = **1,68·10⁷ pesos**, error 1,6e-6 | RAM del host (RSS de Blender 4,8 GB ≈ 290 B/peso, sobre todo arrays de numpy); 6144² cortado por la guarda | 5,3 s por render; VRAM 2,7 GB |
| La rejilla de 512 modos (la anterior) **calculada por un render** de Cycles/OptiX | 512 modos (matriz 512 × 1024 con signo) | — | 198 ms por muestra (lote 4), error 9e-5, 2,7 GB de VRAM |

**Lectura honesta.** En esta GPU, una red convencional con CUDA/cuBLAS admite entre ~143 veces (2,4·10⁹ frente al máximo del render con pesos en textura, 1,68·10⁷) y ~570 veces (frente a la geometría, 4,2·10⁶) más pesos que
el render dentro de Blender y es unas 10⁴-10⁵ veces más rápida por inferencia en tamaños iguales, en estas
implementaciones, esta máquina, fp32 y los lotes medidos. La rejilla, calculada como matriz de transferencia
(torch), escala como una capa densa; simulada camino a camino, su coste crece ~×15 por paso de K y, con
24 GB, el límite de esta implementación (materializar todos los caminos) está entre K = 8 (no probado) y K = 9 (no cabe). Los tamaños
máximos son los mayores observados, no una equivalencia neuronal universal. El render de Cycles/OptiX
**sí calcula correctamente** (Iris, lotes y controles), pero el coste lo domina la maquinaria del render
(construir la escena, el BVH y la imagen), no la operación.

## Evidencia del «render que calcula»

- Escena: tiras emisoras = entradas; máscara de transmitancias (Transparent BSDF, W+ en rojo y W− en
  verde) = pesos; cámara ortográfica = salidas. Cada muestra de cámara es un rayo que OptiX recorre por el
  BVH de la máscara hasta la emisora.
- Iris: la matriz compleja 8×8 de la rejilla entrenada (Re e Im como pesos con signo), las 150 flores en UN
  render: test 0,967 y coincidencia 150/150 con el modelo y con `ray_cast`; 2,9 ms por flor (con `ray_cast`
  en Python: ~2 s por flor).
- Controles (caso con signo N=8, M=16, B=4; EXR conservado): sham 0,0; intervención de un peso = predicción a
  3,6e-7 y el resto de columnas 0,0; intervención de una entrada = predicción a 3,6e-7 y el resto de muestras
  0,0.
- Modo integrador (el propio muestreo del render suma, como un fotodetector): error 0,10 / 0,010 / 0,0014 con
  64 / 1024 / 8192 spp en N = 64; a spp fijo, el error crece con N.

## Qué NO se consiguió o no se afirma

- **Red coherente en núcleos RT dentro de Blender:** no conseguida. Cycles no acumula fase: el render
  calcula la parte lineal (la matriz de la rejilla, ya obtenida del trazado o del modelo), no propaga la onda
  por los espejos. El trazado de caminos coherentes sigue siendo `scene.ray_cast` en CPU.
- La suma por filas (modo celdas), |·|² y argmax se hacen al leer, en CPU (unos 10 ms frente a 380 ms del
  render en el caso de control).
- Modo textura: arreglado a las 00:10 UTC. Cambiar el espacio de color de una imagen generada DESPUÉS de
  escribir sus píxeles la regenera en negro (esa era la causa de los ceros); hay que fijarlo antes, guardar en
  EXR y cargar el archivo. Los valores no lineales de mi script de depuración se debían a que no desactivé el
  denoiser; los scripts de medida sí lo tienen desactivado.
- No hay ventaja de velocidad ni de memoria frente a cuBLAS en ninguna variante medida; eso no descarta
  otras implementaciones (por ejemplo, OptiX directo o hardware óptico).

## Siguiente paso con sentido

**Propuesta, para decidir con Fran, Codex y JEV (no un cambio de rumbo decidido):** si el objetivo es que la
GPU «renderice» con ventaja, lo prometedor es una operación intrínsecamente geométrica, como la búsqueda de
vecinos o una memoria asociativa sobre una escena (los núcleos RT aceleran consultas de rayos frente a millones
de primitivas). En lo medido, una capa lineal densa hecha por render no se acerca a cuBLAS. Experimento
posible: «escena como memoria» (kNN o clasificación por
vecinos con rayos, OptiX) frente a búsqueda por fuerza bruta y FAISS en la misma GPU, con preinscripción.
