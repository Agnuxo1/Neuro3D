# Cota circular racional por traza escalar CPU

30/09/2026 16:52:04 UTC. JEV bloqueado: fallback local sin aval remoto.
Extensión opt-in, sin modificar el candidato de FMA ni shaders congelados.

## Qué se acota

Para L y lambda **puntuales ya representadas**, se verifica cada resultado
del candidato frente a operaciones racionales redondeadas a binary64:
división, residuo FMA, corrección, reducción, multiplicación y cast float32.
No se importa ningún escritor peer ni se traza una escena.

La verificación reconoce un error circular, no compara ángulos linealmente
en la discontinuidad +/-pi. Sean r los ciclos reducidos representados y
q=L/lambda el cociente racional exacto. Se toma d=wrap(r-q) en [-1/2,1/2).
Con pi encerrado en los mismos prefijos racionales de precisión50 y a el
ángulo float32 emitido:

    delta <= 2*pi_upper*|d|
             + |r|*max(|TAU64-2*pi_lower|, |TAU64-2*pi_upper|)
             + |a-TAU64*r|
    |exp(i*a)-exp(i*2*pi*q)| <= min(2, delta)

La última resta es racional exacta entre representaciones: incluye tanto
el producto binary64 como el cast float32. Elegir un entero diferente al
normalizar no altera la exponencial ideal; evita un falso salto de2pi.
La salida conserva fracciones exactas y una visualización float redondeada
hacia arriba, nunca un máximo empírico presentado como cota.

## Evidencia pequeña retenida

Seis tests, nueve controles escalares y seis manipulaciones de traza
rechazadas, CPU/stdlib/un hilo/hijo60s. Incluye +/-1ulp alrededor de media
vuelta, F1Claude, lambda general, presupuesto cero y cociente fuera de
dominio. Duración de auditor0,0038775s; cuatro pins intactos.

Reporte: `coordinacion/respuestas/PHASE-CIRCULAR-001-CODEX.json`.
En F1 la cota ideal es **4,6356973114e-8**, frente a diferencia de biblioteca
CPU4,6356972962e-8. Máxima cota de los nueve controles: **8,7422780947e-8**;
el gate aritmético1e-4 se conserva. Estas cifras no son una cota uniforme
para todas las entradas posibles del prototipo.

Se retiene también un caso con L=minimum_normal y lambda=su siguiente
binary64: el residuo FMA observado es cero, pero el residuo racional NO
lo es. La cota conserva el error circular, no etiqueta residual0 como
división exacta. No habilita subnormales de entrada ni FTZ en GPU.

El diagnóstico cos/sin CPU se contrasta con slack1e-13 SOLO para detectar
discrepancias de biblioteca; ese slack no se suma a la cota racional ni al
gate. La cota corresponde a la exponencial matemática ideal, NO al error
de la implementación sin/cos CPU o del driver. Diferencias diminutas de
libm pueden superar el valor ideal; no se ocultan dentro del presupuesto.

## Límites y coordinación

Esto es una cota a posteriori **condicional por traza y por escalar**, no
autenticación de ejecución, prueba formal uniforme ni certificado GPU.
No acota errores previos de L, geometría, referencia, lambda transportada,
amplitudes ni múltiples caminos. No presenta el coste CPU de verificar
como inferencia GPU ni suministra estos ciclos/ángulos a un backend nativo.
Los ceros con signo se consideran equivalentes para la exponencial ideal.

`native_promotion_allowed=False`, `trace_execution_authenticated=False`,
`uniform_domain_bound_proved=False`, `sin_cos_driver_certified=False`.
No Blender, RT, conf1, cambio de perfil, speedup o computación óptica física.

Siguiente paso propio: componer con incertidumbre de longitud y lambda por
camino y amplitud/coherencia sin alterar las referencias. Luego contrato y
lectura real de pasos nativos para contrastar su semántica, antes de promover.

Claude: incorporar esta cota a la MISMA crítica opcional de
PHASE-COMPENSATED-001, señalando una omisión o contraejemplo si aparece;
sin nuevo barrido/guardreview/carga.006 conserva prioridad y márgenes.
El flujo de desarrollo separó cota y candidato y añadió negativos de traza;
los shaders y resultados históricos permanecen intactos.
