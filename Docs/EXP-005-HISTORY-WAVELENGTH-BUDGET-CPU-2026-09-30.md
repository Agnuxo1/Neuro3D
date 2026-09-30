# Presupuesto espectral multicamino ligado a la escena

Estado: candidato CPU opt-in, sin modificar contratos/runners/shaders
congelados. Auditor ejecutado 2026-09-30 15:41:33 UTC, 1,5875 s, un hilo,
hijo con límite 60 s. JEV bloqueado: fallback local, sin aval remoto.

## Cambio

`history_wavelength_field_budget_v1.py` deriva la historia completa desde
fuentes, triángulos y propiedades de la escena; no admite una lista de
caminos externa ni un máximo de longitud inventado. Reutiliza el perfil CPU
congelado (64 registros/32 de profundidad), longitudes y referencia terminal
encerradas racionalmente. Exige un grupo de coherencia por fuente y límites
explícitos de campo complejo e intensidad.

Compara dos modelos ideales con idéntica geometría, modos, coeficientes y
fuentes, distintos SOLO en lambda original frente a lambda hi/lo decodificada
por el ABI existente. El gate relativo previo permanece intacto.

Para cada camino, con amplitud ideal acotada por A y longitud efectiva
absoluta acotada por L:

    dphi <= 2*pi_upper*L*|1/lambda - 1/lambda_decoded|
    epsilon_camino <= A*min(2, dphi)
    epsilon_grupo <= suma epsilon_camino
    error_intensidad_grupo <= 2*A_grupo*epsilon_grupo + epsilon_grupo^2

Se usa una cota racional superior de pi y enclosures hacia afuera para
raíces de amplitudes de fuente/divisor. Los grupos coherentes suman cotas
de campo; grupos independientes suman cotas de intensidad, no campos.
Se conservan todas las ramas aunque T=0/1, fuente cero o cancelación ideal.
El cálculo de la cota no evalúa exponenciales ni usa la potencia observada
como permiso para ignorar la fase.

`accepted_wavelength_only` solo significa cumplir ambos presupuestos para
esta perturbación espectral condicionada. `native_promotion_allowed` y
`native_precision_certified` permanecen FALSE incluso con error espectral cero.

## Evidencia nueva y aceptación

Siete tests y siete casos PASS. Presupuestos prospectivos: campo 1e-4 e
intensidad 2e-4; dos controles exacto/fuente-cero usan presupuesto cero.
No se cambiaron umbrales anteriores para obtener PASS.

| Caso | Registros | Cota campo Dx por grupo | Diferencia campo CPU Dx | Gate espectral |
|---|---:|---:|---:|---|
| Lambda exacta 0,125 | 13 | 0 | 0 | acepta |
| Lambda 1,00416693877201e-12, fuente única | 13 | 0,04026785 | 0,04026513 | rechaza |
| Misma lambda, dos fuentes coherentes | 26 | 0,08053569 | 0,08053025 | rechaza |
| Dos grupos independientes | 26 | 0,04026785 | 0,04026513 | rechaza |
| Dos fuentes opuestas, cancelación | 26 | 0,08053569 | 0 | rechaza conservador |
| Referencia Dx +0,03125 BU | 13 | 0,04058244 | 0,04057965 | rechaza |
| Fuente cero, lambda inexacta | 13 | 0 | 0 | acepta SOLO espectral |

Error relativo de lambda inexacta 1,6089e-15, dentro de 1e-12: aun así el
campo puede superar 1e-4. La cota de intensidad coherente es cuatro veces
la de una fuente; dos grupos independientes suman dos veces esa cota.
Estos MZI tienen fase de propagación común: la intensidad observada no
cambia, lo cual NO elimina la diferencia de campo complejo. La cota de
intensidad es conservadora, no una predicción del error real.

El contraste numérico usa ideal_fields CPU con ambas lambdas, historias
regeneradas por separado y slack float64/libm explícito 1e-13 SOLO como
diagnóstico del auditor. No se suma ese slack al gate matemático racional
ni se interpreta como certificación de redondeo nativo.

Reporte `D:/PROJECTS/.cognition/neuro3d/exp005_history_wavelength_budget_20260930_1541.json`,
SHA `a6e49baefa5196c2c3740fed3de3eb28cd7ba3fd62a1adb0fa4c30e0d7d3103f`;
14 hashes de código verificados. No ejecución ni modificación de código peer.

## Exclusiones y siguiente paso

NO geometría Bpy real, transporte de posiciones/referencias hi-lo, errores
de coeficientes, acumulación de longitudes o reducción de fase GPU, RT,
solape físico, conf1, presupuesto total ni comparación de velocidad. Las
historias CPU NO se suministran a un backend GPU. Este presupuesto no debe
rechazar ni promover trabajos antiguos silenciosamente.

GPU externa ocupada, RAM libre 1,129 GiB a 15:42: no cargas ni cambios de cola.
Claude: cuando atiendas la siguiente revisión CPU, acusa el alcance espectral
y señala una omisión concreta si la encuentras; los siete casos retenidos
bastan, no se pide repetir barridos ni cambiar tu piloto. RT-CAP-006 sigue
prioridad y debe conservar sus márgenes y entregar sus artefactos al cerrar.
