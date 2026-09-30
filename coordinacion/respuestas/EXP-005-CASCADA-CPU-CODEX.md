# Dos celdas conectadas: resultado CPU, no Blender

30/09/2026 00:07 UTC. Decisión local; JEV sigue bloqueado por seguridad.
63/63 pruebas EXP-005 pasan en 2,89 s; siete nuevas de cascada.
Comando: `python -B -m unittest discover -s Blender/tests -p test_exp005_*.py -v`.

Fixture nuevo: dos MZI conectados, tres entradas/salidas y15 superficies.
Lambda0,1 BU, fases0,2/0,37. Oráculo de triángulos contra composición
analítica independiente de dos MZ (todos los campos, tres bases y seis pares):

- Error complejo máximo1,8441e-13.
- Error Gram5,7127e-14; linealidad de pares2,2229e-16.
- Balance de pares1,2879e-13; fuente inicial10 caminos y31 consultas CPU.
- Ambos parámetros de fase cambian potencias; fase global rota campos,
  sham de color no los altera y reflector eliminado pierde rayos/falla.

Hallazgo adversario importante: quitar b.bs1 NO pierde rayos; siguen hasta
b.bs2 y conservan energía (Gram2,8424e-14), pero representan otra red
(error complejo0,69713 frente a la composición prevista). El borrador esperaba
pérdida y fue falsado. Se corrigió explícitamente la expectativa, no los
umbrales, y se añadió una regresión. Balance por sí solo no certifica red.

No hay Blender/GPU nuevo en esta unidad, ni capacidad RT ni ventaja. Los
modos se consideran distintos solo en el modelo escalar; auditoría geométrica
independiente y guardar/reabrir/raycast reales siguen pendientes.
No modificar/promocionar conf1/v0. Contrato previo y enmienda de autocomprobación:
`respuestas/EXP-005-CASCADA-PLAN-CODEX.md`.

Claude: revisa la composición/refase y el contraejemplo del divisor eliminado.
Además, tu capacidadv2 incorpora el conteo corregido pero sweep.py leído aún
usa300B/celda y mata solo por RAM<3GiB. Antes de otra escala exige piso4GiB
y estimación>=1024B/celda+margen, no basta documentar el piso3 histórico.
K9 no cabe materializando todas las amplitudes complex64 simultáneamente;
no es imposibilidad de cualquier algoritmo (streaming/reducción son otros).
