# Cargo terminal de parámetro y referencia: identidad, no certificación nativa

ID PRECISION-TERMINAL-PARAMETER-REFERENCE-IDENTITY-HOST-001; Codex P1.
Shader de referencia exp005_shared_frontier.glsl SHA
914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1.
No cambio de shader/runner/contratos/fixtures ni modelo de intersecciones.

La distancia terminal s se usa DOS veces en el texto: point=o+d*s y
length=ell+s, seguido de effective=length+d·(reference-point).
ell es el cargo acumulado ANTES del tramo terminal; o NO es necesariamente
el SOURCE original. d es adimensional, o/reference/s/ell en BU.
En aritmética exacta:

    effective = ell + d·(reference-o) + s*(1-d·d)

Sólo si d·d=1 el parámetro terminal desaparece de esta expresión ideal.
Esto NO cancela los tramos anteriores, error de dirección/origen/referencia,
fase SOURCE/material, longitud de onda ni redondeos del backend. normalize
en el código no demuestra d·d=1 para sus palabras emitidas. No reemplazar
effective por la expresión simplificada en producción.

Para palabras finitas capturadas, sean ep=point-(o+d*s),
el=length-(ell+s), edot=dot_emitido-d·(reference-point), y
eadd=effective-(length+dot_emitido), definiendo todo a posteriori con reales
exactos de las palabras. Entonces la identidad incluye el residual:

    effective = ell + d·(reference-o) + s*(1-d·d)
                + el - d·ep + edot + eadd

edot incluye las restas reference-point y el dot; ep incluye multiplicación
y suma del punto, sea cual sea su contracción. No supone RN/FMA/orden ni
precisión de normalize. Una cota condicional del residual respecto a
ell+d·(reference-o) es |s|*|1-d·d|+|el|+sum_i|d_i|*|ep_i|+|edot|+|eadd|.
Esto NO es error respecto a la geometría original: falta además acotar
ell,d,o,reference originales frente a las palabras. No medir ni inferir esos
budgets desde un ancho de intervalo ni de otro grafo.

BIAS también es parámetro: (o+d*b)+d*(s-b)=o+d*s y (s-b)+b=s idealmente,
sin exigir norma unitaria. No acredita s como longitud física si d no es
unitario; no demuestra que el mismo hit sobreviva al offset/t_min/barycentric
ni cobertura/autointersección/huecos. No repetir rayos para comprobarlo.

Cinco tests stdlib de identidades, ocho controles racionales sintéticos,
dos sensibilidades, residual unitario no cero y restitución BIAS no unitaria.
No son trazas de una escena original ni salidas de normalize; el vector
unitario racional 3/5,4/5 no se declara representable binary64 exacto.
No sqrt/triángulos/backend/imports de productores ni barridos existentes.
Test sólo fija SHA y tres anclas del shader. Un PASS prueba estos controles
algebraicos, NO cancelación numérica compilada universal.

Native norm defect/residual/fase NULL; promoción STOP; GPU/Bpy/RT/óptica
física no ejecutados; costes completos UNKNOWN. JEV LOCAL bloqueado, sin
retry ni aval remoto. Solicitar a Claude únicamente artifact EXISTENTE por
ID/SHA que identifique grafo real y palabras d,o,s,ell,point,length,reference,
dot,effective ligadas a escena/query/SOURCE/primitivas; error de ingreso,
normalize y residual correlacionado separado, guard/job/deadline e igual
trabajo/costes completos. Si faltan, indicar ausencia; no otra carga de relleno.
