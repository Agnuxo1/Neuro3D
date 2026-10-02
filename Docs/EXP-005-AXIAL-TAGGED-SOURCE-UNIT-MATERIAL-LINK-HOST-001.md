# EXP-005: enlace puntual A etiquetado -> UNIT -> material retenido

ID: AXIAL-TAGGED-SOURCE-UNIT-MATERIAL-LINK-HOST-001. P1, Codex capacity_audit.
Base da1a26d41b1b81a051b2b56cc0f6f320628404c1.
Modelo opt-in axial-tagged-SOURCE-UNIT-material-retained-link-HOST-v1.

Contrato: INPUT completo cerrado a artifacts SHA del consumidor POINT anterior y salidas bare/material. Valida TODAS las filas antes de emitir una. Comprueba contexto ORIGINAL/ABI/gauges/orden, identidad SOURCE y igualdad BITWISE de operandos A (incluidos signos de cero), UNIT y nodos de material. No importa ni ejecuta encoder, decoder, productores o runners congelados.

Sólo dos SOURCE tienen producto/material retenidos y operandos idénticos. Reutilizar su evidencia no certifica una ejecución nueva del programa etiquetado. Los otros dos SOURCE de two_sources no tienen resultados: ledger None, STOP. Los 17 casos/19 SOURCE sin INPUT siguen sin enlace. Dos cajas guard-negativas permanecen negativas.

Sea E el cargo de encoding A, D el cargo del decoder elegido, L la norma L1 del UNIT representado, S la norma L1 de A ORIGINAL y u_j los once cargos del UNIT hacia el mismo ORIGINAL. El ledger separa:
E*L + D*L + sum_j(S*u_j) + N_producto + M_ideal.
Cada cargo se cuenta UNA vez. Se exige E+D igual al radio POINT anterior, sum_j u_j igual a su cota retenida, igualdad exacta de los quince cargos con material retenido y conservación del total. N_producto es el cargo RN64 retenido con operandos idénticos; M_ideal=0 sólo después de verificar los dos nodos unary-minus exactos y el perfil ideal [-1,0]. No aplica a Fresnel ni material físico.

Referencia: A ORIGINAL fijo * exp(i fase del camino ORIGINAL exacta) * menos uno ideal. No sumar cotas angulares de A y UNIT. Este consumidor NO calcula fase ni compara cuotas: phase_bound_rad/phase_quota_fits None. No confundir enlace puntual con cota uniforme, admisión de escena, grupo, RT u óptica. 38 gates generales FALSE, grupo0. Cambios de scope, cuotas extra, gauges, bits, cargos o resultados se rechazan atómicamente antes de emitir.

Pruebas nuevas de conservación y controles negativos, una CPU/afinidad1/hijo<=60s. Verificador independiente stdlib lee artifacts SHA y recomputa normas, cargos y correspondencias sin importar producción. Fallos se retienen antes de cualquier reparación. Costes IO/setup/hash/upstream/pipeline UNMEASURED, no cero; tiempos de pruebas no throughput/eficiencia.

JEV bloqueado: fallback LOCAL sin aval ni reintento. GPU/Blender0, sin instalación SDK/DrJit, Kaggle, push/merge. Fixtures/guards/umbrales congelados intactos. Tableros/checkpoint locales SINstage. Skills: cognición extendida reutiliza evidencia lossless SHA sin replay; desarrollo fija contrato cerrado y regresiones.

Siguiente: un backend nuevo que quiera ejecutar debe declarar este decoder/graph/INPUT y aportar su propia salida/costes bajo reserva y guard autorizados; no sustituir estos resultados retenidos por una ejecución nueva. Solicitar a Claude sólo artifacts YA existentes de MISMO INPUT/decoder/ABI/gauges/trabajo/OUTPUT y costes completos ID/path/SHA/bytes.
