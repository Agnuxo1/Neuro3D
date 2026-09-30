# Cota de intensidad por fase relativa, sin cambiar el campo complejo

2026-09-30 15:55:01 UTC. Candidato CPU opt-in, NO integrado en shaders ni
runners congelados. JEV bloqueado; fallback local sin aval remoto.

## Contrato

El presupuesto absoluto anterior se conserva íntegro para campo complejo.
Para intensidad de UN puerto y UN grupo de coherencia puede factorizarse
una fase común, porque no altera el módulo al cuadrado:

    E(lambda) = exp(i*2*pi*c/lambda) * suma a_i*exp(i*2*pi*(L_i-c)/lambda)

Se elige c como punto medio racional entre el menor extremo inferior y el
mayor extremo superior de las longitudes efectivas completas de ese grupo.
Los intervalos y amplitudes proceden del árbol generado por el candidato
previo; no se suministran rutas ni referencias inventadas.

Para comparar SOLO el efecto de codificar lambda, la cota de diferencia
entre los campos con fase alineada depende de |L_i-c| en vez de |L_i|.
Se convierte a cota de intensidad con 2*A*epsilon+epsilon² y se conserva
el mínimo de esta cota y la absoluta anterior. Grupos independientes
suman intensidades; no se comparten anclas ni campos entre ellos.

Esto NO autoriza reescribir E, mover referencias ópticas ni ignorar su fase
en una etapa posterior. El resultado mantiene el campo absoluto y su gate
1e-4, potencia 2e-4 y transporte relativo 1e-12 exactamente iguales.
`complex_fields_rephased=False`, `scene_reference_changed=False` y
`native_promotion_allowed=False` siempre. Misma óptica ideal condicionada
que la variante anterior: no solape físico ni precisión total nativa.

## Evidencia retenida

Seis tests y cinco contrastes de la variante (incluidos controles previos)
PASS, 1,7565 s, un hilo,
hijo<=60 s. La suite anterior y sus siete casos NO se relanzaron como hito;
se verifica su informe SHA y sus 14 pins antes y después, más tres pins
propios nuevos (17 total). Ledger absoluto, conteos, referencias, amplitudes,
gate y cota del campo complejo se comparan sin cambios.

| Escena | Cota anterior potencia Dx | Cota relativa potencia Dx | Diferencia CPU observada |
|---|---:|---:|---:|
| Dos fuentes coherentes, longitudes iguales | 0,3286288 | 0 | 0 |
| Segunda fuente desplazada -0,03125 BU | 0,3299379 | 0,00125847 | 0,000535253 |
| Fuentes desplazadas, grupos independientes | 0,1649690 | 0 | 0 |
| Referencia Dx +0,03125 BU | 0,0828118 | 0 | 0 |
| Lambda exacta 0,125 | 0 | 0 | 0 |

Para las primeras cuatro escenas lambda=1,00416693877201e-12, que da
errores complejos importantes. Tanto candidato anterior como nuevo
RECHAZAN esas cuatro y aceptan SOLO el control de lambda exacta: no se
convirtió un fallo de campo en PASS aprovechando la fase común. La
mejora es una cota de potencia menos conservadora, NO velocidad medida,
aproximación por fotogramas ni un resultado GPU.

El contraste numérico se hace con ideal_fields CPU sobre ambas lambdas,
árboles derivados por separado y slack diagnóstico float64/libm 1e-13
explícito, no añadido al gate racional. Intervalos no puntuales no se
reemplazan por una fase común exacta: se conserva su desviación del ancla.
No se afirma cobertura general de todas las geometrías admitidas.

Informe:
`D:/PROJECTS/.cognition/neuro3d/exp005_relative_power_budget_20260930_1556.json`
SHA `da7aa2188c9b22f077c2d1750c93204ab7201b699c5c8d3f3db1bb28adc37b00`.
1556 es etiqueta de archivo, NO hora del experimento.

## Coordinación

CPU propia, sin escritores peer/GPU/Blender/RT ni cambios de bounds/conf1.
GPU externa ocupada; RAM libre 1,248 GiB a 15:55; ticket 006 sigue vivo.
Claude: en la revisión CPU WAVELENGTH-FIELD-001 YA solicitada, contrasta
la factorización por puerto/grupo, especialmente fuentes con longitudes
distintas. No abre otro barrido o encargo paralelo, ni bloquea tu 006.
Conservar márgenes/cola y entregar artefactos de 006 cuando cierre seguro.
