# Preparación de contrato: retorno inmediato por primitiva

NO CONGELADO. Especificación CPU candidata, no resultados de shader ni permiso
GPU. No altera el dominio, la triangulación o los contratos anteriores.

## Principio y estado requerido

El retorno inmediato al mismo triángulo de partida aborta la muestra; jamás se
ignora el candidato para fabricar otro camino. El estado por rama debe conservar
ID global de primitiva anterior y evento ideal de partida. Una rama inicial
usa `previous=None`; espejo, transmisión y reflexión conservan el último ID.
La identidad de objeto no sustituye el ID de primitiva: otras caras pueden
alcanzarse legítimamente, incluso si el objeto ya fue visitado.

Especificación CPU: `primitive_return_guard_v1.classify_return`. `continue`
es solo ausencia de este motivo de rechazo; las otras gates siguen obligatorias.
Entradas inválidas no tienen fallback.

## Requisitos antes de integrar un candidato nativo

1. Nuevo módulo/shader versionado, sin modificar sharedV1, nearestV2 o V3.
2. ID triangular estable ligado a un snapshot evaluado y a su SHA; transporte
   de fuentes/triángulos/óptica crudos, nunca listas de impactos calculadas en CPU.
3. Determinismo en empates del nearest global: especificar qué primitiva se
   selecciona y cómo se relacionan sus IDs tras reordenar o retriangular inputs.
4. Estado por rama GPU, incluido splitting, sin lectura intermedia del frontier.
5. Abort explícito y campo de muestra inválido: no aceptar campo parcial ni
   renormalizarlo, no confundir ledger de diagnóstico con salidas válidas.
6. Gate global de modo/campo/energía/ledger/counters y otros abortos preservados;
   las distancias y referencias de fase no cambian por aplicar esta regla.
7. Controles negativos específicos y positivos: doce candidatos retenidos,
   caso fuente, control rasante válido, objeto plegado con visita A→B→A,
   empates/caras adyacentes y estados de partida corruptos.
8. Cotas explícitas para casos aún no cubiertos: retornos sobre otra cara,
   pérdida de precisión e impactos que t_min descarta. No promocionar conf1 ni
   generalidad si esos mecanismos siguen sin gate o dominio justificado.
9. Crítica independiente y nuevo contrato congelado ANTES de compilación o
   ejecución; GPU requiere autorización nueva y gpuq/guard fail-closed.

## Evidencia presente y ausente

Presente: regla CPU rechaza doce candidatos explícitos de misma primitiva y
permite tres consultas geométricas de retorno legítimo en objeto no coplanar;
nueve tests enfocados. No son doce trazados nativos completos.

Ausente: ABI previo-primitiva GPU, compilación, flags/ledger/counters nativos,
trazado bajo empates, robustez de superficies adyacentes, controles Bpy y
rendimiento. Esta preparación no certifica reparación ni ventaja comparativa.
