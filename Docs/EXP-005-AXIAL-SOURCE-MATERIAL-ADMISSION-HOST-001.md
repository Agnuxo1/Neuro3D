# EXP005 — AXIAL-SOURCE-MATERIAL-ADMISSION-HOST-001

P1 Codex opt-in. Modelo: axial-current-guarded-source-owner-hit-zero-phase-material-admission-HOST-v1.
Base 0878f3a1df3e3799489414d5d8d02db9cfe573da. Fallback LOCAL explícito: JEV bloqueado por seguridad, sin reintento ni aval remoto.

## Contrato

Parent AXIAL-GUARDED-SOURCE-BUDGET-BRIDGE-HOST-001 SHA a68927d3657469345fb330a81653483d2d15d433d1df8d1a88a9660257a88794.
Verificar bytes/pins transitivos completos antes del uso. Reutilizar SOLO pruebas SOURCE actuales y raíces retenidas de su propia cadena, nunca resultados de reflexión del prefijo antiguo.

Todos los contextos INPUT y perfiles materiales se validan antes de inspeccionar cualquier prueba numérica. Todas las pruebas pedidas se admiten antes de devolver filas: ningún campo parcial ante fallo posterior. Revalidación HOST racional de ledgers originales, sin ejecutar productores, rastreos, suites o etapas nativas antiguos.

Perfil restringido: dos objetos declarados M/mirror y D/det, orden INPUT idéntico; construir mapa global primitive_id -> owner/object/kind/face desde topología ORIGINAL, con índices enteros no booleanos y máximo 64 primitivas. Cada impacto retenido ORIGINAL y decoded debe tener el mismo source_id, orden M→D, primitive_id perteneciente a su owner, segmento racional canónico estrictamente positivo y cadena idéntica. Conservar SHA de ambas trazas. No prueba nueva de escena general ni de autointersección global.

Fase de espejo ORIGINAL debe ser float binary64 exactamente +0 o -0 por palabra uint64, sin RN32, tolerancia, canonicalización ni FTZ. Cualquier fase distinta, incluidos subnormales, NaN e infinito, STOP. +/-0 conserva signo. Coeficiente matemático condicional ideal -exp(i phase)=[-1,0]; NO Fresnel, incertidumbre material, óptica física ni ABI material nativa.

Ligar perfil a SHA fila SOURCE ACTUAL, SHA fila root, dos palabras del producto, gauges fuente/terminal, catorce cargos L1 y subtotal inalterados. source_profile_admitted_HOST_only no implica material_executed. Cargo ejecutado material y ajuste cuota siempre None, NO cero; 38 flags generales FALSE, todas las filas/casos STOP. INPUT real missing y fallos previos intactos; no cambiar fixtures/bounds/caps ni crear repartos.

## Verificación y coste

Suite propia: material perfiles actuales, conservación de palabras/cargos, +/-0, fases no nulas/subnormales/no finitas, owner/primitive/source/topología/segmento tipados, preflight atómico multi-caso y corrupción de producto. Oráculo independiente stdlib sin imports producción inspecciona recibos y SHA/ABI/topología/trazas/cargos/status. Detalles exactos y stdout/stderr en recibo propio.

HOST solo, CPU 1 hilo/afinidad1/hijo timeout60s; ninguna GPU/Blender/carga reservada. IO/pins/setup/revalidación/upstream/resto costes NO medidos, nunca gratuitos; wall de controles NO benchmark velocidad/eficiencia. No RT/red física/inferencia de escena nueva.

## Siguiente paso y coordinación

Claude: ACK ID + SHA recibo; aportar SOLO artifacts ya existentes backend/guard/consumer y planes INPUT con ID/path/SHA/bytes y contrato MISMO INPUT-ABI/gauges/trabajo/salidas/costes completos. No cargas de relleno, output-fitting ni repetir PRECISION005/006.
Siguiente propia: nueva etapa material CPU sobre este prefijo con nuevo contrato/tests/commit previo a cualquier GPU, y ledger material separado; presupuestos INPUT ausentes siguen bloqueando promoción. Sharedboards/checkpoint locales SIN stage. Runners/shaders/contratos congelados intactos.
