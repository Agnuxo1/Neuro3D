# OpticNeuroBlender: selección de técnicas para nuestra red

El propietario reafirma la prioridad: **construir nuestro propio sistema de red neuronal óptica funcional dentro de Blender**. OpticNeuroBlender es el nombre de esa aplicación de Neuro3D. La reutilización de otros programas está subordinada a resolver sus entradas, parámetros entrenables, propagación, detectores y aprendizaje. El desarrollo de herramientas de laboratorio acompaña ese objetivo.

Esta evaluación recomienda una arquitectura modular propia. No se sustituyen automáticamente el núcleo neuronal, la semántica de los campos ni los criterios de validación. No se han medido nuevas mejoras de precisión, velocidad, energía o acierto neuronal.

## Selección recomendada

| Problema de nuestra red | Técnica que conviene aprovechar | Procedencia y condición |
|---|---|---|
| Identidad de mallas, unidades y materiales | Flujo escena → malla/modelo científico → datos → resultados; asignación explícita de propiedades | BlenderPhotonics. Adaptar el diseño de interfaces. Iso2Mesh y mallado tetraédrico sólo cuando el componente/medio necesite volumen; añadir tetraedros no beneficia por sí mismo a una red de superficies ópticas |
| Fase, interferencia y polarización | Campos Jones, fase óptica, coherencia y marco de detección común | Blender Optics Simulator. Mantener coherencia entre los canales de entrada y convenciones de fase compatibles con Neuro3D |
| Desalineación, pérdidas y difracción | Haces Gaussianos/ABCD, Fresnel/Snell, apertura, propagación por espectro angular | Blender Optics Simulator como referencia o módulo validado. Definir primero la magnitud que mide nuestro detector y comprobar convergencia y régimen físico |
| Recorrido y coste repetido | Tabla de elementos/superficies, geometría compilada y cachés con invalidación | Aprovechar la organización del trazador de Optics Simulator, conservando una equivalencia demostrada con los triángulos capturados y nuestros contactos/bordes/retornos |
| Barridos, entrenamiento e inferencia | Compilar una vez la geometría fija, calcular todos los caminos o su cociente coherente equivalente y procesar lotes | Implementación propia de Neuro3D. La compilación debe derivarse de la escena; las entradas nuevas no requieren repetir una geometría que no haya cambiado |
| Referencia ondulatoria y GPU | FFT en precisión suficiente, caché de funciones de transferencia, lotes y datos residentes | Técnicas de la capa `field/gpu` de Optics Simulator. Su GPU actual acelera esta capa de campos, no el trazador vivo de rayos |
| Absorción/dispersión en medios volumétricos | MMC/MCX y sus interfaces de transporte Monte Carlo | BlenderPhotonics, como módulo específico cuando nuestra tarea lo requiera. Su salida de fluencia no reemplaza el campo complejo de una red interferométrica |

La mayor reutilización inmediata de física procede de **Blender Optics Simulator**; la de preparación de mallas/medios y transporte dispersivo procede de **BlenderPhotonics**. El cálculo neuronal y la integración permanecen en OpticNeuroBlender.

## Hallazgos que condicionan la integración

### Coherencia entre entradas: requisito prioritario

En el código revisado de Optics Simulator, cada fuente emitida recibe un `src_id` distinto. La medición agrupa por ese identificador: suma campos dentro de cada grupo y añade intensidades entre grupos. Esto representa fuentes independientes, pero no es la semántica actual de los cinco canales coherentes de Neuro3D.

Si trasladamos nuestros canales como cinco fuentes independientes perderíamos términos cruzados:

`I_coherente = |Σ E_j|²`, mientras que `I_independiente = Σ |E_j|²`.

Con dos campos `1` y `−1`, el primer modelo produce `0` y el segundo `2`; con `1` y `1`, producen `4` y `2`. Es una identidad algebraica, no un nuevo experimento ejecutado en los addons. Para una comparación equivalente hay que representar una fuente común con canales modulados, o declarar y validar una coherencia mutua y fases relativas equivalentes. Igual longitud de onda no demuestra por sí sola coherencia entre láseres independientes.

Fuentes primarias: [emisión](https://github.com/emircbngl/blender-optics-simulator/blob/2b488e2e99dff4f56d67f57f9674bd00f812dda1/optical_alignment_sim/tracer.py), [medición](https://github.com/emircbngl/blender-optics-simulator/blob/2b488e2e99dff4f56d67f57f9674bd00f812dda1/optical_alignment_sim/alignment.py).

### Completitud y precisión geométrica

El trazador revisado rechaza `t < 1e-4`, descarta casi paralelismo con `|d·n| < 1e-9`, admite aperturas con tolerancia `1e-3`, y deja de continuar un rayo por profundidad o potencia inferior a `1e-4`. Son decisiones concretas de su banco interactivo; no prueban conservación de nuestras consultas adversas ni una cota de campo omitido. No se importarán automáticamente a la ruta certificada.

Para descartar un conjunto de caminos debe acotarse el error de campo. Una cota conservadora es `ε_E ≤ Σ |a_p|` para los caminos omitidos, seguida de `|ΔI| ≤ 2|E|ε_E + ε_E²` y de la comprobación del margen de decisión. Una contribución individual débil no basta para justificar su descarte en una suma coherente.

El diseño por planos y aperturas puede reducir trabajo, pero debe conservar la **unión exacta de los triángulos**. Sustituir un polígono triangulado por un círculo ideal cambia los hits cerca de su borde. Se mantiene nuestra corrección del abanico y la negativa explícita cuando hay ambigüedad.

### Detectores y régimen físico

Optics Simulator proyecta la polarización a un marco común del detector y restaura la potencia del haz para su lectura de intercepción. Esa convención no debe confundirse con el acoplamiento a un modo específico de nuestra red. Debemos elegir entre lectura espacial integrada y proyección sobre modos definidos, conservando fase, apertura y solapamiento.

La versión Iris emplea λ=0,1 BU y radio nominal 0,2 BU: el diámetro nominal sólo equivale a unas cuatro longitudes de onda. Es un motivo para contrastar el modelo de rayos con una referencia ondulatoria antes de reivindicar fidelidad física. No es una medición de error ni invalida por sí solo el circuito escalar abstracto. Cambiar λ para aproximarse a una plataforma física también exige revisar la resolución de los desplazamientos y el presupuesto de fase.

### GPU: precisión y coste completos

El módulo `gpu.py` de Optics Simulator usa CuPy/NVIDIA o MLX/Apple, con retorno de arrays a CPU. El recorrido vivo de rayos no cambia al activarlo. Su documentación afirma diferencias del orden de `1e-6` en el camino rápido `complex64`; eso no es una cota universal ni demuestra satisfacer nuestro presupuesto de campo. El modo `complex128` es el punto inicial para comparar referencias, sin asumir que la paridad CPU constituye una certificación física.

Sus funciones de campos rellenan valores NaN con cero para ciertos usos de máscaras. Nuestra integración distinguirá una máscara física explícita de un resultado no finito o una lectura incompleta: estos últimos se rechazan. Para muchos pasos, mantener los campos residentes y agrupar ejecuciones puede evitar transferencias repetidas; la ganancia debe medirse.

Fuentes primarias: [GPU](https://github.com/emircbngl/blender-optics-simulator/blob/2b488e2e99dff4f56d67f57f9674bd00f812dda1/optical_alignment_sim/gpu.py), [campos](https://github.com/emircbngl/blender-optics-simulator/blob/2b488e2e99dff4f56d67f57f9674bd00f812dda1/optical_alignment_sim/field.py).

### Alcance de BlenderPhotonics

Los wrappers revisados preparan mallas tetraédricas o vóxeles, propiedades ópticas, unidades, fuentes y simulación MMC/MCX; recuperan `flux/fluence`. Ese flujo puede ser útil para medios dispersivos y la preparación del laboratorio. La intensidad o fluencia por sí sola no determina la fase del campo: no se convertirá en una amplitud compleja conocida mediante una raíz cuadrada y una fase supuesta.

Esto describe los wrappers inspeccionados, no una afirmación sobre toda variante de Monte Carlo o toda capacidad de MCX/MMC. [Código primario](https://github.com/NeuroJSON/BlenderPhotonics/tree/732799f9e3ebe10e013e316b8a21d88452755dc8).

## Orden de trabajo y criterios de mejora

1. Fijar y conservar unidades, fuentes coherentes, referencias de fase, modos/detectores y representación de los parámetros. Completar primero la propagación y los errores del modelo propio.
2. Introducir aceleración que conserve ese resultado: caché de geometría, pruebas por elemento/plano verificadas, estructura espacial y reutilización del grafo óptico. En la captura hay 6.656 triángulos para 104 elementos, 64 por elemento. Es una oportunidad de reducir pruebas repetidas, **no una aceleración medida de 64 veces**.
3. Contrastar componentes con referencias analíticas y ondulatorias equivalentes. Añadir polarización, pérdidas, difracción y solapamiento donde la tarea lo necesite. Mayor realismo puede exigir reentrenamiento; no garantiza mayor acierto inmediatamente.
4. Medir inferencia y entrenamiento completos bajo el mismo modelo, entradas, salidas y precisión: preparación, estructuras espaciales, transferencias, cálculo, lectura y decisión; tiempo, memoria, energía y variación entre ejecuciones.
5. Adoptar cada componente sólo si conserva los criterios de campo/intensidad/decisión, aporta la fidelidad declarada o reduce el coste comprobado. Las pruebas NVIDIA y AMD requieren ejecución real en cada plataforma.

La red lineal en campos con lectura cuadrática conserva los [límites ya derivados](IRIS_LINEAR_FIELD_QUADRATIC_DECISION_2026-10-08.md). Más rayos, mallas o módulos no aumentan automáticamente su expresividad. Las no linealidades ópticas adicionales requieren ecuaciones, estabilidad, referencia y entrenamiento propios; son una etapa posterior a cerrar el núcleo actual.

## Evidencia y estado

Se verificaron los HEAD actuales: Optics Simulator `2b488e2e…` y BlenderPhotonics `732799f9…`. Se inspeccionaron pasajes pertinentes de 11 fuentes de implementación —trazado, geometría, física, Gaussianos, campos, GPU, medición y wrappers/mallado—, además de documentación/API previamente revisada. No se ejecutó código externo ni benchmarks comparativos. Las prestaciones declaradas por los autores se separan de nuestra evidencia.

El [registro de selección](research/optic_neuro_blender_component_selection_v1.json) fija prioridades, conflictos semánticos y referencias. Los módulos nuevos propios conservan su licencia; la distribución o modificación de componentes externos mantendrá sus licencias y atribución. Esta decisión no cierra novedad, precisión nativa, red completa ni superioridad sobre alternativas.
