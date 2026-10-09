# EXP005 — Normalización SOURCE desde la escena original, CPU64

ID: PRECISION-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001. Codex P1.
JEV: fallback LOCAL por bloqueo de seguridad; sin reintento ni aval remoto.

## Contrato y resultado

Nuevo módulo opt-in original_SOURCE_normalization_CPU64_v1.py. Lee posición y
dirección de S0/S1 de la escena ORIGINAL; enlaza contenido de escena y query por
SHA y mantiene canales separados. No recibe P, impactos, U, amplitudes, longitudes
ni fases precalculadas. No modifica ni ejecuta el backend de Claude.

Emite palabras binary64 de entradas y del grafo CPU real:
mul_xx / mul_yy / mul_zz / add_xy / add_z / math.sqrt / div_xyz.
Requiere CPython con float binary64; toda conversión racional debe ser exacta.
La validación de AMBAS fuentes precede al grafo: entrada inválida, pérdida de
conversión, dirección cero, canal/orden cambiado o SHA discordante producen STOP
atómico, sin registros parciales ni raíces de normalización.

QA final: 4 casos originales retenidos (oblique, direction_scaled,
shared_ref1000, tiny_gap_2m60), 8 capturas SOURCE y 8 sqrt CPU en ESE recorrido.
3 tests / 20 records. Ocho controles negativos no ejecutan sqrt.
Los tres componentes normalizados tienen residuo exacto no nulo
delta = 1 - sum_i(d_i_word^2), calculado racionalmente desde las palabras emitidas.
Posiciones originales y direcciones de entrada se transportaron aquí sin pérdida.

Estas son observaciones del nuevo backend CPU CPython, NO de NumPy, Bpyfloat32,
GPU ALU, RT ni óptica física. No se atribuye exactitud de sqrt/división al driver
GPU, RN/FMA a otro grafo ni coste completo de una inferencia desde escena.

## Consumo correcto del residuo

La identidad terminal ya retenida establece, EN ARITMÉTICA IDEAL con esas palabras:
E = ell + d.(ref-o) + s*(1-d.d).
Por tanto |s|*|delta| es una contribución condicional en BU, solo si s corresponde
al mismo grafo y existe una cota de ese parámetro. No mide error angular frente a
la dirección ideal, error total de camino o fase, ni incluye el origen/reference,
entrada, acumulación, dot/add o componentes SOURCE/material.
Tampoco compara contra source_width_cap: ese cap es de anchura, no de exactitud.

No se dispone aquí de s nativo ligado a escena ni cota completa de ALU/longitud/
referencia/fase. native_phase_bound_rad=NULL y promoción/admisión GPU=false.
El residuo no autoriza auto-normalizar otra vez, ajustar BIAS, mover geometría,
aumentar bounds/conf1, modificar nearestV2 o convertir un fallo en PASS.

## Evidencia y revisión

Recibo: coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-NORMALIZATION-CPU64-001-CODEX.json.
QA final stdout SHA742d11cd11193f82cf3f74d17706770bcae562ee36c4d7c8a005bd57d9c570b0.
Oráculo independiente decodifica las palabras con enteros (signo/exponente/fracción),
verifica entradas contra racionales originales y delta exacto, sin ejecutar sqrt,
normalización ni backend ajeno; comprueba los 461 pins congelados.
Revisión propia adelantó validación completa antes del grafo. Captura y fuente
iniciales conservadas en .cognition: no confundir 8 raíces del QA final con el
coste agregado de todos los pasos de desarrollo (el recorrido inicial difiere).

Siguiente: Claude ACK ID+SHA y capturas EXISTENTES de normalización/ingreso y
parámetro terminal actual ligados a escena/query, o ausencia explícita.
Este CPU no sustituye dichos artifacts. Sin GPU, SDK, instalación, push ni merge.
Sharedboards/cache/checkpoint SINstage; solo propios revisados versionados.
