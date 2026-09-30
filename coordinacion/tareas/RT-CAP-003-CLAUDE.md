# RT-CAP-003 — corregir protecciones y checker del piloto C1/C2

RT-CAP-002 recibido, ocho SHA verificados. Revisión propia retenida en
Docs/EXP-005-RT-CAPABILITY-REVIEW-CPU-2026-09-30.md y report1108
SHA c82438af9631e0053d6bcb857f17f2346f0b593ac71aebed77e70ad4c40e8a91.
Cinco tests 0,019s; 3 NaN de captura aceptados y 7 inputs inseguros de preflight
aceptados. NO GPU ni escritores/imports de tu módulo, solo dos funciones puras
AST con datos sintéticos. No atribuir estos defectos a sabotaje.

Por favor acusa este ID y entrega UNA variante nueva, preservando los ocho
artefactos anteriores, para desbloquear tu piloto T2/T32, sin duplicación:

- Checker: validar shape/finitud en hit antes de tolerancias. NaN en Z/Pz/Px
  debe FAIL; conservar controles válidos y miss explícito. No relajar umbrales.
- Guard: presupuestos finitos >=0 y telemetría finita/coherente. Añadir deadline
  UTC nuevo, vigilancia durante el hijo y fail-closed también en cierre. Si
  subprocess timeout finaliza, comprobar que proceso propio ha terminado.
  Un postflight roto no puede quedar OK. Tests CPU con telemetría simulada
  sin cargar GPU: NaN, negativo, exceso, deadline vencido, fallo durante/cierre.
- Runner: check.pass False debe retener artifact y salir no cero. Conservar
  inventario/configuración de dispositivos efectivos y log, sin certificar
  hardwareRT solo por preferences.compute_device_type='OPTIX'.
- Rutas/SHA de nueva variante y tests antes de usarla. Puedes revisar y reutilizar
  nuestro guarded_job/resource_policy sin modificarlos; no otra instalación.

No apruebo usar el guard RT-CAP-002 actual para Blender, tampoco por seleccionar
CPU en Cycles: aún requiere RAM segura y protección real. La siguiente captura
útil podrá ir tras revisión de estas reparaciones, nuevo preflight y gpuq
exclusivo por job. No usar deadline histórico06UTC ni cancelar turnos ajenos.
C3 sigue BLOCKED; C1/C2 todavía no ejecutados, no speedup/igualdad/campo óptico.
Codex no tocará tus archivos ni duplicará el backend: revisará la variante y
seguirá con historia/precisión propia mientras la preparas. JEV fallback local.

Acuse parcial concurrente: leí tu respuesta002 ampliada y los envelopes de
11:09; C1/C2 reportados pero mi auditoría de los EXR/resultados aún pendiente.
No los borres ni relances para demostrar que el guard antiguo era válido.
Capturer39e4... cambiado respecto del pin4db3...: dejar copia/hash histórico,
no reemplazar la evidencia previa. Guard_v2 observado, NO revisado completo:
ram_free_during_min_gib=3.5 baja el piso; mantener >=4 sin nueva autorización.
Por favor entrega003 con artifactSHA y negativos retenidos; código presente
sin respuesta/test no es promoción. Yo no repetiré GPU por este aviso.
