# Decisiones JEV · P0-2 (gobernanza, 2026-10-09) · provenance=jev, remote_decision=true

- stop_criterion (confianza 0,70): ventana de 2 h por ciclo; ciclo nuevo solo con criterio OPEN o PARTIAL_ y preregistro comprometido antes de ejecutar; tres ciclos sin cambio de estado => parar e informar. Es la decision de menor confianza: revisar tras el primer uso.
- chain_disposition (confianza 0,98): cerrar la cadena con documento de cierre e indice generado; documentos en su sitio y congelados.
- single_source (confianza 0,98): acceptance_v1.json como fuente unica; README y articulo coherentes mediante prueba automatica; coordinacion/ solo registro append-only.
- readme_source_link (confianza 0,97): una linea en el README que enlaza GOVERNANCE y el JSON.
