# EXP-005 · consumidor de campos GPU separado (preinscripción v1)

2026-09-30 · unidad Codex; decisión local, JEV bloqueado por seguridad.

Hipótesis: un shader OpenGL suma campos complejos e intensidades desde los
impactos reales retenidos de la cascada v4, sin matriz entrenada ni campos
precomputados durante la inferencia. NO acelera ni sustituye las intersecciones:
esas siguen siendo los raycasts CPU de Blender ya comprobados. No es RT ni
óptica física; el contexto externo ModernGL tampoco es ejecución dentro de bpy.

ABI: longitudes BU y fases de espejo de readback, por impacto; fuente compleja
explícita, puerto y plano de referencia por camino. CPU solo valida y empaqueta.
GPU calcula cada propagación, coeficiente t/r/espejo, suma compleja y abs², y
devuelve Re/Im/intensidad de TODOS los puertos (también oscuros). FP64 en
aritmética/reducción de fase, sin/cos FP32 declarado; sin renormalización.

Antes de medir: seis tratamientos × nueve probes del v4 congelado (54), mismas
entradas. Contraste con oráculo triangular independiente desde snapshot completo
y con campos CPU retenidos, por puerto; abs complejo <=1e-4, potencia <=2e-4,
balance <=2e-4; sham <=1e-12; efectos faseA/B/roof/lambda >1e-3 en basis0.
Hashes de snapshots/.blend y paths de entrada, shader, packer y runner retenidos.
No se acepta solo potencia ni equivalencia de IDs como ortogonalidad física.

Máximo512caminos/caso y64impactos/camino; un trabajo por puerto, suma
determinista sin atómicos. No prueba de capacidad, energía ni velocidad relativa.
Tiempo de despacho+sync+readback separado de validación/carga y contexto; no
usar esta cifra como inferencia completa. Mantener también errores/fallos.

Reserva gpuq, exclusividad con Claude; guard120s, estimaciones conservadoras
host1GiB/device0,5GiB, RAMlibre>=4GiB, VRAMtotal<=18GiB,temp<=80°C y corte06UTC.
No instalar paquetes si faltan ni invadir turno ajeno. Primero pruebas CPU del
ABI, luego runner congelado; si no hay turno libre queda preparado, no PASS GPU.
