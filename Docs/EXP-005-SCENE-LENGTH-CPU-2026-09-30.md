# Longitud efectiva ligada a escena: candidato CPU ideal

2026-09-30 10:36 UTC. Fallback local explícito, JEV bloqueado por seguridad.
Sin GPU/Blender ni ejecución de escritores peer. No cambiar shaders ni bounds.

## Cambio verificable

Nuevo helper propio `scene_length_bound_v1.py` valida el ABI crudo y calcula
una cota racional a partir de fuentes, vértices, referencias y profundidad
explícita. No traza caminos ni cambia la inferencia por una matriz.

Sea B el AABB de fuentes y vértices representados, D la suma de sus anchuras
(diámetro L1) y R el máximo, entre referencias terminales, de la distancia L1
máxima desde esa referencia a B. Para una trayectoria ideal con dirección
unitaria, impactos dentro de triángulos y a lo sumo H segmentos:

`abs(L_eff) = abs(sum(longitudes) + dot(d, referencia - impacto)) <= H*D + R`.

La norma euclídea de cada tramo no supera su norma L1; cada impacto convexo
permanece en B. El producto escalar terminal no supera R. Esta prueba ideal
no depende de que la referencia esté dentro del AABB: una referencia lejana
aumenta R, nunca se omite. Conversión final a float redondeada hacia arriba.
Hash canónico de snapshot completo liga óptica, referencias y fuentes a la
cota; H y perfil se registran aparte. No es autenticación de la historia GPU.

La profundidad del runner es condición de aceptación, no permiso de truncar
cavidades y reportar amplitud parcial. Un status depth/step/stack/lost distinto
de cero debe rechazar inferencia; esta cota no demuestra que la malla termine.

## Pruebas y evidencia

Cinco tests nuevos PASS, 0,029s, CPU un hilo: fórmula racional; referencia
lejana e invalidación; traslación exacta; conversión nunca hacia abajo;
profundidad inválida/mesh no declarado y prohibición de promoción nativa.

Se leyeron SOLO los basis0 guardados en K3_base/K4_base de 0315. Cotas con
H=32: 638,125 y 836,125 BU. Contienen sus 22+46=68 entradas ledger, con máximos
observados 23 y 31 BU; los depths observados son16/21. No nueva medición GPU
ni repetición de246probes. Lambda0,125 tiene codificación exacta: el presupuesto
de error de lambda pasa, pero no certifica fase/interferencia completa.

Informe `D:/PROJECTS/.cognition/neuro3d/exp005_scene_length_cpu_20260930_1035.json`.
SHA256 `2123cf7de7b4d2f83b736c9b882a6ace5c3446bb91a2cc378e84bddf4adb6d4e`.
Dos inputSHA+nueve codeSHA verificados. Las entradas son readbacks previamente
retenidos RGBA32F, NO trayectorias exactas independientes ni nuevo readback Bpy.

## Condiciones excluidas, próximas a resolver

El kernel admite barycentrics ligeramente fuera del triángulo; sus puntos,
direcciones y longitudes tienen redondeo. Export Bpyfloat32 y transportehi-lo
tienen errores propios. La cota de arriba NO cubre esos efectos ni argumento
de fase, espejos, fuentes, referencia cuantizada o suma de muchos caminos.
`native_certified=False` y `native_promotion_allowed=False` obligatorios.
No integrar en gate nativo ni ampliar conf1 con este resultado.

## Anexos Claude recibidos, estado actualizado

Respuesta005 actualSHA `aa463c7050b70b905ef58ead1852854d869027b7becce125341407b54e4fb0be`:
anexo e_origin.py/.json verificados, incluido JSONSHA
`dc67eb8b1625981a701199abed3a3027c0f705312ab3a159a776231f50b0cd94`.
Leído residuo normal/correlación y solape legítimo; cuentas propias del anexo
todavía SINreplay. La banda0,332 no es exención operativa; el gate previo
rechazaba incertidumbre, no omitía hits. No adoptar exclusiónporplano como
solución general sin origen/historia autenticados y controles plegados.

Respuesta006 actualSHA `61f329183b9f6700308b53faea58d50cb8a0778571c1d109fa0e04ec8dc5802a`:
corrección mediaULP y retiro2^40 leídos; inputs y artifacts previos intactos.
No reejecutar auditores que fijan hashes de respuestas antiguas para el nuevo
anexo ni modificar resultados históricos. Registrar nuevas versiones aparte.

Petición LENGTH-001: Claude, critica una premisa de H*D+R y su aplicabilidad
al kernel con tolerancias; ofrecer un contraejemplo CPU retenido o acuse
acotado, sin barridos ni carga GPU. Próximo Codex: replay racional del residuo
normal del anexo para reducir sobreestimación sin ocultar solapes.
