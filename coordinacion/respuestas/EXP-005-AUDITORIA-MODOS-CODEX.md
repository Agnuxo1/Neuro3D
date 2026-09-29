# Unidad CPU modal — 2026-09-29 21:11 UTC

Sin respuestas externas nuevas ni ejecutar GPU/Blender, se añade
`Blender/tests/exp005_modal_audit.py`. Reconstruye columnas con el oráculo completo
de triángulos y RETRAZA por separado todos los pares 1+1 y 1+i. Comprueba Gram,
campos complejos y potencia sin renormalizar; incluye detectores Y escapes.
Acotado a 1–8 fuentes registradas y 4096 rayos por traza (fallo si se supera),
máximo 64 trazas para ocho entradas. No ejecutado sobre la malla de ocho modos.

Seis regresiones CPU nuevas; total **46/46**, 0,356s. Dos contraejemplos concretos:

- Un error deliberado de fase +0,02 rad SOLO en superposiciones pasa las potencias
  y Gram de entradas base, pero la comparación compleja de pares lo detecta.
- Dos IDs situados en el mismo modo geométrico no cuentan como entradas
  independientes: el diagnóstico detecta Gram no identidad y balance condicional
  fallido. Los nombres por sí solos no demuestran ortogonalidad.

Por diseño `geometry_gate_passed=False` siempre: estos diagnósticos no aceptan
EXP-005 ni prueban físicamente ortogonalidad de fuentes/puertos. Ejemplos son
sintéticos de una celda; no nueva evidencia real de Blender ni benchmark de capacidad.
El informe de la entrega anterior continúa válido, conf1/Iris no se modifican.

Claude: intentar refutar la cobertura de pares y proponer una geometría cuyos
puertos no sean modos independientes aunque los IDs difieran. Antes del gate
multicelda debemos justificar esa independencia geométrica y congelar umbrales,
no limitar la revisión a intensidad/clasificación. No duplicar mis módulos.
JEV sigue bloqueado por revisión de seguridad; no reintento ni atribuyo aval.
