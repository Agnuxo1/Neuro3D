# Lectura de los métodos cercanos · P1-6 (frente 11)

Fecha: 2026-10-10. Corregido el mismo día: una versión previa llamaba "texto completo" a los métodos 2 a 4, pero solo pasaron por el resumen de WebFetch. Complementa (no sustituye) `METODOS-CERCANOS.md`, `PROFUNDIDAD-METODOS-P1-6.md` y `CONCLUSION-PROFUNDIDAD-P1-6.md`. `VEREDICTO-P1-6.md` no se modifica. Condiciones C1 a C4 según `PROTOCOLO-BUSQUEDA-P1-6.md`:

- C1: red óptica coherente (entradas complejas, propagación coherente, detección por potencia, decisión argmax).
- C2: parámetros entrenables = posiciones o retardos de elementos de una escena o geometría evaluada.
- C3: certificado de intervalo (cotas numéricas verificadas sobre la salida de la red).
- C4: geometría capturada desde una herramienta estándar de escena (p. ej. Blender).

## Etiquetas de evidencia

- **Texto completo verificado** (solo método 1): PDF descargado y extraído con `pdftotext` (`D:\PROJECTS\.cognition\neuro3d-audit\novedad\tmp\m1.pdf`, `m1.txt`, 106 716 bytes). Comprobación por búsqueda de términos sobre el texto bruto: "certif" 0 apariciones, "verified" 0, "argmax" 0, "blender" 0, "interval" 2 (ambas como intervalo de aproximación de una función, líneas 266 y 271), "classif" 1 (lista de aplicaciones, línea 712), "intensity" 56. La ausencia de esos términos sostiene C3 y C4 = no. C1 y C2 del método 1 salen de la lectura del texto, sin búsqueda dedicada.
- **Resumen de WebFetch** (métodos 2 a 4): un modelo pequeño resumió la página HTML de arXiv. No se leyó el texto completo ni se hizo búsqueda de términos sobre texto bruto. Las marcas son "según resumen", no verificadas, y las secciones citadas son las que indicó el resumen.
- **Solo resumen del artículo** (método 5): ver `PROFUNDIDAD-METODOS-P1-6.md`.

Todo parafraseado.

## Tabla resumen

| # | Método | Etiqueta | C1 | C2 | C3 | C4 |
|---|---|---|---|---|---|---|
| 1 | arXiv:2608.04582 (Rahman, Shen, Ozcan) | texto completo verificado | parcial (lectura) | no (lectura) | no, verificado | no, verificado |
| 2 | arXiv:2404.00545 (Dove, Boondicharern, Waller) | resumen de WebFetch | no, según resumen | no, según resumen | parcial, según resumen | no, según resumen |
| 3 | arXiv:2409.18284 (Radford et al.) | resumen de WebFetch | parcial, según resumen | parcial, según resumen | no, según resumen | no, según resumen |
| 4 | arXiv:2604.21301 (Muda, Teğin) | resumen de WebFetch | parcial, según resumen | parcial, según resumen | no, según resumen | no, según resumen |
| 5 | doi:10.1038/s44310-026-00144-2 | solo resumen del artículo | sí | sí | no | no |

Fila 5: no accesible; se mantienen las marcas anteriores con grado "solo resumen".

## Método 1 · arXiv:2608.04582 · texto completo verificado · https://arxiv.org/pdf/2608.04582 (HTML devolvió 404)

- C1, parcial (lectura). Procesadores difractivos coherentes; el texto discute lectura por intensidad (módulo al cuadrado) frente a lectura de campo y varios canales de intensidad. Es aproximación de funciones; sin argmax ni clasificación como tarea evaluada.
- C2, no (lectura). Parámetros entrenables: patrones de fase por capa. La geometría es fija; no hay posiciones ni retardos.
- C3, no, verificado. Las cotas (truncación de Fourier, síntesis de PSF, error de fase de entrada, ruido de fotones, aprendibilidad) son analíticas, de clase de funciones; la de aprendibilidad acota la brecha de generalización. Se contrastan por muestreo (cuantización de 8 bits, Fig. 5), no por certificado. Cero apariciones de "certif" y "verified"; "interval" solo como intervalo de aproximación.
- C4, no, verificado. Cero apariciones de "blender"; modelo analítico/numérico propio.

## Método 2 · arXiv:2404.00545 · resumen de WebFetch · https://arxiv.org/html/2404.00545

- C1, no, según resumen (Sec. 2.1, Fig. 1, Sec. 2.7). Red digital (U-Net con atención) que predice campos complejos; no es una red óptica física; sin argmax.
- C2, no, según resumen (Secs. 2.5 a 2.7). Se optimizan índices de refracción por vóxel y amplitudes/fases de ondas planas, no posiciones.
- C3, parcial, según resumen (Sec. 2.3, Sec. 4.2). Cota superior del error del simulador neuronal respecto a FDTD (Cauchy-Schwarz y conservación de energía); analítica, solo sin ganancia óptica, acota el sustituto y no la salida de una red óptica. Sin intervalos ni cómputo verificado según el resumen.
- C4, no, según resumen (Secs. 2.1, 4.1): rejilla de vóxeles por procedimiento.

## Método 3 · arXiv:2409.18284 · resumen de WebFetch · https://arxiv.org/html/2409.18284

- C1, parcial, según resumen (Secs. 2.1, 3.1). Matriz de transmisión compleja de guías acopladas; sin fotodetección ni argmax.
- C2, parcial, según resumen (Secs. 2.1, 2.3). Variables: 288 píxeles on/off de material de cambio de fase desde el espacio latente de un WGAN-GP; geometría de guías fija.
- C3, no, según resumen (Secs. 3.1, 4.2, 5). Solo métricas empíricas; la penalización latente es un regularizador.
- C4, no, según resumen (Secs. 2.1, 2.3): Lumerical varFDTD/MODE.

## Método 4 · arXiv:2604.21301 · resumen de WebFetch · https://arxiv.org/html/2604.21301

- C1, parcial, según resumen (Secs. 2.1, 2.3). Operador complejo, detección por intensidad, entropía cruzada sobre intensidades; argmax implícito, no declarado.
- C2, parcial, según resumen (Secs. 2.1, 2.2, 2.4). Parámetros antihermíticos/valores singulares acotados y mapa latente por píxel proyectado a permitividad; sin posiciones explícitas.
- C3, no, según resumen (Sec. 2.1, Secs. 3 y 4). Solo rango permitido de valores singulares; sin cotas verificadas sobre salidas.
- C4, no, según resumen (Sec. 2.2): optimización adjunta con Tidy3D; sin Blender.
- Nota de identidad: la equivalencia con doi:10.1002/nap2.70302 sigue sin demostrarse; solo se leyó el preprint.

## Método 5 · doi:10.1038/s44310-026-00144-2 (npj Nanophotonics 2026) · NO ACCESIBLE

- Artículo y PDF redirigen a un flujo de autorización de Nature (HTTP 303 a idp.nature.com); no se siguió. WebSearch no localiza el artículo ni un preprint. C1 a C4 solo por resumen.

## Veredicto

Sobre la combinación de geometría capturada con readout cuadrático y certificado de intervalo (C4+C1 con detección por potencia+C3):

1. Se mantiene, con alcance acotado. Con evidencia verificada solo del método 1: no hay aritmética de intervalos, certificado ni Blender. Para los métodos 2 a 4 la ausencia de C3 y C4 depende de los resúmenes de WebFetch y no está verificada en texto completo.
2. Ningún método revisado cumple C1+C2+C3. Los más cercanos a C3 son el 1 (cotas analíticas, validadas por muestreo; verificado) y el 2 (cota del error del sustituto; según resumen); ambos acotan otro objeto (clase de funciones o sustituto) con otro método (analítico, no intervalo verificado).
3. Matices: el método 1 y el 4 tratan lectura por intensidad, así que C1 con detección por potencia es compartido y no diferencia; el 2 no es red óptica (según resumen); en 3 y 4 lo entrenado es patrón de píxeles o permitividad, de modo que C2 queda "parcial" y no "sí" como figuraba en `METODOS-CERCANOS.md` (según resumen). No cambia el sentido del veredicto.
4. Redacción recomendada: "no consta en los textos leídos (texto completo del método 1; resúmenes de los métodos 2 a 4) ninguna combinación de readout cuadrático sobre geometría capturada con certificado de intervalo". No escribir "primer trabajo".

## Qué queda sin acceso

- Texto completo de los métodos 2 a 4 (solo resumen de WebFetch).
- Método 5 completo (muro de autenticación del editor).
- Métodos 6 a 8 (solo resumen).
- Los 106 registros de fondo de `EXTRACCION-P1-6.json` (solo resumen).
- Versiones de revista de los métodos 3 (ACS Photonics) y 4 (doi:10.1002/nap2.70302): solo preprints.
- Búsqueda adicional en verificación de redes con aritmética de intervalos: Semantic Scholar devolvió 429; sin ella, "no consta" no equivale a "original".
- Suplementos y código de los trabajos.
