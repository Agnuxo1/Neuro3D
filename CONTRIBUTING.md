# Contribuir a Neuro3D

## Regla de validación

El oracle CPU es la referencia. Cualquier adaptador Blender o Unreal debe demostrar
paridad mediante readback antes de declararse equivalente.

## Antes de activar GPU

No actives shaders, renders o benchmarks GPU sin comprobar que la tarjeta está libre
y sin registrar la versión exacta de Blender, driver y backend. La ruta Blender de
esta versión permanece GPU-dormant por defecto.

## Cambios esperados

- Mantén separadas las capas `Blender/core`, `Blender/addon` y `Blender/shaders`.
- Añade pruebas CPU para cada nueva regla del modelo.
- No subas `Binaries`, `Intermediate`, `Saved`, cachés, credenciales, binarios ni
  telemetría sensible.
- Describe en la documentación qué está verificado y qué es sólo una hipótesis.

## CI

El workflow de GitHub Actions es manual (`workflow_dispatch`) para que la publicación
no lance pruebas automáticamente. Ejecútalo sólo cuando el responsable del proyecto
lo autorice.
