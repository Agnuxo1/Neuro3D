# Certificación secundaria de salidas observadas: método

Se prepara una validación determinista secundaria del resultado de grafo ya recogido, no un nuevo ensayo confirmatorio de H1. La referencia es el **modelo escalar afín representado** del archivo congelado. Los campos de entrada, longitud de onda, segmentos, fases y coeficientes permanecen exactamente los de esa captura; no se ajustan a las salidas.

La composición independiente usa intervalos racionales de 128 bits con redondeo exterior. Encierra π mediante Machin y series con resto, raíces mediante `isqrt`, trigonometría mediante Taylor/Lagrange y reducción con intervalo de π. Cada arco transporta intervalos complejos; las sumas coherentes y potencias se componen hasta los ocho terminales. El error de cada salida nativa observada se obtiene como su máxima distancia al intervalo de referencia.

Se fijan antes de ejecutar este análisis presupuestos de `10^-11` para campo (norma L1 compleja) y potencia absoluta. Son criterios de utilidad numérica del análisis, sin unidades de vatios calibrados. El argmax de R0/R1/R2 se certifica sólo si el intervalo de la potencia ganadora queda estrictamente por encima de los otros. Un solapamiento conserva una decisión desconocida.

Cinco controles verifican fase directa exacta, un divisor/fase no trivial frente a cálculo independiente de 90 dígitos, salidas falsas que exceden el presupuesto, empate sin decisión y rechazo de datos incompletos. El análisis requiere previamente la auditoría independiente de primeros hits y ramas. La vecindad interior de abanicos sigue siendo un predicado del productor validado por sus controles; no una comprobación independiente del nuevo auditor.

Esto puede acotar **esta ejecución nativa observada** frente al modelo exacto. No establece una cota universal de cualquier implementación libm/GPU, error respecto a una escena ideal pretendida, redondeos internos de las transformaciones Blender, difracción/polarización, calibración o un procesador fotónico físico. Esos dominios continúan explícitamente desconocidos. Una decisión correcta del estímulo unitario no es una medida de acierto Iris ni una generalización.

Código: [composición independiente](../Blender/blender_lab/state_graph_enclosure_v1.py), [CLI y auditoría](../Tools/certify_captured_graph_outputs_v1.py).
