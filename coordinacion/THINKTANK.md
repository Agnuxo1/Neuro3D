# Thinktank técnico

## Hechos confirmados

- El circuito actual usa un emisor, un reflector y un receptor. Sus propiedades
  viven en la escena de Blender; Python CPU traza una reflexión.
- El smoke real en Blender 4.5.14 pasó creación, guardado/reapertura y cambios
  de geometría, RGB y frecuencia (`Docs/BLENDER_RUNTIME_REPORT.md`).
- El código actual transporta potencia RGB y una fase escalar por camino, pero
  no suma varios caminos (`Blender/core/scene_optics.py`).

## Inferencias pendientes de comprobar

- Una red de varios caminos necesitará amplitudes complejas por canal o una
  representación equivalente para obtener interferencia constructiva y
  destructiva de forma coherente.
- No deben interferir dos señales sin una condición de coherencia definida;
  mezclar frecuencias como si compartieran fase podría producir resultados
  físicamente engañosos.
- La potencia total del receptor debe permanecer acotada por la energía
  emitida y las pérdidas, con una definición explícita de reparto entre rayos.

## Propuestas abiertas

1. Definir un circuito de dos caminos con un divisor de potencia en la escena.
2. Fijar unidades, criterio de coherencia, fase por camino y normalización.
3. Probar tres casos: suma constructiva, cancelación destructiva y suma de
   potencias incoherentes; incluir un camino bloqueado como control geométrico.
4. Comparar un solo camino con el resultado existente para evitar regresiones.

Claude audita estas propuestas en `coordinacion/tareas/OPT-001.md`. Ninguna se
considera implementación aprobada por aparecer aquí.
