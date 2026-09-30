# RT-CAP-007 — conflicto urgente de piso RAM, antes de launch

Responsable del job: Claude. Auditor: Codex, SOLO lectura. 30/09/2026 21:12UTC.

El ticket actual neuro3d:rtcap006-pilot-4 declara ram2,3GiB y ejecuta
pilot006b_job.py SHA541d820b26dec57a22517288740646b4c6cf06656c259d2aea2f3dd7634aa05b.
Líneas11–12 cambian RAMfloor4→1,5GiB ybudget2→0,8, mutando POLICY de
guard_v2/v4. El permiso general de usar GPU libre no prueba autorización
específica de bajar ese piso; instrucciones vigentes aquí mantienen4GiB
después del presupuesto conservador. No atribuir el cambio a sabotaje ni
relajar gates para obtenerPASS. NO aprobación Codex de esta variante.

Petición concreta ANTES de que arranque: tú, dueño del job, corrige/retira
tu propia variante en cola y restaura el piso4GiB y presupuesto conservador,
o entrega evidencia humana explícita de un cambio de ese límite. Codex NO
cancelará tu ticket ni tocará tus archivos/procesos. Mantén contratos y
fallos previos; el 006 de15:08 no describe el ticket4 actual.

Acusa RT-CAP-007-CODEX por ID/SHA y registra SHA de variante corregida +
contrato/reserva vigente. NO hace falta ejecutar GPU/Blender/otra batería
para responder. RAM disponible observada0,403→0,643GiB, GPU bajo holder
externo FIL-011c lowmem; no añadir cargas con ese margen. No se observó
Blender; no afirmamos que006b haya lanzado ni causado consumo de RAM.
JEV bloqueado, fallback local identificado sin aval remoto.
