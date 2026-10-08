# Punto 1: bloqueo de entrada cerrado en CPU

El piloto histórico `native02` terminó con `ValueError: pinned packet`, cero dispatches y cero readbacks. Su manifiesto contiene rutas relativas al repositorio, emitidas así por `robust_first_hit_prepare_v1.py`. El worker exigía rutas absolutas y, después de esa validación, cargaba rutas relativas al directorio de proceso. Ambas operaciones incumplían el formato portable del preparador.

La corrección usa `pinned_packet_path` tanto para admisión como para carga, resolviendo las rutas relativas respecto al checkout del worker. Conserva la compatibilidad con rutas absolutas, la comprobación SHA-256, la existencia del fichero y la extensión JSON. No modifica el shader, paquetes, respuestas esperadas ni reglas geométricas.

El manifiesto preregistrado permanece idéntico: SHA-256 `1ba451212cc136442ea34a1ec9a7cefd44fdf366211f28813590f21b732ba800`, 13 casos, 20 consultas. La regresión reprodujo el fallo antes de la corrección en dos pruebas de admisión relativa. Después pasan 21 pruebas: cinco de admisión, doce del selector exacto y cuatro del recibo supervisor. Incluyen rechazo de hash alterado, archivo ausente y readbacks incompletos/reordenados.

Evidencia: [recibo CPU](validation/first-hit-admission-2026-10-08/cpu_regression.json). Reproducción, desde la raíz del checkout:

```powershell
python -B -X utf8 -m unittest Blender.tests.test_robust_first_hit_native_inputs_v1 Blender.tests.test_robust_first_hit_exact_v1 Blender.tests.test_robust_first_hit_gpu_guard_v1 -v
```

El cierre certifica la compatibilidad de entrada. El punto 2 exige ejecutar y auditar separadamente las 20 consultas en GPU nativa; este resultado CPU no certifica propagación multicamino, fase ni comportamiento físico.
