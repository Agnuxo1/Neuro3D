# EXP-005: preparación opt-in de exportación del MZI

Fecha: 30/09/2026. Fallback local: JEV bloqueado por seguridad, sin aval remoto.

## Contrato de alcance pequeño

Se prepara un hijo privado de Blender que construye escenas NUEVAS, exporta
la geometría evaluada, guarda y reabre tres archivos nuevos. No renderiza ni
ejecuta un kernel GPU. Los campos de referencia los calcula Python CPU sobre
la exportación real, con historias explícitas comprobadas geométricamente;
no son evidencia de propagación nativa GPU ni de RT.

Casos fijados antes de una eventual ejecución:

| Caso | Fase ideal de MA | Desplazamiento de referencia Dx |
| --- | --- | --- |
| base | 0 rad | 0 BU |
| switch | pi rad | 0 BU |
| reference | 0 rad | 0,03125 BU |

Una fuente; seis objetos; doce triángulos; cuatro caminos terminales.
La fase es una propiedad de escena, NO un desplazamiento geométrico del espejo.
Las coordenadas del fixture son diádicas, representables en float32.

## Gates fijados

- Usar `exp005_scene_readback.py` congelado: geometría evaluada VIEWPORT,
  propiedades ópticas y orden de objetos/IDs globales.
- Exigir igualdad exacta del fixture y de cada exportación antes/después de
  guardar/reabrir: schema, lambda, objetos, fuentes y mallas no declaradas.
  No sustituir propiedades faltantes con valores del fixture ni relajar tolerancias.
- Grupos de coherencia leídos de la escena: `s:g`, sin default externo.
- Reconstruir el árbol completo y campos ideales CPU desde el snapshot real;
  error complejo frente a fórmula MZI independiente <=1e-13.
- Conservar los snapshots, resultados, versión Blender y SHA de cada `.blend`.
  Los oráculos quedan explícitamente fuera de cualquier medición nativa futura.

El constructor no borra objetos ni usa factory reset. Solo la escena activa
nombrada es entrada de la exportación; las escenas previas que puedan persistir
en el archivo no participan en el cálculo. Se rechaza iniciar desde un `.blend`
ya abierto o una carpeta de evidencia existente. El flag CLI de hijo privado
NO sustituye una reserva ni autoriza una carga por sí mismo.

## Validación disponible y límites

Pruebas CPU con doubles del exportador congelado y emulación de almacenamiento
de vértices float32: tres controles y ocho readbacks inválidos. Los negativos
son evaluación ausente, cambio al reabrir, vértice cambiado en ambos snapshots,
fuente cambiada, propiedad ausente, orden cambiado, malla extra y coherencia
cambiada. Pruebas adicionales rechazan grupos ausentes/vacíos; el chequeo AST
constata ausencia de render/kernel/borrado e importación de bpy diferida.

Estos doubles NO prueban `bpy`, contexto headless, guardar/reabrir real, recursos
ni cierre del proceso. El runner todavía NO se ha lanzado en Blender.
El perfil previo GPU, nearest V2, shaders, contratos y fixtures permanecen intactos.
No promoción de conf1, bounds, solape físico, hi-lo ni certificación de fase nativa.

Evidencia CPU ejecutada 13:38:07 UTC: tres tests PASS en 0,062s,
un hilo/hijo limitado a 60s; tres controles/ocho negativos y error máximo
de campo 2,220446049250313e-16. Report local
`D:/PROJECTS/.cognition/neuro3d/exp005_history_mzi_export_cpu_20260930_1338.json`,
SHA `fb30b79a08b05ee5f92d8c2f23f9aa6ad02d840cce3c6a6cb484cf124f55ef44`;
trece code SHA contrastados. La preparación inicial 1334 con siete negativos
queda conservada; se añadió el negativo de coherencia antes del commit.
Los diez pins del fixture/oráculos/shaders del report MZI 1308 siguen iguales.

## Ejecución futura, sin adelantarse a Claude

Después de contrato/tests/commit propios y del turno RT-CAP-006 de Claude:
comprobar gpuq/procesos y memoria/temperatura reales dentro del job; reservar
exclusividad. Guard fail-closed con deadline NUEVO, piloto <=120s; presupuesto
conservador de RAM 2 GiB y piso 4 GiB libre DESPUÉS del presupuesto, geometría
>=1024 bytes/celda más márgenes/temporales; VRAM presupuestada 2 GiB con total
<=18 GiB y temperatura <=80 C. Si el presupuesto real es mayor, ampliarlo,
no reducir reservas ni márgenes. No tocar el deadline nocturno histórico.

Antes de lanzar, pinnear todos los scripts/dependencias y contrato del job,
crear carpeta nueva y proceso privado. Aceptación conjunta: rc0, envelope
guard OK, proceso propio finalizado, readback/gates PASS y hashes verificados
de report y blends; preservar fallos. La propagación GPU requerirá otro contrato.

No instalación, publicación, push/merge, tickets cancelados ni escritores ajenos.
RT-CAP-006 sigue la única petición abierta a Claude; esta preparación no añade
una revisión operacional ni un bucle de críticas.
