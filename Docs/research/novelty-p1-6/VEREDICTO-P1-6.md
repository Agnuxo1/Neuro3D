# Veredicto de novedad · P1-6

Ejecución: 2026-10-09, siguiendo `PROTOCOLO-BUSQUEDA-P1-6.md` (no modificado). Datos: `SEARCH-LOG.json`, `EXTRACCION-P1-6.json`, `METODOS-CERCANOS.md`.

## 1. Cobertura de la búsqueda

- arXiv: 12 de 12 consultas del protocolo con respuesta (3 reintentadas tras un HTTP 429 de límite de tasa). Enviadas como AND de términos, devolvieron 0 a 6 resultados cada una; se añadió una variante complementaria con términos nucleares (12 consultas, 2 a 48 resultados). Se descartó una tercera pasada defectuosa (codificación del operador), sin uso.
- OpenAlex: 12 de 12 con respuesta, 50 resultados por consulta.
- Semantic Scholar: una sonda, HTTP 429, no se insistió. No aporta resultados.
- GitHub (`gh search repos` y `gh search code`): las 4 frases del protocolo dan 0 resultados en ambas modalidades. Con 6 variantes relajadas (complementarias) aparecen simuladores genéricos de redes ópticas y bibliotecas de óptica diferenciable (por ejemplo, neuroptica, ONNet, pado, optiland), solo por nombre y descripción. Ningún repositorio observado combina red óptica, escena de Blender y certificados de intervalo. No se leyó el código.
- Resultados únicos reunidos: 650 (arXiv y OpenAlex). 153 cumplen el criterio de inclusión (al menos dos grupos de términos). Se suman los 106 registros ELIGIBLE de `screening.json`: 105 localizados por identificador o título (4 de ellos sin resumen utilizable) y 1 no localizado (R031); 7 coinciden con resultados de las consultas. Total con criterio del protocolo: **252 registros**. Tras la revisión manual se añadieron **6 registros fuera del criterio mecánico** (ver más abajo): **258 en el conjunto ampliado**.

## 2. Conteo por componente

Marcas de título y resumen. "Sí" cumple la definición del componente; "parcial" se acerca sin cumplirla.

| Componente | Sí (252) | Parcial (252) | Sí (258 ampliado) | Parcial (258) |
|------------|----------|---------------|-------------------|---------------|
| C1 red óptica coherente | 79 | 67 | 83 | 68 |
| C2 geometría entrenada | 2 | 26 | 7 | 26 |
| C3 certificado de intervalo | 0 | 2 | 0 | 2 |
| C4 escena capturada | 0 | 21 | 0 | 22 |

No verificable (solo título o sin resumen): C1 3, C2 5, C4 5 registros.

## 3. Conteo por combinación

| Combinación | Sí (252) | Sí o parcial (252) | Sí (258) | Sí o parcial (258) |
|-------------|----------|--------------------|----------|--------------------|
| C1+C2 | 1 | 11 | 4 | 15 |
| C1+C2+C3 | 0 | 1 | 0 | 1 |
| C1+C2+C3+C4 | 0 | 0 | 0 | 0 |
| C3 solo | 0 | 2 | 0 | 2 |

Los registros con C1+C2 en "sí" son diseños inversos de dispositivos nanofotónicos (arXiv:2409.18284 en el conjunto de 252; además arXiv:2604.21301, doi:10.1002/nap2.70302 y doi:10.1038/s44310-026-00144-2 en el ampliado). Ninguno reporta cotas o intervalos sobre la salida.

El único registro con C1, C2 y C3 al menos parciales es arXiv:2608.04582 (procesadores ópticos difractivos): reporta cotas analíticas de error de aproximación, no cotas numéricas verificadas de la salida de una red concreta, y no entrena posiciones de una escena. Según el protocolo, es el caso de "C1+C2 que menciona cotas" y se analizó a mano: no cumple C3 tal como se definió. El otro registro con C3 parcial es arXiv:2404.00545 (cota rigurosa del error de un simulador electromagnético neuronal, sin red óptica). Ninguno más cumple la definición.

## 4. Veredicto

- **H0 (novedad refutada): no soportada por esta búsqueda.** Ningún registro cumple C1+C2+C3. Tampoco se encontró un trabajo C1+C2 con cotas de error verificadas sobre la salida; el caso de análisis manual (arXiv:2608.04582) no lo es.
- **H1 (ningún trabajo reporta C1+C2+C3 juntos): no refutada.** Resultado consistente con H1 dentro de los límites de esta búsqueda; no equivale a una prueba de ausencia.
- **Por componente.** C1 es común (decenas de registros). C2 en forma de geometría de dispositivo entrenada existe (4 registros con C1+C2 en el conjunto ampliado), lo que obliga a **no afirmar** novedad de "C1+C2" por separado. C3 prácticamente no aparece en el campo de redes ópticas (0 con certificado de salida). C4 (escena de una herramienta estándar) no aparece en ningún registro con red óptica.
- **Formulación prudente para el claim.** La novedad defendible es la combinación C1+C2+C3 (y C4 como rasgo adicional), no cada componente. El trazado de rayos diferenciable con optimización de geometría ya existe (arXiv:2609.16404; doi:10.1364/oe.583744) y la optimización de geometría de redes nanofotónicas también (métodos 3 a 5 de `METODOS-CERCANOS.md`).

## 5. Limitaciones

1. Búsqueda no exhaustiva: 12 consultas fijadas, 50 resultados por consulta y fuente, solo arXiv y OpenAlex con resultados; el resto no contribuyó.
2. Las marcas se basan en título y resumen, no en texto completo. Las reglas por términos son conservadoras para "sí" y laxas para "parcial"; los casos cercanos se revisaron a mano, el resto no. Una marca de C2 "parcial" no implica geometría de escena (en muchos casos refleja términos de geometría en el resumen).
3. Desde un resumen no se puede comprobar la detección por potencia ni el argmax de C1; "sí" en C1 significa red óptica con términos de coherencia, malla, interferómetro o unitaria.
4. Cinco registros pendientes quedan solo con título (R027, R031, R040, R041, R056); sus marcas son "no verificable" o parciales.
5. Semantic Scholar no respondió (HTTP 429), por lo que se pierde su cobertura de citas y de preprints.
6. La consulta de arXiv del protocolo, enviada como AND de todos los términos, es muy restrictiva; se compensó con la variante complementaria (núcleo de términos). Las frases de GitHub dan 0 resultados; las variantes relajadas solo revisan nombres y descripciones.
7. Seis registros añadidos tras revisión manual quedan fuera del criterio mecánico del protocolo (un solo grupo de términos): arXiv:2609.16404, arXiv:2606.25226, arXiv:2604.21301, doi:10.1002/nap2.70302, doi:10.1038/s44310-026-00144-2 y arXiv:1805.09943. Se cuentan aparte y el veredicto no depende de ellos (el resultado con 252 es el mismo).
8. Trabajo muy reciente (2026) puede no estar indexado todavía en las fuentes consultadas.

## 6. Desviaciones del protocolo (declaradas después de la ejecución)

El protocolo se comprometió en `99c25e2` antes de buscar. Estas desviaciones se decidieron durante la ejecución y quedan registradas aquí:

1. **Variantes complementarias de consulta.** Las consultas de arXiv escritas como AND de todos los términos devolvían casi nada. Se añadieron 12 consultas con términos nucleares (arXiv) y 12 frases relajadas (GitHub). Los resultados de las variantes se cuentan aparte en `SEARCH-LOG.json`.
2. **Búsqueda por título de los 106 registros pendientes.** El protocolo no lo preveía. Era necesario para obtener sus resúmenes y sus identificadores (105 localizados, 1 no localizado).
3. **Seis registros añadidos tras revisión manual.** Quedan fuera del criterio mecánico (ver limitación 7). El veredicto no depende de ellos.
4. **Doce llamadas a arXiv mal codificadas.** Se descartaron y no cuentan en el registro.

Estas desviaciones no cambian el veredicto. Sí aumentan el riesgo de sesgo de selección, y por eso el veredicto solo se formula como "no encontrado en esta búsqueda".
