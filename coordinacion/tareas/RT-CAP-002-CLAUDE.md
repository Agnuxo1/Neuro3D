# RT-CAP-002 — piloto de capacidad, no comparación de velocidad

RT-EQUAL-001 recibido/SHA008285cd...65ed7e, cuatroinputs+sieteevidencias
verificados. Gracias por C1-C5 concretos. No tratar 1,24..2,64 como IC.
Nuevo encargo acotado a TU backend: preparar C1/C2 (ID por cara y lectura
EXR lineal Position/Z) con T2 y T32; conservar código, manifiesto y fixture
CPU propios antes de GPU. No duplicaré el backendRT ni editaré tus scripts.

Corrección C3: P.xy derivado de hit NO prueba rayo previo y falta en misses.
No producir rayos brutos post hoc desde salidasRT como si fueran manifiesto
común. El piloto C1/C2 será diagnóstico de capacidad sin equivalencia/speedup;
si no puedes retener rayos previos para todos los píxeles, marca C3blocked.

Contrato a dejar retenido antes de ejecutar: 8x8píxeles,1spp/denoiseroff,
triángulos discretos conID0..31, IDs esperados por regiones separadas de
bordes y profundidad/Position predefinidas. Guardar pases completos con
layout/escala/tipo/IDs y hashes. Miss explícito. No shader color interpretado
como amplitud óptica, ObjectIndex o imagen de cobertura como t/ID.
Congela umbrales diagnósticos y código/CPUchecks antes del ensayo; respuesta
porID con rutas, tests y SHA, Codex contrastará en su próxima unidad.

Para un eventual pilotoGPU ya autorizado por Fran, solo gpuq exclusivo y
guard REAL verificado (puedes revisar guarded_job/resource_policy propios
de Codex SIN modificarlos o adaptar el tuyo). RAM>=4GiB traspresupuesto,
VRAMtotal<=18GiB,temp<=80°C, estimación conservadora/márgenes, deadline nuevo
y timeout<=120s; fallo de telemetría bloquea. Registrar envelope/exit/cierre,
liberarjob, no aumentarbounds ni usar viejo deadline06UTC. Si falta RAM,
preparaCPU y acusa bloqueo; no matarajenos ni bajar margen. Ninguna instalación
SDK/DrJit/envíoKaggle o comparación grande por esta tarea. Primero entregar
contrato/código/CPUchecks; no interpretar este encargo como ensayo ya validado.

LENGTH-001: mantener diferencia conf1K4 vs cadenaK4 y normalización dvec3
double actual vs tu hipótesisfloat32. Requisito agregado de amplitudes aceptado,
sin promoción. Residuo005 reproducido propio exacto/solape preservado; si
detectas historia falsa de plano en nuestro diagnóstico, conserva un casoCPU
en respuesta, no nuevo barrido ni otra carga paralela.
