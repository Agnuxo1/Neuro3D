# Testigo de partida exacta: piloto CPU, no reparación GPU

2026-09-30 09:34 UTC. Fallback local; JEV sigue bloqueado, sin aval remoto.

El modelo de intervalos anterior marca ocho partidas matemáticas t=0 como
posibles contactos próximos. Este piloto distingue esa partida de contactos
positivos sin reducir epsilon, desplazar el origen ni excluir un objeto entero.

Se liga el testigo a SHA geométrico, rayo, ID anterior y evento mirror/t/r.
Recalcula con racionales exactos de los inputs representados t/u/v; exige t=0,
interior o borde y determinante no nulo. Solo incluye otras primitivas del mismo
objeto cuya coplanaridad exacta y contacto t=0 también se prueban. No proyecta
puntos redondeados fuera del plano: rechaza. Máximo ocho triángulos/64 vértices,
coordenadas finitas <=1e6 BU, sin renormalizar rayos guardados.

## Evidencia retenida

- Cuatro fixtures de seis triángulos: ocho partidas reciben etiqueta exacta CPU.
  Los cuatro contactos positivos a 5e-10/1e-9 BU siguen inciertos/prohibidos;
  los controles superiores conservan incertidumbre de borde. NO gate completo PASS.
- Dos rayos guardados del control plegado admiten testigo: IDs [0,1] y [2].
  No se excluyen todas las caras del objeto ni su regreso A→B→A.
- Ocho tests PASS en 0,030s, CPU un hilo: identidad/rayo/owner/proof alterados,
  evento/ID inválidos, partida fuera del plano o paralela, otro objeto en t=0,
  cara distinta del mismo objeto, distancia positiva, bounds e inmutabilidad.
- Artefacto nuevo `D:/PROJECTS/.cognition/neuro3d/exp005_departure_cpu_20260930_0934.json`.
  SHA256 `e358a954d96700e7b90788631028e853a32d67ea0bb91758222db132134323f5`.
  Catorce hashes de código verificados; shaders anteriores incluidos e intactos.

Reproducción: `python -m unittest discover -s Blender/tests -p test_exp005_departure.py -v`.
El auditor acepta `--output` nuevo y rechaza sobrescritura.

## Límites y siguiente paso

El ID previo es declaración del llamador, NO autenticación del impacto histórico.
SHA cubre fixture geométrico, no snapshot óptico completo ni exportador Blender.
La etiqueta es diagnóstico CPU: no autoriza descartar candidatos en el shader.
No hay campos, hardware RT, GPU/Bpy, cotas de transporte/FMA/posición acumulada
ni certificación física. Persisten los bordes/determinantes inciertos.

Antes de integrar: contrato explícito de historia por rama y cotejo de expresión
nativa/error del origen. Claude PRECISION-005 debe intentar una falsa exención
en otro objeto/cara o demostrar una partida válida que este criterio rechaza;
006 sigue después, sin nuevo encargo paralelo. No ampliar conf1 ni bounds.
