# EXP-004 · Gate propuesto para malla geométrica 4 modos × 4 columnas

Estado: **borrador para crítica independiente, no preinscrito ni autorizado
para medir**. 2026-09-29. Continúa el gate híbrido de EXP-003; no prueba
computación óptica física ni ventaja sobre redes convencionales.

## Topología mínima y pregunta

Cuatro modos atraviesan cuatro columnas de acoplamientos vecinos
alternados. Pares por columna: `(0,1),(2,3)`; `(1,2)`;
`(0,1),(2,3)`; `(1,2)`. Son **seis celdas MZI**, no dieciséis.
Cada celda debe aportar dos fases mediante caminos trazados sobre discos
de Blender (`scene.ray_cast`), con su fuente, orden de impactos, puertos
y orientación congelados en un fixture versionado antes de ejecutar.
No se acepta leer desplazamientos `matrix_world.z` y convertirlos
directamente en fases: eso reproduce OPT-007, no extiende EXP-003.

Pregunta falsable: ¿una intervención geométrica en una celda interna
cambia los campos de salida de cuatro modos por los segmentos medidos
en esa celda, mientras rutas, controles y balance se conservan tras
guardar y reabrir la escena? Un fallo de rayo nunca se sustituye por
una longitud analítica.

## Congelar antes de ejecución

- JSON de fixture con SHA-256: coordenadas, normales, radios, roles,
  rutas, fuentes, puertos, longitud de onda, fases de referencia y
  entradas complejas. Readback de mallas y matrices desde `.blend`.
- Oráculo independiente que propague la misma red ideal desde las
  longitudes **medidas**, sin importar el propagador principal; además
  referencia analítica separada solo para evaluar intervenciones.
- Casos: cuatro bases canónicas de entrada y al menos una superposición
  normalizada; base, desplazamiento normal en una celda intermedia,
  sham tangencial y ablación de un espejo de esa celda. La elección
  exacta de celda y valores de desplazamiento se fija en el fixture.
- Umbrales numéricos y límites de recursos antes de medir; no ajustar
  el umbral después de ver los resultados. EXP-003 sugiere tolerancias
  iniciales, pero la acumulación por seis celdas exige presupuesto de
  error explícito por segmento y propagación.

## Gates de aceptación propuestos

1. Todos los recorridos y longitudes salen de raycasts sobre la escena
   reabierta, con trazas y hashes por caso. Ningún peso/fase del fichero
   sustituye una ruta perdida. El cambio de geometría se confirma por
   matrices mundiales y readback de malla.
2. Para entradas válidas, `sum(P_salidas)+P_escape+P_absorbida` conserva
   la potencia de entrada dentro de un umbral congelado. Comparar el
   vector complejo de salida (hasta fase global si procede), no solo
   `argmax` o precisión: puertos coincidentes pueden ocultar errores.
3. Intervención, sham y ablación deben distinguir causalidad de mera
   coincidencia numérica. La ablación registra pérdida o escape en la
   celda afectada y esa pérdida se propaga; prohibido renormalizarla.
4. Tras guardar/reabrir cada tratamiento, repetir readback, raycasts
   y salidas; registrar error antes/después y las trazas completas.
5. Un retrazado independiente (Claude) sobre al menos base,
   intervención y ablación debe reproducir longitudes y salidas.

La implementación será **híbrida**: Blender decide impactos y distancias;
Python combina amplitudes entre celdas. Se reportará también latencia,
memoria y número de raycasts como coste descriptivo, sin comparativa
competitiva. Si el usuario exige que toda interferencia ocurra en la
escena/shader, este gate no satisface todavía ese objetivo; esa vía
necesita experimento y aceptación aparte.

## Revisión solicitada

Claude: buscar un falso positivo específico en el acoplamiento de
celdas (puertos, fase global, pérdidas, rutas que se crucen) y confirmar
si «4×4» debe significar cuatro modos × cuatro columnas o dieciséis
celdas físicas. JEV: decisión de arquitectura pendiente de canal
autorizado con `provenance=jev`; el borrador no se presenta como avalado.

## Auditoría independiente del 29-09, 17:19 UTC · blockers del diseño Clements

Claude confirmó que 4 modos × 4 columnas = 6 MZI es la lectura estándar,
pero mostró cuatro vías de falso éxito en el consumidor sintético:

1. Omite las fases de enlaces fuente→celda, celda→celda y celda→detector.
   Una diferencia de λ/4 en un enlace puede cambiar potencias sin que el
   contrato actual cambie su salida.
2. El cableado y los signos de puertos están fijados en Python; ningún
   impacto demuestra que una salida entre por el puerto correcto siguiente.
3. El balance de una matriz unitaria es tautológico. Un haz huérfano de
   ablación puede impactar otra celda; su escape debe contabilizarse
   coherentemente por canal, no sumar intensidades de caminos aislados.
4. Solo bases canónicas ocultan errores de fase. Exigir además
   superposiciones (1+1) y (1+i), y comparar campos complejos.

Por tanto, `exp004_measured_mesh.py` queda como **contrato CPU parcial**,
no candidato a gate runtime. Ninguna ejecución de Blender de Clements
debe promocionarse hasta medir enlaces/caras de llegada, seguir rutas
huérfanas y comparar con una suma de caminos de la escena completa.

Claude propuso y está probando independientemente una rejilla oblicua
de celdas EXP-003, sin espejos extra de enlace: K=2 da 4 modos/4 MZI y
K=4 da 8 modos/16 MZI. Es una candidata experimental distinta, no una
afirmación de superioridad ni una decisión avalada por JEV. Sus oráculos
CPU A (suma de caminos de todos los discos) y B (matrices independientes)
coincidieron a escala ~1e-13 en K=2..4 según sus reportes; queda por
comprobar en Blender y auditar los artefactos. Codex creó un puente
de construcción de discos con validación de esquema, sin lanzarlo
durante la reserva de Blender de Claude.
