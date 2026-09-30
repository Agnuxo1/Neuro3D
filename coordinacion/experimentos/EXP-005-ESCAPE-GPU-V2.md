# Escape v2 · controles compatibles con referencia en superficie

2026-09-30 01:18 UTC, anterior a Blender/GPU. Diseño v1 rechazado en CPU,
conservado en commitddf6c2b.
No se modifica oráculo ni requisito de planitud/referencia ni tolerancias.

Corrección del control boundary_shift: desplazar aperture en y+.03125BU (tangente
al plano x=6), referencia fija y rayos siguen cubiertos. Campo invariante.
reference_shift: desplazar superficie Y referencia en x+.03125BU, fase i en
escape porque λ0,125BU; los otros puertos no cambian. Referencia longitudinal
despegada de superficie es ahora control negativo de rechazo, no valor esperado.

Resto de v1 intacto:54probes,campos<=1e-4,potencia/balance<=2e-4,
historia/multiplicidad/segmentos<=1e-5,invariancia/refase<=2e-5,sham1e-12,
efectosfase/lambda>1e-3 y diferencia frente a intensidadpathwise>0,1.
Mismo shader nativo, nuevos archivos/guard/safetycaps/exclusividad y no RT.
