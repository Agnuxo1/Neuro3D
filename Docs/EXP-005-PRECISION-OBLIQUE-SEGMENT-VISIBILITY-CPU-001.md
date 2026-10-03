# EXP005 — Visibilidad exacta de segmentos declarados (CPU)

Unidad PRECISION-OBLIQUE-SEGMENT-VISIBILITY-CPU-001, base b9da14556d3954f2347acb10f1fa2d04507b1b66. Modelo opt-in
precision-oblique-segment-visibility-CPU-v1. NO cambia runners/shaders/fixtures,
conf1 ni cotas. CPU racional, no Bpyfloat32, GPU ALU/RT u óptica física.

## Contrato y aceptación

La API pública audit(model, request) recibe solamente un selector cerrado:
case, parent_sha256, intent=SEALED_DECLARED_SEGMENT_VISIBILITY_ONLY.
Lee los caminos sellados de LENGTH001 (SHA139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e)
y verifica los pins retenidos por EQUALWORK001 (SHA2e9eee5cf10def39dcf882044fe3c2e8678aeb260cc7d1a1c2f7fa57d78e8ae0).
No acepta override de evidencia, no ejecuta el productor geométrico ni sqrt/RN.

Conserva los24 STOP parentales antes de leer caminos. En cuatro casos admitidos
valida escena ORIGINAL/literal, dos SOURCE completas, continuidad, extremos,
dirección entrante/reflexión racional, longitudes al cuadrado y certificados
de intervalos ya capturados, todas las cotas SOURCE y relativa. Comprueba ambos
segmentos de cada SOURCE frente a TODAS las primitivas. Calcula t normalizado
sobre el segmento cerrado [0,1] y coordenadas baricéntricas exactas.
No hay epsilon ni veto global/por objeto. t=0 solo se omite para la primitiva
exacta anterior en el segundo segmento; t=1 solo se permite para el destino
exacto. Otras intersecciones interiores, vértices/aristas inclusivos, contacto
con otra cara o empate de destino bloquean atomicamente toda salida.
Coplanaridad se rechaza conservadoramente incluso si habría que demostrar
separación lateral: no se declara cobertura general de coplanares.

Solo emite cuatro segmentos conjuntamente y el ledger completo. El diagnóstico
parcial queda disponible en STOP, pero visibility_rows=[] y admitted=0.
Cada decisión incluye SOURCE, segmento, primitiva, t y baricéntricas racionales.
Un objeto compartido NO justifica omitir otra cara. El hueco2^-60 BU se conserva
exactamente; t normalizado NO es distancia BU ni tiempo. No se añade tolerancia.

## Evidencia independiente y límites

Suite:28 casos sellados (4 admitidos/24 STOP),12 NUEVAS escenas declaradas
sintéticas con un triángulo adicional del mismo objeto sobre geometrías de
hueco1 y2^-60,4 alteraciones de continuidad/certificado/binding/cota,
más4 selectores inválidos:44 corridas,6 admitidas/38 STOP +4 selectorSTOP.
Los dos controles con obstáculo fuera del segmento pasan; otros10 obstáculos
internos, contacto en vértice, contacto inicial, duplicado de destino o
coplanaridad dan STOP. El obstáculo interior afecta inicialmente solo a S0:
aun así no se publica ninguna salida parcial de SOURCE.
Estas nuevas escenas llevan digest nuevo explícito y caminos candidatos
copiados para comprobar visibilidad; NO son inferencia/replay ni observaciones
GPU/Blender ni sustituyen la escena sellada. _audit es auxiliar privado de QA.

Oráculo separado no importa productor/core: resuelve t,u,v por determinantes
de Cramer (distinta fórmula del Gram/baricéntricas del módulo), valida cada
fila diagnóstica, cobertura4*triángulos/2 previous-zero/4 endpoints cuando
admite, fuentes, casos/censos, pins y API pública sin override.
Errores iniciales, si aparecen, se preservan en recibo sin relajar aceptación.

Esto certifica consistencia de visibilidad en escenas/caminos CPU DECLARADOS,
no autenticación de escena física, completitud de ramas/material/amplitud,
barrier/fence/readback o backend nativo. No crea nuevo GPUABI/backend.
Promoción/GPUlaunch/physical siempreSTOP/False; costes UNMEASURED_NOT_ZERO,
sin ganador/ratio. Longitud/ref/fase y cotas del padre no se amplían.
Contrato pareadoV1/RT-AUD001 intactos;16Mvs1M no comparación equivalente.

CPU1hilo, afinidad1, hijo<=60s. JEV LOCAL sin aval ni retry por bloqueo de
seguridad; no nueva telemetría/elevación/bypass, GPU0/Blender0/compile0/RN0.
Cognición extendida favorece captura reutilizable; desarrollo acotado obliga
revisión y oráculo independiente. Cinco archivos propios revisados/versionados;
tableros/checkpoint LOCAL SINstage. Pedir solo artifacts existentes a Claude
por ID/path/SHA/bytes e igual escena/trabajo/costes completos; sin repetir cargas.
