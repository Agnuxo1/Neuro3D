# Componente geométrico GPU nativo: intersecciones, NO RT

Unidad propia de auditoría, no duplica OptiX/RT de Claude. Contrato local,
JEVbloqueado por seguridad/fallbacklocal. No sustituye el trazador completo.

GPU recibe TODOS los triángulos reales de escena reabierta y una batería de
rayos: fuentes + rayos intermedios retenidos del fixture escape0119. CPU solo
empaqueta vértices y consultas, no transmite intersecciones/objetivo/normal.
Kernel Moller-Trumbore exhaustivo devuelve primerimpacto,distancia,normal y
estado miss/hit/ambiguous. No BVH ni núcleosRT; no medir ventajas/capacidad.
Rayos intermedios son inputs de verificación previos CPU, NO propagación GPU.

Limitar256triángulos/256consultas, coordenadasabsolutas<=1e6BU, normales no
degeneradas, direccionesfinitas/nocero; launchbias1e-6BU,epsilonintersección1e-9,
barytol1e-10. Oráculo CPU de triángulos independiente para validar, no fallback.
Objeto exacto/distancia<=1e-5BU/normalabsdoterror<=1e-6. Misses explícitos.
Superficiesdistintas con distancias<=1e-9 producenambiguous; caller lo rechaza.

Solo abrirbase.blend0119, no guardar. Casos:base,shamcolor,shiftx+.03125de
a.r1/a.r2,removea.r1,overlapduplica a.r1. Consultasidénticas en todos; añadir
misses externos. Base/shamidénticos; shift/removed cambian>=1consulta; overlap
produce>=1ambiguous y rechazo. Comparar también conscene.ray_cast donde no
hay ambigüedad. Todo readbackGPU real; FP64cálculo yFP32salida.

CPU tests para ABI/bounds/rechazo y pipeline sin dispatch alimportar. Contrato
congelado antesGPU, artefactos nuevos/snapshots/resultados/hashinputs/código.
gpuq/guard120s/host1,5device1/pisoRAM4/VRAM18/temp80/corte06UTC. No tocar
capacityClaude/conf1/v0/v4/0119. Próximo: revisión independiente y contrato de
frontier completo oadaptadorRT trascoordinar conClaude; no llamarlo redfullGPU.
