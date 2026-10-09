# Neuro3D · eficiencia y velocidad en GPU: técnicas de videojuego y motor ideal (Claude, 30/09)

Petición de Fran: todo en GPU; aprovechar el ray tracing (millones de rayos), DLSS/FSR y otras técnicas de
videojuegos; elegir el motor gráfico ideal o crear uno a medida. Es una propuesta de investigación: cada
idea se convierte en un experimento preinscrito con control y línea base (cuBLAS), como EXP-003/004/005.

## 0. La observación que más acelera: «luz horneada» (lightmaps)

En nuestra red la geometría está fija durante la inferencia; solo cambian las amplitudes de las fuentes
(las entradas). Por tanto **los caminos, sus longitudes y sus coeficientes no dependen de la entrada**. Es
exactamente lo que hacen los juegos con la iluminación estática: se hornea una vez (lightmap) y en cada
fotograma solo se combina.

- Hornear: trazar una vez (RT cores) y guardar, por cada par fuente → detector, la suma coherente de todos
  sus caminos, que es la matriz de transferencia U. Si se quiere conservar la «física», se guarda la lista
  compacta de caminos (fase y coeficiente) y se reduce en la GPU.
- Inferir: aplicar U a un lote grande de entradas, que es un matvec (tensor cores y cuBLAS) o una reducción
  dispersa por caminos. Ya lo medimos: el recorrido camino a camino se multiplica por ~15 en cada paso de K;
  horneado, el coste por inferencia deja de depender del número de caminos.
- Entrenar: al mover un espejo, solo cambian los caminos que lo tocan. Se re-hornea de forma incremental
  (como el «refit» del BVH y la luz dinámica parcial).
- Honestidad: la inferencia horneada ES una multiplicación de matrices. La ventaja real del trazado está en
  hornear y re-hornear escenas grandes y cambiantes, no en cada inferencia.

## 1. Técnicas de videojuego y cómo se aplicarían

| Técnica | En juegos | En Neuro3D | Experimento mínimo |
|---|---|---|---|
| **RT cores / OptiX, DXR, Vulkan RT** | millones de consultas de rayos por fotograma contra un BVH | intersecciones del recorrido (hoy ALU por fuerza bruta en el shader de Codex) | mismo recorrido K3/K4 → BVH OptiX: tiempo frente a la ALU a igual resultado |
| **Refit del BVH** en lugar de reconstruirlo | objetos que se mueven | entrenamiento: mover espejos sin reconstruir el BVH | coste por paso de entrenamiento: refit frente a rebuild |
| **Instancing / TLAS** | miles de copias de un objeto | celdas MZI idénticas instanciadas; solo cambian las transformaciones | rejilla de K×K celdas instanciadas: memoria y tiempo frente a malla única |
| **Wavefront path tracing** (colas por rebote) | GPU con divergencia baja | reemplazar el DFS por hilo por un frente por niveles (el «shared frontier» de Codex va en esa dirección) | caminos por segundo, DFS frente a wavefront |
| **SER** (Shader Execution Reordering) | reordenar rayos incoherentes | agrupar rayos por objeto | ⚠️ solo en Ada (RTX 40); la 3090 no lo tiene: se emula ordenando por clave |
| **Ruleta rusa / culling** | cortar caminos de poca contribución | podar los caminos con |amplitud| < ε, con error acotado y medido | error frente a ε y fracción de caminos podados; debe romper el ×15 por paso de K |
| **ReSTIR / muestreo por importancia** | muchas luces con pocos rayos | muchas fuentes activas a la vez: muestrear caminos por su peso | varianza y coste frente a enumeración exacta |
| **Acumulación temporal (TAA)** | reusar muestras entre fotogramas | reusar campos entre pasos de entrenamiento cercanos (la geometría cambia poco) | error del campo reutilizado frente a θ |
| **DLSS / FSR (reescalado)** | renderizar a baja resolución y reconstruir | calcular a baja «resolución espectral» (menos bandas o λ) y reconstruir; o una red pequeña que corrija un trazado barato | precisión de la tarea con reconstrucción frente al trazado completo |
| **Generación de fotogramas (DLSS 3 / FSR 3)** | inventar fotogramas intermedios | interpolar campos entre dos configuraciones de espejos (fases vecinas) sin trazar | error de interpolación; ⚠️ DLSS 3 FG es solo para RTX 40; FSR 3 FG funciona en la 3090. Cuidado: un fotograma inventado es una aproximación, no un cálculo |
| **Precisión mixta FP16 / tensor cores** | sombreado e IA en FP16 | amplitudes en FP16 y fases acumuladas en FP32/FP64 (el ABI hi/lo de Codex ya lo hace) | error de campo frente a velocidad |
| **Async compute / persistent threads** | solapar render y cómputo | solapar el trazado con la lectura y reducción | latencia de extremo a extremo |
| **Mesh shaders / compresión de texturas** | geometría densa, memoria | pesos como textura comprimida (el modo textura del render ya funciona) | memoria y tiempo frente a la geometría |

## 2. Motor gráfico: evaluación

| Opción | A favor | En contra | Veredicto |
|---|---|---|---|
| **Blender** (actual) | escena, guardar/reabrir, ya validado; gpu.compute nativo funciona | Python no expone RT cores; Cycles no acumula fase; la RAM del host limita las escenas grandes | prototipado y visualización |
| **Unreal Engine 5** | HW RT (DXR), Lumen, escenas enormes, Niagara/compute | pesado, C++, pensado para el render y no para el cómputo; difícil de verificar y reproducir | demo y visualización final, no el motor de cómputo |
| Unity HDRP / Godot | DXR (Unity), ligeros (Godot) | mismas limitaciones para el cómputo coherente | no prioritarios |
| **NVIDIA OptiX + CUDA directo** | RT cores de verdad; programas de rayos a medida (acumular fase en el payload) | hay que escribir el motor mínimo | **núcleo del motor a medida** |
| **Mitsuba 3 + Dr.Jit** | trazador de investigación con backend OptiX (RT cores) y **diferenciable**: gradientes de la salida respecto a la geometría y los materiales; integradores a medida en Python | por defecto es radiométrico: hay que escribir un integrador coherente propio (campos complejos) | **candidato ideal para entrenar la geometría en GPU** |
| NVIDIA Falcor | framework de investigación en tiempo real, DXR | Windows/DX12, C++ | alternativa a OptiX |
| Vulkan RT a medida | portable (NVIDIA y AMD) | más código | segunda fase |

**Recomendación: un motor «Neuro3D» mínimo** = escena → BVH (OptiX) → programa de rayos coherente (fase en el
payload, divisores, espejos con fase y detectores con modo) → horneado de U / lista de caminos → inferencia
con tensor cores → entrenamiento diferenciable (Dr.Jit o gradiente analítico por fase). Blender se queda como
editor y visor (exportar la escena → motor → importar resultados), y Unreal para la demo final. Primer paso
concreto: prototipo en **Mitsuba 3 / Dr.Jit**, con integrador coherente propio sobre la rejilla conf1 (16 MZI),
validado frente a los oráculos A/B y el pytracer. Requiere instalar paquetes (`pip install mitsuba drjit` en D:),
con el OK de Fran.

## 3. Plan de experimentos (orden propuesto)

1. **EXP-006 horneado:** conf1 16 MZI → U horneada desde el trazado (Blender o GPU) frente a la inferencia
   camino a camino: igualdad de campos ≤ 1e-6 y tiempo por inferencia con lotes de 1-65 536.
2. **EXP-007 RT cores:** mismo recorrido en OptiX (Mitsuba/Dr.Jit o programa propio) frente a la ALU de
   Codex: igualdad de campos y rayos por segundo con K = 4 → 64.
3. **EXP-008 poda:** ruleta rusa y umbral ε en el recorrido: error frente al coste; ¿se rompe el ×15 por paso de K?
4. **EXP-009 interpolación («frame generation»):** campos entre configuraciones vecinas sin retrazar:
   error y ahorro de trabajo durante el entrenamiento.
5. **EXP-010 entrenamiento diferenciable en GPU:** optimizar las posiciones de los espejos con los gradientes
   de Dr.Jit en MI o Iris; tiempo por paso frente a PyTorch con la matriz equivalente.

En cada experimento: línea base cuBLAS y torch en la misma GPU, mismas precisiones y lotes, costes de
extremo a extremo y resultado negativo registrado si no hay ventaja.
