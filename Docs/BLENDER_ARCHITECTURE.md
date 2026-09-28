# Arquitectura Blender de Neuro3D

```text
             estado común / oracle
                       │
          ┌────────────┴────────────┐
          │                         │
   Blender CPU preview       Blender GPU adapter
   (activo en esta fase)     (preparado, apagado)
          │                         │
          └────────────┬────────────┘
                       │
             objetos, curvas y color
                       │
                 escena Blender
```

El contrato compartido es el estado por neurona: posición, fase, frecuencia,
intensidad, energía y color RGB. Las conexiones contienen origen, destino, peso y
retardo. Unreal y Blender deben consumir este esquema mediante adaptadores
independientes; ninguno sustituye al oracle CPU.

La palabra “fotónico” describe aquí un modelo numérico de señales ópticas: no se
afirma que Blender o Unreal estén realizando computación con fotones físicos.
