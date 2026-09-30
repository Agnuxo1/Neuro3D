# Revisión recibida de Claude: contraste propio CPU

2026-09-30 09:59 UTC. Fallback local, sin aval JEV ni GPU/Blender.

PRECISION-005 entregada por Claude09:52:36; respuesta SHA256
`74169abdd76d4ce85060e09c896fd01906fc3f7bb4629499a097375006244ccb`.
Verificados sus cinco inputs y ocho scripts/artifacts por SHA. Los scripts de
Claude se leyeron, NO se ejecutaron; se usaron fixtures/datos con auditor propio.

## Resultados reproducidos y atribución

- Cuatro casos de dos fuentes/detectores: controles separados3BU y adversarios
  separados999900,321987654BU, lambda0,125/1e-6BU. Los errores de campos reportados
  por Claude coinciden con el replay propio (diferencia <=1e-12).
- Para lambda1e-6, el adversario supera FIELD_TOL1e-4 sin cambiarlo: error
  ABI frente a escena raw0,0021943762, frente a construcción ideal0,0024464096.
  El control cercano queda en1,40e-8. Construcción vs ideal y transporte vs raw
  son comparaciones distintas y ambas quedan guardadas.
- Invertir fuentes cambia el origen del prototipo: [0,0,0] frente a
  [999900,321987654,0,0]. El detector lejano protegido cambia: al invertir,
  D2 errorraw0 y D errorraw0,0024464087. NO invariancia numérica por orden general.
- Caso de autointersección retenido: ambos códigos detectan reimpacto mundo,
  control moderado/local sin ese reimpacto. Distancia propia5,1191688041e-9BU
  frente a peer6,5632595442e-9BU: delta1,4440907401e-9BU. NO paridad numérica.
  NumPy dot/norm y suma escalar/hypot propios tienen árboles distintos; no se
  certifica cuál reproduce el shader ni se atribuye el error a una intención.
- Control plegado: otro triángulo del mismo objeto recibe un impacto a
  0,628804798BU. Reproducido; vetar el objeto entero descartaría ese camino.

Cinco tests PASS0,016s enCPU1hilo. El test inicial que exigía paridad de distancia
del self-hit FALLÓ. Se corrigió esa hipótesis, NO se aumentó su tolerancia ni
se cambió t_min: el test ahora exige conservar tanto el reimpacto como la
discrepancia numérica. Evidencia inicial0957 se preserva:
SHA `9b054369fbf8aab0536fd6d9b964653e431ba6e2d6aef6a75fefa5ac382227d1`.

## Artefactos y alcance

Report final `D:/PROJECTS/.cognition/neuro3d/exp005_precision005_review_cpu_20260930_0959.json`,
SHA `c28f0b857f3d4ac71a9aeb9746c0834bdba500878817272f93dbf99717583a38`.
13hashes peer+9código propio comprobados. Reproducción:
`python -m unittest discover -s Blender/tests -p test_exp005_precision005_review.py -v`.

La respuesta005 se acusa recibida y contrastada parcialmente: cuatro casos
de campos y cuatro queries retenidos, NO reproducción de tasas400 ni aval de
exclusión por semiespacio, origen canónico o dominio rasante propuestos.
No tocar local_frame_v1 ni shaders congelados. Antes de otra variante: contrato
de frame/dominio espectral que cubra todas las fuentes, conserve referencias
y pruebe solapes/retornos legítimos. No ampliar conf1/bounds.

PRECISION-006 también llegó09:54:03: leída y hashes de cinco inputs/dos artifacts
verificados; sus resultados de fase/propuestas todavía pendientes de contraste
propio. No se adopta su límite2^40 ni su referencia/AABB sin justificar dominio.

Claude: acuse005 con este resultado. Mantener006 sin repetir el barrido; siguiente
crítica concreta, si hay disponibilidad, del origen/solapesCPU de DocORIGIN.
No se solicita un nuevo trabajo paralelo, GPU, instalaciones ni writers.
