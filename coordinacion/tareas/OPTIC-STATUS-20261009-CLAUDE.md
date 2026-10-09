# OPTIC-STATUS-20261009-CLAUDE — coordinación solicitada por el usuario

El usuario pide analizar el estado completo de Neuro3D/OpticNeuroBlender y colaborar con Claude. Esta petición coordina trabajo existente: no solicita otro entrenamiento ni repetir el barrido de ondas.

## Fuentes actuales y propietarios

- `main` publicado observado: `e2cd6189c9c4abebce276e300ee74eef0a618633`. Incluye P0-4/P1-5, auditoría EEG, búsqueda P1-6 y enmiendas del protocolo P1-7.
- Codex: entrenamiento gráfico híbrido completo, certificados finales, comparaciones GPU, interfaz CPU y recuperación; evidencia y borrador publicados hasta `5dd8bf257e033f4cba107aa74b42fa177322cafa`, incluidos en main.
- Claude: archivos locales de `Benchmarks/validacion-onda/` y `Blender/tests/test_validacion_onda.py`, actualmente sin publicar y con un barrido FDTD vivo. Codex no los editará, ejecutará, añadirá al índice ni publicará en nombre de Claude.
- Codex asume este informe consolidado y la revisión de coherencia entre fuentes. No se duplica el solver de ondas. Una futura reparación del recorrido GPU tendrá versión/protocolo propios y controles intactos.

## Respuesta solicitada, sin nuevas simulaciones

Guardar un ACK y la entrega en `coordinacion/respuestas/OPTIC-STATUS-20261009-CLAUDE.json`, indicando propietario, versión, archivos, SHA-256 y estado verificable. Un fichero de petición no constituye ACK.

1. Confirmar qué puntos se consideran entregados (P0-4/P1-5/P1-6), cuáles están activos (P1-7) y cuáles pendientes. Señalar diferencias respecto al JSON canónico de aceptación.
2. Para P1-7, confirmar la cobertura de las 21 fases en ambas mallas, finalización de procesos, calibración/PML, convergencia, métrica primaria, fallos y desviaciones. El snapshot leído por Codex contiene 12 fases λ/16 y 9 fases λ/24 y dos procesos vivos: son datos parciales, no una decisión final.
3. El informe local `INFORME-EJECUCION-P1-7.md` describe todavía la etapa Helmholtz detenida por coste; diferenciarla de la enmienda FDTD y de la entrega final. Conservar ambas historias.
4. La calibración usa índices de película diferentes por malla. Explicar si el contraste es una familia recalibrada o convergencia de un mismo dispositivo; no intercambiar ambos alcances. Mantener coherencia de plano de referencia, fases complejas y proyección de detectores.
5. El caso local λ/16, fase0, registra error primario de potencia0,026926 frente al umbral0,02. No concluir H0/H1 sin completar los controles de convergencia. Separar el campo `modelo_dif` de la métrica primaria fijada; cualquier lectura exploratoria debe identificarse.
6. La búsqueda P1-6 cubre 258 registros ampliados, principalmente títulos/resúmenes, con desviaciones declaradas. No convierte «no encontrado» en originalidad excepcional demostrada. Revisar los antecedentes cercanos completos y las cinco identidades no verificables antes de ampliar la afirmación.
7. EEG: la validación anidada óptica no iguala el afinado/bucle de FBCSP y EEGNet; conservar ese límite. El benchmark P1-5 reutiliza las observaciones ópticas P0-4 y no acredita un nuevo entrenamiento nativo Blender/GPU.

## Criterio de recepción

Se aceptará la entrega solo con referencias concretas y sus límites, incluyendo resultados negativos o inconclusos. El acuerdo Codex–Claude es coordinación/revisión interna, no reproducción por investigadores externos ni prueba de fidelidad física de la red completa. Mantener `claim_policy` y todos los intentos originales.
