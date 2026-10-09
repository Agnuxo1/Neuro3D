# Informe breve de la noche 29-30/09 (Claude, con Codex) · Neuro3D

Todo lo de abajo está verificado con archivos en el repositorio o en `D:/PROJECTS/.cognition/neuro3d/`. Nada se ha enviado a Kaggle esta mañana.

## 1. Noche (sesión anterior, hasta las 06:00 UTC)
- **Capacidad en la RTX 3090.** Red convencional (torch): producto matriz-vector con 2,4·10⁹ pesos y MLP de 4 capas con 98 304 neuronas. Nuestra rejilla coherente como matriz de transferencia: 512 modos y 65 536 MZI. El render de Cycles/OptiX calcula la parte lineal exacta hasta 1,68·10⁷ pesos (lo limita la RAM del PC) y clasifica las 150 flores Iris en un solo render (96,7 %). Torch admite entre ~143 veces más pesos (frente al máximo del render con textura, 1,68·10⁷) y ~570 (frente a la geometría, 4,2·10⁶), y es 10⁴-10⁵ veces más rápido; la red coherente en núcleos RT dentro de Blender no se consiguió.
- **Recorrido de luz nativo en GPU de Blender (Codex, contrastado por mí).** Impactos, reflexiones, ramificaciones, fases y suma coherente en un shader de compute, en cadenas de 2-4 celdas; mi trazador independiente coincide a 1,5e-7 … 4,5e-7.
- **Kaggle Motor Imagery.** Malla óptica polar 0,74 en la tabla pública y rejilla física de 32 retardos 0,72 (histórico: matriz libre 0,77). PR #3 de la demo Iris fusionado.

## 2. Esta mañana (desde las 03:52 UTC)
- **Auditoría de Codex.** El coste pareado no muestra diferencia de latencia (0,98-1,00). Mutation testing: las puertas congeladas solo detectan 9 de 28 defectos. Codex reprodujo el contraejemplo CE3 (ambigüedad que depende del orden de triángulos) y su nearest V2 ya lo rechaza 6 de 6 en GPU real. Conf1 (16 MZI) queda bloqueado hasta un contrato nuevo: en el kernel de un hilo tardaría unos 51 s y Windows reinicia el controlador por encima de ~2 s (inferencia mía).
- **Fusión por estado (motor a medida).** conf1: 136 estados frente a 58 288 casts, U igual al oráculo B (5,5e-13) y a las 246 sondas de la GPU de Codex (4,5e-7). En GPU por lotes: 204 escenas de Motor Imagery a 0,79 ms cada una (unas 39 veces menos que en CPU); rejilla de 1024 celdas en 1,3 s frente a ~18 s. Con una escena pequeña gana la CPU.
- **Tu pregunta sobre rayos, DLSS/FSR y motor.** Con fusión por estado hacen falta 10²-10⁴ lanzamientos, no millones; RT/BVH empezaría a compensar hacia K = 64 (extrapolación) o con ≥10⁵ primitivas. DLSS, FSR, ReSTIR y SER no aplican a campos coherentes; sí la U horneada, la actualización de rango 2 y la interpolación con derivada exacta. Propuesta: motor a medida mínimo (exportador de Blender, grafo de estados, GEMM por lotes), con Blender como editor y visor.
- **Motor Imagery en escena de Blender.** Los 16 retardos de enlace se realizan con una chicane de 4 espejos. Las 12 bandas de S014 se construyen, guardan, reabren y trazan en 4 s; predicciones idénticas a PyTorch (110/110 y 40/40) y controles correctos (sham nulo, ablación aborta). Es una prueba de equivalencia, no de exactitud nueva.
- **Validación anidada (17 sujetos, sin sesgo de selección).** El polar actual da 0,713 sin inflado apreciable; elegir configuración por sujeto no ayuda. Solo mejoran de verdad 12 bandas × 3 ventanas (+0,025) y ≥60 épocas (+0,018). Mejor por familia: matriz libre 0,7285, polar 0,7188, rejilla física 0,6953.

## 3. Pendiente de ti
1. Qué dos ficheros enviar a Kaggle desde el 01/10 00:00 UTC (listos en `motor-imagery/work/`: polar, rejilla física y matriz libre nuevos; polar y rejilla coinciden ~98 % con lo ya enviado).
2. OK para `pip install drjit` (4,3 MB, PyPI, BSD) si quieres medir los núcleos RT de verdad.

## 4. Límites
El límite semanal de la cuenta se agotó (repone el 2/10 00:00 Madrid), así que no lanzo más workflows de subagentes. Los tiempos de GPU son de una sola sesión, sin reloj controlado: órdenes de magnitud, no ventaja frente a redes convencionales. En marcha (exploratorio): evaluación de 5 semillas de los tres finalistas.

Informes completos: `EXP-005-AUDITORIA-KERNEL-CONF1-…`, `MOTOR-ESCALA-ESTADOS-…`, `MI-EN-ESCENA-…` y `MI-ANIDADA-CLAUDE-2026-09-30.md` en esta carpeta.
