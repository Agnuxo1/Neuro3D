# Instalación e interfaz de la red geométrica propia

Estado: PRIMER INTENTO INVÁLIDO, métrica nula; integración nativa pendiente. Este complemento nuevo es una integración del núcleo óptico propio desde geometría evaluada. El complemento histórico y sus resultados se conservan.

## Artefacto reproducible

[ZIP 0.1.0](../Blender/releases/optic-neuro-blender-0.1.0.zip), 619889 bytes, SHA-256 `733ff519696720c08df390e7329161c35d43c2310991098d393d1f5f5ab0e286`. Dos reconstrucciones consecutivas produjeron exactamente esos bytes. El [manifiesto](../Blender/releases/optic-neuro-blender-0.1.0-manifest.json) identifica los archivos internos, las fuentes originales y las únicas reescrituras de importación necesarias para aislar el núcleo. No se empaqueta código óptico de BlenderPhotonics ni BOS. Se incluye la licencia MIT original.

Dependencias: Blender 4.5 con NumPy incluido, biblioteca estándar y supervisión de recursos Windows/Linux. No requiere Python de sistema, Torch, SciPy, una GPU ni un checkout del repositorio para el complemento. Esa portabilidad es una propiedad prevista del paquete; cada plataforma exige su propia ejecución de aceptación.

## Flujo de usuario previsto

1. Conserva la escena actual. Instala el ZIP desde Preferencias → Complementos → Instalar desde disco y activa OpticNeuroBlender.
2. En la barra lateral OpticNeuro, abre el ejemplo entrenado propio. La apertura usa `use_scripts=False`.
3. Selecciona una carpeta existente para conservar evidencia. Introduce cinco amplitudes no negativas y cinco fases en radianes: r0, r1, c0, c1, c2. Son campos mutuamente coherentes en una referencia común. No se aplica una normalización oculta.
4. Inferir captura la geometría evaluada, guarda una copia de trabajo y lanza un proceso propio de Blender. El recorrido debe estar completo y superar la auditoría geométrica independiente antes de producir campos y potencias modales.
5. Entrenar usa el protocolo Iris 120/30 y 60 actualizaciones ya declarado. Restaura la misma geometría absoluta no entrenada, conserva las 61 auditorías y usa gradientes propios; los controles manuales de entrada se reservan para inferencia. El entrenamiento se ejecuta dentro del proceso de Blender y se reconstruye desde las coordenadas nativas finales.
6. Cancelar termina únicamente el proceso creado por ese trabajo. Los archivos quedan conservados. Aplicar/recuperar exige la misma escena, entradas, paquete, petición y recibo de integridad del resultado. Se validan todos los parámetros antes de escribir y se restaura la geometría anterior si falla la aplicación.
7. Guardar exige un nombre .blend nuevo. No sobrescribe el ejemplo ni el archivo activo.

La interfaz informa BU, λ=0,1 BU y potencia modal normalizada. La escala física sigue sin calibrar. Las ejecuciones iniciadas por el usuario son exploratorias y no constituyen un protocolo científico registrado automáticamente.

## Prueba fijada antes de ejecutar

Perfil [own_blender_addon_profile_2026-10-09.json](research/own_blender_addon_profile_2026-10-09.json), UUID `112ba35c-70a9-473d-ba27-fba6db2a4239`, SHA-256 `071d46a1dc6cb7654d43db41c1c327be05864f379549837c798ccf73c854374b`. Incluye 32 fuentes/artefactos y la identidad del ejecutable Blender 4.5.14. La autorización humana de continuidad GitHub se aplica; la vía externa/IPFS sigue pendiente, sin identificadores.

La prueba instala el ZIP realmente en directorios de scripts/configuración aislados, sin consultar el checkout para el núcleo instalado. Comprueba nueve controles:

- Instalación ZIP y registro de operadores/panel.
- Inferencia en un Blender secundario y paridad de las 150 salidas del ejemplo propio, tolerancia 10⁻¹¹ y mismas decisiones.
- Rechazo de resultado obsoleto tras cambiar entradas.
- Rechazo tras cambiar geometría.
- Cancelación de un proceso real de Blender y conservación de su evidencia.
- Entrenamiento propio dentro de Blender con 61 auditorías, reducción de pérdida y reproducción nativa final ≤10⁻¹¹. Se registra la diferencia con la trayectoria anterior, sin exigir identidad entre distintas versiones de Python/NumPy.
- Recuperación de un trabajo completo tras volver a registrar el complemento y aplicación atómica.
- Nueva copia, reapertura e integridad del ejemplo original.
- Rechazo de un resultado cuyo hash ya no corresponde al recibo.

Límites: 1500 s, un núcleo CPU, sin GPU, RAM libre inicial ≥4000 MiB/suelo ≥2500 MiB, RSS agregado de procesos propios ≤2000 MiB y evidencia de ejecución ≤128 MiB. Una interrupción o resultado inválido produce métrica nula, sin convertir el fallo en una aprobación.

Esto evalúa software nativo e instalación local aislada. La automatización sin interfaz gráfica no acredita usabilidad humana, réplica por especialistas externos, ejecución AMD ni fidelidad física.

```powershell
python -X utf8 Tools/run_frozen_own_addon_audit_v1.py --profile Docs/research/own_blender_addon_profile_2026-10-09.json --registration Docs/research/own_blender_addon_registration_2026-10-09.json --out D:/PROJECTS/.cognition/neuro3d-sequential-20261008/own-blender-addon-20261009-run01
```

Referencia de API: [operador de guardar una copia](https://docs.blender.org/UATEST/api/current/bpy.ops.wm.html). La prueba nativa confirma el comportamiento efectivo del ejecutable fijado, por encima de su descripción documental.

## Primer intento: sin resultado de instalación

Publicado `8c3e189bd325ac0f65502e78bada57cc1a66024d`. La verificación previa detectó LICENSE con CRLF en el directorio y LF en el blob Git; era el único desajuste de las 32 fuentes. El operador inició el ensayo pese a ese fallo de verificación, por lo que no se considera un ensayo con todas las preimágenes verificadas. El proceso real de Blender terminó antes de instalar el ZIP: el control comparaba la cadena «4.5.14» con `bpy.app.version_string`, cuyo valor efectivo incluye «LTS».

Se conservan [salida bruta, recibo del operador e índice](validation/own-blender-addon-2026-10-09/attempt01/evidence_index.json): 2,433 s, RSS agregado máximo 151,094 MiB, salida 3, métrica nula, sin resultado de instalación ni de red y procesos propios cerrados. La corrección será un perfil nuevo y publicado, comparando la versión numérica y exigiendo verificación completa exitosa antes de ejecutar. El ZIP y el perfil anterior no se sustituyen.

## Perfil corregido v2, todavía no ejecutado

[Perfil v2](research/own_blender_addon_profile_v2_2026-10-09.json), UUID `094c18d3-fe39-4b40-9078-57818517c0fc`, SHA-256 `b793e9de42ce10f33a6acc962f2660d7620d64da333afb0cb4923003286c4c96`. Usa `bpy.app.version == (4, 5, 14)` y el mismo ejecutable fijado. El ZIP 0.1.0, las nueve comprobaciones, los algoritmos, las tolerancias y los límites de recursos siguen iguales. Se preservan ahora explícitamente en Git los bytes CRLF de LICENSE que ya contiene el ZIP; el texto de la licencia MIT y las versiones históricas se conservan.

```powershell
python -X utf8 Tools/run_frozen_own_addon_audit_v2.py --profile Docs/research/own_blender_addon_profile_v2_2026-10-09.json --registration Docs/research/own_blender_addon_registration_v2_2026-10-09.json --out D:/PROJECTS/.cognition/neuro3d-sequential-20261008/own-blender-addon-20261009-run02
```

La comprobación de todos los bytes Git y del remoto debe terminar con salida 0 antes de lanzar este proceso.

El segundo intento se ejecutó después de verificar las 32 fuentes y el remoto en `02572a80ba966e6a807b993c6e6c3d76dc67fa0a`. La instalación ZIP aislada y el registro de operadores sí funcionaron. La inferencia se detuvo al pasar campos complejos al auditor mediante un conversor que sólo admite racionales. Se conserva [el intento completo](validation/own-blender-addon-2026-10-09/attempt02/evidence_index.json), 42,7916 s, RSS agregado máximo 529,461 MiB, métrica nula y sin resultado de inferencia o entrenamiento. La corrección será un nuevo worker que usa el conversor complejo existente y un ZIP 0.1.1, conservando 0.1.0.
