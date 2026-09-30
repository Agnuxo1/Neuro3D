# Escape coherente y plano de referencia · preinscripción v1

2026-09-30 01:15 UTC. Codex, desarrollo directo; JEV bloqueado, fallback local.

Fixture NUEVO: dos MZI/quads binarios, λ0,125BU, puerto b.X convertido en frontera
explícita b.escape (no absorción ni rayos perdidos). Dos detectores y un escape,
tres entradas. No modificar conf1/v0 ni cascada v4 ni los ensayos anteriores.

Seis tratamientos×9entradas: base, faseb.r1+.4,shamcolor,surfaceescape+.03125BU
con referencia fija, surface+referencia+.03125BU,lambda0,126. Shader nativo ya
validado, sin modificación: recibe raycastsCPU NUEVOS/propiedades de escena.

Predicciones previas: escape se suma como CAMPO antes de abs²; suma |camino|² es
control negativo, difiere>0,1 en basis0. Detectores+escape conservan entrada.
Mover solo superficie con referencia fija no cambia campo; mover también el
plano de referencia da i·campo en escape (λ/4), demás puertos iguales. Sham0.
Fase/lambda cambian potenciaescape>1e-3; eliminar frontera debe rechazar rayo perdido
en Blender, no inventar potencia de escape ni renormalizar.

Gates anteriores a medir:54probes, completo complejo<=1e-4, potencia/balance<=2e-4,
historiales/multiplicidad iguales y segmentos<=1e-5BU frente a oráculo triangular.
Invariancia/referencia<=2e-5,sham<=1e-12; readback exacto tras guardar/reabrir;
propiedad kind=escape explícita. Artefactos nuevos porprobe, hashes y fallos retenidos.

Blender gráfico OCULTO,1hilo,guard120s/pisoRAM4/capVRAM18/temp80/cierre06UTC,
reserva1,5GiBhost/1GiBdevice,exclusividadgpuq. Sin RT ni óptica física ni claims de
velocidad/capacidad. Es gate ideal escalar, NO prueba completa de ortogonalidad.

## Preflight CPU 01:16 UTC · diseño v1 rechazado antes de GPU

Dos errores de prueba: inicial_field del test era lista y no complejo (adaptación
del test a consumidor); más importante, mover escape en x con referencia fija
viola el contrato del oráculo: referencia DEBE estar en la superficie de lectura.
No se ejecutó Blender/GPU ni se relaja ese gate. Fixture/control corregidos como
v2 separada: desplazamiento tangencial y referencia longitudinal válidos; referencia
fuera del plano pasa a control inválido que debe rechazarse. Fuentes v1 recuperables.
