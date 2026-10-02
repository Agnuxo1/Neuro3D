# EXP005 — Enlace de linaje del certificado completo axial a eventos HOST

ID AXIAL-TREE-LINEAGE-HOST-001. Base36a947d8cb1f72c67ac3f743b4b926c665416438.
Opt-in CPU stdlib, no nuevo trazador ni cambio de frozen.

## Qué se reutiliza

Certificado completo AXIAL-TREE-COMPLETENESS-001, SHA
d895ef448dee2a4bb8657da1b6bd3f36635b91f4b8137ae29d194664c6db7d9e.
Fue contrastado independientemente antes: árbol finito source→M→D absorbente,
cuatro primitivas enumeradas por transición, X compartida/YZ exacta, sin epsilon ni snap.
No se vuelve a construir ni revalidar barycentría/trazado. Se conserva la procedencia de esa prueba.
La entrada pública nueva acepta sólo casos retenidos y modelo explícito, no pruebas/eventos/caps externos.

## Comprobaciones nuevas

223 pins heredados, recibos stdout e INPUT fresco. Snapshot ORIGINAL completo,
ABI y sourceorder deben ser idénticos al certificado antiguo.
Reconstruye los bytes serializados de triángulos/fuentes desde el ABI retenido para comparación exacta.
Events debe llevar MISMO packetSHA/sceneSHA/ABISHA/nombre/sourceorder que INPUT.
CertSHA y geometrycaseSHA ligan la prueba retenida a su geometría, sin alias por sólo nombre/snapshot.

Tres nodos source/reflect/detect, parents/hijos y detector sin hijos;
direcciones ±X, selección M primero/D después, primitivas y propietarios exactos.
Compara particiones completas (miss/behind/chosen/departure/later), con IDs estrictos sin boolalias.
Compara raíz positiva y clearance racional antiguos con endpoints signed512 actuales por lectura exacta.
Certificado de salida del espejo debe derivar del primer evento aceptado, mismo ID/source/packet.
No calcula nuevas intersecciones, barycentrías, productos ni trigonometría.

## Gates y controles

13 casos originales:8 matches de certificado completo CPU (9 fuentes) y5 STOP geometría conservados.
4 controles posteriores de metadata no tienen recibo events para su paquete exacto: STOP.
Aunque compartan geometría, no se les presta la prueba antigua por alias.
Los 17casos/19fuentes conservan exactamente5productos numéricos evaluados y14STOP previos,
incluidos fallos de fase: MATCH del árbol NO rescata esos gates ni certifica presupuesto de campo.
Prueba restricción cerrado M/D ideal; NO árbol general BS/refracción/modos ni óptica física.

5 tests nuevos y oráculo independiente sin imports producción:
bytes/SHA/linaje/selector/partición/rangos/STOP más23rechazos.
Los controles de árbol falsificado se rehashean deliberadamente:
SHA autoconsistente no basta para cambiar hijos, selector, raíz o sourceID.
Los controles NO relajan caps/radios/fixtures ni reescriben resultados retenidos.

## Límites y costes

tree_lineage_matches_restricted_CPU_only indica REUTILIZACIÓN de prueba matemática CPU existente
más comparaciones nuevas de linaje/bytes/endpoint, no ejecución nativa ni nueva prueba de aritmética signed512.
accepted_complete_geometry, accepted_full_field_pipeline y amplitude_budget_accepted siguen FALSE.
Sin native/GPU/ALU/Bpy/RT/admisión/auth/coherencia física/suma/reducción/detector.
Lecturas/hash/descompresión/reconstrucción byte/rational endpoint checks son trabajo CPU EXTRA,
NO costes completos ni comparación de velocidad/eficiencia/energía.
Skills cognición/desarrollo aíslan el enlace nuevo y mantienen evidencia previa por SHA.
JEVsecurityBLOCKED fallbackLOCAL sin aval/retry. Boards locales SINstage.
