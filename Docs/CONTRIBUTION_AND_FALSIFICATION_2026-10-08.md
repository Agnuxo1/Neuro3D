# Aportación candidata y criterio de refutación

Registro de formulación: 2026-10-08. Este documento cierra **la definición de la pregunta**, no confirma la hipótesis, la novedad, una ventaja de rendimiento ni una tesis física. El nuevo orden solicitado por el propietario empieza por esta formulación, continúa con antecedentes y después aborda el trazador Blender. Sustituye la anterior regla de esperar al cierre RT antes de definir la contribución.

## Pregunta única

¿Puede Neuro3D calcular desde la geometría real capturada de Blender campos coherentes mediante un backend nativo de rayos, con certificados de error válidos y utilizables para todas las escenas completas de una familia de evaluación fijada de antemano, detectando explícitamente los casos que no puede certificar?

## Aportación que se propone evaluar

Unir tres elementos en un contrato verificable: identidad de la escena representada, completitud/topología de los caminos y error del campo complejo nativo hasta la intensidad y decisión. El resultado propuesto es una salida certificada o una negativa explícita con motivo y datos conservados. La aportación candidata debe demostrar una diferencia relevante respecto a métodos existentes; esa diferencia todavía depende de la revisión sistemática.

El método no propone una nueva ley física. La geometría determina un operador de transporte dentro de un modelo escalar ideal; la GPU realiza cálculo electrónico. No se reivindica novedad por 3D, ray tracing, fase, interferencia, entrenamiento fotónico o uso de RTX. Tampoco se presupone superioridad respecto a CNN, GPT o multiplicación matricial.

## Hipótesis primaria H1: corrección del certificado

Para cada salida marcada `CERTIFIED`, el campo exacto del **modelo escalar representado** debe pertenecer al intervalo complejo comunicado. Las cotas de intensidad y decisión deben derivarse de ese intervalo y de los parámetros admitidos. Debe existir evidencia de todos los caminos no nulos pertinentes, o una cota válida de los caminos reducidos/omitidos.

La verdad de referencia es el problema geométrico y óptico con sus datos representados y unidades declaradas. Se separan la incertidumbre de captura/representación, las perturbaciones admitidas y el error de aritmética del backend. Validar ese problema no demuestra que el dispositivo físico se comporte igual.

Si E_hat es el campo calculado y b_E una cota válida de |E - E_hat|, entonces una cota de intensidad es b_I = 2 |E_hat| b_E + b_E^2. Para componentes o intervalos se utilizará la norma/cota declarada, sin intercambiar normas silenciosamente. Si los intervalos de logits permiten más de un ganador, la clasificación será `UNDECIDABLE`, aunque un argmax numérico haya elegido una clase.

**Refutación:** basta un contraejemplo verificado donde una salida `CERTIFIED` excluya el valor exacto representado, comunique una decisión incompatible con su intervalo o declare completitud pese a perder un camino no nulo no acotado. Un comparador aproximado que difiera no basta: el contraejemplo debe tener una referencia exacta, un intervalo independiente disjunto o una demostración analítica trazable. Un oráculo de precisión alta con error sin cota es diagnóstico, no prueba absoluta de inclusión/exclusión.

## Condición de utilidad: no aceptar el rechazo universal

Además de H1, se exige certificar **todos los miembros completos** de una familia congelada antes de los nuevos ensayos confirmatorios. La familia contendrá:

1. Controles analíticos de uno y dos caminos no nulos, con interferencia constructiva, destructiva y en cuadratura, además de fuente cero y sham.
2. Casos completos del conjunto geométrico adverso: contacto de salida legítimo, costura interior demostrada, hueco positivo y retorno legítimo. Cada caso tendrá un estado esperado explícito derivado del oráculo.
3. Casos deliberadamente ambiguos/incompletos: empate no resoluble, borde sin convención física, ciclo sin cota de cola y recursos insuficientes. Deben rechazar con el motivo esperado; no se incluyen en el denominador de casos completos, pero son negativos obligatorios.
4. La red Iris congelada de 16 interferómetros y ocho modos, con entradas crudas baseline/phase/sham y geometría Blender efectivamente capturada. Debe producir certificados de los campos, potencias y salidas necesarios para la tarea; las muestras próximas a un límite pueden requerir decisión `UNDECIDABLE` y se contabilizan como tal.

La lista exacta de archivos, sus hashes, los intervalos de admisión, las tolerancias de utilidad y los presupuestos de recursos se fijarán **después de antecedentes y antes de nuevos datos confirmatorios**. Este documento fija la afirmación y sus reglas de rechazo; no inventa un registro externo ni finge que la captura/ejecución nativa ya existe. Un criterio de utilidad fallido produce `INCONCLUSIVE_OR_NOT_USEFUL`, no confirma H1 por ausencia de contraejemplos.

## Comparadores y predicciones separadas

| Comparador | Qué permite contrastar |
|---|---|
| Referencia geométrica exacta Fraction/intervalos | Identidad de entradas, first-hit, topología, completitud y cotas del modelo representado |
| Trazado geométrico convencional y variante GPU sin certificación | Calidad/robustez y coste añadido del certificado bajo iguales escenas y salidas |
| Circuito/DAG algebraico equivalente | Corrección de la reducción de caminos y coste cuando la estructura es conocida |
| Operador matricial complejo optimizado CPU/GPU | Coste del cálculo equivalente; incluir formación/actualización del operador cuando la geometría cambia |

La hipótesis de eficiencia será separada y se preregistrará en el punto de comparación/coste: misma tarea, precisión, salidas y preparación. Ningún número de rayos o triángulos constituye una predicción de capacidad o ventaja. Si una supuesta mejora desaparece al incluir todos los costes o al igualar el trabajo, se rechazará esa hipótesis de rendimiento aunque H1 sea válida.

## Dominio y límites explícitos

- Óptica escalar ideal, geometría finita y datos representados con convenciones declaradas. Polarización, difracción, modos guiados, dispersión, fuente/detector físicos y fabricación requieren modelos y mediciones adicionales.
- Interferir sólo campos de modos/frecuencias/estados de coherencia compatibles; potencias de salidas ortogonales no se suman como si fueran un único campo coherente.
- La fase depende de longitud óptica y referencia común. Un desplazamiento de origen o una renormalización no demostrados pueden cambiar el problema.
- Una aceleradora espacial no demuestra selección exacta ni completitud de candidatos. Todo caso no representable o no acotado debe quedar declarado.
- Los resultados históricos 29/30 y 450 acuerdos nativo/referencia son antecedentes del proyecto; no son test nuevo de H1 ni prueba de generalización/novelty.

## Estado de registro y artefactos

Contrato legible por máquina: [contribution_contract_v1.json](research/contribution_contract_v1.json). Es un registro local versionado de formulación. **Registro externo/IPFS: no obtenido.** No se presenta como preregistración externa. La literatura y el diseño confirmatorio siguen pendientes; no se han recogido nuevos datos confirmatorios para H1 en este cierre.

El recibo `point00_completion.json` fija las preimágenes del cierre en el commit `daf5b2e`; el archivo de progreso es un documento vivo y sus versiones posteriores no sustituyen aquella preimagen. La versión histórica se recupera desde ese commit para comprobar su hash.

![Pregunta, contraste y salida certificada](assets/certified-coherent-research-question.svg)

El esquema representa el método propuesto y las comprobaciones requeridas, no una ejecución RT ya completada. El consejo JEV de este cierre tuvo exit 0, status connected y provenance jev; recomendó una formulación falsable con utilidad y conservar como pendientes experimento y novedad.
