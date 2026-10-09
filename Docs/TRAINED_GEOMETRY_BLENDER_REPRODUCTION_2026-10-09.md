# Geometría entrenada: guardar, reabrir y ejecutar dentro de Blender

El entrenamiento propio ya produjo un resultado válido en la geometría
representada. Este perfil posterior comprueba su reproducción nativa en
Blender 4.5.14, bajo la autorización humana de continuidad GitHub, antes de
afirmar que el archivo entrenado reproduce esas decisiones.

Se aplica a r1/r2 la coordenada X nativa float32 registrada para cada pareja.
El `.blend` original se conserva y se verifica su hash después. Se guarda un
archivo nuevo con un identificador explícito del modelo propio y el hash del
resultado de entrenamiento, y se reabre con ejecución de scripts desactivada.
Se recaptura la geometría evaluada y los mismos 32 bindings.

Los criterios fijados antes del ensayo son: identidad de la captura antes y
después de guardar/reabrir; igualdad exacta de objetos ópticos, fuentes y longitud
de onda admitidos con la geometría virtual entrenada; reconstrucción nueva del
grafo completo; diferencia de potencia ≤ `10^-11` para los ocho terminales de
las 150 entradas; y coincidencia de las 150 decisiones del último estado
prefijado. El preprocesado se vuelve a obtener únicamente de las 120 filas
de entrenamiento y debe coincidir con el registrado.

Se fijan 180 s, un núcleo CPU, RAM libre inicial ≥ 4.000 MiB, suelo 2.500 MiB,
RSS propia ≤ 1.500 MiB y artefactos nuevos ≤ 64 MiB. El ejecutable Blender y
29 entradas/fuentes están fijados por SHA-256. El supervisor preserva también
un ensayo fallido. Esto es reproducción local de geometría/inferencia con
Blender real; GPU, reproducción externa y fidelidad física se comprueban aparte.

[Perfil fijado](research/trained_geometry_blender_reproduction_profile_2026-10-09.json),
[registro de continuidad](research/trained_geometry_blender_reproduction_registration_2026-10-09.json),
[ejecutor bpy](../Tools/restore_trained_geometry_in_blender_v1.py).
