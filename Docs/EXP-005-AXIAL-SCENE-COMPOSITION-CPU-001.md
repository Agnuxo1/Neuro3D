# AXIAL-SCENE-COMPOSITION-001: campo CPU contra la MISMA escena original

## Contrato opt-in y límites

Base ffe9d34. Wrapper propio, sin modificar productor, reducción, shaders,
runners, fixtures ni gates congelados. Usa contrato axial de UN espejo
pasivo unitario, fuentes separadas/grupos coherentes explícitos, rayos ±X,
YZ fijos y referencia modal terminal en su mismo plano/dirección entrante.
El radio axial adicional es supuesto CONDICIONAL de referencia co-móvil,
no error medido de GPU. BU no significa metros certificados.

La escena ORIGINAL es la referencia ideal. Primero reconstruye el certificado
de transporte hi-lo modelado de fuente/geometría/lambda/fase espejo/modo.
Luego evalúa la escena ABI decodificada mediante productor CPU congelado:
trazado racional, longitud/sqrt en intervalos, pi/Taylor, conversión binaria32
y reducción RN32 modelada. NO acepta paths/fields/bounds del llamante.

Verifica binding decodificado, todas las fuentes/filas/evidencias únicas,
exactamente tres eventos por fuente (fuente/espejo/terminal), puerto previsto,
palabras de campo y longitud efectiva que encierra la longitud decodificada
certificada. Un modo/camino sin cota devuelve rechazo ANTES del productor;
no admite resultados parciales. No es autenticación de ejecución nativa.

## Composición y gauge

Para cada camino, B_numeric procede del MISMO productor decodificado
(coeficientes, fase, conversión). B_transport=2delta_fuente+2A_original*eta
procede del certificado anterior. B_path=round_outward(B_numeric+B_transport).
Esta suma usa desigualdad triangular entre campo original ideal, campo
decodificado ideal y campo binaria32 producido; no omite términos cruzados.

Rebase explícito al gauge ideal-scene-source-gauge:binding_original, lambda
original y grupos originales. Esto etiqueta la referencia del error, no
recalcula palabras ni sustituye silenciosamente fases del productor.
La reducción congelada cobra su error representado más sum(B_path) por grupo;
intensidad usa su cota absoluta completa, incluidos términos cuadrados.
Grupos incoherentes mantienen campos separados y suman errores de potencia.
Gate final exige TANTO certificado de transporte COMO composición numérica.
NO relativo a un campo oscuro ni crédito por cancelación de fuentes.

El ABI congelado de presupuestos numéricos admite int/float, no Fraction.
El wrapper adapta cada presupuesto racional HACIA DENTRO a binaria64:
si redondea arriba, nextafter hacia cero. Se retienen solicitado y efectivo.
Nunca amplía tolerancias; un presupuesto demasiado pequeño puede ser cero.
No se cambió ningún módulo congelado para aceptar tipos adicionales.

## Evidencia nueva y fallo preservado

Ocho pruebas PASS rc0/1,569615s, un hilo/hijo60s,26pins verificadas.
Diez casos completos/rechazados y cinco controles de rechazo retenidos.
SOLO nuevas entradas de un espejo al productor, no suite/barridos005/006
ni repetición de antiguos MZI. Los imports reutilizan constructores, no tests.

- Longitud5/8/lambda1/8: oráculo exacto campo original=-.1.
- Longitud21/32/lambda1/8: oráculo cuarto de ciclo campo=-i*.1.
  Errores reales de campo/potencia RN32 encerrados por las cotas compuestas.
- Espejo x=.1/fase=.1/fuente=.1: fuente2^-54 y cargo fase positivo separados
  del error numérico propio; bindings original/decodificado diferentes.
- Fuentes posiciones0 y.125, amplitudes.1 y-.1+2^-30: original=-2^-30,
  suma RN32=0. Pérdida COMPLETA del residual oscuro, error absoluto2^-30
  dentro del presupuesto1e-4. PASS absoluto NOdemuestra precisión relativa.
- Mismas fuentes con grupos distintos permanecen separadas.
- Fasebudget0/exactitudfuente0/underflow2^-150 siguen FAIL global aunque
  la composición numérica absoluta pase; no ocultar error previo.
- Fuente.1*2^25: FAILcampo e intensidad NUMÉRICOS, además de fallo de
  intensidad de transporte anterior. Sin ampliar budgets para hacerlo PASS.
- Modo incorrecto devuelve field_values_computed=false sin ejecutar productor.
- Subnormal2^-149 rechaza perfil frozen normal-or-zero; sin hipótesis FTZ.
- Tres alteraciones SINTÉTICAS de salida propia (binding/cobertura/longitud)
  rechazan con razones específicas; NOauditoría de artifacts nativos ajenos.
- Adaptación de presupuesto verificada inward, incluido racional<minbinary64.

Primera ejecución rc1/1,173149s: cinco errores por pasar Fraction al ABI de
presupuestos int/float congelado. Raw completo y huellas previas preservados.
Se corrigió SOLO adaptador nuevo, inward; se precisaron razones en tests de
alteración y añadió test del adaptador. Ningún umbral/frozen se modificó.

## Alcance de resultados y coordinación

field_values_computed=true SOLO donde se ejecutó evaluación CPU sintética
desde escena. No Bpyfloat32, GPU ALU, driver/libm/FTZ/reasociación, aritmética
de detección nativa, RT, óptica física, red general o ganancia activa.
native_promotion_allowed=false y execution_authenticated=false siempre.
Ni ganador, ventaja/eficiencia ni equivalencia de trabajo/costes demostrados.
Este wrapper no alimenta caminos CPU a GPU ni sustituye escena por U/GEMM.

GPUq leído09:58UTC: holderfilament:cv0_ema y dos tickets existentes intactos;
su snapshot es histórico, NOtelemetría/preflight/admisión. Sin GPU/Blender/
reserva/cancelación/peerwriter. Ventana nocturna histórica cerrada intacta.
JEV bloqueado: fallback local identificado, sin reintento ni aval remoto.
Skills contrato acotado/reuso guiaron composición y pruebas nuevas.
Boards/checkpoint locales SINstage; versionar solo cuatro archivos propios.

Claude: acuse AXIAL-SCENE-COMPOSITION-001 por ID/SHA; SOLOgeometry/limbs/
bindings0337 YAexistentes y contrato igualtrabajo/costes completos. No nueva
GPU/suite/barrido/guardreview. FAIL0337 y peticiones006/013 permanecen.
Siguiente: evaluación de precisión relativa/campo oscuro con presupuesto
EXPLÍCITO, o evidencia nativa existente ligada a escena; no promover CPU.
