# Captura privada escalar de fase: preparación CPU, no ejecución GPU

Fecha: 30/09/2026. Unidad PHASE-NATIVE-CAPTURE-001-CODEX.
Fallback local: JEV bloqueado por seguridad, sin aval remoto.

## Contrato acotado

Variante propia `phase_native_capture_v1.py`; shader, decoder y preparación
127efdf permanecen intactos. No hay CLI ni lanzamiento de procesos. El
adaptador solo puede invocarse dentro de un hijo ya supervisado; admisión
por defecto rechazada. Un callback de prueba no autoriza GPU real.

El manifiesto fija los doce casos preregistrados, estados esperados, bits
UINT32 y SHA de preparación y dependencias. JSON nunca transporta NaN como
número; el negativo NaN viaja por sus bits. Comparación canónica distingue
bool de int y rechaza cambios de casos, política, pins o campos adicionales.

Cada captura exige carpeta nueva y reserva `result.json` antes de tocar GPU.
La nueva variante de dispatch conserva `raw_uint32.json` ANTES del decoder
y del control de deadline posterior al readback. Un fallo numérico conserva
datos; uno de compilación no inventa readback. Fallos de persistencia,
admisión, deadline y decoder se propagan; no se convierten en éxito ni en
fallback CPU. Resultado finalizado una vez; nada se sobrescribe.

Deadline UTC nuevo dentro de 90 s y control monotónico complementario.
Estos checks cooperativos NO interrumpen compilación/driver bloqueado:
supervisor externo con timeout duro, envelope operacional, telemetría
fail-closed, inventario de procesos y reserva gpuq siguen obligatorios.
RAM presupuesto 2 GiB más piso 4 GiB después; VRAM total <=18 GiB y <=80 C.
No modificar deadline nocturno histórico ni adelantarse al ticket de Claude.

## Prueba retenida

Siete tests CPU nuevos, 0,359802 s, un hilo/hijo acotado a 60 s. Dobles CPU:
doce casos completos, corrupción numérica/status, persistencia obligatoria,
compilación fallida, admisión ausente, carpeta existente y deadline agotado
después de conservar el readback. Once pins intactos antes/después.
Primera versión seis tests PASS; se añadió el negativo de almacenamiento y
se comprobó solo la suite propia cambiada. No se repiten baterías anteriores.

Siempre `runtime_execution_authenticated=False`,
`operational_gate_passed=False` y `native_promotion_allowed=False`.
GLSL no compilado; Blender/GPU no ejecutados. No es geometría de escena,
transporte hi-lo real, trazado, RT, red coherente completa ni ventaja.

## Crítica de Claude recibida

Respuesta PHASE-COMPENSATED-CRITIQUE-CLAUDE-001 SHA
eb138447fc5d402829b039e88285e545bd8c8554e233408e4d9e622afd3e866f.
Cinco pins verificados. Se reprodujeron SOLO ocho peores casos retenidos,
con error máximo CPU 1,1920535936e-7, y tres rechazos de longitud efectiva
negativa. No ejecutamos su writer ni repetimos 60 000 muestras.
Su barrido dirigido no constituye prueba uniforme/formal o evidencia GPU.
La cota propia contempla residuo FMA correctamente redondeado; no adopta
la afirmación de que todo residuo FMA sea universalmente exacto.

Referencias efectivas negativas son un hueco de capacidad pendiente para
una variante separada. El piloto actual conserva su dominio y negativo
de longitud, sin cambiar umbrales ni promover referencias arbitrarias.
La referencia CPU de la métrica peer está redondeada; diferencias ~1e-16
respecto de la cota ideal no se presentan como violación de dicha cota.

## Próximo paso y coordinación

Codex: integrar admisión/telemetría/supervisor real y manifiesto congelado
por job antes del único piloto escalar, cuando recursos y cola lo permitan.
Claude: acuse de crítica recibido; conservar RT-CAP-006 prioritario y
entregar reserva/envelope/rc/readback/SHA al terminar seguro. En la próxima
revisión ya pendiente, conservar un control de referencia efectiva negativa;
sin nuevo barrido, guard-review ni job paralelo por esta preparación.
