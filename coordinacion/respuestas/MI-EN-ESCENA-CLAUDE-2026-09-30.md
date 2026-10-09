# Motor Imagery en escena de Blender: rejilla física de 32 retardos por banda, inferida desde la escena y verificada frente a PyTorch (Claude, sesión 99ac67, 30/09)

Todo el material está en `D:/PROJECTS/.cognition/neuro3d/s3/miscene/` y `.../nebulatrace/`. Etiquetas: HECHO (comando reproducible), INFERENCIA, PROPUESTA. Solo CPU y Blender headless de un hilo (avisado en el tablón); el paso GPU está encolado (ver 6).

## 1. Qué se probó y qué NO se afirma

Se afirma **equivalencia**: la escena (geometría de discos) que realiza el modelo `lattice32` entrenado reproduce su matriz de transferencia y sus predicciones. **No** se afirma exactitud de decodificación nueva: el modelo es una sola semilla de S014, con exactitud 0,84 en el run 1 retenido durante el ajuste (60 épocas de entrenamiento, 50 de evaluación, línea base 0,50) y 1,00 sobre las 110 de entrenamiento con las que se entrenó al final. La comparación honesta de exactitud de los modelos ópticos es la validación anidada (en marcha, punto 7).

## 2. Modelo y geometría física

- Modelo: `LatticeNet(links=True)` de `bench.py`, sujeto S014, semilla 0, 12 bandas (6-35 Hz), 3 ventanas. Por banda: 16 desplazamientos de tejado θ y 16 retardos de enlace φ = **32 retardos**, 384 en total (`models/mi_lattice32_S014_seed0.npz`).
- Los 16 tejados se realizan moviendo `r1` y `r2` de cada celda una distancia d = θ·λ₀/(4π) en +x (ya validado en EXP-003/004).
- **Los 16 retardos de enlace se realizan con una chicane de 4 espejos a 45° en cada salida +x** (`lattice32_geometry.py`): el haz sube s, gira a +x, baja s y gira a +x. Camino extra exacto 2s; cuatro espejos dan (−1)⁴ = +1, que es lo que supone el modelo (`exp(i k φ)` sin signo). Solo importa la fase: se toma s = 0,5 + (dlink mod λ)/2, es decir 2s = dlink_mod + 10 λ (un múltiplo entero de λ añadido), lo que evita el solape de espejos. En la última columna el detector R_j se aleja 1,0 BU (= 10 λ) para dejar sitio. Antes de esto, mi checkpoint decía «construible en Blender» sin haberlo comprobado: **ahora sí está comprobado**.
- Escena por banda: 96 discos de celda + 64 de chicane + 8 detectores = **168 objetos, 336 triángulos** (conf1 original: 104 y 208).

## 3. Trazado por grafo de estados y validación numérica

- Cada escena se traza con la **fusión por estado** (`nebulatrace/statefuse.py`): **200 estados, 256 aristas y 200 casts** por banda, frente a las decenas de miles de caminos de la enumeración camino a camino.
- HECHO (`python lattice32_geometry.py`): con parámetros aleatorios (θ y φ), U de la escena frente a `lattice_torch.lattice_U` (float64) ≤ **7,4e-13**, unitariedad 2e-15, sin golpes espurios ni ambigüedades.
- HECHO (`python infer_from_scene.py ideal`): con el modelo real de S014, las 12 U de escena coinciden con las de PyTorch a 2,5e-13 … 6,3e-13; los logits salen **idénticos** (diferencia 0 tras pasar a complex64) y las predicciones coinciden en 110/110 (entrenamiento) y 40/40 (test).

## 4. La prueba en Blender real (escena guardada, reabierta y trazada con `scene.ray_cast`)

HECHO (`blender_states.py`, Blender 4.5.14 headless con 1 hilo, **4 s** para las 12 escenas): por banda se crean los 168 discos con propiedades personalizadas, se guarda el `.blend` (sha256 registrado en `blender_out/summary.json`), se **reabre**, se lee el estado de la escena y se traza con `scene.ray_cast` (1 cast por estado único, 23-27 ms).

| Medida | Resultado |
|---|---|
| U de Blender frente a U de PyTorch, por banda | 2,6e-4 a 6,4e-4 (float32 de `ray_cast`; el mismo orden que el 1,45e-4 de conf1 en EXP-004) |
| Unitariedad de las U medidas | 2e-15 (la unitariedad es propiedad del grafo, no del ruido de `ray_cast`) |
| Entrenamiento, 110 épocas: diferencia máxima de logit escena–PyTorch | 3,4e-3 (media 1,1e-3); predicciones idénticas **110/110**; exactitud 1,000 frente a 1,000 |
| Test, 40 épocas: diferencia máxima de logit | 2,3e-3; predicciones idénticas **40/40**; menor \|logit\| del test 0,017 (margen ~7× sobre el error) |
| Diferencia del propio modelo en float32 frente a float64 (referencia de ruido numérico) | 1,6e-6 a 1,9e-6 |

## 5. Controles (banda 3; `blender_controls.py`, `controls_check.py`)

| Tratamiento en la escena reabierta | Efecto previsto por el modelo en U (máx. abs.) | Visto en la escena |
|---|---:|---:|
| Tejado c12: r1 y r2 +0,01 BU en x | 0,499 | 0,499 |
| Chicane c21: chB y chC +0,01 BU en y (dlink +0,02) | 0,713 | 0,713 |
| Sham: r1 y r2 de c12 +0,05 en z (fuera del plano de haces) | 0 | 6,8e-13 |
| Celda c33 completa +0,05 en z | 0 | 1,0e-4 (ruido de `ray_cast`) |
| Ablación: se quita c12.r2 | aborto | **`lost ray`**, sin U (fail-closed) |
| Control negativo: U permutada entre bandas | — | exactitud de entrenamiento 1,00 → 0,47; 58 de 110 predicciones cambian |

## 6. Recorrido en GPU: qué es y qué no es

- La parte que hace la escena (trazar) son **200 lanzamientos de rayo por banda**. La inferencia por muestra no repite el trazado: la escena es fija, así que la U medida se aplica a todo el lote. Un GEMM complejo 8×8 en la RTX 3090 cuesta 0,22 ns por muestra (microbatería propia, `s3/bench`), y la forma completa de Motor Imagery (240 épocas × 12 bandas × 8 canales × 250 tiempos) con \|·\|² y media unos 1,04 ms.
- El recorrido **nativo de Blender en GPU de Codex** (shader de compute) no admite todavía esta rejilla: hoy 5 puertos, ledger de 128 y profundidad 32; la nuestra tiene 8 puertos y profundidad ≈ 36 + 4 por chicane. Además, en un solo hilo tardaría decenas de segundos por banda (ver la auditoría). Por eso el trazado de esta prueba es `ray_cast` de Blender (CPU) sobre la escena, y la aplicación por lotes a los datos es lo que va a la GPU.
- Encolado por gpuq (`infer_from_scene.py blender blender_out --dev cuda`): la misma inferencia por lotes en la GPU con la U de la escena y su tiempo. Se registra al terminar. No se ha ejecutado aún (la cola está ocupada con la validación anidada).

## 7. Qué falta

- Un modelo por sujeto y por semilla distintos (aquí un sujeto y una semilla) y el envío a Kaggle del mejor modelo óptico (no se envía nada hoy: los dos envíos del día UTC están gastados; siguiente ventana ≥ 01/10 00:00 UTC, con aviso previo).
- Trazado nativo en la GPU de Blender de la rejilla de 168 discos: requiere un kernel con estados fusionados o paralelo (propuesta en la auditoría, sección 5.2) y perfil de límites ampliado.
- La comparación de exactitud entre polar, rejilla de 32 retardos y matriz libre sin sesgo de selección: validación anidada preinscrita (`work/nested/PREINSCRIPCION.md`), en curso por la cola de GPU (un job pequeño por sujeto); el estado está en `work/nested/logs/`.
