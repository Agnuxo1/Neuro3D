# Regresión nativa del ciclo de vida del complemento propio

Estado: cinco controles nativos completos y salida sin error de ciclo de vida. El resultado previo de nueve controles de ZIP 0.1.1 y su error de doble desregistro permanecen [archivados](OWN_BLENDER_ADDON_PROTOCOL_2026-10-09.md). Este perfil sólo pretende cerrar ese defecto de software.

[Perfil](research/own_blender_addon_lifecycle_profile_2026-10-09.json), UUID `c0bf7509-aa2a-43f2-8256-edbfb5045b0b`, SHA-256 `bbdaca49159953616da95df7ebc5f56a34ba8069917c1b1b0b184cc8979cea84`; 34 pins. [Autorización GitHub de continuidad](research/own_blender_addon_lifecycle_registration_2026-10-09.json). Registro externo/IPFS pendiente y sin identificadores.

ZIP 0.1.2 tiene SHA-256 `7b1b747ea6148f6f924a55d7b24a5d065db696295297563f5309904962d9f65f`. Dos reconstrucciones independientes producen bytes idénticos. El conjunto de archivos coincide con ZIP 0.1.1 y sólo cambian `__init__.py`, `INSTALL.txt` y `package_manifest.json`. Se verifican además todos los hashes internos: el worker, los módulos científicos y los datos permanecen byte a byte iguales.

Blender real 4.5.14, instalación aislada y autoejecución de scripts desactivada. Cinco controles prospectivos:

1. Igualdad de payload científico y datos entre versiones.
2. Tres ciclos de registro/desregistro con llamadas duplicadas.
3. Dos ciclos mediante `addon_utils.enable/disable` reales.
4. Desactivar el complemento cancela y espera su proceso Blender propio.
5. Inferencia nativa después de reactivarlo: todas las 150 potencias dentro de `10⁻¹¹` de la referencia y las 150 predicciones iguales.

El supervisor exige terminar Blender con código 0 y examina el log entero, incluida la salida: no puede contener traceback, `RuntimeError` o excepción de desregistro. Un fallo no produce métrica 1. Se conserva todo resultado y se termina únicamente el árbol de procesos creado. No se repite entrenamiento porque el worker y núcleo científico no cambian.

Límites: 180 s, un núcleo, sin GPU, RAM libre inicial ≥4000 MiB y suelo ≥2500 MiB, RSS agregado propio ≤1500 MiB, evidencia ≤128 MiB. El archivo fuente Blender y el ejecutable están fijados por hash. Publicación y comprobación de todos los blobs Git deben preceder la ejecución.

```powershell
python Tools/run_frozen_addon_lifecycle_v1.py --profile Docs/research/own_blender_addon_lifecycle_profile_2026-10-09.json --registration Docs/research/own_blender_addon_lifecycle_registration_2026-10-09.json --out D:/PROJECTS/.cognition/neuro3d-sequential-20261008/own-addon-lifecycle-20261009-run01
```

Esto no prueba usabilidad humana, recuperación de caída del host, Blender nativo Linux, física completa, GPU AMD o réplica por especialistas independientes.

Publicado y verificado antes de ejecutar en `ae6952c7363e69c7b22a69a0a13e0485a551df8e`, todos los 34 pins y recibos idénticos a Git. [Resultado nativo](validation/own-addon-lifecycle-2026-10-09/attempt01/worker/result.json) e [índice de evidencia](validation/own-addon-lifecycle-2026-10-09/attempt01/evidence_index.json). Estado `VALID_NATIVE_ADDON_LIFECYCLE_AUDIT`, métrica 1: cinco controles pasan, diferencia máxima de las 150 potencias cero y predicciones idénticas. Tiempo completo 65,0446 s, RSS agregado máximo 516,715 MiB; todos los procesos propios terminados. El log completo tras salir de Blender no contiene traceback ni errores de desregistro. El fallo de 0.1.1 se conserva. Se cierra este defecto específico; continúan las limitaciones de alcance descritas arriba.
