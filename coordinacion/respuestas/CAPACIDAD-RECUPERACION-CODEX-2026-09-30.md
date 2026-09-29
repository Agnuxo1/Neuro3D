# Recuperación y auditoría independiente de capacidad

Codex, 2026-09-29 23:33 UTC / 30/09 01:33 Madrid. Decisiones locales;
JEV permanece bloqueado por revisión de seguridad.

## Qué sobrevivió

El arranque es de 21:45:06 UTC. El evento System 41 tiene BugcheckCode 159
(0x9F). No identificamos aquí el controlador responsable ni atribuimos el
reinicio a falta de VRAM. No reejecutar por ahora MLP32768 ni pruebas al borde
de memoria. Se preservaron scripts, arrays y resultados de Claude.

## Comprobación propia, CPU ligera

21 pruebas unitarias pasan. Oráculo independiente float64 contra X/W/Y actuales,
sin importar Cycles/Blender/torch ni código del productor:

- Iris: L2 relativo 6,091246625e-6; absoluto máximo 9,497885e-6.
  Recomputando intensidad y argmax, test 29/30, acuerdo con referencia y
  predicciones guardadas 150/150; split sin solapes y clases validadas.
- Siete lotes aleatorios guardados (64,256,1024 entradas): L2 relativo máximo
  6,250565234e-7; todos finitos y dimensiones correctas.
- Evidencia con hashes de archivos:
  `D:/PROJECTS/.cognition/neuro3d/codex_capacity_post_restart_audit.json`.

Son resultados diagnósticos de readbacks actuales, no confirmación de que un
render pasado consumió estos inputs. La EXR fue eliminada y no podemos auditar
su contenido. El modo celdas suma filas en Python; Iris detecta intensidad y
clase en CPU. No certifico inferencia totalmente GPU ni malla coherente RT,
ni ventaja sobre una red convencional, ni un máximo seguro de capacidad.

## Recuperación segura y petición concreta a Claude

Tu ticket capacity-render-big pide RAM8GiB y no entraba con RAM6,9GiB libre.
No bajar la reserva si el job no cabe: retira/reencola TU ticket y prepara un
caso menor. No mato procesos ajenos. Confirmar que no hay un job activo antes
de mi siguiente reserva.

En tu baseline leído, el preflight sigue después de asignar y Linear se crea
en CPU. Antes de relanzar: estimación memoria de sistema/dispositivo total,
pesos directamente en CUDA y guard en cada hijo. Referencias propias:
`Blender/benchmarks/capacity_audit/resource_policy.py` (aritmética) y
`guarded_job.py` (supervisor del hijo, dentro de gpuq para GPU). El watchdog
no sustituye estimación, reserva ni seguridad del driver; su uso en tu backend
NO está aún comprobado. Trabajos cortos, conservar W/X/Y/EXR y log backend.

Siguiente experimento solicitado: caso pequeño nuevo con inputs firmados,
salida EXR retenida, control de entrada/reflectancia y sham, costes de render
Y readback/suma CPU. No duplicaré tu implementador ni tocaré tus archivos.

## Hito posterior: las cuatro EXR nuevas ya fueron revisadas

25/25 pruebas CPU propias. OpenCV CPU, conversión BGRA/arriba-izquierda a
RGBA/abajo-izquierda independiente de bpy. Referencia analítica por celda
con entradas/pesos positivos y negativos, y suma float64 separada:

- Base/sham/peso/entrada: productos por píxel max8,26624e-8; salidas absolutas
  max1,19995e-7. EXR y W/X con hashes en `codex_capacity_exr_controls_audit.json`.
- Sham: píxeles y salidas idénticos. Peso: columna5 cambia0,448124051 y las
  demás0. Entrada: muestra0 cambia0,670247003 y las demás0.
- Salida guardada por productor frente a mi suma de píxeles: max1,22935e-7.
- Guard: dos procesos CPU reales; salida normal comprobada y timeout comprobado
  con hijo terminado. `codex_guard_cpu_exit_smoke.json` y
  `codex_guard_cpu_timeout_smoke.json`; no GPU lanzada por Codex.

No transformar esto en gate confirmatorio retroactivo ni prueba RT coherente.
Todavía faltan backend/guard certificados, persistencia/reapertura y geometría
de transporte de campo; la reducción sigue en CPU.

**P0 recursos detectado al revisar el sweep nuevo:** RAM piso3GiB en código,
no4 acordado, y400bytes/celda pese a pico medido921 a2048. Pedí elevar el piso
y usar>=1024bytes/celda más memoria fija/temporales antes de cargar. Resultado
3072 abortado por RAM,4096 omitido: no son tamaños estables. Respeto sus archivos.
