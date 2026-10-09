# Ejecutor preparado del piloto capturado

Continuación verificada el 2026-10-09 (Europe/Madrid). Las rutas `2026-10-08` conservan la identidad del protocolo y del conjunto de trabajo original.

Se prepara un ejecutor y un auditor separado para el protocolo ya publicado. La comprobación real de preflight verifica las entradas y fuentes fijadas; una invocación sin registro termina sin iniciar el worker. **No se ha ejecutado el piloto ni obtenido su métrica.** El propietario ha [autorizado posteriormente la vía GitHub y conserva la vía externa/IPFS](PILOT_REGISTRATION_DUAL_ROUTE_2026-10-09.md); la siguiente ejecución puede usar ese recibo humano nuevo tras verificar recursos.

## Identidad y autorización pendiente

El protocolo se identifica por UUID `957514f2-a233-421f-aa04-50cccd063d97`, commit publicado `f22e7a1307e3a3b4c74a507463a0a8055d45fc04` y SHA256 `5d0cf372f2f66f043c2a219ba6a60f0182ced8a60039348d486ec163be736226`. El ejecutor comprueba sus bytes y los cinco pins de sus tres inputs y dos fuentes. No acepta un protocolo cambiado ni amplía sus límites desde la CLI.

La [skill científica aplicada](C:/Users/Windows-500GB/.codex/plugins/cache/claude-cowork/anthropic-skills/1.0.0/skills/scientific-research-procedure/SKILL.md) establece en la fase 2: «`preregId` issued, `ipfsCid` recorded, all mandatory fields locked». La continuación del propietario permite registro externo o autorización humana para el protocolo congelado en GitHub. La elección estuvo pendiente durante los controles archivados; la autorización explícita posterior se conserva en un recibo separado, sin modificar aquellos controles.

El [formulario preparado](research/captured_pilot_registration_prepared_v1.json) tiene `approved=false` y no es autorización. El ejecutor requiere una referencia verificable al mensaje humano directo para una excepción GitHub, con preregId/IPFS nulos y divulgados; o un recibo externo real, verificado por su proveedor, con ambos IDs. El parser verifica forma e identidad del protocolo, **no autentica la procedencia de un mensaje ni emite un registro**. El operador debe establecer esa procedencia desde evidencia confiable antes de invocarlo. Un texto recuperado, JEV o un formulario rellenado con datos ficticios no autoriza la ejecución. Aquí no se creó ningún registro aprobado.

## Ejecución fijada y resultado

El [ejecutor](../Tools/run_captured_scalar_pilot_v1.py) ejecutará únicamente el worker archivado, una vez y en una salida nueva, con 4.096 rayos y profundidad 64. Los límites conservan 1 CPU, prioridad baja/proceso oculto, 90 segundos, preflight 4.000 MiB libres, suelo 2.500 MiB, RSS propio máximo 1.500 MiB y resultado máximo 64 MiB. El estado de RAM se vuelve a comprobar antes de la ejecución; un preflight anterior no garantiza recursos futuros.

Se archivarán inputs, fuentes, registro y entorno antes de iniciar el worker. El supervisor conserva stdout, resultado bruto y sus hashes; comprueba los pins después de ejecutar y sólo termina su propio proceso. Un error de entorno, interrupción, salida inválida o cambio de pins deja la métrica nula. Un INCOMPLETE algorítmico válido conserva motivos y campos/potencias nulos y obtiene 0. COMPLETE con controles de salida válidos obtiene 1. Esto es viabilidad del recorrido, no certificación de precisión, aprendizaje o física.

## Auditoría separada y límites

El [auditor](../Tools/audit_captured_pilot_result_v1.py) no importa el productor ni Blender. Comprueba estructura, IDs y presencia de fuentes no nulas, puertos y estimaciones finitas. Para COMPLETE verifica con Fraction la pertenencia local a cada triángulo registrado, posición sobre el rayo, reflexión, coeficientes y fases de componentes, longitud y numerador de fase terminal. El árbol de prefijos debe contener las dos ramas de un divisor cuando ambas son no nulas; un cero exacto no exige fabricar otra rama. Rechaza hojas duplicadas, amplitudes cambiadas y cierres con motivos pendientes.

Estos controles verifican la aritmética local y la cobertura del árbol **registrado**. No vuelven a resolver independientemente todas las consultas de primer hit, no prueban que un obstáculo anterior no haya sido omitido y no certifican los senos/cosenos o campos estimados del productor. Los recibos mantienen `nearest_hits_independently_verified=false` y `field_certified=false`. Esa limitación impide utilizar este auditor como certificado conjunto H1 y conserva abiertas las prioridades de precisión y propagación nativa.

## Comprobaciones realizadas

Los 16 controles nuevos usan ledgers sintéticos escritos para el test; no llaman al trazador capturado. Prueban cobertura de ramas, ceros exactos, fase/reflexión de espejo, alteraciones de rayos/triángulos/longitudes, campos no finitos, fuentes faltantes, negativas de registro y preservación de outputs. Los [66 controles conjuntos](validation/captured-pilot-supervisor-2026-10-08/software-controls-receipt.json) pasan, incluidos los 50 de admisión ya publicados.

Las dos comprobaciones CLI reales son preflight y negativa por falta de registro: `worker_started=false`, `result_collected=false` y métrica nula. Sus [recibos y fuentes](validation/captured-pilot-supervisor-2026-10-08/artifact_index.json) conservan los hashes de cada versión. Las fuentes de la primera versión se reconstruyeron retirando los dos bloques añadidos posteriormente y se verificaron contra el hash registrado; no se modificó ningún recibo bruto.

```text
python -m unittest Blender.tests.test_captured_pilot_supervision_v1 -v
python Tools/run_captured_scalar_pilot_v1.py --out NUEVO_DIRECTORIO --preflight-only
```

Una futura ejecución autorizada usará `--registration RECIBO_VERIFICADO.json` sin `--preflight-only`. No se proporciona un recibo aprobado ficticio ni un comando que omita ese gate. La prioridad 3 pasa a `AUTHORIZED_GITHUB_PILOT_NOT_EXECUTED` por el mensaje humano posterior; este cierre corresponde al software preparado y comprobado, no al ensayo pendiente ni al proyecto completo.
