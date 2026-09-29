# EXP-004 · Auditoría independiente de la primera rejilla Blender K=4

Fecha: 2026-09-29 ~17:44 UTC. **Resultado mixto: gate estructural
prometedor; gate numérico original FALLA.** No se acepta EXP-004 como
red estable todavía y no se abre la batería comparativa.

Claude construyó en Blender 4.5.14 una rejilla oblicua K=4 de 8 modos,
16 MZI y 104 discos (103 tras ablación). Su trazador de árbol completo
usa `scene.ray_cast`; Python suma campos complejos y potencia. Es una
simulación digital híbrida gobernada por geometría, no cómputo óptico
físico ni interferencia realizada íntegramente por la luz de Blender.

## Readback propio de Codex

`Blender/tests/exp004_independent_readback.py` abrió, sin guardar,
`base.blend`, `delta.blend`, `sham.blend` y `ablation.blend` en
`D:\PROJECTS\.cognition\neuro3d\exp004\run_K4`. Comprobó SHA-256
bruto del fixture y de cada `.blend`, conjunto exacto de roles, clase
de disco, posiciones por tratamiento, orientación de normal sin
inversión, radios de los 64 vértices, planitud, cara única, escala,
ausencia de modificadores/padres y fuentes de la escena. Los cuatro
casos pasaron; error máximo de posición `0 BU`, de normal
`3,43e-8` y de radio `9,23e-9 BU`. SHA-256 bruto del fixture:
`5595acb8be43dae78fa5cb6ac1ea8071aa2ec561db89566b8d2db61c2dcedbb7`.
El script falló primero por un uso incorrecto de la API `Vector.distance`;
se corrigió y la corrida estricta terminó con `rc=0`. La reserva `gpuq`
quedó libre. Esto verifica geometría persistida, **no** retraza de forma
independiente el árbol óptico de Claude.

## Umbrales originales y hallazgo adicional

El comparador previo de Claude fijó `|ΔL|≤1e-5 BU`, error de campo
`≤5e-3`, balance `≤1e-6`, y paridad pre/post `0`. En K=4 los conjuntos
de rutas coincidieron con su oráculo CPU y la paridad pre/post fue 0,
pero el sham tuvo `|ΔL|=1,0097e-5 BU` y la ablación alcanzó error de
balance `7,5241e-5`. Por tanto, **la primera corrida NO PASA**.

Codex recombinó las salidas y escapes complejos guardados de las fuentes
`r0` y `c0` con entradas `(r0+c0)/√2` y `(r0+i·c0)/√2`, sin invocar el
trazador. Los errores absolutos de balance fueron:

| Tratamiento | 1+1 | 1+i |
|---|---:|---:|
| base | 1,417e-5 | 5,206e-5 |
| delta | 5,316e-5 | 4,310e-6 |
| sham | 1,838e-5 | 4,717e-5 |
| ablación | 1,1927e-4 | 3,619e-5 |

La comparación publicada por Claude dejaba `escape_power_sup=null`;
por ello no auditaba todavía ese balance coherente. El máximo de
impactos por camino en `base.json` es **36** (media 26,72), no ~15.
Un presupuesto de redondeo fundado en 15 tramos no basta para justificar
un límite global de `2e-5 BU`. Los umbrales nuevos sugeridos (`2e-5 BU`,
`1e-3` de campo, `2e-4` de balance) no pueden convertir la primera
corrida en PASS retrospectivo.

Se añadió `Blender/tests/exp004_coherent_balance.py`: sin ray tracing,
construye la matriz de dispersión aumentada de los campos y escapes
guardados y evalúa `S†S−I` y **todos** los pares de entradas con fases
relativas `1` e `i`. Las cuatro mediciones K=4 dieron:

| Tratamiento | error máximo S†S−I | balance máximo superposición |
|---|---:|---:|
| base | 8,163e-5 | 6,337e-5 |
| delta | 9,148e-5 | 6,340e-5 |
| sham | 1,0225e-4 | 8,182e-5 |
| ablación | 8,107e-5 | 1,1927e-4 |

El escape usa la clave de canal que emitió el trazador de Claude;
queda pendiente demostrar que esa agrupación corresponde siempre a
un único canal físico bajo otras geometrías. El control es más amplio
que las dos superposiciones iniciales, pero tampoco rescata el gate
numérico original.

## Siguiente gate propuesto

Antes de otra corrida, congelar por separado:

1. un presupuesto de error por tramo y por camino que incluya hasta 36
   impactos, escala de coordenadas, longitud de onda y suma coherente;
2. balances de bases y de superposiciones 1+1 y 1+i, incluyendo escapes
   agrupados por canal, sin renormalizar;
3. uno o más fixtures de confirmación nuevos fijados antes de ver sus
   medidas, además de los K4/K4c ya explorados;
4. gate de rutas/causalidad, gate de precisión numérica y coste como
   resultados separados, con resultados negativos preservados.

La decisión de tolerancias y promoción sigue pendiente de revisión
independiente y de JEV. El conector JEV permanece bloqueado sin canal
autorizado; estas conclusiones son un fallback local, no un aval JEV.
