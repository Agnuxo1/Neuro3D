# EXP005 — potencia HOST uniforme de grupos completos singleton

ID AXIAL-SINGLETON-POWER-DOMAIN-HOST-001;base3da8d7d083c6ca1f252800f860af224270277c6a.
Acuse SINGLETON-GROUP-DOMAIN-HOST001/SHAd24f30f6ae6155bc628755883237230bb1fb32e748f40b5ddd4810d0f905b19b.

## Contrato opt-in

Modelo axial-complete-singleton-uniform-power-retained-HOST-v1.
Sólo API de selección única/acotada de casos retenidos + modelo explícito:
no valores/cupos/escenas/recibos ni fuentes parciales del caller.
288 pins heredados;292 con cuatro propios. INPUT fresco y mismos gauges,
partición completa, ABI, ORIGINALsnapshot, fuente/domain, reducción y potencia.

Dos grupos completos positive/D/g ynegative/D/g ya constantes sobre dominio
axial restringido y fuente fija. HOSTpower es módulo cuadrado re^2+im^2:
unidades amplitud ORIGINAL al cuadrado, NO energía/potencia calibrada en watts.
Se reutilizan ocho recibos con tres nodos RN64 separados (sin FMA).
Se comprueban 24 celdas retenidas RN-even (8 nodos cero exacto,16 normales),
operandos/grafo/fracciones/hashes/cargos. NO floatcast, RN nuevo, productor,
encoder, suma, campo o potencia ejecutados de nuevo.
Cero sólo exacto +0 en este grafo restringido: no ocultar underflow/FTZ/-0.
Los controles sintéticos RN tie-even no son pruebas físicas ni cargas de escena.

Constancia uniforme deriva del certificado previo del grupo COMPLETO y su
fuente, NO de interpolación de esquinas. Misma copia y fuente/reflexión ORIGINAL
fija; para cada parámetro del dominio el grafo recibe exactamente las mismas
palabras y produce el mismo recibo HOST.

## Referencia y errores separados

ORIGINAL es la fuente binaria64 ORIGINAL fija también negada, no nominal 0.1.
P0 exacta=12980742146337070512478121581609/
1298074214633706907132624082305024;P0>0.
Error absoluto uniforme exacto HOST respecto a P0=
7926335344172073/1298074214633706907132624082305024
(aprox6.106226635438361e-18).
Error relativo exacto usa P0, SINepsilon:
7926335344172073/12980742146337070512478121581609.

Se conserva por separado fieldL1B=1/2^55 y cargo powerRN=
45035996273705/81129638414606681695789005144064.
La envolvente antigua 2*max(|HOSTre|,|HOSTim|)*B+B^2+RN es idéntica;
no se rebaja una cota anterior ni cambia umbral para obtener PASS.
El error exacto cabe en esa envolvente y en su referencia lower ORIGINAL.
Estas igualdades NO aceptan un presupuesto ni una etapa downstream.

## Bloqueos

NUEVO restricted_complete_singleton_power_error_to_ORIGINAL_proved sólo dos.
Missing source/reduction/power INPUTallocations permanece STOP también en ellos.
Planes syntheticINPUT antiguos se usan sólo como recibos; gates/PASS_PARTIAL
NO heredados.15 grupos STOP,14unitSTOP y2nonzero intactos;two_sources other
sin dominio y sin suma parcial. Zeroabsolute yzerorelative FAIL antiguos
preservados con hash/status. Detector/fullpipeline/native/signzero/physical/
coherence/GPU/RT/auth/generaluniformpower siguen falsos.
No validación de detector físico, Fresnel/polarización, incertidumbre de amplitud,
eficiencia ni motor ganador; no U/GEMM sustituyendo escena.

## Verificación y seguridad

Cuatro tests propios stdlib,40rechazos;primera suite4PASS0.5944978999905288s.
Captura100739bytes SHA2f4d1d7f07942257f4f449b9542eef4e4c77db666fed0ca5e84e2cbbff4a7537.
Oráculo stdlib independiente SINimports producción verifica pins/INPUT/
referencia/cadena/celdas/errores/STOP/FAIL;capturas ytimings en reporte.
CPU1hilo/afinidad1/hijo<=60s;sin GPU/Blender/SDKDrJit/Kaggle/pushmerge.
JEVbloqueado:LOCALsinaval/retry/elusión.
Cinco propios revisados en commit local;boards/checkpoint locales SINstage.
Runners/shaders/contratos congelados/fixturesconf1-v0-v4-0119-0315-nearestV2/
radios/cupos/FAIL intactos;0337CERRADOdeadline histórico intacto.
GPU futura sólo exclusividadClaude/telemetría/guardfailclosed/NUEVOdeadline/
todoslímitesoriginales. Metadata grande decimalstrings ycaptura original exacta;
discrepancia de resumen ancestro preservada,no nuevos números binary64 truncados.

## Continuidad

Siguiente propia: contrato explícito de readout/detector HOST restringido y
conservación de referencias/unidades/partición, sin validar física ni native;
restantes dominios y allocations por separado. No repetir cargas por relleno.
Claude ACKesteID+reportSHA y SOLO artifacts YAexisting backendguard/certificados
matching INPUT-scene-ABI-source-gauge yigualtrabajo-salidas-costes completos.
