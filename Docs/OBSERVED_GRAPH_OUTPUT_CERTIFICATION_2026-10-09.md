# Certificación secundaria de salidas observadas: método

Se prepara una validación determinista secundaria del resultado de grafo ya recogido, no un nuevo ensayo confirmatorio de H1. La referencia es el **modelo escalar afín representado** del archivo congelado. Los campos de entrada, longitud de onda, segmentos, fases y coeficientes permanecen exactamente los de esa captura; no se ajustan a las salidas.

La composición independiente usa intervalos racionales de 128 bits con redondeo exterior. Encierra π mediante Machin y series con resto, raíces mediante `isqrt`, trigonometría mediante Taylor/Lagrange y reducción con intervalo de π. Cada arco transporta intervalos complejos; las sumas coherentes y potencias se componen hasta los ocho terminales. El error de cada salida nativa observada se obtiene como su máxima distancia al intervalo de referencia.

Se fijan antes de ejecutar este análisis presupuestos de `10^-11` para campo (norma L1 compleja) y potencia absoluta. Son criterios de utilidad numérica del análisis, sin unidades de vatios calibrados. El argmax de R0/R1/R2 se certifica sólo si el intervalo de la potencia ganadora queda estrictamente por encima de los otros. Un solapamiento conserva una decisión desconocida.

Cinco controles verifican fase directa exacta, un divisor/fase no trivial frente a cálculo independiente de 90 dígitos, salidas falsas que exceden el presupuesto, empate sin decisión y rechazo de datos incompletos. El análisis requiere previamente la auditoría independiente de primeros hits y ramas. La vecindad interior de abanicos sigue siendo un predicado del productor validado por sus controles; no una comprobación independiente del nuevo auditor.

Esto puede acotar **esta ejecución nativa observada** frente al modelo exacto. No establece una cota universal de cualquier implementación libm/GPU, error respecto a una escena ideal pretendida, redondeos internos de las transformaciones Blender, difracción/polarización, calibración o un procesador fotónico físico. Esos dominios continúan explícitamente desconocidos. Una decisión correcta del estímulo unitario no es una medida de acierto Iris ni una generalización.

## Primer análisis conservado y ajuste de la composición

El análisis01 devolvió cotas válidas que excedían el presupuesto: campo L1 ≤ `1.5115874489789405e-7`, potencia ≤ `1.9253736898548343e-7`. Conservamos certificado y fuentes en [analysis01](validation/observed-graph-output-enclosure-2026-10-09/analysis01/evidence_index.json). El argmax representado de R0/R1/R2 quedó certificado como R1. Estas cotas no demuestran un error nativo de esa magnitud.

La pérdida de estrechez se localizó en el redondeo a la rejilla de 128 bits durante Horner: coeficientes de Taylor mucho menores que la rejilla reciben intervalos anchos que luego se amplifican por potencias. La nueva composición evalúa el polinomio **exactamente con fracciones** en el centro racional del ángulo reducido. Redondea sólo el intervalo final. Añade el resto de Lagrange y la suma de los radios del ángulo original y de la reducción por π, usando `|sin'(x)| ≤ 1` y `|cos'(x)| ≤ 1`. La reducción por un número entero de períodos no depende de aproximaciones flotantes. Para un radio demasiado ancho conserva `[-1,1]`.

Se mantienen los mismos presupuestos y salidas observadas. Siete controles incluyen el ángulo que dio la mayor anchura original y ángulos negativos, grandes y con radio explícito, frente a 90 dígitos independientes. Este método se publica antes de recalcular el certificado secundario.

Código: [composición independiente](../Blender/blender_lab/state_graph_enclosure_v1.py), [CLI y auditoría](../Tools/certify_captured_graph_outputs_v1.py).
