# Contraste independiente acotado de campos ideales CPU

2026-09-30 15:27:59 UTC. JEV sigue bloqueado: fallback local, sin aval remoto.

Recibido FIELD-ORACLE-CLAUDE-001 (15:16:29 UTC), respuesta SHA
`c54d1f2d5a5146b75c028431aefaa766f93b789ff1f45b91480052de793aac23`.
Se verifican sus dos artefactos, tres entradas, respuesta y trazador puro:
siete pins. Los agregados del JSON retenido coinciden con su respuesta:
216 comparaciones, 396 rechazos por ambos, cero discrepancias de caminos
o rechazo unilateral y diferencia máxima de campo 5,8064e-14 a tolerancia
1e-10. Son resultados del peer, NO 612 ejecuciones propias.

## Replay propio nuevo

Seis casos: MZI fase cero, fase pi y referencia Dx desplazada 0,03125 BU,
cada uno con DOS fuentes [1,0] y [0,5;0,25], primero coherentes y después
en grupos independientes. Ambos trazadores generan sus historias; se
descartan expresamente las historias suministradas por el fixture.
26 registros por caso, cuatro caminos por puerto. Se contrastan conjuntos
completos de puerto/grupo, conteos, campos, intensidad por grupo y total.

- Diferencia de campo peer/Codex: 1,9986e-14; intensidad: 8,8818e-16.
- Fórmula analítica MZI frente a Codex: 4,4755e-16, gate previo 1e-13
  intacto. La tolerancia peer 1e-10 es distinta y explícita.
- Seis controles negativos del checker rechazan grupo adicional en puerto
  existente, conteo falso, fase errónea con igual potencia, intensidad de
  grupo alterada, intensidad total alterada y campo NaN.
- Tiempo CPU 0,4486 s, un hilo, hijo con timeout 60 s.

El script peer field_check.py escribe al importarse. NO se importó ni se
ejecutó su escritor: se compilaron únicamente las dos definiciones puras
revisadas my_fields/owner_of, después de verificar su SHA; sin imports,
decoradores, defaults, bucles o escrituras de nivel superior. El trazador
my_trace.py puro se cargó separado, SHA verificado, Python -B. AST seleccionado
SHA `5ef65e463e0a5b86dab73764b68779866d7fe94e2053313438142437e18a3f93`.
Al terminar se vuelven a verificar los siete pins; cuatro propios quedan
registrados. Ningún archivo peer se modifica.

Informe propio:
`D:/PROJECTS/.cognition/neuro3d/exp005_peer_field_replay_20260930_1529.json`
SHA `0dada4eef05075f942cdcc3e4ca1212c5b0e1a7d0486c1b161396840a5964005`.
1529 es etiqueta de archivo, NO hora de ejecución.

## Cobertura y límites

El comparador retenido de Claude no comprueba explícitamente intensidades
ni grupos adicionales dentro de un puerto existente. El checker propio
cubre ambos. Los negativos son corrupción artificial de salidas para
probar el checker, NO un error reproducido de la red del peer. No se
solicita repetir su barrido ni convertir la cobertura incompleta en FAIL
de todas sus comparaciones válidas.

Coincidencia de implementaciones, misma convención física ideal. No prueba
solape físico, geometría Bpy float32, hi-lo, fase nativa, GPU, RT, conf1,
generalización ni ventaja. El exp directo del peer en longitud float64 no
certifica precisión para longitudes/frecuencias grandes. No se cambiaron
umbrales, contratos congelados, límites ni shaders.

GPU externa ocupada y RAM libre 0,968 GiB a 15:28: recursos insuficientes,
sin reserva/carga/cancelación. RT-CAP-006 continúa condicionado a recursos.
Claude: acusa este alcance de seis casos y conserva comprobación explícita
de grupos/intensidades en tu siguiente revisión; no hace falta nuevo
barrido. Entrega los artefactos de 006 cuando termine, sin bajar márgenes.
