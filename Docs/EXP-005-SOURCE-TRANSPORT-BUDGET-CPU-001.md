# Presupuesto hi-lo de fuentes ligado a escena, solo CPU

P1 / SOURCE-TRANSPORT-BUDGET-001-CODEX. Módulo nuevo opt-in; no cambia
productor, packer, split, shader, contrato ni fixtures congelados. Usa el
mismo scene_binding y las posiciones reales3/7 de cada fila8 del ABI.
Conserva orden, ID, grupo coherente y gauge por escena; no recibe campos
terminales ni cotas elegidas a posteriori. Es una capa de entrada de fuentes,
NO un backend de inferencia ni un certificado completo de precisión.

Separa, con racionales exactos:

- Error de suma exacta de los dos limbs float32 frente a la entrada binary64.
- Redondeo adicional del modelo de reconstrucción CPU64.
- Error total firmado por componente y normaL1 por fuente, sin acreditar
  cancelación entre fuentes distintas.

Presupuestos absolutoL1 (unidades field_reim) y relativoL1 (adimensional)
son explícitos y obligatorios. Para fuente cero, error relativo0 solamente
si error absoluto0. Un PASS es únicamente del transporte CPU de esa fuente;
no reemplaza los gates ópticos históricos ni los umbrales de otros runners.

## Verificación acotada

Seis tests PASS, rc0, 0,3153555s, un hilo y timeout de hijo60s. Tres escenas
retenidas de SCENE-CONVERSION-001 se leen y su binding coincide exactamente;
no se vuelve a ejecutar productor/tracer ni barridos PRECISION005/006.
Cinco pins congelados verificados, incluido el FAIL LEDGER-INTERVAL-001.

| Entrada/caso | Resultado de esta capa |
|---|---|
| Fuente ordinaria .1 | Error firmado -2^-55; presupuesto de exactitud0 falla. |
| Fuente alta .1*2^25 | Error firmado -2^-30; no implica recuperar el cast final del detector. |
| Dos fuentes casi oscuras retenidas | Errores -2^-55 y -3*2^-55 separados, suma firmada -2^-53; no cancelar presupuestos por fuente. |
| 2^-150, NUEVA frontera CPU | Hi=lo=0: pérdida100% relativa aunque pase presupuesto absoluto2^-149. Rechazo numérico conservado. |
| 2^-149, NUEVA frontera CPU | Limbuint32=1, reconstrucción exacta CPU; necesita semántica subnormal nativa no acreditada. NO admite GPU. |

Cero, signo de cero y canal imaginario tienen controles separados. NaN,
infinito, bool, overflow del split, IDs duplicados, grupos incompletos y
presupuestos malformados rechazan. Los casos subnormales son nuevas entradas
CPU dentro del packer existente: no se cambian bounds/conf1 ni se envían GPU.

`native_admitted`, `native_promotion_allowed`, `GPU_executed`, `scene_traced`
y `terminal_bounds_certified` permanecen false, aun con PASS numérico.
Geometría/autointersección/huecos, longitud/referencia/lambda/fase,
amplificación por coeficientes, reducción/detección, RN/FTZ/FMA/dtype
nativos, RT y óptica física están fuera de este resultado. No se acredita
la causa del FAIL de captura0337 ni se cambia su intervalo o umbral.

## Continuidad

Fallback local sin aval JEV; no reintentos del canal bloqueado. GPU ocupada
por holder ajeno cv0_cons observado; no hay reserva, cancelación ni Blender.
La skill de implementación mantuvo la nueva capa separada y la de cognition
reutilizó escenas retenidas con fracciones exactas, sin repetir el productor.

Claude: acuse por ID/SHA. Si YA existen artifacts de la captura0337 con limbs
de fuentes, bindings y semántica efectiva de reconstrucción, incluirlos en
la petición pendiente; no generar nuevaGPU/suite/barrido/guardreview.
Siguiente integración: cargar estos errores de entrada por ID de fuente
antes de componer coeficientes/fase, con contrato propio, sin atribuirlos
silenciosamente a la precisión nativa o al antiguo productor ideal.
