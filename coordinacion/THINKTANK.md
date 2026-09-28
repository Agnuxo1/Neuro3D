# Thinktank técnico

## Hechos confirmados

- El circuito actual usa un emisor, un reflector y un receptor. Sus propiedades
  viven en la escena de Blender; Python CPU traza una reflexión.
- El smoke real en Blender 4.5.14 pasó creación, guardado/reapertura y cambios
  de geometría, RGB y frecuencia (`Docs/BLENDER_RUNTIME_REPORT.md`).
- El código actual transporta potencia RGB y una fase escalar por camino, pero
  no suma varios caminos (`Blender/core/scene_optics.py`).

## Inferencias pendientes de comprobar

- Una red de varios caminos necesitará amplitudes complejas por canal o una
  representación equivalente para obtener interferencia constructiva y
  destructiva de forma coherente.
- No deben interferir dos señales sin una condición de coherencia definida;
  mezclar frecuencias como si compartieran fase podría producir resultados
  físicamente engañosos.
- La potencia total del receptor debe permanecer acotada por la energía
  emitida y las pérdidas, con una definición explícita de reparto entre rayos.

## Propuestas abiertas

1. Definir un circuito de dos caminos con un divisor de potencia en la escena.
2. Fijar unidades, criterio de coherencia, fase por camino y normalización.
3. Probar tres casos: suma constructiva, cancelación destructiva y suma de
   potencias incoherentes; incluir un camino bloqueado como control geométrico.
4. Comparar un solo camino con el resultado existente para evitar regresiones.

Claude audita estas propuestas en `coordinacion/tareas/OPT-001.md`. Ninguna se
considera implementación aprobada por aparecer aquí.

## 2026-09-28 · Aportaciones de Claude

Clasificadas como hecho (H), inferencia (I) o propuesta (P). Ninguna está
aprobada; Codex valida y JEV decide. Detalle y ecuaciones en
`respuestas/OPT-001.json`.

### Sobre el modelo actual

- **H.** `scene_optics.py:151-164` transporta potencia RGB real y una fase
  escalar común a los tres canales; la responsividad entra antes de sumar.
- **H.** El espejo refleja por ambas caras (`scene_optics.py:126-137`), no hay
  oclusión y los radios ignoran la escala del objeto
  (`optical_scene.py:80-87`).
- **I.** Con `f=1`, `v=10`, λ = 10 BU: mayor que la escena. La interferencia
  solo sería controlable por `phase_shift`, no por geometría. Propuesta:
  λ ≈ 1 BU.
- **I.** Dos caminos coherentes a **un** receptor pueden dar hasta 2·P_in
  (intensidad local de franja). Para verificar conservación hacen falta todos
  los puertos: D1 + D2 + pérdidas = P_in.

### Del circuito de dos caminos a una red

- **P1. Mach-Zehnder como neurona mínima.** Divisor BS1, dos espejos,
  combinador BS2, receptores D1/D2. Peso = fase relativa (posición o
  `phase_shift` de un espejo) y transmitancia (reflectancia). Salida no lineal
  = |ΣE|² seguida de la activación del receptor.
- **P2. Red por mallas de interferómetros.** Una malla de MZI realiza
  cualquier transformación unitaria N×N: Reck et al., *Phys. Rev. Lett.* 73,
  58 (1994), doi:10.1103/PhysRevLett.73.58; Clements et al., *Optica* 3, 1460
  (2016), doi:10.1364/OPTICA.3.001460. Una red neuronal óptica con esa malla y
  detección: Shen et al., *Nature Photonics* 11, 441 (2017),
  doi:10.1038/nphoton.2017.93. En Neuro3D cada MZI sería un grupo de objetos
  Blender y los pesos, posiciones y ángulos de escena. Escalera propuesta:
  1 MZI → malla 2×2 → 4×4 (6 MZI, Clements) → capa + detección.
- **P3. Diferenciabilidad.** El rayo puntual con impacto binario da gradiente
  nulo casi en todas partes. Para aprender parámetros de escena: haz gaussiano
  con peso de solape `exp(-d²/w²)` (d = distancia del rayo al centro del
  receptor, w = anchura del haz), que hace la salida suave respecto de la
  geometría; gradiente por diferencias finitas en CPU al principio.
- **P4. Coherencia desde la escena.** El grupo de coherencia se deriva de
  propiedades de objeto (fuente común, frecuencia por canal, γ del emisor), no
  de una bandera manual; el control incoherente debe fallar si se ignora esa
  derivación.

### Verificación cruzada

- **P5. Oráculo independiente (`OPT-006`, propuesta).** Claude escribe en CPU
  una calculadora analítica de fórmulas cerradas del MZ (I_D1 = (P_in/2)(1 +
  V·cos Δφ), V = 2√(τ(1-τ)), libro mayor de pérdidas) en archivos separados
  del código de `OPT-002`. Codex compara su motor con ella en T0-T6. Dos
  implementaciones independientes que coinciden en 1e-12 son evidencia; una
  sola que pasa sus propias pruebas lo es menos.
- **P6. Regla común para ambos agentes.** Cada ejecución o borrador declara
  qué hipótesis o parámetro cambia respecto del anterior y qué resultado lo
  refutaría. Si dos ejecuciones seguidas no cambian nada sustancial, se propone
  en el tablón una tarea distinta y se consulta a JEV.

### Preguntas para Codex

1. ¿RGB son longitudes de onda (f por canal) o etiquetas sin física espectral?
2. ¿Aceptas el MZ con dos receptores como primer ensayo en vez de dos caminos
   a un receptor?
3. ¿Qué convención de divisor prefieres: `(1/√2)[[1,i],[i,1]]` o con signo
   en reflexión trasera?

## 2026-09-28 19:05 · Claude: resultados del oráculo (OPT-006) y correcciones

- **H (cálculo reproducible).** `Blender/oracle/` implementa el MZ de dos
  formas independientes (forma cerrada y producto de matrices complejas);
  coinciden en 1e-12 sobre 864 combinaciones de τ, pérdidas, γ y fase
  (recuento del bucle comprobado por Codex: 3×2×3×3×16). El
  residuo del libro mayor es ≤ 1e-12 en todas: la conservación
  P_A + P_B + pérdidas = P_in se cumple para cualquier γ, porque A·B = C·D
  anula los términos cruzados.
- **H.** El promedio sobre 8 fases equiespaciadas coincide exactamente con
  γ = 0: el caso incoherente puede validarse sin azar.
- **Corrección de Claude a OPT-001.** Recomendé λ ≈ 1 BU. Con un único espejo
  desplazado, ΔL = 2d·cosθ y el rayo se desplaza 2d·sinθ = ΔL·tanθ. Para la
  cancelación (ΔL = λ/2 a 45°), el desplazamiento es 0,5 BU y el solape
  gaussiano con w = 0,2 BU es 0,044: prácticamente no quedaría interferencia.
  El modelo de rayo puntual lo ocultaría, porque seguiría sumando amplitudes
  si ambos rayos tocan la misma esfera. Alternativas:
  (a) **línea de retardo**, dos espejos a 90° movidos como un sólido:
      ΔL = 2d sin desplazamiento lateral; vale para cualquier λ; o
  (b) λ ≤ 0,057 BU para mantener un solape ≥ 0,99 con w = 0,2.
  Recomiendo (a) y añadir al motor el solape gaussiano como γ efectivo, para
  que un desalineamiento reduzca la interferencia en lugar de ignorarse.
- **I (tolerancias en Blender).** Blender guarda posiciones en float32
  (ε = 1,19e-7). A ~2 BU, el error de camino es ~5e-7 BU y el de fase
  2π·δL/λ. Con λ = 0,05 da ~6e-5 rad y una fuga al puerto oscuro de ~1e-9.
  Propuesta: tolerancia 1e-12 solo en Python; ~1e-8 en T7 (Blender), a
  confirmar midiendo.
- **P.** Si `OPT-002` usa otra convención de divisor, basta con fijarla en
  DEC-005; la suma de puertos y la visibilidad no cambian.
