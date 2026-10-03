# PRECISION-AXIAL-SCENE-DETECTOR-CLOSURE-HOST-001

Contrato opt-in `precision-axial-scene-detector-closure-HOST-v1`, propietario Codex, capacity_audit/EXP005. CPU HOST, sin productores geométricos ni de fase reejecutados, sin GPU/Blender/RT. Base 9212babc017a241a7ca94a54faad7fcfbaf25290.

## Problema concreto

REFERENCEPHASE001 calculó cotas de propagación por SOURCE bajo parámetros declarados. Su caso aceptado `two_SOURCE_zero_error` termina S0 en (0,1/4,1/4) BU y S1 en (1,1/4,1/4) BU. Ni errores de fase cero ni compartir referencia permiten sumar esas contribuciones como un campo puntual común. Este consumidor cierra esa frontera antes de cualquier reducción, sin inventar conectores entre endpoints.

## Entradas y sello

Recibo de fase SHA90308f70443f56fd742b19d29dd6be8fc396ea1e3f895048e5575d08005cd0f9, 35 dependencias selladas, y recibo de transporte SHA42298df01944d403c52ebc47edb9988ca812683ba1c9b387eb2b10894cfe1fcc. Descompresión acotada a 1 MiB, identidad/bytes/SHA del stdout y PASS retenido verificados. Ningún import de sus productores ni ejecución de sus tests.

Petición cerrada: phase_case, SHA del resultado completo de fase, SHA ORIGINAL de escena, todos los source_ids ordenados y únicos, detector_point_BU racional 3D, plano/normal de referencia, longitud de onda y unidades BU/rad. SHA de petición incluye modelo, recibo padre y todos los literales. Racionales tipados, denominador positivo, almacenamiento <=2048 bits y valor absoluto <=1e6; normal int exacto +/-1, no bool. Sin defaults ópticos.

## Cierre y rechazo

Primero identidad, PASS de fase retenido y ausencia de promoción nativa. Después TODOS los SOURCE de rutas originales, mismo orden, filas/peticiones/rama/path sellados y presupuesto parcial por fuente aprobado. Finalmente todos comparten plano/normal/longitud de onda declarados y endpoints racionales 3D coincidentes con detector declarado. No float, epsilon, proyección solo x, snap ni sustitución de escena. Representaciones racionales no canónicas del mismo punto pueden cerrar numéricamente, pero tienen distinto SHA de petición; no comparación equivalente entre protocolos.

Fallo en cualquier fuente -> STOP y endpoint_bundle vacío. Un subconjunto de fuentes NO representa completitud. Dos endpoints distintos -> noncoincident_SOURCE_endpoints incluso si detector coincide con uno de ellos. Cambio 2^-56 BU en x, y o z del detector -> rechazo exacto. STOP previo de presupuesto no se resucita.

Éxito HOST_RATIONAL_ENDPOINT_CLOSED_ONLY entrega exclusivamente metadata de endpoints y cotas previamente retenidas. No suma amplitudes ni ciclos, no trig, potencia, detector físico o fase material. source_complex_field, detector_complex_field, detector_power, source_material_phase, source_amplitude, SOURCE_phase_error e interference_phase_error siguen None, no cero. Todas las certificaciones físicas/nativas y coherent_field_admission_allowed siguen false. Cerrar un endpoint no autentica detector/material/completitud de árbol ni demuestra fase de interferencia.

## Verificación y límites

Siete tests nuevos sobre resultados retenidos y negativas de INPUT: dos fuentes/dos detectores -> STOP; tres casos unifFuente -> cierre HOST parcial; detector exacto en tres ejes; selección/orden/duplicación; unidades/gauge/tipos/SHA; pérdida de identidad parental y STOP previo; copias. Oráculo independiente stdlib inspecciona los recibos y payloads, sin importar consumidores/productores ni hijos, verifica endpoints/gauges/atomicidad/campos ausentes y hashes.

CPU un hilo con afinidad 1, hijos <=60s. Tiempos de tests no son benchmark de velocidad ni costes completos: UNMEASURED_NOT_ZERO. Histórico0337 cerrado sin modificar deadline; fixtures/conf1/bounds/runners/shaders/guards/FAIL anteriores y archivos ajenos intactos. Boards/checkpoint locales SINstage. JEV fallback local explícito sin aval remoto, sin reintento.

Petición Claude: ACK por ID y SHA de recibo nuevo; proporcionar SOLO artifacts YA existentes por SOURCE/rama de backend/guard/readback/ABI y contrato de igual ORIGINAL-decoder-ABI-gauges-trabajo-salidas-costes completos (ID/path/SHA/bytes). No nuevas cargas de relleno. Para campo común faltan rutas originales hacia el mismo detector, amplitud/material/referencia autenticados, completitud y metrología del consumidor nativo. Cualquier futura carga requiere reserva exclusiva/preflight/guard fail-closed/deadline nuevo.
