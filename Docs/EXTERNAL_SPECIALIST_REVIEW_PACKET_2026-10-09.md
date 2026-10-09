# Paquete para reproducción y crítica especializada

Estado: preparado para revisión, **sin revisión especializada recibida ni envío a una revista**. Las reproducciones en GitHub Actions son ejecuciones externas reales de software; no equivalen a que un investigador independiente haya evaluado el método. JEV aporta recomendaciones, no revisión científica ni prueba de originalidad.

El [manuscrito reproducible](paper/optic_neuro_blender_reproducible_draft_2026-10-09.md), los [criterios de aceptación](research/optic_neuro_blender_acceptance_v1.json) y el [registro de progreso](SEQUENTIAL_RESEARCH_PROGRESS_2026-10-08.md) delimitan las afirmaciones. Los ZIP del complemento, protocolos fijados, fuentes previas y resultados conservan identificadores y hashes. El autor y las afiliaciones deben confirmarse antes de una presentación formal.

## Afirmaciones concretas que revisar

| Afirmación acotada | Evidencia principal | Posible refutación |
| --- | --- | --- |
| El grafo representa todas las ramas no nulas admitidas de la escena escalar | [Progreso y protocolos](SEQUENTIAL_RESEARCH_PROGRESS_2026-10-08.md), 133 estados / 186 aristas / 17.060 ocurrencias de caminos | Una rama no nula admitida omitida, fusión de estados con operadores futuros diferentes o intersección anterior válida no detectada |
| Las decisiones observadas del lote nativo tienen margen riguroso positivo | [Certificado de los 150 casos](validation/native-training-batch-certificate-2026-10-09/analysis01/worker/certificate.json) | Campo exacto fuera del intervalo o margen certificado no positivo; diferenciar predicción incorrecta de error numérico |
| Las cajas de traslación declaradas tienen topología válida y cobertura de decisiones reportada | [Cajas condicionales](CONDITIONAL_PARAMETER_BOX_PROTOCOL_2026-10-09.md) y [familia completa](GLOBAL_TRAINING_FAMILY_PROTOCOL_2026-10-09.md) | Un punto de la caja con superficie seleccionada inválida o competidor anterior; no convertir UNKNOWN en estabilidad |
| El operador fijo tiene rango cinco y conserva la norma de todos los canales dentro de la cota indicada | [Gram racional](NATIVE_OPERATOR_GRAM_PROTOCOL_2026-10-09.md) | Un vector complejo cuya razón de normas esté fuera de las cotas; revisar conjugación, aritmética LDL y radios de Gershgorin |
| Entrenamiento propio y ejecución nativa son reproducibles bajo el contrato | [Instalación y Linux Blender real](EXTERNAL_NATIVE_BLENDER_PROTOCOL_2026-10-09.md) | Diferencia fuera del presupuesto, dependencia externa oculta, uso de pesos analíticos históricos o acceso a etiquetas reservadas durante entrenamiento |
| NVIDIA ejecuta la aritmética declarada, con costes completos publicados | [Pareja CPU/CUDA](GEOMETRY_CUDA_TRAINING_PROTOCOL_2026-10-09.md) | Falta de ejecución/readback real, comparación de precisiones u observables distintos, costes dominantes excluidos |

Los protocolos y nombres de archivos de validación deben comprobarse en el commit seleccionado, no mezclarse con fuentes posteriores. Para repetir un protocolo histórico, usa su commit publicado o sus preimágenes archivadas. Copia la evidencia a una carpeta nueva y conserva los fallos.

## Preguntas para especialistas

1. **Óptica:** ¿qué contrato de modos transversales y normalización de flujo permitiría contrastar la escena completa con un modelo independiente de ondas? ¿Qué errores de polarización, difracción, aperturas y acoplamiento detector dominan? La prueba de norma escalar no responde a estas preguntas físicas.
2. **Geometría y verificación:** ¿las pruebas de uniones de triángulos y exclusión continua cubren todos los casos admitidos? ¿Qué preimágenes de transformaciones/mallas nativas faltan para cerrar el presupuesto desde la intención geométrica?
3. **Aprendizaje:** ¿los controles de partición y codificación son suficientes? ¿Qué tareas, divisiones múltiples y datos ciegos ampliarían la evidencia sin selección a posteriori? La familia de decisiones es cuadrática restringida, sin activaciones ópticas intermedias.
4. **Rendimiento:** ¿son equivalentes las entradas, salidas, precisión y alcance de las referencias? ¿Se contabilizan construcción, verificación, transferencias, recuperación y memoria? La pareja CUDA original no muestra aceleración global; AMD y energía no están medidos.
5. **Originalidad:** ¿existe la misma cadena de geometría evaluada, campos coherentes y certificados de decisiones en un antecedente no revisado? [Tres precedentes próximos](GEOMETRY_COHERENT_CERTIFICATION_PRIORS_2026-10-09.md) y 106 extracciones históricas pendientes impiden afirmar ausencia de antecedentes.

## Registro de una futura reproducción

El revisor debe consignar: nombre e institución si procede; independencia respecto a los autores; fecha; commit; protocolo y hashes; plataforma, Blender/Python/NumPy/GPU reales; comandos; costes completos; archivos originales de salida; verificación de hashes; desviaciones y fallos; conclusión y alcance. Una afirmación de aceptación requiere un informe recibido y verificable. Esta plantilla vacía no cuenta como reproducción ni revisión.

No se ha contactado a especialistas desde este paquete. El registro externo/IPFS sigue pendiente y no se atribuyen identificadores a los ensayos anteriores. La fabricación sigue siendo opcional; una afirmación de procesador fotónico físico exige mediciones reales. Una aportación de importancia excepcional e impacto duradero permanece como aspiración, no como resultado de estos controles de software.
