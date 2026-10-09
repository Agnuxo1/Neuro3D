# Preinscripcion: validacion anidada de Motor Imagery (modelos opticos)

Fecha de fijacion: 2026-09-30, 04:05 UTC (hora local 06:05), ANTES de ejecutar la rejilla `full`. Autor: subagente Claude (tarea "nested").
Cualquier cambio posterior de la rejilla, de las reglas o de los estimadores debe ir en una seccion "Enmiendas" con fecha, y los resultados
deben informar de ambas versiones.

## 0. Estado de conocimiento (honestidad sobre el sesgo residual)
Quien fija esta rejilla ya conocia los LORO historicos (libre 0,697; polar 0,682 -> 0,713 con f12w3; lattice32 0,677 -> 0,687). La rejilla se
construye con esas dos features (`f8w1`, `f12w3`) y esos tres modelos, luego el CONTENIDO de la rejilla no es independiente de los datos.
La anidacion elimina el sesgo de elegir DENTRO de la rejilla mirando el test externo, pero no el de haber elegido la rejilla. El unico
control totalmente limpio es el test oculto de Kaggle (que, ademas, esta limitado a 2 envios al dia y ya usados hoy).
Para acotar ese sesgo la rejilla incluye alternativas perdedoras (f8w1, wd mayor, mas y menos epocas, libre) y se informa de la media de la rejilla.

## 1. Datos y particion
- 17 sujetos (S001..S020 sin 8, 13, 15). Entrenamiento etiquetado por `run` (campo `run` de `work/data/S###.npz`): 3 runs de 50/50/10 epocas
  (S006: 25/50/10; S007: solo runs 1 y 3: 50/10). El test oculto de Kaggle (40 epocas por sujeto) NO se usa en nada.
- Bucle externo: leave-one-run-out (LORO) por sujeto, igual que `bench.py` con `CV=loro` (semilla del entrenamiento = indice del fold).
- Bucle interno: dentro del entrenamiento externo (los runs restantes), leave-one-run-out interno. Grupo = `run`. Nunca se mezclan epocas
  de un mismo run entre entrenamiento y validacion internos, y el run externo de test no aparece en el bucle interno. Se verifica con
  aserciones en `nested_bench.py` y con `test_nested_groups.py` (datos reales, 300 disposiciones aleatorias, indices guardados).
- Fold interno valido: entrenamiento interno >= 20 epocas y validacion interna >= 10 epocas. Con la estructura de runs real esto deja
  1 fold interno valido cuando el run externo de test es el 1 o el 2 (entrenar con el otro run grande, validar en el run 3 de 10 epocas) y
  2 folds cuando el run externo es el 3. Sin folds internos validos (S007 entero) se usa la configuracion por defecto (seccion 3, N3).
  LIMITACION DECLARADA: la validacion interna de 2 de cada 3 folds externos son solo 10 epocas, muy ruidosa; se espera que la seleccion
  por sujeto (N1) tenga poca potencia. Por eso se declara tambien N2 (seleccion global entre sujetos), que no depende de ese ruido.

## 2. Rejilla declarada (36 configuraciones = 12 entrenamientos x 3 instantaneas de epoca)
- Modelo: `polar` (malla unitaria 8x8 por banda, descomposicion polar), `lattice32` (rejilla fisica 4x4, 16 tejados + 16 enlaces = 32 retardos
  por banda), `free` (matriz compleja 8x8 por banda).
- Features: `f8w1` = 8 bandas (8,10,12,14,17,20,24,28 Hz), 1 ventana; `f12w3` = 12 bandas (6,8,10,12,14,16,18,20,23,26,30,35 Hz), 3 ventanas.
- Decaimiento de pesos (AdamW): 1e-3, 1e-2. lr = 2e-2 y batch 32 fijos (como el historico).
- Epocas: 30, 60, 90 (una sola ejecucion de 90 epocas guarda las tres instantaneas: la trayectoria es identica hasta cada epoca; comprobado en el test).
- Escalado por banda/canal con la std del entrenamiento (`--norm train`, como `bench.py`). Una semilla por entrenamiento en la rejilla.

## 3. Estimadores declarados (todos calculados en `analyze_nested.py` sobre logits crudos guardados)
- Metrica: exactitud del sujeto agrupada sobre sus epocas de test externo (como `bench.py`), media entre 17 sujetos. Sin ponderar por sujeto.
- N1 (PRIMARIO): por sujeto y fold externo, se elige la configuracion de menor log-loss (BCE) de validacion interna agrupada (ponderada por
  tamano del fold interno) sobre los folds internos validos; se puntua en el run externo con la configuracion reentrenada sobre todo el
  entrenamiento externo. Empates -> configuracion por defecto. Sin fold interno valido -> defecto.
- N1b (sensibilidad): igual pero criterio = exactitud de validacion interna (desempate BCE, luego defecto).
- N2 (PRIMARIO 2): seleccion global "leave-one-subject-out": para el sujeto s, la configuracion con mayor LORO medio sobre los otros 16 sujetos.
  Estimador limpio de "elegir una sola configuracion de la rejilla con otros sujetos y aplicarla a uno nuevo".
- N3 (REFERENCIA): configuracion fija `polar | f12w3 | wd 1e-3 | 60 epocas` = la del pipeline actual. Su cifra historica (0,713) esta
  contaminada por seleccion (se eligio mirando LORO), por eso NO es un "a priori limpio"; el sustituto limpio es N2.
- Referencias sesgadas (solo para medir optimismo, nunca para informar rendimiento): MAX_LORO = mejor configuracion de la rejilla por LORO
  medio (sesgada al alza), MEAN_over_grid = media de las 36, ORACLE_per_subject = mejor configuracion por sujeto.
- Optimismo estimado = MAX_LORO - N2 y MAX_LORO - N1.
- Contrastes (emparejados por sujeto, IC95% bootstrap por sujetos con 20 000 remuestreos, p por permutacion de signos): N1-N3, N2-N3, N1-N2,
  N1-MEAN_over_grid, N3-MEAN_over_grid. Para juzgar "distinguible del ruido" se exige IC95% que excluya 0; con 5 contrastes primarios el
  umbral Bonferroni es p < 0,01.
- Efectos marginales por dimension (modelo, features, wd, epocas), emparejados por sujeto (descriptivo).
- Diagnostico de la validacion interna: Spearman medio entre la BCE interna y la exactitud externa a traves de las 36 configuraciones, por fold.
- Frecuencia con que se elige cada configuracion y cada nivel de cada dimension (N1, N1b, N2).
- Exploratorio (no primario, sin correccion; todos se calculan de logits ya guardados, sin reentrenar):
  E1/E2 conjuntos por media de logits `polar+lattice32` y `polar+lattice32+free` en la configuracion por defecto;
  T1 umbral en la mediana de los logits del run de test (sin etiquetas; supone test equilibrado) solo en folds externos exactamente
  equilibrados (runs 1 y 2 con 25/25), frente al umbral 0; ademas el sesgo de prior medio (fraccion predicha 'move' menos real).

## 4. Criterios de decision
- "Seleccion interna util" solo si N1 - N3 > 0 con IC95% que excluye 0 y Spearman medio < 0 (BCE baja <-> exactitud alta) con fraccion positiva < 0,5.
- Si N1 <= N3 y N2 <= N3: la cifra historica de N3 esta inflada por seleccion en la magnitud MAX_LORO - N2 y no debe usarse para elegir entre
  variantes cuya diferencia sea menor que esa cantidad.
- Cualquier configuracion nueva para un envio a Kaggle debe salir de N2 (o de N1 si N1 - N3 es significativa), no de MAX_LORO.
- Envios a Kaggle: 2 por dia, preferiblemente de modelos opticos; siempre informar antes de enviar. Esta tarea no envia nada.

## 5. Etapas de ejecucion (las lanza Claude principal por la cola gpuq; el subagente solo ejecuto la prueba de humo en CPU)
- Etapa 0 (hecha): humo en CPU, 2 sujetos, rejilla minima (`--grid smoke`), y `test_nested_groups.py`.
- Etapa 1: rejilla `full`, solo bucle externo (`--no-inner`), 17 sujetos -> N2, N3, MAX, marginales, tabla LORO de 36 configuraciones.
- Etapa 2: rejilla `full` completa con bucle interno, primero en 5 sujetos fijados por orden de identificador (`S001,S002,S003,S004,S005`, sin mirar
  su rendimiento) para medir coste y el primer N1; despues los 17.
- Etapa 3 (ideas de mejora, ver informe): cada una se preinscribe en una enmienda antes de correrla. Ya implementadas en el codigo, sin cambiar la
  rejilla: `--seeds 5` (promedio de logits de 5 semillas en el bucle externo; semillas k+1000*s) y `--norm run` (escalado por run sin etiquetas).

## Enmiendas
- Enmienda 1 (2026-09-30 04:09 UTC, antes de cualquier ejecucion `full`): se anade el exploratorio T1 y se anaden `lattice32|f12w3` y `free|f12w3` a la
  rejilla de humo. La rejilla `full` y los estimadores primarios no cambian.
