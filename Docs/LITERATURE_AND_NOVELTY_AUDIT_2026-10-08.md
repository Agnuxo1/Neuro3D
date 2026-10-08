# Antecedentes: búsqueda sistemática y revisión crítica acotada

**Resultado:** los ingredientes centrales de Neuro3D tienen antecedentes. La novedad científica de la integración candidata todavía **no está demostrada**. Este informe termina una búsqueda reproducible y una revisión seleccionada de métodos, pero no se presenta como lectura exhaustiva de todos los resultados ni cierra positivamente el nuevo punto 1 «demostrar la novedad».

## Procedimiento y alcance

Se fijó [un protocolo de cinco consultas](research/literature_search_protocol_v1.json) antes de buscar, en arXiv, Semantic Scholar y OpenAlex. Hubo 15 solicitudes iniciales y cinco búsquedas arXiv adicionales con [ampliación explícita de sintaxis](research/literature_search_amendment_v2.json), porque exigir todas las palabras devolvía sólo un registro. No se alteraron hipótesis ni umbrales experimentales.

Las búsquedas devolvieron **194 registros brutos, 175 únicos y 19 duplicados**. Semantic Scholar devolvió HTTP429 en las cinco consultas; no se convirtió esa limitación en ausencia de antecedentes ni se insistió indefinidamente. Se añadieron fuentes primarias requeridas por el propietario, búsquedas editoriales/autorales y referencias hacia atrás de artículos centrales.

El [catálogo de extracción](research/literature_catalog_v1.json) contiene **30 entradas: 29 artículos/preprints/comentarios científicos y un capítulo metodológico de autores**. Se recuperaron 26 PDF primarios, el cuerpo editorial relevante de LAMP y un capítulo de PBRT; se inspeccionaron los pasajes pertinentes de método, resultados y límites. No se afirma haber leído íntegramente cada PDF. Ashtiani se contrasta mediante preprint de los autores y abstract de la publicación final; Fevola y Andreas conservan acceso sólo a identidad/abstract en este pase. Los PDF completos quedan en el archivo privado de investigación, identificados por hash; no se redistribuyen sin verificar licencia.

La [auditoría de búsqueda y cribado](research/literature_review_audit_v1.json) distingue 16 registros incluidos en extracción desde las búsquedas, 106 antecedentes potencialmente pertinentes aún sin extracción completa, 52 exclusiones por título/alcance y una exclusión por retractación. Las restantes entradas seleccionadas proceden de búsqueda primaria adicional y referencias fundacionales. Se inspeccionaron además los abstracts de25candidatos próximos, lo que motivó ampliar las extracciones de25a30. Los106pendientes son una limitación real: **no llamamos a este pase revisión sistemática exhaustiva** ni usamos su selección para demostrar ausencia universal.

No se ordenan las precisiones de tareas distintas en un ranking común. Un porcentaje MNIST, un test de vocales, una tasa de rayos y una cota geométrica no son métricas intercambiables.

## Comparación de métodos y resultados inspeccionados

| Antecedente primario | Tarea/método y resultado | Diferencia que Neuro3D no puede reivindicar como nueva |
|---|---|---|
| [Cao et al., LAMP, 2026](https://doi.org/10.1038/s41467-026-72316-9) | Red programable 3D en vidrio, ocho capas; MNIST dígitos0–3:200 entrenamiento/48 test,93% train y91.7% test; patrones>94% similitud | Red física 3D, programabilidad, entrenamiento de fases y transformación coherente.6554TOPS es una estimación teórica limitada por detector, no coste completo medido |
| [Ashtiani et al., Nature2026](https://doi.org/10.1038/s41586-026-10262-8), [preprint autoral](https://arxiv.org/abs/2506.14575) | BP/activaciones en chip; publicación informa>90% en dos tareas. Preprint:mejor inferencia92.5% en separación2D,200puntos/50seleccionados para entrenar | Retropropagación fotónica y no linealidad ya se demostraron. La plataforma también tiene electrónica de control; no extrapolar potencia total cero ni tratar el número del preprint como test final independiente |
| [Shen et al.,2017](https://arxiv.org/abs/1610.02365) | Vocales:138/180=76.7% hardware,165/180=91.7% simulación; mejor calibración entre tres ejecuciones | Redes coherentes y multiplicación óptica. Diferencia entre simulación y hardware/calibración ya conocida |
| [Hughes et al.,2018](https://arxiv.org/abs/1805.09943) | Método adjunto e intensidad para obtener gradientes; entrenamiento de red simulada numéricamente | Derivar BP óptica no es nuevo; ese manuscrito no debe confundirse con una demostración fabricada |
| [Pai et al.,2023](https://arxiv.org/abs/2205.08501) | Gradientes in-situ medidos; clasificación de anillo90% enFig1 | Lectura de amplitud/fase y BP experimental anteriores a2026 |
| [Wright et al.,2022](https://arxiv.org/abs/2104.13386) | Entrenamiento físico con surrogate digital; sistemas óptico, mecánico y eléctrico;93% test vocales óptico enFig2 | Entrenar un proceso físico mediante un método híbrido ya existe |
| [Lin et al.,2018](https://arxiv.org/abs/1804.08711) | Capas difractivas3D impresas THz;91.75% precisión de diseño MNIST, demostraciones físicas seleccionadas | Capas3D, interferencia y diseño entrenado de óptica. No convertir la cifra de diseño en adquisición física de todo el test |
| [Wei et al., comentario](https://arxiv.org/abs/1809.08360) y [Mengu et al., respuesta](https://arxiv.org/abs/1810.04384) | Debate sobre linealidad, profundidad, restricciones de parametrización y eficiencia | Deben distinguirse operador fijo lineal y familia física entrenable; el debate no prueba por sí solo que todas las arquitecturas sean equivalentes |
| [Clements et al.,2016](https://arxiv.org/abs/1603.08788) | Malla unitaria, profundidad N frente a2N−3; mismo número N(N−1)/2 de divisores | Universalidad matricial y tolerancia a pérdidas ya estudiadas; ocho modos no significan una transformación arbitraria sin comprobar sus grados de libertad |
| [Miller,2013](https://doi.org/10.1364/PRJ.1.000001) | Diseño lineal universal y autoconfiguración progresiva mediante feedback local | Componentes ópticos lineales universales/configurables no son nuevos |
| [Moughames et al.,2019/2020](https://arxiv.org/abs/1912.08203) | Interconexiones3D:225entradas/529salidas,0.46×0.46mm²; filtros Haar | Interconexión3D y filtros análogos a operaciones CNN preceden incluso aLAMP; no son automáticamente una red general entrenada |
| [Fldzhyan et al.,2024](https://arxiv.org/abs/2408.00669) | Matrices no unitarias con diseños compactos/tolerantes a errores de componentes | Tolerancia física a errores no es una novedad suficiente; tampoco equivale a certificado de aritmética nativa |
| [Yang et al.,preprint2025/versión2026](https://arxiv.org/abs/2502.12385) | Revisión/modelos de arrays continuamente acoplados | Modelos/materiales de arrays programables ya tratados; triángulos geométricos no sustituyen modos guiados |
| [Willis et al.,2020](https://arxiv.org/abs/2005.09736) | Historias de fase SAR, OptiX/multirrebote;1.53Mrays/sRTX2070 frente156.38rays/sMATLAB enTable2 | Fase y GPU/RTX ya combinadas. El baseline interpretado no demuestra ventaja frente a cálculo matricial optimizado ni presupuesto neural equivalente |
| [Keksel et al.,2023](https://arxiv.org/abs/2308.04816) | Metrología óptica OptiX,>100imágenes y>1e9rayos/imagen; comparación cualitativa con equipo físico | Ray tracing masivo para óptica científica y escena de instrumento ya existe |
| [Steinberg et al.,2023/2024](https://arxiv.org/abs/2303.15762) | Rayos generalizados, coherencia/difracción; validación de doble rendija contraRayleigh–Sommerfeld | Transporte ondulatorio global mediante rayos ya existe. La formalización física no equivale a una cota de toda la aritmética finita; no atribuimos backendGPU a los pasajes inspeccionados |
| [Hoydis et al.,SionnaRT2023](https://arxiv.org/abs/2303.11103) | Trazado GPU diferenciable sobreMitsuba3 para canales RF/materiales/geometría | Geometría electromagnética, campos y aprendizaje de parámetros ya integrados; régimen RF y certificación numérica conjunta son cuestiones distintas |
| [Fevola et al.,online2019/2020](https://doi.org/10.1107/S1600577519014425) | Abstract describe rayos de Huygens para difracción coherente y ptychography; detalles completos pendientes | Difracción coherente por rayos también tiene antecedente; acceso fallido no demuestra ausencia de garantías |
| [Shewchuk,1997](https://people.eecs.berkeley.edu/~jrs/papers/robustr.pdf) | Predicados exactos/adaptativos bajo hipótesis de aritmética | Exactitud geométrica y precisión adaptativa son métodos fundacionales |
| [Woop et al.,2013](https://jcgt.org/published/0002/01/05/) | Intersección watertight conservadora, fallback double raro y BVH conservativa | Bordes/costuras robustos ya tratados. Watertight no significa intersección exacta ni certificado del campo |
| [Ize,2013 corregido2015](https://jcgt.org/published/0002/02/02/) | BVH/AABB robusta, estudio de1/2ULP; autor señala versiónFMAoriginal incorrecta | Robustez del recorrido no demuestra robustez de primitivas. Se enlaza la versión corregida |
| [Bartels et al.,2022](https://arxiv.org/abs/2208.00497) | Filtros rápidos con cotas y fallback exacto | Filtros/error arithmetic y exactitud adaptativa tampoco son nuevos |
| [Parker et al.,OptiX2010](https://research.nvidia.com/sites/default/files/pubs/2010-08_OptiX-A-General/Parker10Optix.pdf) | Programas de generación/intersección/recorrido GPU; limita representación de rayos aunque admite operaciones double | SDK científico programable no es aportación deNeuro3D; backend/versión importan |
| [PBRT4,cap6.8](https://pbr-book.org/4ed/Shapes/Managing_Rounding_Error) | Intervalos/error de intersección y posicionamiento acotado de orígenes | Cotas geométricas y evitar epsilon arbitrario ya son métodos establecidos |
| [Pasquale et al.,2026](https://arxiv.org/abs/2604.09243) | Multirrebote EM, BVH, NVIDIA/AMD y MPI; muestreo≤λ/5 para evitar aliasing de fase; esferaPEC frenteMie | Incluso usar ambas marcas con campos electromagnéticos tiene antecedente. La regla de muestreo no certifica toda la aritmética finita |
| [Ruah et al.,2023](https://arxiv.org/abs/2312.12625) | Calibración probabilística de geometría/fase de canales medianteEMvariacional ySionna | Estimar/compensar errores de fase ya se estudió; calibración estadística no es inclusión determinista de intervalos |
| [Meister et al.,paper2020/arxiv2025](https://arxiv.org/abs/2506.11273) | Reordenación de rayosRTX mejora1.3–2.0×el kernel, pero recuperar el coste de ordenar es problemático | Las optimizaciones de videojuegos requieren medir coste total; no basta una tasa de rayos mayor |
| [Ren et al.,2026](https://arxiv.org/abs/2603.07174) | Procesador coherente no local32entradas; arquitectura y clasificación físicas reportadas | Procesadores matriciales no locales ya existen. Cobertura numérica de blancos no demuestra aquí exactitud universal para cualquier matriz |
| [Andreas et al.,2015](https://doi.org/10.1364/JOSAA.32.001403) | Abstract de integral vectorial/rayos para difracción y metrología no paraxial; texto completo pendiente | Los métodos de campo vectorial mediante rayos también son anteriores; comparar límites por acceso legítimo |

## Delimitación de la aportación

La diferencia candidata será **un certificado conjunto y verificable de identidad geométrica, caminos y campos/salidas nativos**, con negativa explícita y una condición de utilidad que impida rechazarlo todo. Su ámbito es el modelo escalar representado, no Maxwell ni un dispositivo físico. La certificación tendrá que cubrir decisiones de recorrido/intersección, cuantización, longitudes, fase, suma coherente y márgenes de decisión, y compararse con los baselines existentes.

**Lo demostrado por este pase:** no hay base para reivindicar como descubrimiento el simple uso de Blender,3D,RTX,interferencia,matrices fotónicas oBPóptica. **Lo no demostrado:** que la integración propuesta sea original, que sus certificados nativos sean válidos/utilizables, que aporte una ventaja o que cambie una capacidad científica aceptada. La columna no resuelta del mapa siguiente representa esa falta de evidencia; no es prueba de que ningún antecedente lo haga.

![Mapa de evidencia de antecedentes](assets/literature-evidence-map-2026-10-08.png)

## Trabajo necesario antes de cerrar «demostrar la novedad»

1. Completar la extracción de los candidatos más próximos aún pendientes, empezando por los que describan campos coherentes, cotas o representaciones exactas; obtenerFevola completo por acceso legítimo.
2. Formular qué certificado o algoritmo concreto añade el prototipo frente aPBRT/predicados exactos y frente aSionna/simulación coherente, mostrando por qué no es sólo conectar herramientas.
3. Aportar implementación/prueba y una comparación verificable con los antecedentes pertinentes. Mantener cualquier ganancia de coste como hipótesis separada.

El nuevo punto1 permanece **ABIERTO** para esa demostración. Se publica este trabajo intermedio con resultados negativos y limitaciones, sin saltar al cierre de los puntos2–19.

Se añade un [testigo exacto de pérdida de información por cuantización](QUANTIZATION_INFORMATION_LOSS_WITNESS_2026-10-08.md): geometrías distintas pueden producir los mismos bytesfloat32pero intensidades analíticas1y0. Es un control matemático CPU de un principio conocido, con GIFexplicativo. No es un descubrimiento nuevo, una refutación deH1para el modelo representado ni un experimento confirmatorio/GPU/físico.

## Laboratorio virtual: comprobación actual

Las páginas públicas deP2PCLAW responden. La ruta documentada de búsqueda anónima `/api/literature/search` devuelve404 en el sitio actual. El código público del ExperimentTracker generaUUID/hash en el navegador y conserva los registros en `localStorage`; eso no acredita un registro externo inmutable,IPFS o cómputo remoto. No se reintentaron credenciales previas inválidas. No se publicó un borrador generado automáticamente por el laboratorio: su plantilla contiene afirmaciones de resultados y referencias genéricas que no corresponden a este estudio.

Estos hechos se conservan con hashes de los archivos públicos examinados. No hay recibo de cómputo remoto, preregId externo niCIDemitido por un registro externo para este nuevo estudio. La preregistración confirmatoria se prepara por separado antes de medir nuevos resultados.
