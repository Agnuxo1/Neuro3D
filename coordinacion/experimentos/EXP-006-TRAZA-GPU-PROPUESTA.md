# Siguiente mejora: de escena causal a evaluación de campos en GPU

Propuesta local de investigación, NO contrato congelado ni ventaja demostrada.
Depende de EXP-005 multicelda. No sustituye el trabajo ya asignado a Claude.
JEV bloqueado por seguridad: pendiente consulta autorizada, no eludir canal.

## 1. Cerrar física digital antes de optimizar

Codex aporta el oráculo independiente de triángulos y ledger de escapes.
Claude critica primer impacto, fase común, topología y contrasta un caso adverso.
Próximo gate: campos de todos los modos y S†S sobre escenas nuevas guardadas,
fuentes base y pares 1+1/1+i, incluyendo retirada de un espejo con rayos huérfanos.
No basta clasificar bien ni cerrar energía por normalización.

## 2. Compilar caminos, no predicciones

Una representación intermedia por camino contendría fuente, secuencia de objetos,
distancias medidas, coeficientes y puerto con referencia de fase. El evaluador GPU
recibe amplitudes y calcula propagación compleja, acumulación y detección; Python
solo organiza/controla y comprueba readback. No cargar intensidades precalculadas
ni una matriz de entrenamiento oculta y llamarlas transporte geométrico.

Válida mientras geometría/topología no cambia: todo cambio de malla/transformación
invalida caminos y obliga retrazado. Fase/lambda pueden reevaluarse sin retrazar
solo tras verificar que esos cambios no alteran geometría ni regla de reflexión.
En una red lineal también sería legítimo usar su matriz de transferencia medida;
debe ser una baseline explícita, no ocultarse para ganar una comparación.

Contrato futuro mínimo: amplitudes 1/i, fase/lambda/sham, invalidación al mover
espejo, todos los campos frente al oráculo y errores medidos de precisión GPU.
Portar a motor gráfico posterior no garantiza aceleración por sí solo.

## 3. Entrenamiento robusto ligado a geometría

Antes de entrenamiento largo: contraste de derivadas de intensidad respecto a
desplazamiento real de espejo con diferencias finitas centradas en escenas,
varios tamaños de paso y el modelo diferenciable de Claude. Detectar cambios
de topología donde la derivada deja de ser válida; no optimizar un circuito que
la escena no puede representar. Después entrenar con tolerancias de fase/posición
preinscritas y evaluar en perturbaciones reservadas sin reajustar el test.

## Comparación posterior, no promesa

Solo tras cerrar gates: misma función/entradas/precisión contra matriz CPU/GPU,
medir trazado inicial, compilación, transferencias, acumulación/readback, memoria,
warmup y tiempo total para lotes. Registrar casos donde el método pierde.
Memoria dinámica/no linealidad requieren un experimento separado con mecanismo
de estado definido: una malla lineal por sí sola no prueba memoria cognitiva.
