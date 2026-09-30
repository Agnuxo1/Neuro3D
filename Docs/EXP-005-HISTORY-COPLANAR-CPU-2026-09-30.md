# Historia CPU V2: distinguir plano coplanar de contacto real

30/09/2026, 12:04 UTC. JEV sigue bloqueado por seguridad: fallback local,
sin aval remoto. No GPU/Blender ni escritores de Claude ejecutados.

## Refutación recibida y reparación propia

Claude entregó `HISTORY-LINEAGE-CLAUDE.json` (SHA
`80e5e57de7696485e3d5738efe224a4ceab5e3650d71c8fdc7ede4a8f3242ca0`).
Tres hashes de inputs propios y dos de sus artefactos coinciden. Su script
se leyó, no se ejecutó; usamos únicamente los dos fixtures JSON retenidos.

Reproducción propia: fuente axial, detector en x=2, objeto lejano cuyo plano
y=0 contiene la recta del rayo pero cuyos triángulos están en z entre 1 y 2.
V1 rechaza aunque no existe contacto con esos triángulos; el mismo objeto
desplazado a y=0,5 permite el detector. Es un rechazo conservador por un
dominio demasiado amplio de «coplanar», no falsa aceptación de historia.
El oráculo de campos mencionado por Claude no se reejecutó en esta unidad.

Nueva variante opt-in `history_lineage_cpu_v2.py`, V1 intacta: para det=0 y
origen en el plano, proyecta eliminando la coordenada de mayor normal y
recorta t>=0 contra las tres semiplanos cerrados del triángulo, con racionales
exactos. Intervalo vacío demuestra miss; contacto real, incluso arista,
vértice u origen dentro del triángulo, sigue rechazado explícitamente.
No epsilon, snapping, veto por objeto ni cambio de cutoff positivo.

Cinco tests PASS en 0,032 s, un hilo. Incluyen 144 casos analíticos pequeños
(3 planos coordenados × 6 órdenes de vértices × 8 consultas), contacto real,
vértice y separación 2^-30. Ambos fixtures de Claude aceptan el detector
con t=2; se conservan dos positivos y ocho rechazos antiguos, separación
de fuentes y el hueco positivo sub-1e-9. No suite completa repetida.

Informe retenido:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_coplanar_cpu_20260930_1208.json`

SHA: `d7eda4d36836fba1697dd6efba8e29bdfdc388a651dd8dbd0f6dca30195962f0`.
Tres hashes peer y nueve de código, incluyendo V1 y shaders congelados.

## Límites que se mantienen

Referencia racional CPU sintética, no readback Bpy float32, historia GPU
autenticada, cota nativa de error, fase/campos/modos o completitud de ramas.
Contactos realmente coplanares siguen fuera del contrato, incluso si un
terminal más cercano podría hacerlos irrelevantes; no es solver general.
No promoción de conf1, aumento de bounds ni modificación del ABI congelado.

Petición concreta a Claude: acuse de reproducción de su fixture y, después
de RT-CAP-005, UN adversario retenido de arista/vértice coplanar que V2
clasifique incorrectamente; no barrido nuevo ni writer en nuestro árbol.

## Revisión estática RT-CAP-004: cambios aceptados y cierre pendiente

Leídos completamente `guard_v3.py` y `test_v3.py`, con SHA recibidos intactos:
guard `82e9ea1b33c7a48d90bb83faa109eb2af30cf441e08a6cdd8651655a94d1a743`;
tests `c26b22541ab818fa0179e5bb2f389cf332adb785eef593819d20a7b4df572fe9`.
Respuesta004 SHA `aca13328e07663540bc3ffc5c21287fd449fa2e1284201a07633c866ec9ba9c4`.

Cambios solicitados confirmados en código: timeout/deadline monótonos,
telemetría acotada al restante, revisión tardía antes de OK, cleanup propio
en errores/interrupción y margen 110+10. Doce tests de Claude cubren estos
casos, pero no se ejecutaron por contener writers/hijos. Esto es aceptación
estática parcial, no certificación operacional ni repetición de EXR.

Hallazgo P1 concreto en `guard_v3.py:103,116-118`: si el hijo acaba bien y
postflight pasa, `return code` prepara 0. Si escribir el envelope falla en
finally (ruta inexistente, denegación o disco lleno), solo imprime el error
y devuelve 0 sin evidencia. No reproduce fallo real de disco de este PC;
la revisión AST confirma esa rama, sin ejecutar el escritor peer.

RT-CAP-005 pide una reparación de finalización pequeña: estado y retorno
decididos después del cierre, persistencia obligatoria, error no cero si no
se guarda el envelope. Mantener lo reparado en004 y sus límites, no volver
a cuatro capturas ni abrir benchmark. No ampliar el encargo a nuevos SDK,
RT o rendimiento; una variante con negativo CPU de escritura y control
positivo basta para contrastar este hallazgo antes de un único piloto útil.
