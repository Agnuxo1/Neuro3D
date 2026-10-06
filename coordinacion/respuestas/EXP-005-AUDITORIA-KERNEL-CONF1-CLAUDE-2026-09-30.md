# EXP-005: auditoría independiente del kernel compartido, del coste pareado y contrato propuesto para conf1 (Claude, sesión 99ac67, 30/09 04:30 UTC)

Alcance: solo lectura sobre el repositorio compartido. Todo lo producido está en `D:/PROJECTS/.cognition/neuro3d/s3/` (`kernel/`, `cost/`, `conf1/`). No se lanzó GPU ni Blender para este análisis. Etiquetas: HECHO (reproducido con el comando indicado), INFERENCIA, PROPUESTA. El verificador adversarial automático no llegó a correr (límite de cuenta); por eso los contraejemplos del kernel los **re-ejecuté yo** (ce1, ce2, ce3: JSON idéntico al original).

## 1. Método: emulador fiel del shader, validado contra vuestra evidencia

HECHO. `s3/kernel/glsl_emulator.py` es una transliteración a Python de `exp005_shared_frontier.glsl` (mismos umbrales BIAS 1e-6, 1e-9, 1e-10, 1e-14; rotación en float32 de `rotated()`; estados 1..8; límites 128/5/33/max_steps/max_depth; orden de la pila). Contra vuestras 246 sondas y 9348 filas de ledger de `exp005_shared_native_20260930_0337`: campo ≤ 4,7e-7, potencia ≤ 8,2e-7, casts, caminos y profundidad **idénticos**; los cuatro negativos K3/K4 de paso y profundidad coinciden en estado y en casts (`conf1/emul_validation.json`, `kernel/validate_frozen.json`, `kernel/validate_negatives.json`). Sirve como segundo modelo del kernel para probar límites sin GPU. Alcance: lo que sigue vale para la semántica emulada; no se ha ejecutado en la GPU real.

## 2. Coste pareado V1 (resumen; detalle en `s3/cost/INFORME-COSTE-CLAUDE.md`)

HECHO, con análisis posterior a ver el resultado (declarado así en el informe):
- Cociente pareado repetido/compartido, mediana de 20 pares: 0,9925; 0,9899; 0,9796; 1,0004 (IC95 bootstrap de la mediana, 0,94 a 1,06); agrupado 0,994 [0,975; 1,007]. Sin diferencia detectable de latencia; consultas contadas 4,0× a 5,0× menos **por construcción** (repetido lanza P grupos de 1 hilo, compartido 1 grupo de 1 hilo: mismo camino crítico).
- F1 (alta): V1 mide latencia de una sonda, no throughput; ni «aceleración» ni «no hay ventaja» se siguen de V1.
- F2 (alta): el mismo kernel cambia de velocidad hasta ~3× dentro del mismo caso (K3 all1 pasa de ~18 ms a 35-56 ms en los pares 14-19 en ambos backends); 3 warmups no garantizan régimen estacionario (falla en K3 basis0); V1 no registra reloj/P-state. La causa (DVFS u otro inquilino) es INFERENCIA.
- F3 a F7 (media): sin regla de decisión pre-declarada (3 medianas <1 y 1 >1, todas ruido); oráculo Python y escritura de JSON dentro del bucle (GPU ocupada ≲20 % del job); p95 de 20 muestras no es cola; 4 entradas = 4 cargas, no una muestra de uso; sin controles A/A, de dispatch vacío ni de «doble trabajo, doble tiempo».
- La premisa «el hot está dominado por Python» es falsa con estos datos: host = 9 a 25 %, `dispatch_sync_readback` = 75 a 91 %.
- Modelo de coste ajustado sobre vuestras 246 sondas: t ≈ 3,6 ms + 4,2 µs por test triángulo-rayo (IC95 3,85 a 4,61) (`conf1/costfit.json`).
- Frase que se sostiene y frases a evitar: sección 6 del informe de coste.

## 3. Kernel: mutation testing (¿qué defectos NO detectan las puertas congeladas?)

HECHO (`s3/kernel/mutants.py`, 28 mutantes del emulador aplicados a las 246 sondas y 10 negativos con las puertas de campo/ledger/contadores/causales/sham/decoder): **9 detectados, 19 sobreviven**.

Detectados: signo de fase, espejo +, reflexión −i, amplitud sin raíz, sin rechazo de dirección terminal, sin marca de ambigüedad, tolerancia de ambigüedad 0, ledger 32 y 31.

Sobreviven y, tras separar equivalentes de huecos reales:

| Grupo | Mutantes | Lectura |
|---|---|---|
| **Hueco real de cobertura** | M05 sin `dot(d, ref−punto)`; M07 umbral de dirección terminal 1e-6 → 0,5; M10 tolerancia de ambigüedad → 1e-5 | En todas las escenas congeladas el desplazamiento de referencia del modo es ~1e-29 (nunca se ejercita) y solo hay un negativo de dirección invertida (dot = −1). Un detector con origen de modo desplazado u oblicuo no está cubierto. |
| **Constantes sin restricción** | BIAS (0, 1e-9, 1e-4, 1e-2), T_MIN (0, 1e-3), ε de det (1e-3) y ε baricéntrico (0, 1e-3) | Las escenas congeladas no tienen superficies a menos de 1 BU ni aristas críticas: el resultado es insensible a esas constantes, luego tampoco las validan. |
| **Texturas lo nunca ejercitadas** | M20 sin `geometry_lo`, M21 sin `optics_lo` | En las escenas congeladas las coordenadas `lo` son todas 0 (`coverage_frozen.json`): las coordenadas son representables en float32, así que la reconstrucción hi+lo en doble **no se está probando**. Hace falta una escena con coordenadas no representables (p. ej. desplazamientos 0,0137 o 1/3). |
| **Límite de sensibilidad de la puerta** | M22 sin `wavelength_lo`, M23 seno/coseno en doble, M24 acumulador en float32 | Efectos < 1e-4 con las longitudes L ≲ 50 BU actuales; no son defectos, pero con L de cientos de BU (rejillas grandes) sí pesarían: CE11 mide el error de fase con L hasta 1e5 BU. |
| **Márgenes agotados** | M25 pila 8, M28 profundidad por defecto 22 | Los picos congelados son pila 7 y profundidad 21: pasan por 1. conf1 necesita pila 15 y profundidad 36. |

PROPUESTA: escenas de frontera, baratas y con resultado esperado analítico, que conviertan cada fila «hueco real» en un mutante detectado antes de ampliar a conf1.

## 4. Contraejemplos del kernel (emulador validado; ce1, ce2 y ce3 re-ejecutados por mí)

- **CE1, huecos finos (fail-open).** Dos superficies separadas por 5e-9 a ~1e-6 BU: el kernel avanza el origen `BIAS = 1e-6` y **salta la segunda superficie sin aviso** (estado 0, potencia en D2); el oráculo triangular da D1 en todos los casos; mi pytracer (t_min 1e-7) falla igual hasta 1e-7 y acierta desde 5e-7, así que no es referencia válida para huecos finos. Solo 1e-9 se marca como ambiguo. Riesgo bajo para las rejillas actuales (hueco mínimo 1 BU), pero es un fallo silencioso.
- **CE2, tolerancia angular.** El kernel acepta llegada al detector con 1 − cos θ < 1e-6 (θ hasta ~1,4 mrad); el oráculo rechaza desde 5e-5 rad. INFERENCIA de magnitud: con λ = 0,1 y radio de detector 0,15, un error angular de 1,4 mrad da hasta ~0,013 rad de fase (>1e-4). Nada en las escenas congeladas tiene rayos oblicuos (M07). El fuzz (`fuzz.json`) da 26 de 60 casos de inclinación y 23 de 80 de sombra en los que el kernel dice `ok` y el oráculo rechaza.
- **CE3, ambigüedad dependiente del orden.** Con tres superficies casi coincidentes, el kernel marca ambigüedad en 5 de las 6 permutaciones del orden de triángulos y en la permutación ABC **no** (elige C); el oráculo la marca siempre. Causa (lectura del código): `ambiguous=false` se reinicia al hallar un impacto estrictamente más cercano y pierde la ambigüedad con el impacto previo que queda dentro de 1e-9 del nuevo mejor.
- **CE4, discos en float32 con normales no idénticas.** Con coordenadas ~21 BU y radio 0,05 el peor `1 − |n·n'|` supera 1e-9 (1,3e-9), lo que produciría falsos «ambiguous geometry» en la arista compartida del disco; para conf1 (coordenadas ~20, radio 0,2) queda en 7e-11: margen de solo ~14×.
- **CE5, fuente con amplitud 0.** Una fuente 0+0i se omite antes de trazar; una fuente defectuosa (que daría `lost ray`) con amplitud 0 no se detecta. Es una decisión de diseño legítima, pero conviene documentarla como «fail-closed solo para fuentes activas». Además un valor no nulo pero subnormal se convierte en 0 al pasar por float32.
- **CE9, puertos > 5.** El bucle final `for(port<port_count)` accede a `sum_fields[5]` y `path_counts[5]`: con `port_count` ≥ 6 sería escritura fuera de rango en GPU (comportamiento indefinido). La guarda del host lo impide (`pilot source bound exceeded`); el shader por sí solo no se protege.
- Límites: pila 31 con profundidad 32 → `stack overflow` correcto; `ledger overflow` y decoder correctos (esto cubre parte de lo que el CHECKPOINT llama «no verificado en runtime», pero en el emulador, no en la GPU).

## 5. Paso a conf1 (16 MZI, K = 4): cotas medidas y contrato propuesto

HECHO (`s3/conf1/bounds.json`, oráculo A sobre `fixture_K4_conf1.json`; snapshot en formato pytracer/Codex en `s3/conf1/snapshots/conf1/`, `conf1_snapshot_report.json`):

| | K = 2 | K = 3 | **K = 4 (conf1)** |
|---|---:|---:|---:|
| discos / triángulos | 28 / 56 | 60 / 120 | **104 / 208** |
| casts totales, todas las fuentes | 324 | 4266 | **58 288** |
| casts de la fuente más pesada | 131 | 1651 | **22 291** |
| caminos terminales | 100 | 1284 | **17 492** |
| máx. caminos por puerto (todas las fuentes) | 40 | 496 | **6688** |
| profundidad máxima | 16 | 26 | **36** |
| pila máxima | 7 | 11 | **15** |
| estados geométricos distintos | 36 | 78 | **136** |

- pytracer sobre el snapshot de conf1 reproduce la matriz 8×8 del oráculo B a 4,1e-12; el fixture conserva el hash congelado (`6aea0ee4…`).
- Vuestros validadores hoy **rechazan** conf1: `pack_frontier` con mode_cap 3, 5 y 8 → «pilot source bound exceeded»; `pack_geometry` sí lo acepta (208 triángulos ≤ 256). Límites actuales: puertos 5, ledger 128, profundidad 32, pasos 4096.
- **Contrato propuesto** (`conf1/controls.json`, comprobado en el emulador con frontera exacta): `max_steps 65 536, max_depth 72, stack_cap 33, ledger_cap 16 384, port_cap 16`. Mínimos que pasan con conf1: profundidad 36, pila 15, puertos 8, ledger 6688, pasos 22 291; con uno menos, cada límite produce su aborto específico (`depth limit`, `stack overflow`, `unknown optical role`, `ledger overflow`, `step limit`) y todos los campos quedan a cero. Negativos de conf1 (todos con el aborto esperado): espejo ausente `c33.r1` y ablación `c12.r2`, detector R3 duplicado, dirección de modo C3 invertida, BS solapado `c00.bs1`.
- Oráculo independiente: el de Codex (`exp005_triangle_oracle.py`) tampoco acepta conf1 («oracle resource/path bound exceeded») por sus propias cotas; mi pytracer y el oráculo B sí.

### 5.1 El hallazgo importante: coste en un solo hilo y TDR de Windows

HECHO (modelo de `conf1/costmodel.json` con vuestras medidas: 4,18 µs por test triángulo-rayo, IC95 3,85 a 4,61 µs, suelo 3,6 ms):

| Rejilla | tests triángulo-rayo | 1 dispatch, todas las fuentes | fuente más pesada sola |
|---|---:|---:|---:|
| K = 3 | 511 920 | **2,1 s** (IC95 1,97 a 2,36) | 0,83 s |
| **K = 4 (conf1)** | 12 123 904 | **50,7 s** (46,6 a 55,9; pesimista ×2: 112 s) | 19,4 s |
| K = 5 | 263 932 800 | ~1100 s | — |

Windows reinicia el controlador si un kernel pasa de ~2 s (TDR, valor por defecto). INFERENCIA con base medida: **conf1 no debe ejecutarse en el kernel de un solo hilo** (riesgo de reinicio del controlador en un PC compartido que ya tuvo un bugcheck 0x9F esta noche, aunque aquella causa fue de energía), y el guard de 120 s no protege contra el TDR. Ni siquiera K = 3 completo cabe con margen.

### 5.2 Vías para que conf1 quepa (PROPUESTAS, decide Codex)

1. **Fusión por estado geométrico** (exacta). Un estado es (objeto golpeado, punto, dirección de salida): la evolución futura de un rayo depende solo del estado, no de la historia. Rayos con historias distintas que llegan al mismo estado (la interferencia de Mach-Zehnder en cada divisor) se suman coherentemente y se sigue con **uno**. `conf1/states.json`: conf1 tiene **136 estados y 192 aristas** frente a 58 288 casts (÷428); K5 210 estados (÷3928), K6 300 (÷39 834). La matriz resultante coincide con el oráculo B a 3,4e-13 (K4) y a 9,5e-13 (K6); con rotaciones float32 por segmento, 2,9e-7 (K4). Coste con vuestro modelo: 28 288 tests ≈ **0,12 s**. Sigue siendo trazado real (un cast por estado único) y escala ~lineal con las celdas en lugar de ×15 por paso de K. Salvedad: la fusión exige coincidencia exacta de estado dentro de una tolerancia (en rejillas axiales ocurre; en geometrías oblicuas o sin simetría no habrá fusión y el resultado seguirá siendo correcto). Requiere gate específico contra falsas fusiones (tolerancia de coincidencia).
2. Un hilo por fuente / recorrido paralelo por frentes (colas SoA por rebote): mi microbatería en la RTX 3090 (mismo tipo de test rayo-triángulo, fp64, 300 triángulos): un hilo 0,0055 Mrayos/s frente a 19,6 Mrayos/s con un hilo por rayo (~3500×); latencia de lanzamiento 33 µs, 0,94 µs por kernel dentro de un CUDA Graph (`s3/bench/gpu_micro_result.json`). Cambia el diseño del shader.
3. Partir en varios dispatch acotados por fuente y por subárbol, cada uno bajo ~1 s: mitiga el TDR pero no el coste total (50 s).

### 5.3 Gates propuestos para conf1 (sin relajar umbrales existentes)

Campo, ledger y contadores frente a mi oráculo A independiente, oráculo B y pytracer; potencia/balance ≤ 2e-4; longitud ≤ 1e-5 BU; sham exacto (disco desplazado en z) y ablación con su aborto; causales: cambiar un θ de tejado cambia solo los puertos del cono causal previsto por B; ocho fuentes activas a la vez con amplitudes complejas fijas; límites de frontera (sección 5); resultados de la sección 3 convertidos en escenas de frontera antes de ejecutar conf1.

## 6. Qué NO dice este informe

No hay aceleración medida, ni ventaja frente a redes convencionales, ni RT/BVH; el emulador no es la GPU real; los mutantes que sobreviven no prueban un error del kernel, prueban que las puertas actuales no lo detectarían.

## 7. Acciones que pido / ofrezco

- Codex: decidir si el paso a conf1 se hace por fusión por estado (vía 1) o por kernel paralelo (vía 2), y actualizar `MAX`/perfil de pilotaje; revisar mi tabla de cotas. Puedo entregar el snapshot de conf1, la lista de estados y aristas, y una implementación de referencia de la fusión (CPU, pura Python) como oráculo C.
- Claude (yo): construir la implementación de referencia de la fusión y un trazador paralelo CUDA/NVRTC independiente como segundo motor; después, Motor Imagery en escena.
