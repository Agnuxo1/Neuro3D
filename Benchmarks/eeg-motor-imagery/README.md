# Benchmark EEG Motor Imagery (validacion anidada)

Codigo, evidencias y limites del benchmark de decodificacion de imaginacion motora (17 sujetos, 8 canales) usado para evaluar los modelos opticos frente a FBCSP y EEGNet. Estado: **validacion anidada verificada; superioridad NO establecida**.

## Contenido

| Carpeta | Contenido |
|---|---|
| `codigo/work/` | Modulos del benchmark (`bench.py`, `lattice_torch.py`) y `nested/` con el analisis anidado (`nested_bench.py`, `analyze_nested.py`, `bias_inventory.py`, `test_nested_groups.py`, `predict_var.py`, `run_*.sh`) y `prep.py` (preparacion de datos desde el zip de la competicion). |
| `codigo/MANIFEST-SHA256.txt` | Origen de cada archivo: SHA-256 del original, SHA-256 de la copia, cambios de portabilidad. |
| `evidencia-validacion-anidada/` | Preinscripcion, addendum, informe, resultados JSON y TXT, logs, inventario de sesgos y los JSON historicos de LORO (`bench-historico/`). Bytes originales, sin conversion (`.gitattributes`). |
| `evidencia-validacion-anidada/RAW-NPZ-MANIFEST.txt` | Hashes de los 36 `.npz` derivados. Los datos no se redistribuyen. |

## Cifras (fuente: `results_full.json`, `results_seeds5.json` y la auditoria de `AUDIT-EEG-NESTED`)

Exactitud media por sujeto, 17 sujetos.

| Estimador | Valor | Nota |
|---|---:|---|
| N2 (eleccion por sujeto, excluyendo al evaluado) | 0,7274 | Estimador anidado principal |
| Media de las 36 configuraciones de la rejilla | 0,6912 | Cota sin seleccion |
| Maximo LORO de la rejilla (optimista) | 0,7285 | Mirando los resultados |
| Media por modelo (12 configuraciones cada uno) | free 0,7041; polar 0,6907; lattice32 0,6787 | |
| Bases (LORO no anidado) | FBCSP 0,6526; EEGNet 0,6273 | Sin rejilla anidada comparable |

Diferencia matriz libre frente a malla polar: +0,0134 a favor de la libre (p = 0,0015; 15 de 17 sujetos). La matriz libre **no es una malla unitaria realizable**.

## Lo que la validacion anidada sostiene

- El procedimiento esta bien construido: sin fugas (normalizacion solo con el entrenamiento, particiones por sujeto y por run, aserciones en el codigo).
- El analisis se reproduce desde la evidencia cruda: `analyze_nested.py` regenera `results_full.json` y `results_seeds5.json` byte a byte.
- Los logits del codigo actual reproducen los guardados (un sujeto, una configuracion: diferencia maxima 4,7e-5).
- La direccion del efecto dentro de la familia optica es robusta.

## Lo que NO sostiene

1. **No establece superioridad frente a FBCSP ni EEGNet.** Esas bases no pasaron por el bucle anidado ni por una rejilla comparable. El modelo optico tuvo 36 configuraciones, cambio de caracteristicas y 5 variantes de arquitectura; las bases ninguna.
2. Los contrastes frente a FBCSP (p = 0,004 a 0,005) y EEGNet (p = 0,010) salen de `bias_inventory.py`: LORO no anidado, no preinscrito, con una configuracion elegida mirando ese mismo LORO. Son **exploratorios**. Polar frente a EEGNet no supera Bonferroni (0,05/10 = 0,005).
3. **`ADDENDUM-SEEDS5.md` es una enmienda post hoc.** Sus finalistas son el maximo LORO de una semilla por modelo. Su hipotesis H1 queda refutada (polar 0,7188 a 0,7113 con cinco semillas). `results_seeds5` esta degenerado (N1 = N3): no debe citarse como validacion anidada.
4. Un analisis parcial de 9 sujetos se genero a las 07:05, antes de terminar la ejecucion (17 sujetos a las 07:46). No estaba documentado; la rejilla no cambio despues.
5. No se puede demostrar con un diff que `nested_bench.py` no cambio a las 08:40, despues de `results_full.json`. Esto no tiene git ni copia previa que lo pruebe. Lo que si se verifico es que el codigo actual reproduce los logits del run de un sujeto.
6. El criterio Spearman de la preinscripcion tiene signo opuesto al de `analyze_nested.py`. No cambia la decision (N1 a N3 = -0,0119, IC95 incluye 0).
7. Las cifras de Kaggle (0,72-0,77 en la tabla publica) quedan por encima del LORO (0,69-0,73) y no estan explicadas.
8. Generalizacion: es un LORO dentro de sesion (tres runs por sujeto). No hay validacion en otros sujetos ni sesiones, ni en el test oculto de la competicion.

## Reproduccion

- **Analisis desde la evidencia (CPU, segundos):** restaurar `raw/full` y `raw/seeds5` de la copia de seguridad del proyecto y ejecutar

  ```bash
  NEURO3D_EEG_RAW=/ruta/a/nested/raw python -m unittest Blender/tests/test_eeg_evidence_integrity.py
  ```

  La prueba copia el analizador a una carpeta temporal y compara los JSON con los de `evidencia-validacion-anidada/`. Sin la variable, la prueba se omite.
- **Entrenamiento completo:** requiere los datos de la competicion de Kaggle (no incluidos, sujetos a sus reglas), `prep.py` para generar `data/S###.npz`, GPU o CPU y varias horas. No se recomienda ejecutarlo sin una preinscripcion nueva.

## Pendiente

- Incluir FBCSP y EEGNet dentro del mismo bucle anidado, con preinscripcion comprometida antes de ejecutar. Solo entonces podria afirmarse una comparacion limpia.
- Explicar la diferencia entre la puntuacion publica y el LORO.
