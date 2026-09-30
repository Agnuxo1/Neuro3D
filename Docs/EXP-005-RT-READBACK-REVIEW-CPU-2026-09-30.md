# Readback RT-CAP-002 y revisión parcial RT-CAP-003

2026-09-30 11:31 UTC. Fallback local: JEV bloqueado por seguridad, sin aval
remoto. Trabajo propio CPU ligero, un hilo; ninguna nueva carga Blender/GPU.
Se aplicaron revisión de código y pruebas focalizadas, no una suite general.

## Resultado numérico retenido confirmado

Doce EXR reales de las cuatro capturas T2/T32 CPU/GPU se decodificaron desde
sus bytes, sin Blender ni importación de scripts de Claude. Los 256 píxeles
coinciden exactamente con los JSON de readback del autor y cumplen un checker
propio independiente: 68 hits, 188 misses, ID correcto (desviación máxima
1,9073486328125e-6), error Z/P.z cero, desvío P.xy máximo8,65064091354095e-5 BU.
Umbrales originales sin cambios: ID1e-4, Z/P.z1e-6 BU, radio diagnóstico.03 BU.

Esto verifica lectura ID/Position/Z en estas escenas pequeñas de planos
perpendiculares. NO certifica red coherente RT, ambigüedad entre capas,
rasancia, fase, igualdad de rayos ni ventaja temporal. C3 sigue bloqueado.
Los envelopes antiguos siguen sin protección operacional completa: no se
validan retroactivamente porque sus resultados numéricos sean correctos.

El primer lector propio falló: OpenCV no devuelve estos canales como RGB
convencional. Conservado antes de reparar en
`D:/PROJECTS/.cognition/neuro3d/exp005_rt_readback_initial_fail_20260930_1126.json`,
SHA90a5622b43082d0a4df2e46753548f865fecc052899e9663c17c76c2f1cb27e8.
La solución no altera archivos/umbrales: decoder propio limitado a scanline
8x8, FLOAT, sin compresión, canales con nombre, con negativos de formato y
test sintético XYZ distinto. Se verificó la estructura en la
[documentación oficial OpenEXR](https://openexr.com/en/latest/OpenEXRFileLayout.html).
No acepta HALF, tiles/deep/multipart, subsampling o bloques incompletos.

## Reparaciones CPU de la variante003 contrastadas

Respuesta003SHA26815689760cf4ff989ef049efae26d44d19340c279d8f6989d09db7a50d02fb
y seis fuentes/snapshots revisados por SHA. Se extraen solo siete funciones
puras inspeccionadas por AST, namespace restringido, sin imports/main/writers
de Claude. Cuatro NaN de captura ahora rechazados; cinco inputs inválidos
de presupuesto/telemetría/deadline rechazados; piso RAM4 aceptado y3,9 rechazado.
No se ejecutan sus tests de runner que escriben archivos/lanzan hijos.
Su código conserva salida no cero tras checkerFAIL e inventario de dispositivo.
Es aceptación parcial de validación pura, NO certificación de todo el guard.

Siete tests propios PASS0,021s. Report:
`D:/PROJECTS/.cognition/neuro3d/exp005_rt_readback_review_20260930_1132.json`,
SHA33fa40ac7f2148794341baa574da3459b2e25e73f486b8136ecde50076ea8d53.
27 inputs+2 fuentes propias SHA verificados. Inputs históricos de003 apuntan
a nuestra tarea/doc antes del anexo; no se modifican para fingir coincidencia.

## Dos pendientes operacionales concretos, revisión estática

- P1, `guard_v2.py:93-112`: tiempo de pared y telemetría bloqueante hasta10s,
  seguida de sleep1, con comprobaciones solo al principio del while. Si el
  hijo finaliza durante esa consulta después del timeout, el siguiente poll
  salta a OK sin comprobar elapsed/deadline. Ejemplo de flujo (NO runtime
  ejecutado): consulta a119,9s, duración10s, hijo acaba125s con timeout120;
  poll a130,9s puede ir aOK. Usar reloj monotónico y limitar consulta/espera al
  tiempo restante; comprobar cierre tardío antes de permitirOK. Para garantizar
  máximo120 del piloto, reservar explícitamente tiempo de cancelación/cierre.
- P1, `guard_v2.py:120-123`: excepción externa tras Popen llega aERROR/finally
  sin una ruta garantizada de terminación del hijo. El except tampoco protege
  interrupción KeyboardInterrupt. Inicializar handle antes del try, cleanup
  propio garantizado, guardar estado/exit y verificar fin en rutas de error.
  No matar ajenos; un callback ahora falla fuera del try de telemetría.

Estos pendientes no invalidan los nueve negativos CPU anteriores, pero sí
impiden aprobar todavía el guard completo para nuevas cargas. Petición004 a
Claude: dos tests CPU retenidos de consulta lenta/hijo que termina tarde y
excepción tras spawn/interrupción; variante nueva, hashes, reparación y control
válido. Después, un piloto útil acotado para operación protegida, sin repetir
cuatro renders solamente para llenar GPU ni escalar conf1.
