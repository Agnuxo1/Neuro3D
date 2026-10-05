# Ray tracing masivo, jaulas tetraédricas y Mega Geometry: aplicación a Neuro3D

Fecha de consulta: 2026-10-05. Autor: Codex. Investigación documental y cálculos escalares, sin ejecución GPU. Base local: `7535f84151799b06e9d9cddbe3c1f1f3de7bde57`.

## Dictamen

La vía merece investigación: reutilizar geometría y estructuras de búsqueda puede eliminar costes grandes que no son el cálculo neuronal en sí. No hay evidencia que convierta los 500 millones de triángulos del anuncio en 500 millones de neuronas independientes calculadas por paso en una RTX 3090. Tampoco se ha establecido aquí una referencia de 80 millones de neuronas bajo ese contrato.

Separamos tres preguntas: representar una escena enorme, consultar sus intersecciones y calcular una red completa a partir de esa escena. Aprobar la primera no aprueba las otras dos. La propuesta es un backend RT numérico opcional, no sustituir la inferencia geométrica por una matriz precalculada ni cambiar los runners congelados.

## 1. Identificación del anuncio

Hay dos tecnologías diferentes:

| Línea | Mecanismo | Evidencia pertinente |
| --- | --- | --- |
| AMD: tetrahedral cages | Deformar una envolvente tetraédrica y transformar rayos hacia geometría de referencia | Demostración en Radeon RX 9070 XT |
| NVIDIA: RTX Mega Geometry | Estructuras de aceleración por pequeños grupos de triángulos, reutilización y gestión de geometría | SDK y APIs NVIDIA; compatibilidad de familia incluye Ampere |

AMD muestra dos casos: una escena de aproximadamente 585 millones de triángulos animados a 60 FPS y un vídeo con 25.000 plantas. Este último pasa de 2.800 millones de triángulos en máximo detalle a unos 500 millones mediante LOD; usa rayos primarios y de sombra, en RX 9070 XT y 1080p. No demuestra iluminación avanzada ni transporte coherente. [AMD, explicación inicial](https://gpuopen.com/learn/ray-tracing-massive-amounts-animated-geometry/).

La actualización del 17 de septiembre informa aproximadamente 1,7 GB de memoria BVH y 3,3 ms de actualizaciones BVH por frame para el caso de plantas, frente a hasta 80 GB y más de 300 ms con la alternativa convencional. Son cifras del BVH, no de toda la VRAM ni de toda la inferencia. Aritméticamente, 80/1,7 = 47,06 y 300/3,3 = 90,91; estos cocientes no son mejoras del tiempo total. [AMD, memoria BVH](https://gpuopen.com/learn/how-tetrahedral-cages-significantly-reduce-bvh-memory-usage/).

El artículo de investigación identificado es *Ray Tracing Massive Amounts of Animated Geometry*, Gruen, Benthin, Kern y McAllister, DOI `10.1145/3820014`, presentado en HPG 2026. El acceso directo al editor falló durante esta consulta. Las conclusiones cuantitativas anteriores se apoyan en las explicaciones oficiales de AMD, no en una supuesta revisión completa del PDF editorial. [Programa oficial HPG](https://highperformancegraphics.org/2026/schedule/).

## 2. Qué se ahorra realmente

AMD anima una jaula y transforma los rayos para consultar pequeños BLAS estáticos de la malla base compartida. La deformación afín por tetraedro aproxima la animación. Su explicación, publicada el 22 de julio y actualizada el 2 de septiembre de 2026, anunciaba muestras DXR y biblioteca C++ en desarrollo; no se certifica aquí un paquete listo para integrar. [AMD, explicación inicial](https://gpuopen.com/learn/ray-tracing-massive-amounts-animated-geometry/).

Deducción para Neuro3D: si muchos componentes usan la misma forma, compartir su representación geométrica puede ahorrar memoria. Sus pesos, fases, señales y estados independientes siguen necesitando una representación propia. Una instancia de un mismo triángulo no crea gratis una nueva neurona con estado e interconexiones distintos.

También importa si nuestra geometría cambia. Si sólo cambian señales o parámetros ópticos de una geometría fija, la actualización de una malla animada puede no ser el cuello de botella. En ese caso probar primero BLAS estáticos e instancias exactas es una hipótesis más directa que introducir jaulas deformables. Esto es una propuesta de diseño, no un resultado medido.

## 3. Compatibilidad real con la RTX 3090

El whitepaper de NVIDIA declara Mega Geometry compatible con todas las RTX desde Turing y enumera DX12/NVAPI, Vulkan con extensiones y OptiX 9. Blackwell incorpora mejoras específicas; compatibilidad de API no implica obtener sus prestaciones en Ampere. [Whitepaper NVIDIA, página 22](https://www.nvidia.com/content/dam/en-zz/Solutions/design-visualization/quadro-product-literature/pdf/NVIDIA-RTX-Blackwell-PRO-GPU-Architecture-v1_1.pdf).

Un ingeniero de NVIDIA confirma soporte de clusters en Ampere. La comprobación operativa propuesta es consultar `OPTIX_DEVICE_PROPERTY_CLUSTER_ACCEL` en nuestra combinación exacta de dispositivo, driver y runtime. No se ha ejecutado esa consulta ni un benchmark en la 3090 en esta investigación. [Respuesta técnica NVIDIA](https://forums.developer.nvidia.com/t/is-optix-9-clusters-api-supported-on-ampere/333524).

El repositorio oficial RTXMG ofrece caminos Cluster LOD y Cluster Tessellation. Como referencia, publica para Zorah en RTX 5090, 4K con DLSS Quality: 15,5 ms/frame, 56 millones de triángulos únicos y 778 millones contando instancias, con 1,5 GB de malla residente y 2,3 GB de CLAS. Esos dos conjuntos de memoria no constituyen toda la VRAM. No es un resultado de nuestra tarjeta. [RTXMG oficial](https://github.com/NVIDIA-RTX/RTXMG).

La cabeza del repositorio consultada mediante la API GitHub fue `9f7644a854776ed896900f011367df420c6fb389`, fecha de commit 2026-09-04T11:11:04Z. No se clonó, instaló ni compiló el SDK.

## 4. La equivalencia triángulo-neurona no está definida

Para evitar mezclar magnitudes, un experimento debe publicar por separado:

- Triángulos únicos, triángulos contando instancias y triángulos residentes.
- Componentes geométricos, neuronas con estado y conexiones/pesos independientes.
- Rayos lanzados, intersecciones, rebotes y caminos que contribuyen a cada salida.
- Pasos completos de la red por segundo, no únicamente FPS de una cámara.

Una imagen consulta una gran escena desde ciertos rayos. No tiene que actualizar un estado independiente por cada triángulo. Con 1920×1080 píxeles y dos rayos nominales por píxel se obtienen 4.147.200 rayos por frame, no 500 millones de actualizaciones neuronales. Es una cuenta ilustrativa, no un contador hardware: las sombras, fallos y rayos secundarios efectivos dependen del algoritmo.

El flujo que habría que certificar es:

```text
escena + fuentes + estado de entrada
        ↓
búsqueda RT: identidad de instancia/primitiva y encuentro geométrico
        ↓
longitud óptica, amplitud y fase por camino
        ↓
suma coherente por fuente/detector y operación neuronal definida
        ↓
estado y salida de un paso completo
```

Los RT cores pueden acelerar la búsqueda, pero las demás etapas y sus buffers no desaparecen. Renderizar colores e intensidades tampoco demuestra sumar campos complejos con interferencia.

La evidencia local retenida distingue modos, células MZI, caminos, pesos y neuronas. La auditoría de conteo conserva 297.402.880 caminos para una fuente en un caso K8 y 786.619.732 para todas las fuentes; ninguno es un conteo de neuronas. El informe de capacidad de Claude describe 98.304 neuronas para su MLP de cuatro capas y ancho 24.576; es una evidencia histórica declarada por el informe, no una repetición ni validación nueva en este turno. No se identificó en los documentos revisados un PASS de 80 millones de neuronas bajo igual trabajo. [Auditoría local de conteo](../coordinacion/respuestas/CAPACIDAD-CONTEO-REVISION-CODEX-2026-09-30.md), [informe retenido de capacidad](../coordinacion/respuestas/CAPACIDAD-CLAUDE-2026-09-30.md).

## 5. Presupuesto: qué cabe y qué no demuestra esa cuenta

Cálculos deterministas ejecutados con Python estándar:

| Supuesto para 500 millones de entidades | Memoria, sin ningún otro coste |
| --- | --- |
| Un estado float32 por entidad | 1,862645 GiB |
| Un estado complejo de dos float32 | 3,725290 GiB |
| Todos los pesos de una matriz densa 500M×500M, float32 | 10^18 bytes, 1 exabyte decimal |
| Política actual de admisión: 1024 bytes por célula simultánea | 476,837158 GiB antes de márgenes |

Por tanto, 500 millones de estados escalares no son aritméticamente imposibles por sí solos; 500 millones de neuronas completas con conectividad arbitraria son otra pregunta. Bajo el límite operativo de 18 GiB, la media máxima sería 38,654706 bytes por entidad si todo el presupuesto se dedicara a ellas, sin driver, BVH, temporales ni otros consumidores.

La estimación de 1024 bytes/célula es una regla conservadora de seguridad, no un límite físico universal ni una igualdad célula=neurona. Para 80 millones de células da 76,293945 GiB. Procesar lotes pequeños podría reducir residencia simultánea; habría que contabilizar estados persistentes, transferencias y tiempo total. No se puede retirar esa regla sin una nueva decisión y evidencia.

Un límite adicional es Amdahl: si la parte acelerada ocupa una fracción f del tiempo, acelerar esa parte por s da como máximo `1 / ((1-f) + f/s)` de mejora total, bajo trabajo fijo. Por ejemplo, f=0,2 y s=50 sólo permiten 1,244× global. Son ejemplos hipotéticos, no perfiles de Neuro3D.

## 6. Riesgos de precisión que afectan al cómputo

El ejemplo Cluster LOD cuantiza posiciones por defecto (`Pos Drop Bits=7`), usa un umbral de error de un píxel y permite elevarlo automáticamente cuando aumenta la ocupación. El detalle seleccionado depende de la cámara. Para un experimento numérico, esos ajustes no constituyen una garantía de conservación geométrica: desactivarlos requiere además verificar el resto de transformaciones y el pipeline completo. [Cluster LOD, documentación fijada al commit consultado](https://github.com/NVIDIA-RTX/RTXMG/blob/9f7644a854776ed896900f011367df420c6fb389/docs/ClusterLOD.md).

Propuesta propia de contrato:

1. No perder primitivas, fuentes, huecos finos o superficies por LOD/culling de cámara. Una geometría simplificada sólo entra con cota numérica explícita aprobada previamente.
2. Conservar identidad global de instancia/primitiva, autointersección, desempates y primitiva previa, además de distancia e intersección. Un color parecido no es comparación equivalente.
3. No usar DLSS, reconstrucción de imagen o denoising como certificado del campo calculado. La advertencia de NVIDIA indica que DLSS-RR no converge necesariamente a la imagen de referencia. [Explicación OptiX 9](https://developer.nvidia.com/blog/fast-ray-tracing-of-dynamic-scenes-using-nvidia-optix-9-and-nvidia-rtx-mega-geometry/).
4. Para una jaula con transformación `x = A·x_ref + b`, transformar origen y dirección con A inversa. Renormalizar la dirección de referencia cambia el significado de t si no se compensa. Calcular longitudes y normales en el espacio correspondiente; una transformación singular o no admitida debe provocar STOP. Son obligaciones matemáticas propuestas, no una certificación del backend AMD.
5. Reconciliar particiones de tetraedros, encuentros en fronteras e identidades de los fragmentos con la primitiva original. Conservar transporte hi-lo donde lo exija el contrato; no restaurar precisión perdida mediante una conversión posterior.

Para un medio uniforme, `δφ = 2π·δL/λ`. Un ejemplo meramente ilustrativo: a λ=500 nm, un presupuesto de 0,001 rad limita δL a aproximadamente 7,96×10^-11 m. No es el umbral aprobado del proyecto. Con índices variables se necesita la integral de longitud óptica y las fases de frontera, no sólo la distancia geométrica.

En una suma `E = Σ a_j exp(iφ_j)`, una cota absoluta suficiente, con las mismas contribuciones y amplitudes exactas, es `|δE| ≤ Σ |a_j|·|δφ_j|`. Cambios de amplitud requieren su propia cota. Cerca de cancelaciones, una cota relativa exige una referencia no nula certificada. Esta derivación explica por qué un error imperceptible en pantalla puede importar mucho en nuestro cálculo.

## 7. Trabajo verificable propuesto, sin lanzarlo todavía

Orden de investigación recomendado:

1. Aprovechar artifacts ya retenidos de backend, contrato y guard; no repetir los cinco tamaños RT por relleno. La auditoría local encontró muestras y salidas diferentes entre Cycles y fuerza bruta, por lo que el cruce extrapolado no certifica igual trabajo. El piloto 8×8 tiene datos útiles, pero no certifica una red coherente completa. [Auditoría RT](EXP-005-RT-REPORT-AUDIT-CPU-2026-09-30.md), [piloto retenido](EXP-005-RT-PILOT006-RETAINED-AUDIT.md).
2. Diseñar un backend directo a buffers numéricos con geometría estática compartida. Separar el catálogo de formas de los estados y parámetros por instancia. No reconstruir el BVH cuando sólo cambian datos que no alteran sus límites, si el contrato lo permite.
3. Comparar primero BVH convencional exacto e instancias con CLAS exacto sobre la misma escena/rayos/salidas. Añadir jaulas sólo si se acredita un coste dominante de deformación y una cota válida sobre sus aproximaciones.
4. Validar fuentes separadas, encuentros, autointersección, huecos, longitudes y fase contra referencias retenidas, sin modificar fixtures ni umbrales. El contrato incluye las fuentes originales, no una sustitución sintética silenciosa.
5. Tras contrato, tests y commit propios revisados, preparar un piloto acotado. Medir también preprocesado, construcción/actualización BVH, transferencias, ejecución, sincronización, lectura y reducción. Publicar picos RAM/VRAM, no únicamente pools. El profiler oficial reconoce memoria sin atribuir y buffers auxiliares. [QuickStart RTXMG](https://github.com/NVIDIA-RTX/RTXMG/blob/9f7644a854776ed896900f011367df420c6fb389/docs/QuickStart.md).

La curva de capacidad debe variar independientemente formas únicas, número de instancias, estados independientes, conectividad y rayos activos. Sólo un paso completo correcto permite declarar capacidad neuronal; el número lógico de elementos de una escena no basta. Mantener diferenciadas CPU sintética, datos Blender float32, GPU ALU digital, hardware RT y óptica física.

## 8. Alcance y continuidad

No se lanzaron cargas GPU/Blender, instalaron SDKs, modificaron backends, cambiaron boards, enviaron mensajes a Claude, hicieron commits/push ni alteraron deadlines. Sólo se añadieron este informe y un checkpoint propio de investigación. JEV permanece bloqueado por seguridad: análisis local explícito, sin aval remoto ni reintento.

Para pruebas futuras siguen vigentes: reserva exclusiva por job, gpuq/procesos/telemetría antes de cada carga, guard fail-closed y deadline nuevo verificable, RAM libre ≥4 GiB después del presupuesto conservador con temporales, VRAM total ≤18 GiB, temperatura ≤80 °C, piloto ≤120 s y otros hijos ≤600 s. No MLP32768 ni pruebas próximas al límite tras 0x9F. La investigación documental no habilita ejecución por sí sola.

Conclusión operativa: investigar esta vía como ahorro de representación y búsqueda RT, conservando una inferencia realmente derivada de la escena. El objetivo de 500 millones queda como hipótesis de capacidad con unidad y trabajo por definir, no como resultado o extrapolación aprobada.
