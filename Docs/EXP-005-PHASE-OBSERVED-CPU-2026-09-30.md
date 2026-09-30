# Longitudes observadas y fase: contraste sintético CPU

## Resultado

PHASE-OBSERVED-001-CODEX, 30/09 17:24:44 UTC: seis pruebas nuevas PASS
en 0,87734 s, un hilo y timeout de hijo 60 s. Baseline y código propio
se verifican por SHA antes/después; no se repiten suites congeladas.

La variante opt-in valida un ledger terminal comunicado frente a referencias
regeneradas desde la escena CPU. Requiere binding de escena, lambda decodificada,
coherencia y cobertura exacta de IDs/fuentes/puertos/grupos. El orden de los
terminales no importa; IDs duplicados, ausentes, extraños o booleanos rechazan.
No utiliza caminos comunicados como oráculo ni manda caminos CPU a GPU.

Control coincidente: 13 registros, cuatro terminales, presupuesto aceptado.
Alterar una longitud efectiva en 1e-7 BU, y recalcular perfectamente su fase
compensada, produce cota por camino 0,10980668 y potencia por puerto 0,23167093:
el presupuesto falla con gates intactos 1e-4/2e-4. Validar la aritmética interna
de una traza no basta para validar la longitud que la alimentó.

## Contrato de datos, no autenticación

La envolvente ideal L/lambda viene de la escena CPU representada y congelada.
La longitud comunicada se contrasta con esa envolvente; no se acepta una
tolerancia de longitud declarada por el productor. La cota compuesta cobra
su discrepancia aunque el fasor comunicado sea internamente consistente.
Se comprueban los pasos RN del candidato ya congelado y se conservan los
grupos independientes: intensidad se suma entre grupos, no campo complejo.

La entrada exige etiqueta explícita `exp005-synthetic-observed-phase-CPU-v1`.
Los controles sintéticos pueden fabricar trazas perfectamente válidas; los SHA
solo vinculan datos, no prueban que se ejecutaron en GPU. Por eso siempre
`observation_execution_authenticated=false` y `native_promotion_allowed=false`.
NO es ABI nativa desplegada, readback Bpy, autenticación de topología/caminos,
incertidumbre geométrica hi-lo, sin/cos driver, error total ni ventaja de velocidad.
La cota de longitud observa solo el modelo representado: no recupera geometría
perdida antes de exportar ni prueba procedencia de ningún snapshot.

## Negativos y fallo conservado

Las seis pruebas incluyen cobertura, bindings espectrales/de fuentes/grupos,
NaN/Inf, fase antigua adulterada y falsas etiquetas/campos de certificación.
Primer intento: seis pruebas, dos errores; el validador nuevo exigía IDs string
pero el trazador congelado usa enteros no negativos. Se corrigió únicamente
esta variante opt-in y se añadió rechazo de bool. No se cambiaron shaders,
contratos antiguos, fixture, umbrales ni oráculos para obtener PASS.
El fallo inicial queda descrito en el reporte retenido, no como fallo de GPU.

## Coordinación y siguiente paso

JEV bloqueado por seguridad: fallback local, sin aval remoto. GPU sigue
reservada externamente; no se lanzó Blender/GPU ni se alteró cola/ticket006.
Claude: si encuentra una omisión concreta del contraste longitud/referencia,
incluirla en la MISMA crítica CPU opcional PHASE-COMPENSATED, sin nuevo barrido,
guardreview ni job; RT-CAP-006 mantiene prioridad.
Codex: productor nativo opt-in y contrato de evidencia real separados de
esta etiqueta sintética, solo con GPU libre/reservada y guard operacional;
no aceptar datos fabricados como prueba GPU ni escalar conf1.
