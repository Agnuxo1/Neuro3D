# Cotas de intersección: modelo CPU de intervalos

Preparación de precisión, no certificado GPU ni reparación. El modelo propio
propaga intervalos binary64 de t, u, v, determinante y u+v con redondeo hacia
afuera mediante nextafter. Usa un árbol de operaciones explícito; no presupone
equivalencia con FMA, reassociation, fast-math, FTZ o compilador GLSL.
Los extremos iniciales son las coordenadas representadas, sin incluir error
de Blender, cuantización/exportación, transporte o posición acumulada del rayo.

50 consultas sintéticas pequeñas: 24 sobre planos de los fixtures F5, 24 de
interior con coordenadas0/100/1e4 y dos paralelas. En las48no paralelas, los240
valores racionales exactos de t/u/v/det/u+v quedan dentro de las cotas calculadas.
Esto contrasta la referencia CPU; no prueba todas las geometrías ni runtime nativo.

| Clasificación del modelo CPU | Consultas |
|---|---:|
| Posible impacto en intervalo cercano | 12 |
| Pertenencia al borde triangular incierta | 12 |
| Impacto interior hacia delante | 24 |
| Determinante incierto/contiene cero | 2 |

Ocho de los doce casos cercanos son partidas exactas t=0. Una regla ingenua
«abortar todo intervalo que toque0» rechazaría esos controles válidos de partida.
No se fuerza una cota0 para convertirlos enPASS. Los dos casos paralelos
conservan incertidumbre, no se convierten silenciosamente en miss. Los bordes
inciertos tampoco se descartan: falta justificar su pertenencia/partida.

Siete tests enfocados PASS0,018s:128 comprobaciones aritméticas con referencia
racional, consultas completas, cancelación exacta con intervalo no puntual,
denominador cero/overflow/NaN/bounds, triángulo exterior y parámetro negativo.
Sin GPU, Blender, campos ópticos, escritores de Claude ni suites completas repetidas.

Report D:/PROJECTS/.cognition/neuro3d/exp005_interval_cpu_20260930_0920.json
SHA `712423f4935ec0c9e73a512908cc34917edf43ae892ea812fc73547e7a986be8`;
15 hashes de código, inputs, intervalos y racionales retenidos.

Pendiente antes de integrar: certificado de partida y primitiva/snapshot,
enclosure del árbol real nativo y de la pertenencia triangular, transporte y
posición acumulada, flags por rama y gates de campos/phase/ledger completos.
Este modelo no sustituye inferencia de escena por oráculos CPU. No cambia los
shaders/contratos congelados, ni t_min, ni bounds/conf1. JEV bloqueado, fallback local.
