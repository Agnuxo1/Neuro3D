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

## Resultado nativo

El perfil se publicó en `2e14f4c1189ece21ab670d774ba522ddd8a0358b` antes
de ejecutarse. Los 29 archivos fijados coincidían con los bytes en GitHub.
El [recibo con fuentes y artefactos](validation/trained-geometry-blender-reproduction-2026-10-09/attempt01/evidence_index.json)
da `VALID_NATIVE_BLENDER_REPRODUCTION`, métrica 1: 37,63 s supervisados y
298,59 MiB de RSS máxima observada, sin interrupción.

Blender 4.5.14 LTS guardó y reabrió el archivo nuevo. La identidad de la captura
se conserva y la geometría óptica recapturada coincide exactamente con la
representada entrenada. El grafo reconstruido tiene 133 estados. Las potencias
de las ocho salidas para las 150 entradas coinciden con diferencia observada
máxima 0, y las 150 predicciones son idénticas. El cero describe esta comparación
entre dos ejecuciones; no un error nulo frente al modelo exacto o físico.

La auditoría independiente secundaria también verifica primeros hits, ramas
y vecindades interiores en los 133 estados de la captura reabierta. El `.blend`
original conserva su hash. Se publica el [archivo entrenado nuevo](validation/trained-geometry-blender-reproduction-2026-10-09/attempt01/worker/trained_geometry.blend).
Es reproducción local dentro de Blender; la réplica por un equipo externo y
la instalación limpia de la interfaz siguen pendientes.
