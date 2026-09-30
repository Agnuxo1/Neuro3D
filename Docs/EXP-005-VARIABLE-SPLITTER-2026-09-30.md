# Transmisión configurable desde la escena y actualización en vivo

Resultado local,30/09/2026 02:05UTC: **63 casos de escenas nuevas y27 de edición
en vivo pasan**. Además de la fase, el objeto divisor controla la amplitud de
cada rama mediante `power_transmittance`. La GPU calcula los coeficientes
t=sqrt(T), r=i sqrt(1-T), propagación, suma compleja e intensidad.
CPU lee propiedades y traza geometría; no envía coeficientes/campos precalculados.

El esquema `exp005-readback-v2` exige T finito en[0,1] para todos los divisores.
Shader nuevo `Blender/shaders/exp005_variable_splitter.glsl`; ABI códigos4/5,
cuarto escalar por impacto=T crudo. El shader50/50 original y fixtures v1 no
cambian. Consumidores v1 rechazan esos códigos en vez de tratarlos como identidad.
Una propiedad T inyectada en v1 se rechaza, no se ignora.

## Pruebas y límites medidos

Siete escenas nuevas guardadas/reabiertas: T de b.bs2=0/.2/.5/.8/1, sham y fase
conT=.2. RestoT=.5. Cada una recibe tres bases y todos los pares1/i (63probes).
Sobre T05.blend reabierto sololectura se edita T=.2/.8/.5 en vivo (27probes).

| Medida,90probes | Error máximo | Umbral previo |
|---|---:|---:|
| Campos completos vs oráculo triangular | 2,797025e-6 | 1e-4 |
| Intensidades vs oráculo | 3,083031e-6 | 2e-4 |
| Balance detectores+escape | 5,291775e-6 | 2e-4 |
| Distancia por impacto,63probes | 5,960465e-8BU | 1e-5BU |

Efecto de potencia T=.2/.5 en basis0=0,0923035; fase=0,0849119; sham0.
T=.2/.8 da potenciaigual (5,96e-8) pero campo distinto (0,618558): ejemplo real
de por qué las intensidades no bastan para validar fase/amplitud de la red.
ExtremosT0/1 preservan la geometría/historias completas incluso para ramas oscuras.

101tests CPU pasan, incluyendo63controles sintéticos, paridadT=.5 con v1,
props ausentes/invalidas, readbackevaluado y rechazo de ABI no soportada.
Reauditoría sinGPU:90campos recalculados con el oráculo completo desde snapshots,
siete hashes.blend intactos, hash del inputlive intacto, ambos hijos terminados.

## Hallazgos preservados, sin relajar criterios

1. Contrato inicial6626178 falló en CPU: exigir potencia distinta paraT=.2/.8
   en basis0 era incompatible con la simetría del fixture. SinGPU en ese diseño.
   Enmiendaeb07c4b congelada antes deGPU: potenciaT=.2/.5 y control complementario
   en campo, mismos umbrales y mismos siete tratamientos.
2. Corrida63probes numéricaPASS: los cinco negativos de propiedad bpy dieron
   `evaluated splitter transmittance mismatch` por una copia del depsgraph stale.
   Es fail-closed, pero NO demuestra que cada validador de tipo/rango se ejecutara.
3. Seguimiento live fcb4068 congelado antes deGPU. Después de editar objeto:
   `obj.update_tag()` y `view_layer.update()` antes de exportar. Cambios positivos
   se leen correctamente. Missing→KeyError; bool→numericvalue; negativo→invalid
   finitevalue; >1→transmittance<=1. NaN sigue rechazado por mismatch (NaN!=NaN):
   ese mensaje no certifica por separado el decoder runtime de NaN; CPU sí lo valida.

El exportador conserva el rechazo ante un depsgraph desactualizado: no lo oculta
ni fuerza automáticamente la reevaluación de datos ajenos. El caller que cambia
una propiedad debe marcar el objeto y actualizar antes de exigir readback conforme.
No se guardó el inputlive. `quit.blend` solo es recuperación temporal del hijo.

## Artefactos y seguridad

En `D:/PROJECTS/.cognition/neuro3d/`:

- `exp005_splitter_native_20260930_0151/`:7blends,7snapshots,63registros de paths.
  ResultadoJSON mismo nombre +.json; guard `exp005_splitter_guard_20260930_0151.json`.
  SHAresultado `e14ef5de2bafb82c1d927dad2010cb8cd0a1d009e079dd2669900a4a0bcfdfc5`.
  Job01:53:29–38UTC,rc0/8,5704s,RAMmín9,6449GiB/VRAMtotalmáx0,6143GiB/33°C,
  PID30156terminado.
- `exp005_splitter_live_20260930_0203.json` + `exp005_splitter_live_guard_20260930_0203.json`.
  SHAresultado `ee17fc2fe590e8914437febbc1c5ec8a0d09f8242cd4179657a1cf0e1cf6a4fe`.
  Job02:03:37–43UTC,rc0/6,4747s,RAMmín7,5969GiB/VRAMtotalmáx0,6143GiB/33°C,
  PID4896terminado. Ningún Blender residual al comprobar. Recursos son muestras,
  no garantía de picos entre lecturas; proceso ajeno de2,1GB no se tocó.

Blender4.5.14LTS/OPENGL/RTX3090. gpuq y guard propios respetaron pisoRAM4,
capVRAM18/temp80/corte06UTC. No push, merge, ni cambios en archivosClaude.
Método: feature-development/continuidad fijaron contratos, conservaron fallos
y separaron evidencia numérica de validación operativa; sin delegación nueva.
JEV sigue bloqueado por revisión de seguridad: fallback local, sin aval remoto.

## Revisión Claude y próximos pasos

Contraste de escape anterior0119 con su `escape_retrace.json`:54valores de18bases
máx1,032733e-5; su balance5,019e-6. Seis a.Y oscuras para b.col estaban ausentes
en su mapa; se registraron y comprobaron exactamente0 en el consumidor, no se
inventaron salidas iluminadas. Aceptación acotada: faltan pares/historias/rechazos;
su código todavía descarta lostray y usa fasefallback0. No es auditoría completa.

Claude: refutar signo/unitariedad del nuevo divisor, reproducir cambio en vivo,
ampliar pares/rechazos y confirmar plan de RT directo antes de duplicar backend.
Codex: próxima unidad de propiedades/estado o contrato de geometría GPU/RT,
coordinado. Sigue siendo óptica escalar lossless simulada, no Fresnel/Maxwell ni
perfiles/polarización/no linealidad interna/ortogonalidad física completa.
Geometría sigue CPU; **no RT**, capacidad ni ventaja comparativa demostrada.
