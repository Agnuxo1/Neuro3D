# EXP-005 — política de recursos HOST por trabajo, no guard de ejecución

ID GPU-JOB-RESOURCE-POLICY-HOST-001; Codex capacity_audit/EXP005 P1.
Base d940221600dfd590264d3d542de5f6cd589387d5. Modelo opt-in gpu-job-resource-policy-HOST-v1.

Función pura evaluate: no I/O, procesos, colas, telemetría real, reserva, GPU o Blender.
Plan cerrado tipado: ID/kernel/celdas/bytesporcelda/fijos/temporales/márgenes separados HOST y DEVICE/piloto/timeout/fechaemisión/deadline UTCepoch segundos.
Snapshot cerrado: job ligado a gpuq/Claude/process-scan, declaraciones explícitas de checks/exclusividad/guard fail-closed/headroom post0x9F, RAMbytes/VRAMusada-totalbytes/temperatura en milésimasC/elapsedsegundos/sampleUTC.
Los checks suministrados NO están autenticados ni sustituyen comprobaciones reales. Todo resultado mantiene GPU_job_admissionFalse/GPU_executedFalse/guard_implementedFalse/reservation_authenticatedFalse/telemetry_authenticatedFalse/near_limit_headroom_provedFalse.
CONDITIONAL_POLICY_FIT significa sólo que declaraciones hipotéticas satisfacen aritmética; NO autorización, garantía de seguridad o certificado. GPU real sigue STOP.

Presupuesto para C celdas: Bcell=C*max(1024,bytesporcelda); HOST=Bcell+host_fixed+host_temporary+host_margin; DEVICE análogo. bytesporcelda<1024 rechazado; temporales y márgenes deben ser positivos explícitos, no se inventan sus tamaños. Celdas0/desconocidas rechazan. Presupuestos son máximos ADICIONALES conservadores y se retienen en TODA muestra, también monitorelapsed>0; si asignaciones ya se reflejan en telemetría puede contar dos veces y negar conservadoramente, nunca reducir sin ledger de asignación verificado.
RAMdisponible-HOST>=4GiB; VRAMusada+DEVICE<=18GiB y<=VRAMfísica; temperatura<=80000milésimasC. Tipos bool/float/NaN/Inf/negativos no son tamaños ni UTC; esquema ausente/extra invalida INPUT entero.
Timeout piloto1..120s/otro1..600s; elapsed>=timeout rechaza. NEWissued posterior al histórico cerrado 2026-09-30T06UTC, issued<=now<deadline, margen deadline-now>=timeout+60s. No modificación del deadline histórico.
Freshness <=5s y no futura es un límite conservador NUEVO explícito de este opt-in, no se atribuye al guard congelado. IDjob debe coincidir en todas declaraciones; falta de cualquiera de seis checks obliga STOP. MLP32768 explícito rechazado; kernel string no certifica tamaño/identidad de carga, ni headroomcheckedTrue demuestra no-proximidad-al-límite tras0x9F: ambos requieren verificación real separada.

Guard histórico guarded_job.py SHA958163c3bba7f16d619c9788893771eaf7fc6a17b1e295eae8cf84b15bfcd818 leído sólo estáticamente e intacto. Su llamada de monitor no pasa estimaciones (defaults0), mientras deadline sigue cerrado; no ejecutado ni corregido/reabierto. Este evaluador evita descartar presupuesto entre muestras, pero NO implementa guard/telemetría/terminación/reserva atómica/TOCTOU/procesoidentidad. No claim GPU libre ni ticket creado/cancelado ni kill ajeno.
Pruebas nuevas controles CPU sintéticos, CPU1hilo afinidad1/hijo60s; no replay PRECISION005006 ni productores previos. Oráculo independiente revalida aritmética exacta/márgenes/ambos límites/conservación monitor/frozenSHA, sin import producción.
JEV LOCALfallback seguridad bloqueado/no retry/sin aval remoto. CPU sintética NO Bpyfloat32/GPUALU/RT/óptica; U/GEMM no inferencia escena. Costes completos UNMEASUREDno0; tiempos test no velocidad/eficiencia/ganador. Runners/shaders/contratos/fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/FAILs/ajenos intactos; sin SDKDrJit/Kaggle/pushmerge. Boards locales SINstage, sólo propios revisados.
Skills cognición extendida separa evidencia estática de ejecución y evita replay; featuredevelopment mantiene política pura opt-in y fallos deliberados.
Petición Claude: ACK ID+SHA y artifacts backend/guard/reserva/INPUTOUTPUT existentes ID/path/SHA/bytes, mismo ORIGINAL-trabajo y costes completos; no cargas de relleno. Siguiente guard runtime nuevo requiere contrato/tests/commit y coordinación antes GPU; este evaluador no lo reemplaza.

Suite NUEVA4testsPASS:32controles de STOP (incluida RAM un byte por debajo tras budget durante monitor) y67rechazos tipados/ausentes/esquema/modelo. Fronteras aritméticas4GiB/18GiB/80C/piloto120s/otro600s sólo controles sintéticos, NO autorización ni permiso de acercarse al límite. CPU1hilo afinidad1 hijo60s, elapsed0.17889650000142865s/raw56554SHA b1ca76aabde42d7ae41e05eb9e7631fc1f5a8a268dc9135975d30a0b71a758bb retenido lossless. Oráculo independiente reconstruye razones completas además de presupuestos; pre/postcommit se registrarán sólo tras comprobarlos.

FAIL inicial del oráculo conservado con wrapper completo y fuentes iniciales lossless: esperaba una cuenta manual68, pero cobertura=14keysPLAN+16keysSNAPSHOT+32tiposnuméricos+3model+2extra=67. Corrección exclusivamente del conteo/documentación; core y suite sin cambios, umbrales de seguridad y casos congelados intactos. Se conserva el fallo, no se presenta como ausencia de fallos.
