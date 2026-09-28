# EXP-001 · Contrato pre-Blender de interferencia escalar de dos caminos

Estado: **cerrado antes de cualquier ejecución MZ en Blender; ejecución
bloqueada por recursos y revisión final**. Revisión de la propuesta de Claude
`EXP-001-PROPUESTA-CLAUDE.md` con JEV remoto (DEC-009). Se conservan también
el borrador anterior y la propuesta original; este documento fija los
criterios para una futura prueba, no comunica un resultado experimental.
Enmienda previa a toda ejecución Blender (DEC-010, 2026-09-28 21:45 UTC):
primera intersección válida de detector y compuerta de solape dependiente
de la anchura del haz. Los umbrales de aceptación de puertos no cambian.

Las pruebas CPU exploratorias ya se hicieron antes de cerrar este contrato.
Por tanto, la coincidencia CPU previa no se presentará como confirmación
independiente ni como física electromagnética real. El resultado que se
preinscribe es la **lectura de objetos de escena Blender guardados/reabiertos
por el adaptador MZ**, sin render ni GPU. Si falla, se registra el fallo sin
retocar esta tabla ni las tolerancias a posteriori.

## Modelo, unidades y escena inicial

- Interferómetro Mach–Zehnder escalar de siete objetos ópticos (más un empty
  auxiliar de agrupación, que no calcula potencia). Geometría no
  rectangular `NonRectMZ(60, X=2, Y=2)` en unidades Blender (BU). La escena
  debe construirse con objetos del adaptador y después leerse desde sus
  transformaciones y propiedades guardadas; el oráculo solo predice, no
  alimenta al motor al medir.
- BS1 y BS2: transmisión de potencia 0,5; espejos: reflectancia RGB `(1,1,1)`;
  fuente: potencia total 1, RGB `(1,1,1)` como canales de potencia etiquetados,
  frecuencia 100 ciclos/s simulado, velocidad 10 BU/s, longitud de onda
  escalar simulada λ=0,1 BU, fase 0, `beam_waist=0,2 BU`,
  `mutual_coherence=1`, absorción 0. Detectores a 1 BU de BS2 por las
  direcciones de salida, radio 0,2 BU.
- `beam_waist` es una anchura constante fenomenológica; no hay difracción,
  propagación gaussiana completa, polarización, longitudes de onda RGB
  distintas ni fotones físicos. El cálculo óptico se hace en CPU con la
  geometría y propiedades leídas de la escena; Blender no renderiza la luz.
- BS2 y ambos detectores se agrupan bajo un empty padre. En B-geo se mueven
  **M1 y ese grupo**, dos ediciones coordinadas que cambian solo geometría;
  fuente, BS1, M2, fases de material, frecuencia, potencia, anchura,
  coherencia y divisores permanecen invariantes. No se describirá como
  movimiento de un único objeto ni como un cambio de fase material.

## Controles primarios congelados

Los valores A/B son potencias ópticas totales (suma RGB). `residual_rgb`
debe cumplir `max(abs(...)) ≤ 1e-12` en todos los controles, sin NaN/Inf.
Registrar también `input_rgb`, salidas RGB, absorción, pérdida de espejo,
escape, no resuelto, señal/activación y los diagnósticos de solape.

| Control | Cambio respecto de A | A / B esperado | Condiciones adicionales |
|---|---|---|---|
| A | Ninguno; P=(2,2) | 0 / 1 | `status=ok`, dos modos válidos, solape≈1, `unresolved=0` |
| B-geo | M1 y grupo BS2+detectores; desplazar P `t=0,323205080756... BU` a lo largo de la dirección del brazo 2, M2 fijo | 1 / 0 | Solo geometría; `status=ok`, dos modos válidos, `unresolved=0` |
| B-mat | Volver a A y sumar π rad a `phase_shift` de M2 | 1 / 0 | Solo propiedad óptica; `status=ok`, dos modos válidos, `unresolved=0` |
| C | Repetir A, B-geo y B-mat con `mutual_coherence=0` | 0,5 / 0,5 en las tres | `effective_coherence=0`, `status=ok`, `unresolved=0`; no depende de la fase |
| D | Desde A, girar la **normal de M2 +10° alrededor del eje Z mundial**, antihorario visto desde +Z; posición fija | 0,25 / 0,25 | `escape=0,5`, `unresolved=0`, `status=missed_bs2`, sin interferencia de dos brazos |

La escena B-geo debe conservar coincidencia de impactos en BS2 dentro de
la compuerta del modelo, coincidencia direccional y llegada de ambos modos a
sus detectores **como primera esfera intersecada**. Con `beam_waist=0,2`,
la compuerta espacial es `mode_overlap≥0,01`; el umbral absoluto
`overlap_tolerance=0,02 BU` solo corresponde al modo ideal sin anchura.
Ningún detector puede envolver el punto de salida BS2; un empate o un
detector equivocado primero deja la potencia sin resolver. En A/B/C,
registrar `transverse_separation`, `mode_overlap` y
`effective_coherence`; para `mutual_coherence=1`, exigir solape ≥ `1−1e-9`
en Blender. Si cualquier modo queda `unresolved`, el control falla.

## Comprobaciones secundarias, no sustitutos del criterio primario

- E: barrido CPU de 16 fases de M2 con τ1=0,5 y τ1=0,8. Visibilidad de B
  esperada 1 y 0,8, respectivamente; error absoluto ≤1e-9. Se registra
  como sensibilidad del modelo, no convierte una falla A–D en éxito.
- F: repetir/documentar el circuito monocamino histórico EXP-000. Valor
  esperado de intensidad 0,7053474966, activación 0,3657724623 y fase
  2,6376104167 rad según el informe previo. Es control de regresión de otra
  arquitectura, no criterio de interferencia de dos caminos.

## Umbrales y procedimiento fijados antes de Blender

1. CPU: construir A–D desde la escena declarada; guardar entradas, salidas,
   versión/commit del motor y valores del oráculo en un JSON. Error absoluto
   de puertos/escape ≤1e-12 y balance por canal ≤1e-12. Las exploraciones
   CPU anteriores se etiquetan como tales; una nueva ejecución para este
   paso es comprobación de reproducibilidad, no confirmación independiente.
2. Solo cuando haya margen y autorización del usuario: Blender background
   CPU, un hilo, prioridad baja, RSS ≤1,5 GiB, RAM libre ≥2,5 GiB y hasta
   45 s por fase, sin render/GPU. Crear A con objetos, guardar `.blend`,
   reabrir y leer transformaciones/propiedades. Aplicar B-geo mediante M1 y
   el empty padre, guardar/reabrir; repetir B-mat, C y D. Conservar artefactos
   y no borrar resultados fallidos.
3. Blender: puerto oscuro ≤1e-9, puerto brillante ≥`1−1e-9`; en C cada puerto
   dentro de 1e-9 de 0,5; en D A, B y escape dentro de 1e-9 de 0,25, 0,25
   y 0,5. Balance por canal ≤1e-12. Status y rutas deben concordar con la
   tabla; A/B/C requieren `status=ok`. Una traza CPU reconstruida **solo de
   los valores leídos del `.blend`** debe coincidir con la traza del adaptador
   en 1e-12. Registrar matrices/transforms antes y después de guardar.
4. La estimación float32 previa de Claude no incluye la conversión real
   Euler→`matrix_world` de Blender y **no** cuenta como ejecución Blender.
   Una discrepancia real superior a los umbrales se informa como fallo o
   límite del contrato; no se amplían los umbrales después de medir.

Parar si falta RAM libre, se supera cualquier presupuesto, hay NaN/Inf,
el balance no cierra o una condición primaria no puede construirse desde
objetos guardados. OPT-003 permanece bloqueada hasta la revisión final de
este contrato, la verificación runtime del empty padre en el adaptador y la
liberación de recursos. Aun si A–D pasan en Blender, el
resultado solo demostraría cálculo escalar gobernado por objetos de escena,
no una red neuronal entrenable ni computación óptica física completa.
