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
