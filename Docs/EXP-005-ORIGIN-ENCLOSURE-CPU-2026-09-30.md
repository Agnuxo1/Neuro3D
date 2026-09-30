# Cota del origen reconstruido: válida en el modelo CPU, demasiado conservadora

2026-09-30 09:49 UTC. Fallback local; JEV bloqueado, sin aval remoto.

Continuación del replay de partidas redondeadas, sin alterar el testigo previo,
los shaders ni los criterios congelados. No nuevo muestreo de self-hits.

Para cada una de las 24 consultas retenidas se reconstruye el punto ideal de
la primera intersección, sobre los inputs ya representados, con racionales.
El árbol de intervalos CPU encierra t; se calcula la caja de `o + d*t` y la
distancia máxima por eje desde el punto redondeado guardado hasta esa caja.

Para normal no normalizada n y dirección de salida d, se proyecta la cota:

`radio_t = suma(|n_i| * radio_i) / |n · d|`.

Las sumas/radios de esta proyección se calculan como racionales, no redondeando
hacia abajo. Cada distancia firmada racional del replay cae dentro de la cota;
la identidad de plano coincide exactamente con el t de Möller-Trumbore previo.
No se fuerza a cero el residual ni se desplaza/proyecta el punto guardado.

## Resultado y limitación operacional

24 distancias firmadas contenidas, 72 componentes de punto encerradas.
Cuatro tests PASS en 0,039s, CPU un hilo: caso plano exacto, salida paralela/ID
inválido, binding del query, cobertura única completa e inmutabilidad.

| Frame | Radio proyectado mínimo–máximo (BU) | Máximo radio por eje (BU) |
|---|---:|---:|
| Mundo | 0,007367525–0,332009787 | 3,810005467e-8 |
| Local | 0,007367445–0,332009538 | 3,810005222e-8 |

Aunque contiene los offsets retenidos, la caja sin correlaciones se amplifica
mucho con incidencia rasante. Una banda de partida basada directamente en
estos radios podría bloquear superficies separadas y rayos útiles; NO adoptarla
como gate eficiente ni convertirla en una exención por primitiva. La cota no
es un error real observado: es un sobreestimador del modelo de intervalos.

## Evidencia y límites

- Report nuevo `D:/PROJECTS/.cognition/neuro3d/exp005_origin_enclosure_cpu_20260930_0950.json`.
  SHA256 `b8c61151cff172b6c872a8017810b2d699d6df1442ac5383c7180ca17ec6ba28`.
- Inputs0804/0942 verificados por sus SHA congelados; 18 hashes de código
  comprobados. Cotas/radios racionales y consultas retenidas en los artefactos.
- Reproducir: `python -m unittest discover -s Blender/tests -p test_exp005_origin_enclosure.py -v`.
- Inputs traducidos/redondeados tratados como exactos; no incorpora su error
  previo, certificación del primer nearest global ni autenticación histórica.
- Dirección reflejada tomada como input, NO cota de error de reflexión.
- No certifica árbol GPU/FMA/FTZ, Bpy, transporte, campos/fase, RT ni rendimiento.

Siguiente unidad: comparar una cota que conserve la correlación del plano con
estas cajas, con contraejemplos de gap/otras caras y sin bajar tolerancias.
Esto exige contrato propio antes de cualquier integración nativa.

Claude PRECISION-005: critica un caso local retenido y propone un control
de solape que impediría omitir una superficie legítima. No nuevo encargo
paralelo; 006 después. No GPU ni writers ajenos.
