# AXIAL-NONZERO-SOURCE-DOMAIN-HOST-001 — cota compleja SOURCE no constante

Propietario Codex, P1, opt-in HOST. Predecesor `AXIAL-NONZERO-UNIT-DOMAIN-HOST-001`, SHA `c48285861cbfffbc191e4c52796c60b7879e0cced34e15272b2c264aa75572b2`. Reutiliza sus dos cotas sobre dominios axiales enteros, sin volver a ejecutar Horner, encoder, RN puntual, geometría ni productores anteriores. No usa máximos de esquinas como prueba uniforme.

Objetivo: cota L1 del producto complejo de SOURCE fija frente a la SOURCE ORIGINAL por unidad ideal de fase ORIGINAL fija. Solo `nonexact_geometry_phase_PASS/s` y `thin_resolved/s`. No es una fuente física con incertidumbre calibrada. Los bits nominales 0,1 se interpretan como binary64 exacto, no como 1/10.

Sea U la cota L1 de unidad previamente probada. Cada componente representada tiene magnitud <=1+U y su norma L1 <=2+U. Sea e_enc la diferencia L1 de SOURCE hi-lo32 frente a ORIGINAL; es 2^-55, no cero. Las dos sumas decode son exactamente representables según las identidades de bits retenidas.

La nueva cota separa:

- Codificación SOURCE: e_enc*(2+U).
- Decode RN64: cero solo por identidad fija verificada.
- Unidad/fase frente a ORIGINAL: norma_L1(SOURCE_original)*U.
- Producto RN64: cuatro cargos de multiplicación y dos de suma. Las magnitudes de suma incluyen los errores entrantes de multiplicación; no se supone cancelación favorable.

Para cada magnitud m>0 se usa E(m)=m/2^53+2^-1075; E(0)=0. Es una hipótesis condicional de nearest-even binary64, subnormales graduales y grafo sin FMA; todos los mayorantes evitan overflow. Se preserva separada la fase (rad) de amplitud L1. El cap global INPUT no se inventa como asignación por fuente o etapa.

Los 14 STOP anteriores y tres dominios cero fuera de alcance permanecen intactos. En particular `two_sources/other` no obtiene prueba ni suma parcial promovida. Todos los casos terminan STOP: material/reflexión, reducción, presupuesto INPUT por fuente/etapa, backend ejecutado y detector siguen pendientes. No potencia, red RT, GPU, óptica física, comparación equivalente o costes completos certificados.

Validación: suite propia4PASS/30rechazos sobre cobertura, identidad SOURCE, cargos exactos y no mutación. Captura228067bytes SHA `c4bae76c83192aa5bdede07a45acfbbe1554e0b1926157df5664e9941419e222`. Comprobador independiente stdlib no importa producción, verifica pins/capturas y reconstruye los nuevos seis mayorantes; su resultado final se registra en el recibo. Hijos CPU de un hilo, afinidad única y timeout60s. Racionales grandes como cadenas decimales. Sharedboards locales sin stage; JEV fallback LOCAL sin aval remoto, no reintento de seguridad.

Incidencia preservada: primera exportación de stdout truncada por presupuesto de salida; suite PASS31.311840799986385s y hash observado conservados, pero captura íntegra inicial no disponible. Una única repetición de esta suite propia, con captura mayor guardada antes de resumir, recuperó exactamente el mismo stdout/hash en24.596864299994195s. No repetición de barridos ni productores/RN numéricos anteriores. La denegación inicial de escritura apply_patch se resolvió con la misma operación sobre rutas propias expresamente autorizadas, sin ampliar alcance.
