# Entrenamiento propio con CUDA desde geometría capturada

Estado al congelar: **preparado, no ejecutado**. Autorización humana de continuidad GitHub aplicada; registro externo/IPFS pendiente, sin identificadores emitidos.

Se repetirán, en el mismo equipo, el entrenamiento CPU original y una ejecución CUDA propia. Ambos utilizan los mismos 120 ejemplos de entrenamiento, 30 de evaluación, inicialización, 16 parámetros, 60 actualizaciones Adam, temperatura de pérdida, cotas geométricas y cuantización nativa del [perfil Iris original](research/captured_geometry_training_profile_2026-10-09.json). Cada ejecución auditará independientemente sus 61 estados y reconstruirá desde cero la geometría final. No se seleccionarán semillas ni pasos usando las etiquetas de evaluación.

La ejecución NVIDIA realizará propagación coherente complex128, Jacobiano propio, pérdida por entropía cruzada y actualización Adam float64 en el dispositivo. La preparación afín exacta, los argumentos de fase, la cuantización binary32 nativa y las auditorías geométricas permanecerán en CPU. No se afirma trazado de triángulos en CUDA ni entrenamiento íntegro de Blender en GPU. Autograd no participa en el entrenamiento; sus controles de software son separados.

En cada estado CUDA se compararán campos, potencias, pérdida y gradiente con el evaluador CPU en esa misma geometría. Tolerancias fijas: 10⁻¹¹ para campos, potencias y pérdida, y 10⁻⁹ para gradientes. Se conserva el control inicial por diferencias finitas ≤10⁻⁴ y la reconstrucción geométrica final ≤10⁻¹¹. Las trayectorias CPU y CUDA finales podrán diferir; se publicarán las diferencias y el acuerdo de las 150 decisiones sin imponer igualdad bit a bit del optimizador.

Se medirán tiempos completos de los dos workers, importación, compilación geométrica, preparación y subida, cálculo CUDA, descargas, controles CPU y auditorías. CUDA tiene controles adicionales por estado que se contabilizan. Es una pareja de ejecuciones, sin intervalo estadístico de velocidad ni medición energética. Cualquier comparación de tiempos quedará limitada a ese contrato y a este equipo.

El ensayo entrará en la cola FIFO compartida con reserva de 4 GiB de VRAM y requisito de 8 GiB de RAM libre. Límites: un núcleo CPU, 900 segundos por entrenamiento, 1.900 segundos totales, suelo de RAM de 4.000 MiB, RSS propio de 1.500 MiB, memoria reservada CUDA de 1.024 MiB y evidencia de 128 MiB. Solo se cancelarán descendientes propios.

Se fija la RTX3090 por UUID, junto a las versiones reales de Python, NumPy, Torch, CUDA y driver en el [perfil](research/geometry_cuda_training_profile_2026-10-09.json). Los tres controles de pérdida/gradiente/Adam han pasado contra referencias independientes CPU antes de congelar el ensayo; eso no es una ejecución científica de entrenamiento NVIDIA. Un ensayo incompleto o fallo de entorno tendrá métrica nula; una pareja completa con descenso de pérdida suficiente en ambos tendrá métrica 1; un descenso insuficiente conservará métrica 0.

[Autorización](research/geometry_cuda_training_registration_2026-10-09.json), [worker](../Tools/train_captured_geometry_cuda_v1.py), [supervisor](../Tools/run_frozen_geometry_cuda_training_v1.py). AMD sigue pendiente porque no hay hardware AMD disponible; no se sustituirá con emulación ni NVIDIA.

## Resultado de la pareja fijada

Perfil SHA`b614463917a04f8bfb7118af89ccc0b66802150fbb9b7f7272427cb37509c3a2`, publicado en `9225699b918af274380d5958d21580a16c007020` y25pins/Gitblobs verificados antes de entrar en la cola FIFO. Ambos entrenamientos completan61auditorías y obtienen110/120aciertos de entrenamiento y27/30reservados. Pérdida CUDA6,255440538→0,309706672. Las coordenadas finales coinciden exactamente; las150decisiones también, con diferencia de potencia3,8858×10⁻¹⁶.

Controles máximos CUDA frente a CPU en la misma geometría: campo5,404×10⁻¹⁶, potencia6,662×10⁻¹⁶, pérdida8,882×10⁻¹⁶ y gradiente2,843×10⁻¹³. Control por diferencias finitas1,475×10⁻⁶ y reconstrucción final desde geometría5,118×10⁻¹⁶, ambos dentro de las tolerancias prefijadas. No se usó autograd para entrenar. RTX3090/UUID fijado, Torch2.6.0+cu124/CUDA12.4/driver581.29. Pico CUDA reservado22MiB; RSS agregado878,60MiB.

Costes completos de los workers: CPU370,46s y CUDA390,09s; pareja760,80s. Esta observación no muestra aceleración global de entrenamiento. Es una sola pareja sin intervalo estadístico de tiempos. Las auditorías geométricas CPU consumen350,49s en el baseline y363,40s en el worker CUDA; el rebuild final consume17,57/17,79s. La parte CUDA de pérdida/gradiente/Adam suma2,12s; preparación de fase/subida1,16s, readbacks0,018s y controles CPU extra1,22s. El baseline suma1,17s en pérdida/gradiente/actualizaciones. Se conservan importación, compilación y todos los costes adicionales. No se midió energía.

[Índice permanente](validation/geometry-cuda-training-2026-10-09/attempt01/evidence_index.json), [supervisor](validation/geometry-cuda-training-2026-10-09/attempt01/supervisor.json), [resultado CUDA](validation/geometry-cuda-training-2026-10-09/attempt01/cuda/result.json) y [CPU](validation/geometry-cuda-training-2026-10-09/attempt01/cpu/result.json). AMD real, GPU de triángulos, integración CUDA en el complemento instalado y calibración física permanecen sin validar.
