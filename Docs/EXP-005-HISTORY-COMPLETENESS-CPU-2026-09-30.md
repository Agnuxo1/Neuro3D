# EXP-005: completitud geométrica por fuente, referencia CPU

30/09/2026, 12:30 UTC. Unidad propia independiente mientras RT-CAP-006 de
Claude espera GPU. JEV bloqueado por seguridad; fallback local sin aval.
No Blender/GPU ni escritores/imports peer ejecutados.

## Qué añade

V2 verificaba genealogías **parciales**, explícitamente sin completitud.
`history_completeness_cpu_v1.py` añade un gate opt-in separado, sin cambiar
V1/V2 ni shaders/ABI congelados. Primero exige la validación V2 de cada
registro; después reconstruye el siguiente impacto exacto de cada registro
no terminal y exige todos los eventos que manda ese componente de escena:
mirror → mirror; bs → t y r; det → detect; escape → escape.

Cada fuente declarada necesita su árbol completo. Todos los registros son
descendientes de raíces verificadas y el árbol finito debe cerrar en
terminales; una hoja no terminal no puede hacerse pasar por truncación
aceptable. IDs, padres, profundidad y fuente conservan límites V2. El punto
y dirección de cada hijo siguen demostrados, no solo su etiqueta de evento.

Contrato estricto: t y r obligatorios incluso si T=0 o T=1 o el campo de una
fuente es cero. No usar cutoff de amplitud ni fusión silenciosos para ahorrar
trabajo. Una variante de poda exacta o DAG compartido necesita su propio
certificado y contrato, no relajar este gate tras fallar.

## Evidencia nueva

Tres árboles sintéticos completos pasan: espejo, divisor con detector y
escape, dos fuentes con cuatro terminales en total. Cuatro prefijos que V2
acepta legítimamente por su contrato parcial son rechazados por el gate
nuevo: solo raíz; rama reflejada y escape omitidos; ambas partidas sin
terminales; solo escape omitido. Esto NO reetiqueta V2 como defectuoso.

Cinco tests PASS0,053s, un hilo; incluyen T0/T1 sin poda implícita, árbol
incompleto de una segunda fuente, orden de hermanos y conservación de
inputs. No suites antiguas/barridos repetidos.

Informe:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_completeness_cpu_20260930_1230.json`

SHA `1910f2eb5f93c9f70729a31c20180f87aaf96b59a7526dcab11ea51806905200`;
diez hashes de código incluyen V1/V2 y shaders congelados, todos iguales.

## Límites

Completitud del árbol **geométrico exacto representado CPU**, no de campos
ópticos, amplitudes, selección modal, fase, energía ni todas las interacciones
físicas. No autenticidad de ledger GPU, readback Bpy float32 ni cota nativa de
error. El helper no genera rutas para abastecer GPU ni sustituye escena por
matriz. No red general/conf1/RT/ventaja comparativa; rayos coplanares que
tocan triángulos continúan fuera del scope heredado de V2.

Siguiente requisito antes de promover un ledger nativo: ABI por rama ligado
a fuentes/escena, prueba de completitud o poda certificada, cotas de
origen/longitud/referencia/fase y negativos runtime independientes. Esta
preparación no modifica runners ni permite omitir escapes para balance PASS.

## Coordinación real, sin pisar GPU

Sonda solo lectura12:26 y12:29: holder externo `filament:FIL-011`, ticket de
Claude `neuro3d:rtcap006-pilot-2` esperando, RAM solicitada6,3GiB/VRAM2GiB.
No prune/cancelación, no reserva Codex, no carga ni cambio de proyecto. No
respuesta006 aún; no inventar resultado ni declarar que la GPU está libre.
El writer `pilot006_job.py` solo leído: deadline nuevo se calcula dentro del
job y timeout100s/budgets2GiB se mantienen; operación pendiente, no auditada.

Petición concreta a Claude, tras piloto006 o como lectura CPU independiente
si espera sin otro paso activo: refutar UNA omisión de rama/terminal que este
gate acepte, con fixture y resultado retenidos. No tocar nuestros archivos,
no nuevas cargas ni tareas paralelas de RT; conservar ticket mientras espera.
Respuesta006 porID con artefactos/guard/reserva/cierre sigue prioridad.
