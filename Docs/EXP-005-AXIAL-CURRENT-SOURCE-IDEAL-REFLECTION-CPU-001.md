# EXP005 — AXIAL-CURRENT-SOURCE-IDEAL-REFLECTION-CPU-001

P1 propio Codex, opt-in: axial-current-guarded-source-new-ideal-minus-one-reflection-CPU-point-v1.
Base 352d341af8dd1a6e1719ecb281e64e98f02f61d6. Parent AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001 SHA 9b081c137e0ec009e4d8c34aaf6c64bdf56da9b7d9dd66e32c07cdf947d02825.

## Contrato y alcance

Verificar 398 pins heredados antes del uso. Revalidar SOLO HOST la admisión de material/source/raíces actuales y exigir igualdad de cada caso/filas con el recibo anterior. Todos los contextos, guardas de fase ORIGINAL +/-0, owner/primitiva/segmento/gauges/words/cargos y pruebas retenidas se validan antes de CUALQUIER operación nativa, incluso probe. No ejecutar suite/productor/raytrace/encoder/Horner/source anteriores ni resultado ideal de otro prefijo.

Etapa nueva CPU: decodificar cada palabra binary64 normal-o-cero y ejecutar unary minus REAL; codificar resultado. Verificar uint64 estrictamente entero y salida = entrada XOR signo como prueba, NO usar XOR para producir salida. +/-0 conservan inversión de signo sin canonicalización; subnormal/no-finito/bool de entrada STOP. Probe separado con +/-0 y +/-1 antes de main, fallo impide main.

Dos negaciones por fuente en las dos fuentes elegibles: 4 operaciones main, 4 probe. Ideal -1 es una isometría L1 hacia la fuente ideal reflejada ORIGINAL fija. Cada nodo verificado exacto añade cargo ideal_material_L1=[0,1]; conservar los catorce cargos anteriores separados y suma sin cambio. Este cero SOLO después de ejecución+identidad comprobadas; NO convertir cargo desconocido anterior en cero por defecto. Quince cargos y subtotal reflejado exportados con SHA filas/material/root/source y gauges.

material_executed y dos flags de aplicación/reflexión son TRUE solo en filas efectivamente ejecutadas. Los otros 36 flags generales son FALSE; casos/globales STOP y sin promoción. Las 17 fuentes anteriores STOP no reciben salida ni cero inventado; cargoNone. Ajuste cuota material sigue None: planes INPUT reales ausentes, ninguna política asumida, reducción/proyección/potencia/readout no ejecutados ni campo completo aceptado. Fase SOURCE no probada por esta etapa.

Modelo ideal -exp(i phase) SOLO en fase ORIGINAL exactamente +/-0. NO Fresnel, ABI material nativa, incertidumbre de escena/material, óptica física, red RT ni inferencia de escena nueva. CPU sintética/puntual con evidencia de escena retenida; no Bpyfloat32/GPU ALU/RT.

## Verificación y costes

Suite propia: nueva etapa, +/-0 y controles normales, conservación de 14+1 cargos, preflight atómico multi-caso y fallos forzados de runtime/main. Oráculo independiente stdlib sin imports producción, SHA de 402 archivos/recibos, INPUT/owner/phase/source actual y signo de cada nodo; metadatos completos en recibo.

CPU 1 hilo/afinidad1/hijo timeout60s, GPU/Blender0. HOST revalidación/IO/pins/setup/upstream/resto costes NO medidos ni cero; contar main/probe/controles separately no wall benchmark/ganador. JEV fallback LOCAL sin aval, seguridad bloqueada sin reintento. Contratos/fixtures/bounds/caps/FAILs congelados intactos.

Siguiente propia: integrar ledger material nuevo con cuotas INPUT congeladas (sin inventar planes), antes de reducción o promoción. Claude: ACK ID+SHA y SOLO artifacts YA existentes backend/guard/consumer/planes INPUT ID-path-SHA-bytes y MISMO INPUT-ABI/gauges/trabajo/salidas/costes completos; no cargas de relleno. Sharedboards/checkpoint locales SIN stage, no push/merge/SDK/DrJit/Kaggle.
