# Neuro3D · Programa comparativo propuesto

Estado: **diseño, sin ejecutar**. 2026-09-29. La batería amplia empieza solo
cuando haya una red estable cuya inferencia dependa causalmente de la escena.
La autorización del usuario para GPU y Blender está vigente; no constituye
por sí sola una reserva de recursos ni convierte el prototipo digital en red
óptica funcional. JEV no pudo validar esta propuesta en este turno:
el conector quedó bloqueado y la revisión de seguridad rechazó enviarle
el estado del proyecto. Revisión independiente y consulta JEV pendientes.

## Gates antes de comparar aplicaciones

1. **Causalidad de una celda (EXP-003):** impactos y longitudes derivados
   del `scene.ray_cast` tras guardar/reabrir, cinco desplazamientos, sham,
   ablación, balance y umbrales ya congelados. No se admiten distancias
   analíticas como respaldo de inferencia.
2. **Red mínima estable:** al menos cuatro entradas y cuatro salidas con
   varios caminos/elementos ajustables; salida reproducible tras reabrir;
   intervención geométrica cambia la salida prevista y sham no la cambia;
   tests de energía, tolerancia numérica y topología. Definir umbrales y
   congelar fixture antes de medir. Un MZI aislado no satisface este gate.
3. **Equivalencia de implementación:** separar tres vías en los informes:
   (a) simulación digital que lee parámetros de escena, (b) ray tracing
   geométrico que decide impactos/longitudes, (c) acumulación e interferencia
   ejecutadas por shader/escena. No atribuir a (b) resultados de (c) ni
   inferir ventaja energética de ninguna simulación por usar GPU.

## Batería escalonada tras los gates

| Orden | Hipótesis falsable | Comparadores mínimos | Métrica primaria |
|---|---|---|---|
| 1 · señal y fase | Geometría/interferencia ofrece ventaja en tareas dependientes de fase relativa, con fase global como perturbación irrelevante | MLP real sobre las mismas componentes, red compleja y clasificador lineal | Error en test oculto y robustez al cambio de fase global |
| 2 · memoria secuencial | La dinámica de la red retiene información útil a retardos largos | GRU/LSTM y red unitaria, con presupuestos de parámetros y entrenamiento publicados | Exactitud de copia/recuerdo frente al retardo |
| 3 · visión pequeña | Una codificación espacial de 16–64 modos mejora una tarea visual a igual presupuesto | Regresión logística, MLP y CNN pequeña | Exactitud y calibración en test oculto |
| 4 · robustez/olvido | La geometría da estabilidad ante perturbación o tareas secuenciales | Los mismos modelos con perturbación equivalente y regularización comparable | Degradación de exactitud y olvido medio |
| 5 · sistemas | Trazar la red en GPU mejora una frontera de calidad/latencia/memoria | Implementación matricial optimizada y ray tracing de igual función | Latencia p50/p95, throughput, VRAM y energía solo si se mide de forma válida |

Creatividad, programación, matemáticas e «inteligencia» general quedan como
**hipótesis posteriores**, no se extrapolan de dígitos ni de una celda.
Requieren tareas operativas y baselines de capacidad comparable; no afirmar
ventaja sin esos experimentos.

## Reglas comunes de comparación

- Congelar generador/dataset, particiones train/validación/test y seeds antes
  de entrenar. Ajustar normalización y selección de hiperparámetros solo
  con train/validación; evaluar el test oculto una vez por protocolo.
- Igualar información de entrada, tarea y criterio de calidad; informar
  parámetros **y** tiempo de ajuste, cómputo, precisión numérica y coste de
  pre/postprocesado. Igual número de parámetros por sí solo no iguala coste.
- Registrar resultados por seed, intervalos de incertidumbre y controles
  de etiquetas barajadas, geometría aleatoria/congelada, sham y ablación.
  Publicar también resultados negativos. Corregir comparaciones múltiples
  o reservar un test final independiente si se prueban muchos nichos.
- Para rendimiento: calentamiento, sincronización GPU, lotes 1 y mayores,
  tiempos de construir/actualizar escena, transferencias y medición
  end-to-end. La energía del equipo necesita medición apropiada; TDP,
  ocupación de GPU o FLOPs teóricos no son julios por inferencia.
- Antes de cada corrida reservar `gpuq`, comprobar RAM/VRAM, procesos de
  Claude y duración máxima; una sola carga larga a la vez. Guardar versión
  de código, escena, drivers, Blender y hardware junto con resultados.

OPT-007 corregido (simulación digital exploratoria) sirve para diseñar
controles, no como resultado de la batería: en cinco seeds, dígitos 4×4
dio 0,8933 frente a 0,8844 de regresión logística y 0,8841 de MLP;
Iris 0,7867 frente a 0,9200 de regresión logística. Codex leyó el JSON
y comprobó que el escalado se ajusta después del split, pero no reprodujo
el entrenamiento ni verificó la inferencia en Blender. No hay evidencia
de mejora de velocidad, memoria, energía o inteligencia.

Metodología externa orientativa: [MLPerf Inference](https://mlcommons.org/working-groups/benchmarks/inference/)
define comparaciones representativas y reproducibles;
[MLPerf Power](https://docs.mlcommons.org/inference/power/) requiere
instrumentación específica para energía. No se presenta este programa
como una prueba oficial MLPerf.
