# Arquitectura óptica de Neuro3D en Blender

## Fuente de verdad

El objetivo es que la escena 3D determine el cómputo. En el primer circuito,
Blender guarda tres objetos (`emitter`, `reflector`, `receiver`), sus posiciones,
orientaciones y propiedades ópticas personalizadas. El operador lee estos datos,
traza un rayo en CPU y escribe la señal recibida en el objeto receptor. Si se
guarda el `.blend`, esos parámetros y el resultado quedan en la escena.

```text
objeto emisor ──rayo──> disco reflector ──rayo reflejado──> esfera receptora
  intensidad             normal, radio                         sensibilidad RGB
  RGB, frecuencia        reflectancia RGB                      estado recibido
  fase                   desfase
```

La dirección reflejada es `r = d - 2(d·n)n`. El rayo debe cortar el disco y
después la esfera receptora. Para cada canal `c`, la potencia recibida es

`P_c = I_emisor × (color_c / Σcolor) × reflectancia_c × sensibilidad_c × exp(-αL)`.

Si todos los canales de color son cero, la potencia recibida es cero. La
normalización evita crear potencia total por superar RGB la suma de uno.

La fase al llegar es `fase_emisor + desfase_reflector + 2πfL/v`, reducida al
intervalo angular principal. `L` se mide en unidades Blender; `v` en unidades
Blender por segundo simulado, `f` en ciclos por segundo simulado y `α` en
absorción por unidad Blender. Es un modelo numérico de óptica geométrica; no
resuelve las ecuaciones de Maxwell ni mide fotones físicos.

La neurona receptora convierte la potencia total `P = ΣP_c` en activación con
`a = 1 - exp(-g·max(0, P - θ))`, donde `θ` y `g` son propiedades del objeto
receptor. Así, el estado neuronal depende de la trayectoria, el material y la
respuesta del receptor.

Python CPU ejecuta el trazado porque Blender no expone directamente el resultado
de un rayo visual como estado neuronal persistente. Python lee la geometría y
las propiedades de la escena como entradas y escribe el resultado en ella.
La antigua vista previa de 64 neuronas se conserva como material histórico y
**no** demuestra cómputo óptico en la escena.

## Compuerta de validación

El primer resultado medible debe cumplir tres relaciones: al girar el espejo o
mover el receptor se pierde la señal; al cambiar la reflectancia cambia su
potencia por color; al cambiar distancia, absorción o frecuencia cambia la
amplitud o fase conforme a las ecuaciones anteriores. Las pruebas ligeras del
núcleo matemático cubren estas relaciones. La ejecución dentro de Blender, el
guardado y la reapertura de un `.blend` siguen pendientes de disponer del
ejecutable en esta máquina.

## Límites actuales y evolución

La versión inicial usa un rayo, una reflexión y un receptor. No calcula
oclusiones, refracción, difracción, dispersión, interferencia entre caminos,
polarización ni entrenamiento de pesos. Tampoco usa Cycles, Eevee, shaders de
cómputo o GPU. La siguiente extensión debe añadir varios emisores/caminos y
acumulación coherente con una prueba de paridad frente al circuito mínimo.
