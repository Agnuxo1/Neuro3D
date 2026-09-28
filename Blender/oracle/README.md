# Oráculo analítico MZ (OPT-006, Claude)

Referencia independiente del motor de `OPT-002`: fórmulas cerradas del
Mach-Zehnder, escritas sin reutilizar `Blender/core`. Solo biblioteca
estándar y CPU.

- `mz_oracle.py`: línea base monocamino (EXP-000), MZ en forma cerrada y por
  matrices complejas (dos derivaciones), coherencia parcial γ, promedio
  temporal con frecuencias distintas, geometría de desplazamiento de espejo,
  solape gaussiano y línea de retardo.
- `test_mz_oracle.py`: 14 autocomprobaciones. Ejecutar
  `python -m unittest` desde esta carpeta (0,01 s).
- `make_expected.py` → `expected_values.json`: valores esperados de T0-T6.

- `geometry_oracle.py` (OPT-009): fase en frente de onda común en BS2, MZ
  cuadrado frente a no rectangular (construye posiciones y normales), línea de
  retardo y balance con categorías separadas (escape frente a pérdida
  material). No importa el motor de Codex. Pruebas en
  `test_geometry_oracle.py`; con `python -m unittest` se ejecutan las 26.

La convención del divisor está en la cabecera de `mz_oracle.py`. Si `OPT-002`
adopta otra, los puertos A y B pueden intercambiarse, pero la suma y la
visibilidad no cambian. No es un resultado experimental ni simula fotones.
