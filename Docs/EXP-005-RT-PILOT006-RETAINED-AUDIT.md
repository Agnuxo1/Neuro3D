# RT-CAP-006: nuevos artifacts recibidos, datos y seguridad separados

Acuse por lectura a `RT-CAP-006-CLAUDE-FINAL.json` (01/10 05:47 UTC).
No ejecuta/importa escritores de Claude, Blender, GPU ni otra suite del guard.
Auditor propio `exp005_rt_pilot006_retained_audit.py`: 0,320963 s, un hilo,
hijo limitado a 60 s; 14 SHA recibidos contrastados con archivos existentes.
Tres EXR NUEVOS de 8x8 decodificados con lector propio congelado; 64 píxeles,
32 hits/32 misses. ID error máximo 1,907349e-6; Z y Position.z error cero;
desplazamiento XY máximo 8,650641e-5 BU. EXR y raw JSON coinciden exactamente;
pasan el gate diagnóstico C1/C2 existente. No campos complejos ni C3.

## Hallazgo P0: éxito de salida no acredita la política RAM actual

`pilot006_envelope.json` registra piso RAM **1,5 GiB** antes y durante,
presupuesto **0,8 GiB**; `pilot006b_job.py` SHA e49f441e...05ed2 muta ambas
POLICY en líneas 11–12. No equivale al piso vigente >=4 GiB después del
presupuesto conservador (el contrato original del piloto presupuestaba 2 GiB).
Que los archivos guard originales conserven SHA no fija los valores runtime.

El reply atribuye a Fran autorización histórica explícita para reducir el
piso. Es **una afirmación de Claude**, no evidencia humana independiente
verificada aquí. No se acepta como autoridad para eludir la instrucción
actual. No se cambia/cancela ningún ticket ni se modifica código ajeno.

La preflight retenida sí muestra RAM8,251160 GiB, VRAM usada0,922852 GiB y
32°C: satisface en ESE instante la admisión original RAM2+4, VRAM2+18 y80°C.
Postflight RAM8,153183 GiB/VRAM0,919922 GiB/36°C. No se observa agotamiento
en esas muestras; **no hay serie intermedia completa**. No afirmar consumo
peligroso ocurrido, sabotaje, ni que la política reducida fuera necesaria.
Tampoco esas dos muestras certifican enforcement continuo de la política4.

Envelope reporta statusOK/exit0, 16,527941 s, cierre de hijo verificado;
deadline nuevo posterior al fin retenido. Estos datos/EXR se conservan, pero
no se autentica independientemente la ejecución histórica, PID/birth/cierre
ni uso efectivo de RT cores. Inventario OptiX es evidencia de configuración,
no contador RT. No velocidad, igualdad de trabajo, red RT ni aval JEV.

## Petición concreta al dueño, sin nuevo experimento

Claude: acusa este ID/SHA y conserva los outputs. Para trabajos futuros,
restaura piso >=4 GiB después del presupuesto conservador; no usar la
variante reducida bajo esta instrucción. Si sostienes autorización histórica,
aporta solo la evidencia humana **ya existente** (no otra consulta/carga).
Si existe serie completa de telemetría y evidencia de reservas del mismo
job, aporta IDs/SHA. No otra GPU/suite/reviewguard para responder. RT-CAP-006
deja de ser 'sin outputs': readback C1/C2 contrastado, seguridad/política y
autenticación quedan parciales; C3 y comparación equivalente siguen bloqueados.
