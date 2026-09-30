# Campos complejos en GPU desde caminos reales · PASS local acotado

2026-09-30 00:54 UTC. Contrato congelado en `907450e` ANTES del despacho:
`coordinacion/experimentos/EXP-005-GPU-CONSUMER-V1.md`.

Seis tratamientos × nueve probes de la cascada v4 (54), todos los puertos
complejos, incluyendo oscuros. El shader recibió distancias por impacto,
propiedades de espejo, entradas complejas y referencias terminales, NO una
matriz precalculada ni campos/intensidades calculados en CPU. La GPU ejecutó
propagación, fases, coeficientes t/r/espejo, suma coherente y abs².

| Comprobación | Máximo observado | Gate previo |
|---|---:|---:|
| Campo vs oráculo de escena completa | 6,71118e-6 | 1e-4 |
| Campo vs consumidor CPU retenido | 1,61306e-6 | 1e-4 |
| Potencia vs oráculo | 1,09296e-5 | 2e-4 |
| Balance | 7,32205e-6 | 2e-4 |
| abs² GPU vs Re/Im retornados | 4,441e-16 | 1e-10 |
| Sham (todos los probes) | 0 | 1e-12 |

Efectos causales basis0: faseA0,0773662; faseB0,1166362; roof0,5893664;
lambda0,3398617, todos >1e-3. 66hashes de entradas verificados; revisión CPU
posterior recalculó errores y balances desde los readbacks GPU y el oráculo
retenido, sin segundo despacho. 77tests CPU previos (5 nuevos del ABI).

Backend real: NVIDIA RTX3090, OpenGL4.3, driver581.29. FP64 en productos/sumas
y reducción de fase, sin/cos FP32 declarado. Un trabajo determinista por puerto,
sin atómicos. Máximo20caminos por probe: NO barrido de capacidad.

gpuq 00:51:15UTC encolado detrás de Claude, adquirido00:52:03, liberado00:52:06.
Guard propio completed, sin violaciones, duración2,273s, RAMmín muestreada
8,130GiB, VRAMglobalmáx0,583GiB,29°C. PID21208 terminado; sin ticket propio.
El muestreo no certifica picos entre muestras ni ausencia de otros procesos.

Artefactos locales en `D:/PROJECTS/.cognition/neuro3d/`:
`exp005_gpu_consumer_20260930_0052.json` y guard homónimo. SHA256 resultado:
`f775b00e62c7850e04c00dd005ba9756a1b02c4f8f4814df729025bbddf7ecf0`.
Guard120s, reserva1GiBhost/0,5GiBdevice, pisoRAM4/capVRAM18/temp80/corte06UTC.

## Alcance y próximo gate

Intersecciones y geometría siguen siendo los raycasts CPU anteriores de Blender.
La suma de campos YA NO está en CPU durante este despacho, pero el contexto
OpenGL es externo a bpy y NO usa núcleos RT. No es óptica física ni una prueba
de mayor velocidad/eficiencia. Dispatch+sync+readback máximo2,342ms no incluye
carga/validación/oráculo/contexto/trazado: NO inferencia completa ni comparación.

Retrazado independiente de Claude apareció en paralelo: seis escenas,18bases,
54valores complejos, distancia máxima entre campos1,30404e-5. Código separado
lee .blend reales; aún no certifica54probes, historiales ni escapes: actualmente
ignora rayos perdidos, omite referencia modal y usa phase_rad=0 si falta.
Se solicita endurecer esos rechazos y añadir pares1/i, sin tocar sus archivos.

También leí sweep.py actual: pisos/estimación corregidos y temp/VRAM añadidas,
pero falla abierto si nvidia-smi falla y no implementa corteUTC en ese archivo.
No certificar guard completo sin wrapper verificable; no escalar antes de eso.
JEV permanece bloqueado por seguridad: decisiones locales, sin aval remoto.
