# Plan de pruebas Blender — Neuro3D

## Regla de seguridad de esta entrega

No se ejecuta Blender, no se inicializa un contexto GPU y no se despacha ningún
shader. Esta entrega deja el material preparado y valida todo lo que no necesita
la tarjeta gráfica.

## Fase 0 — pruebas sin GPU (incluidas)

- Reproducibilidad: mismo grafo y semilla producen el mismo checksum.
- Propagación: un pulso llega a un nodo conectado.
- Aislamiento: una arista con peso cero no activa el objetivo.
- Atenuación: aumentar la atenuación no aumenta la amplitud emitida.
- Límites: intensidad, energía y color permanecen acotados; no aparecen NaN/Inf.
- Evolución: el checksum cambia después de un pulso y varios pasos.
- Contrato estático: el shader contiene la interfaz esperada y el addon mantiene la
  ruta GPU desactivada por defecto.
- Circuito óptico geométrico: espejo alineado entrega potencia; su rotación o el
  desplazamiento del receptor corta la señal; reflectancia RGB filtra color;
  absorción reduce potencia y longitud de camino cambia fase.

## Fase 1 — validación dentro de Blender, aún CPU

Ejecutar en una máquina donde Blender esté disponible, con el dispositivo GPU no
seleccionado para cómputo:

- instalar el addon y crear **Optical Circuit** (tres objetos vacíos);
- ejecutar **Trace Optical Pulse (CPU)** y verificar en el receptor que
  `optical_hit=True`, `received_intensity>0` y `received_rgb_power` tiene
  tres canales y `activation>0`;
- girar el reflector y confirmar `optical_hit=False` y potencia cero;
- restaurarlo, variar `reflectance_rgb` y confirmar el cambio por canal;
- guardar y reabrir el `.blend`, repetir el trazado y comparar el resultado;
- confirmar que no se crea ningún shader compute ni buffer GPU.

## Fase 2 — primer gate GPU (requiere autorización explícita)

- Compilar el GLSL en la versión exacta de Blender.
- Ejecutar una red mínima de 2–8 neuronas.
- Comparar cada campo de salida con el oracle CPU dentro de una tolerancia
  documentada, separando error de fase, intensidad, frecuencia, color y energía.
- Verificar doble buffering y ausencia de lecturas/escrituras simultáneas inválidas.
- Hacer readback sólo después de que termine el dispatch.
- Comparar checksum CPU/GPU y registrar frame, latencia y tamaño del grafo.

## Fase 3 — estabilidad y visualización

- 1.024 neuronas y grafo fijo.
- 10.000 pasos con semilla fija.
- Pulsos repetidos, pulsos simultáneos y ausencia de pulsos.
- Frecuencias extremas, colores fuera de rango, pesos cero y retrasos cero.
- Pausar, reanudar, reiniciar y cambiar de escena.
- Visualizar neuronas como instancias y conexiones como curvas sin que la capa
  visual vuelva a calcular la red.

## Fase 4 — rendimiento

- medir throughput y latencia en 64, 256, 1.024 y 16.384 neuronas;
- medir coste de readback separado del coste de cómputo;
- comprobar memoria y estabilidad durante una sesión prolongada;
- repetir en Eevee y Cycles sólo cuando la paridad GPU esté aprobada.

## Criterio de salida

La ruta Blender no se llamará “GPU validada” hasta completar Fase 2. Hasta ese
momento, el estado correcto es **CPU-ready / GPU-dormant**.
