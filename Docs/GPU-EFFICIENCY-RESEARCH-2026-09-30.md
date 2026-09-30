# Neuro3D: eficiencia GPU y elección de motor

Investigación iniciada30/09/2026. Decisión provisional local; JEV bloqueado
por revisión de seguridad, sin consulta remota ni aval atribuido.

## Punto de partida comprobado

EXP-005 ejecuta trayectorias, reflexión, división de amplitudes, fases y
campos en un shader GPU desde escena cruda. Es simulación digital ALU,
no óptica física ni RT todavía. K3/K4 siguen siendo una cadena ideal pequeña,
no una red neuronal general con memoria/no linealidad demostradas.
El coste pareado184readbacks muestra ~26–88ms por llamada caliente;
menos recorridos no produjo una mejora clara. Ver informe SHARED-COST.

CPU hoy administra escena, exporta, valida, empaqueta y entrega entradas;
GPU hace propagación e interferencia; CPU lee/verifica el resultado.
Objetivo «todo GPU»: recorrido, evolución del estado, reducción y siguiente
paso permanecen residentes; host solo control/editor y verificaciones. No
se promete eliminar CPU/controlador ni computar físicamente con fotones.

## Diseño propuesto y frontera de responsabilidades

```text
Blender: edición + estado evaluado + revisión óptica
     │ cambios explícitos y versionados, NO resultados precalculados
     ▼
Escena cruda residente + fuentes + propiedades ópticas
     ▼
BVH/RT nearest-hit → colas de rayos → interacción/fase GPU
     └─────────────────────── siguiente segmento ──────┘
     ▼
Reducción compleja por detector/modo → intensidad/estado GPU
     ├─ readback final para oráculo, auditoría y métricas
     └─ visor independiente; DLSS/FSR nunca alimentan el cálculo certificado
```

El contrato incluye posiciones, dirección, amplitud compleja, longitud óptica,
frecuencia/λ, identidad coherente y modo, propiedad de fuente, límites de
profundidad/colas y flags globales. No introducir una matriz entrenada como
sustituto oculto del trazado. Cambiar topología/modo/λ invalida explícitamente
el estado; no conservar campos de otra escena. La caché guarda recursos,
no respuestas. Casos inválidos no entregan campos parciales.

## Tecnologías prioritarias

| Técnica | Uso en Neuro3D | Prueba que decide |
|---|---|---|
| Escena/buffers residentes | Evitar volver a asignar/subir geometría inmutable | A/B pareado con mismo shader y export evaluado; setup separado; invalidación ante cambios |
| RT + BVH | Acelerar búsqueda geométrica, sin perder fase | Mismos impactos/longitudes/campos/ledger, errores y costes completos frente ALU |
| Wavefront y compacción | Muchos caminos activos repartidos en colas GPU | Igualdad de caminos y modos, orden/reducción estable, tiempo con colas incluidas |
| Batching GPU | Paralelismo entre entradas, sin repetir geometría | Batch1/8/32, latencia p95 por muestra y throughput; sin esconder cola/espera |
| Instancias/BVH actualizado | Reutilizar celdas y actualizar solo geometría cambiada | Comparar rebuild/refit; mismo resultado tras mover espejo, con costes de actualización |
| SoA/payload pequeño | Reducir tráfico y presión de registros | Profiling/ocupación y tiempo, no solo contadores de rayos |
| Precisión mixta | FP64/hi-lo para longitud/fase, FP32 donde el error permita | Cancelaciones casi oscuras, longitudes grandes y λ pequeña; error complejo y energía |
| Trabajo incremental | Recalcular solo estados afectados por edición demostrable | Cono causal, control sham e invalidación completa cuando haya duda |
| CUDA Graphs/colas asíncronas | Reducir lanzamientos/coste host del futuro core | Medir host, GPU y sincronización, no ocultar transferencias/readback |
| LOD/culling/VRS/denoisers | Principalmente visor; aproximación separada para cálculo | Nunca descartar ópticos fuera de cámara ni ramas débiles sin cota de error |

La residencia y transferencias por lotes tienen apoyo en las prácticas de
[CUDA](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html):
reducir tráfico host↔device y mantener intermedios en device. Es una hipótesis
aplicada a nuestra implementación, no una aceleración ya demostrada.

[OptiX](https://developer.nvidia.com/blog/how-to-get-started-with-optix-7/)
ofrece ray tracing programable y búsqueda acelerada RTX. Los RT cores no
calculan automáticamente interferencia: nuestros kernels seguirán haciendo
fase e interacción. También hay que medir construcción/actualización del BVH,
transferencias y reducción, no solo millones de consultas por segundo.

La arquitectura [wavefront](https://research.nvidia.com/sites/default/files/pubs/2013-07_Megakernels-Considered-Harmful/laine2013hpg_paper.pdf)
separa tareas y compacta colas para combatir divergencia. Sus resultados de
rendering no demuestran ventaja en esta red: hay que probar nuestra fase y
ramificación. En RTX3090 no asumir beneficio del reordenamiento hardware SER:
el [whitepaper de NVIDIA](https://developer.nvidia.com/sites/default/files/akamai/gameworks/ser-whitepaper.pdf)
describe reordenamiento en Ada y no-op en generaciones anteriores; usar
capability query y considerar clasificación/compacción software.

Para geometría repetida, comparar instancias y rebuild/refit siguiendo las
[prácticas RTX](https://developer.nvidia.com/blog/best-practices-using-nvidia-rtx-ray-tracing/).
Excluir decoración de la geometría óptica declarada, NO componentes ópticos
fuera del encuadre. Una fase distinta puede requerir actualizar propiedades
sin cambiar BVH; mover un espejo sí cambia geometría, pero el primer piloto
residente invalida ambas cosas por seguridad.

## DLSS/FSR: qué investigar y qué no confundir

[DLSS](https://www.nvidia.com/en-us/geforce/technologies/dlss/) reconstruye
imágenes. Su tabla oficial no ofrece Frame Generation para RTX30; sí Super
Resolution/Ray Reconstruction. No instalaremos modificaciones no oficiales
ni contaremos fotogramas generados como inferencias científicas.

[FSR3.1](https://gpuopen.com/fidelityfx-super-resolution-3/) interpola frames y
requiere datos gráficos como profundidad y vectores de movimiento. Puede
mejorar la presentación, pero su coste también consume GPU. La suma de ondas
complejas no está garantizada por reconstruir RGB ni por una imagen bonita.

Rama aproximada futura: ¿puede un predictor temporal reducir cálculos cuando
la escena y entrada cambian lentamente? Preinscribir exacto/predictor,
saltos de fase, espejo movido, fuentes nuevas, interferencia destructiva y
fuera de distribución; medir error complejo, balance y tasa de rechazo.
Si falla el gate, volver al cálculo exacto y contabilizar ese coste. No es
DLSS integrado hoy; es investigación separada que puede ser refutada.

## Motores: recomendación provisional, no ganador medido

| Opción | Papel aconsejado | Limitación/riesgo |
|---|---|---|
| Blender + shader actual | Editor, fixtures y oráculos; prototipo validado | API/contexto e integración host actuales; shader pequeño no explota aún RT |
| Unreal + RDG/RHI + RT propio | Visor interactivo o backend comparativo | Integración C++/DXR y dependencias; no hereda automáticamente coherencia óptica |
| Core mínimo OptiX + CUDA | Candidato de cálculo para RTX3090; Blender como frontend | NVIDIA-specific, build/SDK, errores de fase y reducción a validar |
| Core Vulkan/DXR | Backend portable/Windows si justifica el coste | Desarrollo extra, capacidades/precisión/interop a verificar |

[RDG de Unreal](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-dependency-graph-in-unreal-engine)
permite organizar passes compute, dependencias y recursos persistentes;
no basta activar Lumen/Nanite para resolver nuestra óptica coherente.

Conclusión de diseño: separar editor/visor del núcleo y comparar un **core
mínimo propio**, no construir primero un motor de videojuegos entero.
Retirar del camino numérico cámaras, tonemapping, texturas decorativas,
postprocesado y render del visor; conservar su uso visual opcional. Eso no
implica que Unreal sea lento por definición: decidir con datos equivalentes.

## Experimentos y aceptación

1. **RES-001**: buffers residentes con shader compartido intacto, contra
   fresh, cuatro entradasK3/K4; gates previos y campos/ledger completos.
   Reloj caliente incluye export e invalidación; setup/lifecycle separado.
2. **RT-001 (Claude)**: escena cruda idéntica, nearest-hit con ties/ambigüedad,
   bias y distancia compensada; después propagación/reducción GPU completas.
   Millones de nearest-hit no bastan para certificar inferencia ni capacidad.
3. **WAVE-001**: colas/batching residentes; CPU solo oráculo, no frontier
   intermedio ni lista de impactos suministrada. Nuevos bounds antes escalar.
4. **ENGINE-001**: mismo asset/inputs y exactitud en core/Blender/UE. Medir
   setup, warmup, p50/p95, muestras/s, RAM/VRAM, transferencias, energía si
   hay telemetría válida, CPU residual, errores y fallos. No comparar FPS.
5. **VIEW-001**: visor DLSS/FSR encendido/apagado sin tocar estado óptico;
   medir latencia/inferencia y recursos adicionales. Aproximación aparte.

20paresAB/BA,3warmups/backend/input, muestras completas/hashes y oráculos
fuera del reloj; no escoger solo tamaños ganadores. Comparativa con MLP
posterior a malla estable, tarea/precisión/batch/presupuesto equivalentes.
La optimización de juegos es reutilizable cuando preserva el contrato, no
porque todos sus trucos sean válidos para simulación científica.

## Riesgo específico RT: precisión de fase, no solo tasa de rayos

La interfaz de triángulos del ejemplo oficial OptiX utiliza vérticesFLOAT3.
Nuestra fase depende de la longitud. Una estimación local de primer orden es
δφ≈2πδL/λ; al reducir campos, δI=2Re(conj(E)δE)+|δE|². Cerca de una
cancelación, medir error absoluto además del relativo y de la energía.
Por ejemplo δL=1e-5BU conλ=.125BU corresponde a~5.03e-4rad; que sea pequeño
visualmente no garantiza el gate complejo1e-4. Es un cálculo ilustrativo,
NO error medido de una consulta OptiX ni una cota del sistema completo.

RT-001 debe incluir segmentos largos, λ pequeña, cancelación, bordes y dos
impactos casi empatados. Dos alternativas a medir, aún NO implementadas:

- Triángulos RT con candidato y refinamiento geométrico FP64 GPU. Refinar
  solo el ganador no corrige un ganador equivocado: hace falta comprobar
  candidatos/ambigüedad y casos de borde con un margen conservador.
- BVH sobre AABB conservadores y narrow-phase FP64 GPU propio. Puede usar
  aceleración de búsqueda espacial sin afirmar intersección triangular RT
  nativa; medir el coste extra. Bounds deben contener la geometría exacta.

Nada de nearest-hit CPU enviado como entrada al kernel. Si el margen/tie
no puede verificarse, rechazar o elegir el fallback GPU exacto identificado,
con su coste registrado. Revisar esta decisión con Claude antes de implementar
un backend distinto del que tiene asignado.

## Coordinación y seguridad

Codex: residencia/invalidation y pruebas. Claude: OptiX/RT y capacidad,
revisión independiente de esta propuesta. No duplicar carpeta ajena.
GPU por gpuq exclusivo y guard real; floorRAM4GiB/VRAM18GiB/temp80°C,
piloto120s, cierre06UTC. No cargas al límite tras reinicio0x9F. Mantener
resultados fallidos/fixtures antiguos. Este documento no autoriza publicar
trabajo ajeno, instalar drivers ni ampliar la autorización nocturna.
