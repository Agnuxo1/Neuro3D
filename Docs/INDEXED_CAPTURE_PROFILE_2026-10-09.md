# Perfil posterior de recorrido: ejecución inconclusa

**Resultado posterior:** el worker autorizado se ejecutó y agotó su límite de 90 segundos sin producir salida: 90,055583 s, pico propio de 32,699219 MiB, `WORKER_DEADLINE`, `primary_metric=null`, limpieza verificada. El [recibo](validation/indexed-capture-execution-2026-10-09/attempt01/supervisor.json) y [los bytes archivados](validation/indexed-capture-execution-2026-10-09/artifact_index.json) conservan fuentes, perfil y autorización antes de ejecutarse. No hay una comparación de velocidad válida ni un campo que auditar. El bloque inferior describe el perfil prospectivo original, que permanece intacto.

**Autorización recibida:** el propietario respondió «Sí, autorizo esa continuidad en GitHub» a una pregunta que vinculaba este perfil y los siguientes protocolos de esta secuencia, siempre publicados y fijados antes de cada ensayo. El [recibo separado](research/github_sequence_authorization_2026-10-09.json) conserva esa ampliación y declara ausentes los IDs externos. No se solicitará otra vez la misma autorización.

El [piloto original](CAPTURED_PILOT_EXECUTION_2026-10-09.md) conserva su interrupción a los 90 segundos y métrica nula. El nuevo [perfil congelado](research/indexed_capture_profile_prepared_2026-10-09.json) usa **la misma escena, campos y límites**, pero cambia el selector mediante cajas racionales conservadoras por objeto. Es otro ensayo; su resultado no reescribirá el anterior.

- UUID: `4a0adb28-92de-4910-b2cb-5252df5fa8ef`.
- SHA256 del perfil: `8e0937bfb8db349ed2a52ba4263221465782c0bb8e28734d90d9c654ee1914ab`.
- Límites: 4.096 rayos, profundidad 64, 90 s, una CPU, 4.000 MiB de RAM libre inicial, suelo de 2.500 MiB, pico propio máximo de 1.500 MiB, resultado máximo de 64 MiB.
- Métrica: `COMPLETE→1`, `INCOMPLETE` algorítmico válido `→0`, interrupción o salida inválida `→null`.
- Escena y ocho fuentes de código fijadas por SHA256 antes del ensayo. No GPU, gradientes, generalización, certificado de campo o fidelidad física incluidos.

El supervisor exige un recibo nuevo enlazado a este UUID/hash. La autorización del piloto anterior no se convierte silenciosamente en autorización del perfil modificado. Se conserva además la vía externa/IPFS, sin identificadores emitidos. Cuatro controles del perfil verifican pins, registro ausente, preflight sin arranque y rechazo de recibos inconsistentes; son controles de software, no un recorrido de la captura.

```text
python Tools/run_frozen_indexed_profile_v1.py --profile Docs/research/indexed_capture_profile_prepared_2026-10-09.json --registration RECIBO_VERIFICADO.json --out DIRECTORIO_NUEVO
```

La publicación permite revisar el cambio concreto antes de resolver el registro. El parser no autentica a una persona o un proveedor: el operador debe verificar el origen real de la autorización o recibo.
