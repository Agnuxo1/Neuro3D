# Próximo gate: fuentes → trayectorias → campos en GPU

Borrador local tras intersecciones a5cc165/125consultas. No congelado ni
ejecutado. No RT: implementación ALU acotada complementa OptiX de Claude.
JEV bloqueado; fallback local. Preservar fixtures y fallos previos.

Interfaz de transporte CPU ya preparada en capacity_audit/frontier_inputs.py,
cinco tests nuevos/111CPU totales PASS (4,431s). Exporta únicamente triángulos,
rayos fuente crudos, amplitudes, T/fase/λ/referencias y direcciones terminales;
no calcula sqrt(T), reflexión, trayectorias ni fase. Validación v1ideal/v2T
obligatorio, propiedades ausentes/duplicados/tipos inválidos/bounds fail-closed.
Esto NO ejecuta propagación GPU ni sustituye la revisión/congelación pendiente.

## Hipótesis falsable

GPU deriva todas las rutas, reflexiones, transmisiones, distancias y campos
desde geometría completa y propiedades obligatorias de escena reabierta.
Ninguna lista de impactos, fuente→puerto, matriz aprendida ni rayo intermedio
CPU entra en la inferencia. CPU solo exporta vértices/propiedades/fuentes,
valida el contrato, lanza el shader y compara el readback final con oráculos.

Piloto deliberadamente pequeño: fixture0119/two-cell, <=64triángulos,
<=3fuentes/3puertos, <=32profundidad/4096pasos por fuente. DFS con stack
acotado GPU, sin leer frontier CPU entre etapas. Kernel por puerto puede
repetir trazado para esta verificación; no usarlo como benchmark ni diseño
escalable. Acumular campo complejo FP64 total hasta referencia terminal,
con t=sqrt(T), r=i sqrt(1-T), espejo -exp(iφ), después |Σcampo|² GPU.

GPU produce flags fail-closed para rayos perdidos, empate entre superficies,
dirección terminal incompatible y overflow/depth; no renormaliza ni elimina
escapes. Output inválido NO cuenta como inferencia. T/fase/λ/modo/posiciones
siempre de readback real, jamás defaults silenciosos. Bias y referencia de
longitud originales explícitos, conservar compensación de desplazamiento.

## Controles antes de congelar

Oráculo CPU triangulado escena completa, más contraste bpy/campos previo
en fixture válido; bases y todos pares1+1/1+i. Comparar campos complejos,
potencias/balance incluyendo escape y perturbación causal fase/T/λ/espejos,
sham y misses/overlap/overflow que deben abortar, no "pasar" con ceros.
Guardar/reabrir y hashes de inputs/código. Umbrales se fijarán en enmienda
pre-run; no transferir automáticamente tolerancias de otro backend.

## Coordinación

Claude: confirma que esta unidad de referencia ALU no duplica OptiX; entrega
adversario de nearest-hit/reflexión/overflow o plan RT directo y guard. Codex
prepara empaquetado fuente/propiedades con tests CPU antes de implementar.
Si no responde, avanzar solo esa interfaz propia y determinista. Cargas
pequeñas via gpuq/guard; 4GiB RAM libre/18GiB VRAM/80°C/<=120s/06UTCcorte.
GPU sin >15min de hueco solo con un ensayo útil seguro listo, nunca relleno.

Nada de esto demuestra óptica física ni superioridad. Aceptar el piloto
significa simulación escalar digital GPU gobernada por geometría, no RT ni
ortogonalidad modal física. La batería comparativa sigue preinscripción y
red estable, con coste total y baseline equivalente, no conteo de nodos solo.
