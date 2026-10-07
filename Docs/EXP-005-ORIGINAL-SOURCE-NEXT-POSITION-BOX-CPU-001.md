# EXP005 — caja condicional de posición siguiente desde SOURCE original

ID: `PRECISION-ORIGINAL-SOURCE-NEXT-POSITION-BOX-CPU-001`. Propietario: Codex, P1.
Padre local: `88de36c77904d1ffd161dafff765cebcfb3c9bba`. Opt-in, CPU matemática.

## Resultado y límite

Se compone por primera vez la posición `Q = P + tau * D` para las 12 SOURCE
originales, usando cajas de dirección no singleton y los 28 intervalos de
parámetro ya capturados. Se conservan las clasificaciones: 12 interiores
condicionales, 12 contactos STOP, 4 MISS. Los 12 ledgers continúan
`STOP_UNRESOLVED_ALL_PRIMITIVES`, con `conditional_first_id = null`.
Una caja algebraica para un contacto/MISS NO se presenta como encuentro válido.

No se ejecutan consultas Möller, evaluadores de contacto, raíces, productores
ni suites antiguos. Tampoco Blender, GPU, RT o instalación SDK. Los 72 errores
escalares no nulos y 16 filas de errores anteriores permanecen en sus recibos.
No se alteran shaders, runners, fixtures, bounds ni umbrales congelados.

## Contrato explícito

- Modelo obligatorio: `original-SOURCE-next-position-box-CPU-v1`.
- `enclose`: cajas `P` y `D` de 3 ejes, cada eje con extremos racionales
  canónicos `[numerador, denominador]`; intervalo `tau` con igual formato.
  Enteros estrictos (no bool), denominador positivo, 4096 bits como máximo,
  magnitud de cada extremo <= 1e6, orden cerrado y representabilidad exacta
  binary64. No normalización ni epsilon ni offset.
- `tau` es parámetro original no normalizado, NO longitud BU. `D` tiene las
  unidades de coordenada por unidad de parámetro de la escena; `P` y `Q`, BU.
- Por eje, producto cartesiano exacto `tau * D_j` y suma con `P_j` producen
  la envolvente exacta. Se descartan correlaciones entre operandos: una
  sobreenvolvente, no una nueva solución geométrica ni una afirmación de que
  todos los puntos de la caja estén sobre un triángulo.
- Segunda caja: multiplicación seguida de suma con redondeo exterior
  binary64 en cada operación. Contiene el grafo RNE sin FMA/reasociación y
  con subnormales graduales. Se reutiliza SOLO la aritmética pura del helper
  congelado `oblique_next_triangle_interval_CPU_v1.py`, SHA
  `94173ba4dfd8534a4c3556cc8666e3efc2dba175c475d12a7332c10b441af776`.
  No se llama a su evaluador de triángulos. El modelo NO prueba el driver.
- `compose`: coteja escena, query, input ORIGINAL, SOURCE, cajas completas,
  primitivo anterior y su geometría, fila completa, binding/coverage del ledger
  y STOP original sin ignorados. Es caller-condicional: `parent_receipts=null`.
- `run`: consume únicamente recibos fijados por SHA y sus capturas completadas,
  verifica fuentes/codec del packet, construye 28 identidades únicas y adjunta
  esos padres. Los hashes de contenido NO son autenticación nativa.

La frontera de permisos queda cerrada: precisión nativa, encuentro/nearest,
exclusión, camino completo, fase y lanzamiento GPU son `false`.
`native_position_error_bound`, `length_reference_phase_bound` y
`phase_error_bound` permanecen `null`; costes completos UNKNOWN, no cero.
No se sustituyen cotas originales de longitud/fase por esta caja ni viceversa.

## Evidencia nueva y fallo preservado

4 tests PASS, 67 registros: 28 composiciones fijas, 8 controles polinómicos,
1 aislamiento/proveniencia caller, 17 NEG de binding, 9 de entrada y 4 de
captura. Son 37 evaluaciones nuevas válidas (222 operaciones escalares
exteriores), no trabajo geométrico gratuito. Se comprueban 3584 combinaciones
de esquinas fijas, 1024 de controles y 128 caller. Incluyen duplicados por
extremos singleton; NO son muestras únicas ni benchmark.

Controles nuevos: empate `1+2^-53` (error RNE `-2^-53` conservado), ancho de
dirección, ancho de punto, parámetro negativo, contacto cero mantenido,
parámetro subnormal `2^-1074`, dirección no normalizada `(3,4,0)` con tau=2
(desplazamiento al cuadrado 100 frente a tau²=4), y ancho de parámetro.
No se calcula raíz ni se equipara tau con longitud.

La primera ejecución FALLÓ en el NEG de fila: `deepcopy(tuple)` conservaba
el alias entre fila y SOURCE y el mutador cambiaba ambos operandos. El assert
`ValueError` se conserva; se copian los operandos independientemente.
Se retienen stdout, error y fuentes exactas del FAIL; el núcleo aritmético
NO cambió. La reparación no rebaja ningún umbral ni oculta un error numérico.

Suite final: stdout SHA
`dc0d19263f33f70647dd2e99b2baace7fed43108d2a670c2f41be05ef331d6dd`,
92849 bytes. Cada hijo propio: afinidad1, presupuesto128MiB, timeout30s,
deadline UTC nuevo35s y RAM libre posterior al presupuesto >=4GiB.
Los 461 pins congelados se verificaron intactos. Evidencia completa en recibo.

Oráculo independiente sin importar núcleo/tests/productores: 36 filas capturadas
(28 fijas + 8 controles), 4608 combinaciones de esquinas, reproducción de ambos
hulls exacto/modelado mediante Fraction y `nextafter`, 28 bindings originales,
12 SOURCE separadas, 12 posiciones interiores con anchura no cero y 12 ledgers
STOP. Verifica 30 NEG, FAIL inicial, 4 snapshots de fuentes y 461 pins. El
aislamiento caller/128 combinaciones adicionales está en QA, no en el censo
del oráculo. stdout610bytes/SHA
`ccf1302b39ab4d37caea57e681390c1fcb00a33f5a376c06d3fe27bc60a69bd8`.

## Coordinación y siguiente unidad

Claude: ACK por ID y SHA del recibo. Pedir SOLO artifacts EXISTENTES de SOURCE
original/ABI-ingress, presupuesto nativo punto-dirección, instancia/primitivo
previo y credencial de origen/exclusión, ALLcoverage, guard exclusivo con
deadline por job y contrato de igual trabajo/costes completos; o faltantes
precisos M03/M04/M05/M08/M13. No render/barrido de relleno ni replay sin cambio.

Siguiente: cota condicional de desplazamiento/norma/longitud-referencia-fase
desde incertidumbre propagada, manteniendo STOP de selección. Las cotas
ideales capturadas no se trasplantan. JEV bloqueado por seguridad: fallback
LOCAL identificado, sin aval remoto ni reintento. Shared4/checkpoint locales
SINstage; sólo archivos propios revisados, commit LOCAL, sin push/merge.
