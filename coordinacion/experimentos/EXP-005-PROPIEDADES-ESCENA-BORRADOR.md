# EXP-005 — propiedades ópticas leídas de la escena (borrador, NO GO)

Objetivo acotado: comprobar que la escena guardada gobierna no solo la **longitud geométrica** (EXP-004), sino también al menos una fase óptica y una longitud de onda. Continúa siendo un trazador digital híbrido; no demostraría que Cycles o los fotones ejecuten por sí mismos la inferencia. No ejecutar antes de congelar fixture, oráculo, código, umbrales y recursos. JEV no ha avalado este borrador: la consulta sigue bloqueada por revisión de seguridad; se usa fallback local explícito.

## Estado de partida verificable

Conf1 conserva 16 MZI/8 modos y pasa el gate híbrido local DEC-022. En `blender_lattice_run.py`, `T`, `R` y `M` son constantes Python, `lambda` procede del JSON externo, y cada objeto guarda solo `kind`. Así, un cambio de propiedad óptica del objeto en `.blend` no puede afectar el cálculo actual. Mantener conf1 y su v0 sin cambios; crear fixture/escenas nuevos.

## Contrato mínimo propuesto

1. Guardar en `scene` una longitud de onda simulada `lambda_BU > 0` y en cada espejo una fase `phase_rad` finita; el trazador debe leerlas **después de reabrir** el `.blend`. Para esta primera versión, magnitud del espejo = 1 y el factor de campo es `-exp(i·phase_rad)`. Las constantes del divisor pueden mantenerse fijas, pero esa limitación debe declararse. Valor ausente, no finito o fuera de esquema → fallo cerrado, no fallback silencioso al fixture.
2. Hacer una copia de la escena base y cambiar solo `c12.r1.phase_rad` de 0 a `+0,1 rad`; guardar/reabrir, comparar SHA y verificar que ninguna matriz/posición/normal/topología cambió. Control sham: cambiar únicamente el color de visualización del objeto; los campos simulados deben permanecer idénticos. El color visual no equivale a longitud de onda física.
3. Hacer otra copia que cambie solo `scene.lambda_BU` de `0,100` a `0,101 BU`; guardar/reabrir. Todos los demás parámetros, incluidas las posiciones, quedan idénticos.
4. Para los tres tratamientos (base, fase, longitud de onda), conservar trazas de primer impacto con secuencia, distancia, cara de llegada, coeficiente complejo aplicado y campo **por camino** antes de la suma. Comparar con un oráculo independiente de escena completa que no consuma el acumulador del runner. El consumidor por celdas debe concordar con la suma de escena completa en cada campo complejo; umbral propuesto `≤ 2e-3` hasta medir precisión numérica del oráculo por separado.

## Gates falsables antes de cualquier promoción

- G0: hashes de código/fixture y tres `.blend` registrados; readback exacto de propiedades ópticas y de geometría no editada.
- G1: `base→fase` conserva multiconjunto de rutas y longitudes dentro de `1e-6 BU` por impacto. Un camino que toca `c12.r1` **n veces** recibe el factor relativo `exp(i·n·0,1)`; los que no lo tocan conservan campo por camino. Si esta topología garantiza n≤1, demostrarlo con el historial, no asumirlo. Un camino contrario refuta el gate.
- G2: `base→lambda` conserva multiconjunto y longitudes; para cada camino de longitud L, la fase relativa esperada es `exp[i·2πL·(1/0,101−1/0,100)]`. Se evalúa el campo complejo, no solo intensidades.
- G3: ambas perturbaciones cambian al menos una salida de forma concordante con el oráculo; el sham deja campos complejos iguales. El umbral mínimo de cambio se fijará a partir del oráculo **antes** de la medición, no a posteriori.
- G4: conservación de energía de la matriz ampliada de detectores/escapes, incluidos los 28 pares de entradas con fases 1/i; objetivo `max|S†S−I| ≤ 1e-3` en los tratamientos sin pérdida.
- G5: si eliminar o ignorar las propiedades guardadas en escena deja la salida igual, el experimento falla aunque las intensidades aparenten ser plausibles.

No iniciar benchmarks de ventaja con este resultado por sí solo: demostraría propiedades de escena consumidas por software, todavía no computación óptica física ni neuronas dependientes de intensidad. Para esa meta hará falta otro gate de no linealidad, libro mayor de absorción y una comparación honesta de coste/precisión con cómputo digital.

## Unidad CPU previa al runtime — 2026-09-29

`Blender/tests/exp005_scene_properties.py` valida una instantánea con longitud de
onda y fases explícitas, sin defaults del fixture, y registra coeficiente y campo
por impacto de un camino suministrado. Once pruebas CPU sintéticas pasan: factores
de fase por multiplicidad, lambda, sham, inmutabilidad y fallos cerrados. No lee
todavía `.blend`, no genera rutas, no suma escapes y NO es un oráculo independiente
de escena completa. El experimento sigue **NO GO** hasta completar esos componentes,
recibir crítica y congelar los umbrales/fixture. JEV continúa bloqueado, sin aval.

Puente de readback preparado (sin ejecución Blender):
`Blender/tests/exp005_scene_readback.py`. Exporta vértices de malla en mundo y
caras reales, fase de espejo/lambda obligatorias, IDs y fuentes guardados en escena
y SHA del archivo reabierto. Diez tests con escenas falsas pasan; con el consumidor,
21/21 CPU sintéticos. El constructor de un fixture nuevo deberá guardar
`optical_object_ids` y `optical_sources` según
`coordinacion/respuestas/EXP-005-READBACK-PREPARADO-CODEX.md`. No cambiar conf1 ni
confundir este interfaz preparado con readback real ya ejecutado.
