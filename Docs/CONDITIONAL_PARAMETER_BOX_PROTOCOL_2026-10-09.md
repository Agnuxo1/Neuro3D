# Estabilidad condicional en intervalos continuos de parámetros

Estado: cuatro análisis continuos completos; topología demostrada en las cuatro cajas y decisiones desconocidas conservadas. La certificación nativa anterior fija la aritmética de 150 filas, pero no la geometría pretendida ni una tolerancia física. Este análisis añade una familia virtual explícita de perturbaciones sobre las superficies representadas.

[Perfil](research/native_parameter_box_profile_2026-10-09.json), UUID `3dc215f1-e2b6-4288-9944-2b9b8ae5a9c6`, SHA-256 `283249c645c3457f874f8ff85bfd50938412cd9c78f8aab6fb76d7f217f727b7`, 29 pins; [continuidad humana GitHub](research/native_parameter_box_registration_2026-10-09.json). Registro externo/IPFS pendiente y sin IDs.

## Familia y prueba

Dieciséis parámetros desplazan conjuntamente cada pareja r1/r2 en world-X. En torno a cada coordenada final capturada se define el intervalo cerrado entre las mitades de las distancias a los dos números binary32 adyacentes. Se fijan cuatro ampliaciones de esos intervalos: **1, 10, 100 y 1000**. Es una definición matemática de caja; no prueba las preimágenes de redondeo de toda la canalización Blender, ni una tolerancia de fabricación.

El módulo independiente deriva de los planos las expresiones afines exactas de origen, punto, distancia y referencia terminal. Exige igualdad de las expresiones de origen en cada fusión y normals/direcciones fijas bajo traslación. Para cada uno de los 133 estados:

- Demuestra distancia positiva y pertenencia de todo el punto perturbado a una vecindad cuadrada cubierta por la unión de triángulos del objeto seleccionado.
- Comprueba todos los otros objetos: intersección detrás, estrictamente después de la seleccionada, fuera de cada triángulo, paralelo separado o excluido durante todo el intervalo temporal para posible coplanaridad.
- Sólo excluye contacto cero con el plano anterior si es una identidad afín exacta. No añade epsilon ni elimina una rama de potencia no nula.

Si cualquier competidor o soporte no queda probado, la caja devuelve `UNKNOWN_TOPOLOGY_NOT_PROVED` y no calcula campos. El conjunto de primitivas coincidentes puede cambiar dentro de la unión: se prueba el objeto y la propagación óptica, no una identidad artificial de triángulo.

Si la topología queda probada para **todos los puntos** de la caja, intervalos racionales dirigidos componen las fases geométricas y campos de las 150 entradas con el codificador ideal entrenado sólo en 120 filas. Se reportan intervalos de potencia y argmax estable sólo por separación estricta. Los solapamientos permanecen desconocidos; no significan una inestabilidad observada.

Las cotas entre el campo/potencia nativo del centro y cualquier valor matemático de la caja incluyen variación geométrica. No deben compararse ni confundirse con el presupuesto de redondeo `10⁻¹¹` del ensayo anterior. No se promete certificar un número mínimo de filas ni se ajustan ampliaciones después de observar resultados. Se informan decisiones estables correctas y equivocadas por separado.

Cinco controles independientes pasan antes de publicación: rango afín firmado exacto, caja continua y salidas frente a composición de 90 dígitos sobre geometría reconstruida, caja grande no demostrada que prohíbe campos, rechazo de fusión con espejos sin emparejar y superficie competidora muy cercana que impide una falsa certificación basada únicamente en soporte interior. Las posiciones de control no sustituyen la prueba continua.

## Recursos y alcance

900 s, un núcleo, sin GPU, RAM libre inicial ≥4000 MiB/suelo ≥2500 MiB, RSS propio ≤1500 MiB, evidencia ≤128 MiB y certificado JSON ≤64 MiB. Métrica 1 significa análisis válido de las cuatro cajas, incluso si algunas decisiones/topologías permanecen desconocidas. Una interrupción o fuente inválida conserva métrica nula. Las fuentes/perfil deben publicarse y verificarse contra Git antes de analizar.

```powershell
python Tools/run_frozen_parameter_boxes_v1.py --profile Docs/research/native_parameter_box_profile_2026-10-09.json --registration Docs/research/native_parameter_box_registration_2026-10-09.json --out D:/PROJECTS/.cognition/neuro3d-sequential-20261008/native-parameter-boxes-20261009-run01
```

Esto no encierra incertidumbre de malla/transformación original, medición de entradas, redondeo de ejecuciones nativas perturbadas no observadas, difracción/polarización/Maxwell o calibración física. No se afirma que el presupuesto de error completo hasta un dispositivo físico esté cerrado.

## Resultado y límites de utilidad

Publicado y verificado antes de analizar en `1a27b3c9373930907a839564cfbd322998a5aee6`, todos los 29 pins idénticos a Git. [Certificado completo](validation/native-parameter-boxes-2026-10-09/analysis01/worker/certificate.json) e [índice de evidencia](validation/native-parameter-boxes-2026-10-09/analysis01/evidence_index.json). Tiempo completo 276,3123 s, RSS máximo 64,731 MiB. Métrica 1 significa **análisis válido**, no robustez de todas las decisiones.

En cada caja se prueban los 133 estados y las 13.699 exclusiones de objetos competidores, con pertenencia continua a las uniones de superficies seleccionadas. No queda topología desconocida para estas cuatro cajas. El máximo desplazamiento por parámetro de la caja 1 es `9,5367431640625×10⁻⁷ BU`.

| Ampliación | Máximo desplazamiento BU | Argmax estables | Desconocidos | Estables correctos / equivocados |
|---|---:|---:|---:|---:|
| 1 | 9,5367431640625×10⁻⁷ | 147/150 | 3 | 137 / 10 |
| 10 | 9,5367431640625×10⁻⁶ | 131/150 | 19 | 127 / 4 |
| 100 | 9,5367431640625×10⁻⁵ | 40/150 | 110 | 40 / 0 |
| 1000 | 9,5367431640625×10⁻⁴ | 0/150 | 150 | 0 / 0 |

La primera caja deja indeterminadas las filas 56, 83 y 84; las tres son errores del clasificador en el centro. No se ha demostrado que esas filas cambien de clase con una perturbación. En la ampliación 1000 la inclusión conservadora deja todas las decisiones desconocidas: no significa que todas sean físicamente inestables.

Las cotas máximas campo L1/potencia frente al centro nativo son 0,012213/0,006176, 0,121962/0,068354, 1,215121/1,341013 y 14,316026/108,262837. Son cotas superiores de variación, redondeadas hacia arriba en este resumen, no variaciones medidas ni fallos del presupuesto aritmético `10⁻¹¹`. Dependencias repetidas y sumas de numerosos caminos pueden ensancharlas; el método no promete cotas óptimas. La prueba sólo cubre la familia afín conjunta declarada.

![Cobertura y cotas de estabilidad condicional](assets/native-parameter-boxes-2026-10-09.png)
