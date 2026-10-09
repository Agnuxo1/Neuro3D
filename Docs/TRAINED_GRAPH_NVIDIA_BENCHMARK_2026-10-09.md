# Grafo entrenado: ensayo NVIDIA y baselines equivalentes fijados

La GPU se valida sobre el grafo derivado de la escena entrenada, guardada y
reabierta realmente en Blender. Se ejecutan campos, potencias y Jacobianos
propios de las 16 traslaciones; renderizar una imagen no cuenta como esta
validación. La geometría exacta y los argumentos de fase se preparan en CPU;
las funciones trigonométricas, raíces, transporte coherente y regla de la
cadena se evalúan en CUDA. No se afirma trazado de triángulos en GPU.

Se fijan 60 entradas complejas: cinco bases, veinte interferencias entre
parejas, 32 entradas aleatorias, cero y dos controles de signo/fase global.
Todos sus números se publican antes del ensayo. CPU y CUDA utilizan
`complex128/float64`. Las tolerancias previas son `10^-11` para campo/potencia
y `10^-9` para Jacobianos. Una acumulación funcional separada con autograd
comprueba la derivada de una pérdida ponderada; autograd es una referencia,
no el origen de los gradientes propios.

La implementación Torch en CPU y CUDA usa el mismo programa, argumentos,
precision y calentamiento. Se conserva también la referencia NumPy, cuyo
tiempo incluye preparar los argumentos de fase en cada llamada. El baseline
matricial se compila mediante las respuestas geométricas a las cinco bases,
incluyendo sus Jacobianos. Calcula campos, potencias y ambos Jacobianos para
las mismas entradas. Es un baseline algebraicamente equivalente; no un
payload de pesos aprendidos para el trazador.

Se comparan lotes de 1, 150 y 2.048 entradas, con cinco repeticiones prefijadas.
Se publican todas las muestras, mediana, preparación, transferencia de entrada,
ejecución sincronizada y lectura de los cuatro outputs. El tiempo de compilación
del baseline y su transferencia también se registran. No se exige una mejora
de velocidad; un resultado lento debe publicarse. La igualdad entre programas
flotantes es un control de software, separado de las cotas independientes.

Se fija la RTX 3090 por UUID, se requiere lectura efectiva de resultados CUDA
y se informa driver/runtime. El trabajo entra por la cola FIFO compartida,
solicitando 8 GiB de RAM libre y 4 GiB de VRAM más el margen de la cola.
El worker tiene 180 s, un núcleo CPU, RSS ≤ 1.500 MiB, RAM libre inicial
≥ 8.192 MiB/suelo ≥ 4.000 MiB, reserva propia CUDA ≤ 1.024 MiB y evidencia
≤ 64 MiB. La reserva propia CUDA se audita al terminar; los tamaños de los
lotes y del grafo fijan la carga. No se atribuye el consumo ajeno a este ensayo.

Dos controles Torch en CPU pasan frente a los gradientes/campos NumPy y una
referencia funcional independiente; no cuentan como validación NVIDIA.
No se ha detectado una GPU AMD local: la comprobación real de ese fabricante
permanece pendiente y no se sustituye por compatibilidad declarada.

[Perfil y entradas fijados](research/trained_graph_cuda_profile_2026-10-09.json),
[autorización de continuidad](research/trained_graph_cuda_registration_2026-10-09.json),
[backend propio](../Blender/blender_lab/torch_geometry_backend_v1.py).

## Ejecución NVIDIA comprobada

El perfil se publicó en `0afc6e260da72f4b7d0ffdd983e9687d1860e1dd` antes
de ejecutar; sus 18 pins coinciden con los bytes publicados. El [recibo y la
evidencia](validation/trained-graph-cuda-2026-10-09/attempt01/evidence_index.json)
conservan la admisión FIFO, driver 581.29, Torch 2.6.0+cu124, runtime CUDA 12.4
y lecturas reales de la RTX 3090 fijada. Resultado `VALID_ACTUAL_NVIDIA_TRAINED_GRAPH_RESULT`,
métrica 1, worker 6,72 s, RSS propia máxima observada 996,10 MiB, reserva
Torch CUDA máxima 112 MiB y asignación máxima 104,61 MiB. El turno se liberó.

Los errores máximos CUDA/NumPy son `3,61×10^-16` en campo, `3,89×10^-16`
en potencia, `5,55×10^-14` en Jacobiano del campo y `3,55×10^-14` en Jacobiano
de potencia. La referencia funcional autograd difiere `1,56×10^-13`.
La matriz/Jacobiano compilados desde las bases geométricas también cumplen
sus gates. Estas comparaciones flotantes se complementan con una certificación
racional independiente de los datos CUDA observados.

La [certificación secundaria](validation/trained-graph-cuda-2026-10-09/attempt01/interval_analysis02/certificate.json)
encierra los campos/potencias exactos del modelo representado de las 60
entradas: error de campo L1 ≤ `2,94×10^-15` y potencia ≤ `1,39×10^-15`,
por debajo de los presupuestos inalterados `10^-11`. Certifica 59 argmax;
la entrada nula conserva decisión indeterminada. Las fuentes de ambos análisis
se conservan; el segundo añade verificación explícita de hashes de la geometría
fijada y de la completitud de los arrays. Las cotas no certifican los gradientes,
otros backends, una escena física o cualquier ejecución futura de esta GPU.

| Lote | Grafo Torch CPU | Grafo CUDA | Matricial CPU | Matricial CUDA |
|---:|---:|---:|---:|---:|
| 1 | 14,45 ms | 24,50 ms | 0,0712 ms | 0,4349 ms |
| 150 | 17,43 ms | 27,06 ms | 0,4988 ms | 0,5586 ms |
| 2.048 | 75,00 ms | 25,72 ms | 8,5968 ms | 0,8973 ms |

Son medianas de cinco ejecuciones calientes, para campos, potencias y ambos
Jacobianos, con geometría fija. CPU/CUDA Torch comparten programa y caché de
argumentos. El grafo CUDA es más lento en lotes pequeños; en 2.048 entradas
reduce el tiempo de cómputo frente al mismo grafo CPU. El baseline matricial
equivalente evita recorrer nuevamente el grafo y es más rápido para estos
lotes. Su compilación cuesta 20,85 ms y su transferencia CUDA 0,242 ms.

![Medidas de coste con la misma precisión](assets/trained-graph-cpu-cuda-scaling-2026-10-09.png)

El coste frío también importa: importar Torch costó 2,14 s; preparar/transferir
el backend, 0,350 s; la primera ejecución de las 60 entradas CUDA, 0,452 s.
En lotes de 1/150/2.048, transferir entradas costó 0,251/0,121/0,155 ms y leer
los cuatro outputs del grafo, 0,359/0,300/1,336 ms. Todas las muestras y fases
están en el recibo. El worker total de 6,72 s contiene el conjunto de controles
y benchmarks; no se equipara a entrenar el modelo o recapturar/reconstruir Blender.
No se demuestra una ventaja global de energía, de fabricación o de todo el
proyecto. AMD real y más escalas/ablaciones siguen pendientes.
