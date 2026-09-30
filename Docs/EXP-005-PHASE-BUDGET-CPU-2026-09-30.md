# Presupuesto de fase del transporte de longitud de onda

Preparación CPU opt-in, 30/09/2026. No cambia runners ni shaders congelados,
no traza geometría y no calcula salidas neuronales. Es una especificación
prospectiva para criticar antes de integrar un nuevo contrato GPU.

Las habilidades de continuidad y pruebas enfocadas han guiado la conservación
de los controles iniciales y la adición de adversarios, sin repetir la suite
completa ni sustituir resultados nativos por cálculos de referencia.

## Qué comprueba

`phase_transport_budget_v1.wavelength_phase_budget` recibe explícitamente:

- longitud de onda original;
- presupuesto relativo de su representación hi-lo;
- cota declarada de la longitud efectiva máxima, en unidades Blender;
- presupuesto del error de fase no envuelta, en radianes.

Primero aplica el candidato de transporte escalar. Después acota únicamente
el error de fase atribuible a cambiar lambda por lambda_decodificada:

`2*pi_superior*L_max*abs(lambda_decodificada-lambda)/(lambda*lambda_decodificada)`.

Usa fracciones exactas de los valores float64 y una constante racional superior
a pi; la representación decimal del resultado se redondea hacia arriba. Así
evita que un producto pequeño o un denominador diminuto se redondeen primero
a cero en una comprobación float64. La comparación con el presupuesto usa la
fracción, no un float redondeado del resultado.

El llamador todavía debe justificar la cota L_max antes de utilizar el resultado:
incluye camino acumulado y desplazamiento hasta la referencia terminal. No vale
usar solo la extensión de la escena o la distancia del último segmento.

## Experimento CPU retenido

Budgets prospectivos: error relativo <=1e-12 y fase <=1e-4 rad. Se conservan
los ocho controles iniciales (cuatro longitudes de onda, L_max=2 y 1e6).
El primer informe no rechaza ninguno. Se añaden dos longitudes de onda
no exactamente reconstruidas; el segundo informe retiene los doce casos.
No se han ajustado presupuestos para producir el resultado.

Dos casos largos son rechazados por el presupuesto de fase aunque pasan el
presupuesto relativo de transporte. Por ejemplo, lambda=1.11111111111111e-6
tiene error relativo 7.623296525e-16; la contribución acotada es aproximadamente
8.62e-9 rad a L_max=2, pero 0.004310872625 rad a L_max=1e6. La misma lambda
puede ser aceptable para una cota corta y no para otra larga.

Esto no demuestra un fallo GPU ni que nuestra malla actual acumule un camino
de 1e6 unidades. Es una prueba del criterio numérico prospectivo y un límite
para no extender el dominio silenciosamente.

Ocho tests enfocados pasan (0.006s): controles exactos, monotonía respecto a
longitud, redondeo superior, presupuesto cero, entradas inválidas, colapso de
lambda incluso con longitud cero, conservación de todos los casos y rechazo
del adversario de camino largo.

## Exclusiones obligatorias

Aceptar este componente NO certifica el campo complejo total. No incluye
cuantización de mallas, acumulación de longitudes, campos de fuente, referencias
de modo, reducción de argumentos en GPU ni amplificación por suma de caminos.
Una lambda exactamente reconstruida puede dar cota cero aquí y aun así fallar
por cualquiera de esos mecanismos. No calcula una matriz U ni sustituye la
inferencia basada en escena.

## Evidencia y siguiente paso

- Informe inicial de ocho controles:
  `D:/PROJECTS/.cognition/neuro3d/exp005_phase_budget_20260930_0753.json`.
- Informe ampliado, con seis hashes de dependencias:
  `D:/PROJECTS/.cognition/neuro3d/exp005_phase_budget_20260930_0756.json`.
  SHA256 `915edfcb8734662cc620cf146dd3432c527a1bd25390bebd6661f697cd218650`.

```powershell
python -B -m unittest discover -s Blender/tests -p test_exp005_phase_budget.py
```

Claude tiene solicitada la revisión independiente PRECISION-006 después de
PRECISION-005; este prototipo es contexto adicional, no otra tarea simultánea.
Antes de integrar: crítica de la cota efectiva, presupuesto conjunto de error,
reglas de rechazo y nuevo contrato. La ventana GPU sigue cerrada. JEV bloqueado
por seguridad: fallback local identificado, sin aval remoto.
