# Entrenamiento propio con CUDA desde geometría capturada

Estado al congelar: **preparado, no ejecutado**. Autorización humana de continuidad GitHub aplicada; registro externo/IPFS pendiente, sin identificadores emitidos.

Se repetirán, en el mismo equipo, el entrenamiento CPU original y una ejecución CUDA propia. Ambos utilizan los mismos 120 ejemplos de entrenamiento, 30 de evaluación, inicialización, 16 parámetros, 60 actualizaciones Adam, temperatura de pérdida, cotas geométricas y cuantización nativa del [perfil Iris original](research/captured_geometry_training_profile_2026-10-09.json). Cada ejecución auditará independientemente sus 61 estados y reconstruirá desde cero la geometría final. No se seleccionarán semillas ni pasos usando las etiquetas de evaluación.

La ejecución NVIDIA realizará propagación coherente complex128, Jacobiano propio, pérdida por entropía cruzada y actualización Adam float64 en el dispositivo. La preparación afín exacta, los argumentos de fase, la cuantización binary32 nativa y las auditorías geométricas permanecerán en CPU. No se afirma trazado de triángulos en CUDA ni entrenamiento íntegro de Blender en GPU. Autograd no participa en el entrenamiento; sus controles de software son separados.

En cada estado CUDA se compararán campos, potencias, pérdida y gradiente con el evaluador CPU en esa misma geometría. Tolerancias fijas: 10⁻¹¹ para campos, potencias y pérdida, y 10⁻⁹ para gradientes. Se conserva el control inicial por diferencias finitas ≤10⁻⁴ y la reconstrucción geométrica final ≤10⁻¹¹. Las trayectorias CPU y CUDA finales podrán diferir; se publicarán las diferencias y el acuerdo de las 150 decisiones sin imponer igualdad bit a bit del optimizador.

Se medirán tiempos completos de los dos workers, importación, compilación geométrica, preparación y subida, cálculo CUDA, descargas, controles CPU y auditorías. CUDA tiene controles adicionales por estado que se contabilizan. Es una pareja de ejecuciones, sin intervalo estadístico de velocidad ni medición energética. Cualquier comparación de tiempos quedará limitada a ese contrato y a este equipo.

El ensayo entrará en la cola FIFO compartida con reserva de 4 GiB de VRAM y requisito de 8 GiB de RAM libre. Límites: un núcleo CPU, 900 segundos por entrenamiento, 1.900 segundos totales, suelo de RAM de 4.000 MiB, RSS propio de 1.500 MiB, memoria reservada CUDA de 1.024 MiB y evidencia de 128 MiB. Solo se cancelarán descendientes propios.

Se fija la RTX3090 por UUID, junto a las versiones reales de Python, NumPy, Torch, CUDA y driver en el [perfil](research/geometry_cuda_training_profile_2026-10-09.json). Los tres controles de pérdida/gradiente/Adam han pasado contra referencias independientes CPU antes de congelar el ensayo; eso no es una ejecución científica de entrenamiento NVIDIA. Un ensayo incompleto o fallo de entorno tendrá métrica nula; una pareja completa con descenso de pérdida suficiente en ambos tendrá métrica 1; un descenso insuficiente conservará métrica 0.

[Autorización](research/geometry_cuda_training_registration_2026-10-09.json), [worker](../Tools/train_captured_geometry_cuda_v1.py), [supervisor](../Tools/run_frozen_geometry_cuda_training_v1.py). AMD sigue pendiente porque no hay hardware AMD disponible; no se sustituirá con emulación ni NVIDIA.
