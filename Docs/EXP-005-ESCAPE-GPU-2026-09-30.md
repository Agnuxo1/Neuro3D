# Escape coherente en GPU nativa Blender · PASS local acotado

2026-09-30 01:21 UTC. Contrato corregido/congelado en a0ea442 antes de Blender/GPU.
Shader nativo de etapa anterior sin cambios; fixture NUEVO de dos MZI/tres entradas,
dos detectores y una frontera b.escape, λ0,125BU. NO absorción ni óptica física.

54probes: seis escenas nuevas guardadas/reabiertas con readback evaluado exacto,
raycastCPU nuevo e impactos crudos al shader nativo. Todas las bases y pares1/i,
campos completos/historias/multiplicidad/longitudes frente al oráculo triangular.

| Gate previo | Medido |
|---|---:|
| Campo complejo <=1e-4 | 3,14016e-6 |
| Potencia <=2e-4 | 3,08304e-6 |
| Balance detectores+escape <=2e-4 | 5,29178e-6 |
| Segmentos <=1e-5BU | 5,96047e-8BU |
| Movimiento tangencial/invariancia <=2e-5 | 0 |
| Referencia y superficie movidas λ/4 → i·campo <=2e-5 | 0 |
| Sham <=1e-12 | 0 |

Fase de b.r1 altera potencia de escape0,106140; λ0,125→0,126 la altera0,084429,
ambas>1e-3. Intensidad sumada camino a camino es control incorrecto: gap0,706534
vs escape coherente GPU en basis0. La frontera explícita recibe amplitudes que
interfieren; no se inventa fuga ni se renormaliza para cerrar balance.

## Rechazos y diseño inicial preservado

- Retirar frontera b.escape en Blender provoca `lost Blender ray`: fallo cerrado.
- Referencia longitudinal fuera de superficie provoca rechazo del oráculo de
  escena completa ANTES de sumar campo; no se aceptó como salida.
- Diseño v1CPU ddf6c2b inicialmente esperaba invariancia de ese caso inválido.
  V2 cambió el control a desplazamiento TANGENCIAL de aperture y mantuvo el gate
  de referencia en plano. Sin modificación del oráculo ni relajación numérica.

Seis hashes .blend verificados contra bytes actuales;54readbacks únicos y sus
gates recalculados en revisión CPU posterior (sin segundo despacho).86testsCPU.
Fuente/contratos propios versionados, archivos Claude/conf1/v0/v4 preservados.

## Recursos y alcance

gpuq adquirido01:19:37/liberado01:19:46UTC,rc0/guard completed,8,646s.
RAMlibre mínima muestreada7,100GiB,VRAMtotalmáx0,632GiB,GPU33°C;PID23004terminado,
sin procesos Blender residuales. Guard120s/pisoRAM4/capVRAM18/temp80/cierre06UTC,
ventanaoculta1hilo,host1,5GiB/device1GiB. Muestreo no certifica todos los picos.

Artefactos en `D:/PROJECTS/.cognition/neuro3d/`:
`exp005_escape_native_20260930_0119.json`, folder homónimo con6blends/54paths/
snapshots, `exp005_escape_guard_20260930_0119.json` y tempD propio.
SHAresultado `5015d6d1cd2a58addb79a187f37cda1744ad9b48f29ab470d95e253c4208780d`.

Intersecciones siguen en CPU, campos/intensidades en GPU dentro de Blender.
Esto prueba un escape escalar coherente en este fixture, NO ortogonalidad física
completa ni redRT ni ventaja de capacidad/energía/velocidad. Sigue pendiente
revisión/refutación Claude y propiedades ópticas no ideales/múltiples modos.
JEV bloqueado por seguridad: fallback local, sin aval remoto. Desarrollo con
contrato pre-run y checkpoint; el diseño inválido se conserva como evidencia.
