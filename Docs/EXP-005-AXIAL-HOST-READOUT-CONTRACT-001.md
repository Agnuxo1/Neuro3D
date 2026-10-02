# EXP005 — contrato opt-in de salida HOST, no detector físico

ID AXIAL-HOST-READOUT-CONTRACT-001. Base a12f3b4bd775f405a94ed035b81444842003e944.
Acuse AXIAL-SINGLETON-POWER-DOMAIN-HOST-001 / SHA
6fc6191ae3fed5ccaa52df1922df3c7947950b234d064f2c6ede1c39f6db96d2.

## Interfaz y alcance

Nuevo modelo axial-HOST-readout-retained-power-contract-v1.
API validate_contract(plan, model=MODEL): exige modelo opt-in, esquema exacto,
17 salidas ordenadas por caso/grupo completo, snapshot ORIGINAL, INPUT, escena,
ABI, contrato de grupos, fuentes, gauges y referencias terminales/fase.
No modifica ni ejecuta runners/shaders/contratos congelados.

make_proposed_contract devuelve exclusivamente SYNTHETIC proposed INPUT:
es una propuesta declarativa, NO un INPUT que estuviera en los recibos de escena.
La aceptación del esquema no admite ejecución, presupuesto, detector ni comparación.
Se comprueban recibos existentes y hashes; no encoder, RN, copia, suma, potencia,
readout, Blender ni GPU nuevos. Los dos recibos disponibles no son lecturas nuevas.

| Elemento | Contrato HOST v1 |
| --- | --- |
| Observable | Módulo cuadrado del campo de cada grupo coherente COMPLETO |
| Unidades | Amplitud ORIGINAL al cuadrado, no watts ni joules |
| Readout declarado | Identidad de palabra uint64 retenida; sin redondeo nuevo |
| Referencias | Fase de cada fuente y plano/modo terminal ORIGINAL explícitos |
| Grupos | Salidas separadas; no suma entre grupos ni integración de detector |
| Ganancia, offset, exposición, área, calibración, cuantización | Ausentes; introducirlos exige otro contrato/modelo |
| Allocations INPUT | Ausentes; no inventadas ni aceptadas por esta propuesta |
| Costes completos | Once etapas explícitas UNMEASURED; null no significa cero |
| Comparación de motores | STOP sin igual trabajo/salidas autenticados y costes medidos |

Costes: ORIGINAL_ingress, scene_transport, source_encoding, reflection, reduction,
power, readout, upload, execution, download, host_validation.
Esta taxonomía de contabilidad no dice que todas las etapas ejecuten GPU ni las
duplica: al medir, deberán definirse fronteras no solapadas en un futuro contrato.
Este modelo v1 NO acepta mediciones ni guard/reservas inyectados y NO concede carga.
No estima velocidad/eficiencia, no autentica guard, reserva o deadline.

## Bloqueos preservados

Dos proofs de potencia restringida ya existentes: negative/D/g y positive/D/g.
Quince grupos aguas arriba no probados, 14 unit STOP y dos dominios nozero intactos.
Las 17 salidas siguen STOP: también las dos con proof carecen de allocations
source/reduction/power/readout INPUT y de recibo ejecutado de salida.
two_sources conserva s+other sin salida parcial.
Zeroabsolute y zerorelative FAIL preservados; ni caps, radios, conf1 o umbrales cambian.
Conserva los errores ORIGINAL y cargos de potencia del predecesor, sin refinarlos.
No prueba incertidumbre óptica física, detector, native, RT, fullpipeline ni
autenticación de ejecución/coherencia. No sustituye escena por U/GEMM.

## Verificación

Una suite stdlib nueva de cuatro tests y 43 rechazos: PASS primera ejecución,
4.075940900016576s, afinidad CPU1, un hilo, hijo <=60s.
Captura 79968bytes SHA
6d8914654f26fd9ba19c35033f532f25e73b3b171d0895f06b58b34bd65c4415.
Rechazos de partición/fuentes parciales, gauges/referencias, escena/snapshot/ABI,
unidades físicas, redondeo/ganancia/exposición/área/calibración, presupuestos
inyectados, costes falsos/omitidos, equivalencia/guard/admisión y SHA alterado.
Oráculo stdlib independiente sin imports de producción valida captura, 297 pins
(293 heredados y cuatro propios), INPUT fresco y las salidas/gates declarativas.
No vuelve a ejecutar productores, suites antiguas ni barridos numéricos.

## Continuidad y seguridad

Próximo paso real: exigir al backend existente el mapping de salidas completas
y recibos/calibración/allocations/costes con iguales INPUT, fuentes y referencias.
No encadenar nuevas pruebas de identidad ni repetir cargas sólo para rellenar.
Claude: ACK ID+SHA y artifacts YA existentes de backend/guard, contrato de igual
trabajo/salidas/costes completos. No duplicar RT/capacity de Claude.

Sólo CPU ligera propia; GPU futura requiere coordinación exclusiva por job,
telemetría, guard fail-closed, nuevo deadline y todos los límites autorizados.
0337 cerrada y deadline histórico intacto. JEV bloqueado: fallback LOCAL
explícito sin aval remoto, sin reintento/elusión. Sin SDK/DrJit, Kaggle, push/merge.
Versionar cinco propios revisados; cuatro boards/checkpoint locales SINstage.
Fixtures conf1/v0/v4/0119/0315/nearestV2 y archivos ajenos intactos.
