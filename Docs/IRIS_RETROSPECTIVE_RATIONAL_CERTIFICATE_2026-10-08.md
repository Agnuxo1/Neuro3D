# Cotas racionales de los readbacks Iris ya archivados

**Cierre de este análisis retrospectivo:** las salidas de `native02` cumplen las tolerancias históricas con cotas racionales; el control negativo `native01` las incumple de forma demostrable. No se volvió a ejecutar la GPU ni se recogieron nuevos datos confirmatorios de H1. El trazado de triángulos y la novedad permanecen abiertos.

## Qué se certifica

El problema es el circuito **algebraico canónico representado** de 16 interferómetros y ocho modos. Las features, scaler, fases, referencia, gain y constantes se leen de los words binary64 históricos, vinculados a CSV/estado congelados por hash. Se verifican job, guard, nonce, eco y headers de los readbacks completos. Se comparan 150 filas por caso en baseline/phase/sham.

Un checker separado utiliza fracciones e intervalos dyádicos de 256 bits para formar el operador complejo y propagar entradas normalizadas. No importa Blender, GPU, productor, auditor90dps ni mpmath. π se encierra con Machin/arctan64; sqrt usa isqrt; sin/cos usan Taylor32, resto de Lagrange y cota Lipschitz del intervalo original.

La nueva cota de exp usa una serie positiva de 128 términos. Para x≥0, la cola desde t_(N+1) se acota por t_(N+1)/(1−x/(N+2)) cuando esa razón es menor que1; para x<0 se invierte el intervalo positivo. Se admite |x|≤32. Es análisis conocido, no un nuevo teorema físico.

Las inclusiones se apoyan en las reglas matemáticas de intervalos y en la implementación comprobada. No es una prueba mecanizada de Python, del compilador GPU ni de cada programa futuro. Certificar una salida concreta no garantiza todos los inputs posibles.

## De campo a intensidad y decisión

Para el campo nativo y=a+ib, el intervalo R+iJ contiene el campo exacto del modelo. Las máximas distancias de a a los extremos de R y de b a los extremos de J dan una cota L1. Las distancias mínimas al rectángulo proporcionan **cotas inferiores**, que distinguen un incumplimiento real de una cota demasiado ancha.

Si b_E acota ese error y |y|_up acota el módulo nativo exacto,

|I_native−I_truth| ≤ |I_native−(|a|²+|b|²)| + 2|y|_up b_E + b_E².

El primer término incluye el error adicional del cálculo de potencia nativo. Se conservan esta cota propagada y una cota directa más estrecha frente al intervalo de intensidad. Los logits se encierran con el intervalo del gain positivo. La decisión se certifica cuando el límite inferior del logit elegido supera todos los límites superiores de los otros dos.

La norma/potencia normalizada se compara también con1. Es balance de campos digitales, **no energía de hardware medida en julios**.

## Resultados del modelo canónico

| Cantidad | Cota superior global `native02` | Tolerancia histórica |
|---|---:|---:|
| Amplitud de entrada normalizada | ≤1.991e-16 | 1e-12 |
| Campo complejo, error L1 | ≤1.282e-13 | 1e-11 |
| Intensidad por modo, cota directa | ≤3.323e-14 | 1e-11 |
| Intensidad, cota propagada desde campo/lectura nativa | ≤1.857e-13 | 1e-11 |
| Logit | ≤3.202e-12 | 1e-9 |
| Balance de potencia normalizada | ≤2.563e-15 | Informativo; no coste energético |
| Decisiones certificadas | 450/450 | Familia histórica; no450aciertos de etiquetas |

Los decimales se redondean hacia un valor mayor. Los límites racionales completos están en [attempt06](validation/iris-retrospective-interval-2026-10-08/attempt06-native02/certificate.json). SHA del readback histórico: `0f48a27f8edf9567d7ef4e72126e356495ca21e05ef2bba2e7e2e55c57c8e34e`.

El [control negativo native01](validation/iris-retrospective-interval-2026-10-08/attempt07-native01/certificate.json) conserva450/450decisiones del modelo, pero una cota **inferior** del error de campo supera1.51e-5 frente al límite1e-11. El logit también incumple su tolerancia. Coincidir en clases no demuestra precisión de campos/salidas completas. No se atribuye ese resultado a una causa definitiva del driver.

![Cotas y decisiones de datos históricos](assets/iris-retrospective-certificate-2026-10-08.png)

## Intentos conservados y controles

- `attempt01-native02`: intervalos128bits;450decisiones certificadas, pero cota de campo2.656e-8 demasiado ancha. Es limitación del checker, no demostración de falloGPU.
- `attempt02-native02`: precisión256bits, mismos datos/umbrales; cumple.
- `attempt03-native01`: mismo checker256bits, datos históricos negativos; excede utilidad.
- `attempt04/05`: añaden norma/potencia normalizada, con fuentes congeladas.
- `attempt06/07`: añaden cotas inferiores para distinguir error real de intervalos anchos. El positivo cumple y el negativo incumple con prueba inferior.

Se conservan todas las preimágenes. El módulo de intervalos previo no se editó; el nuevo checker establece precisión en un proceso privado y registra la resolución. [Catorce controles CPU analíticos](research/retrospective_math_controls_v1.json) verifican fases cardinales, exp/recíproco, dos puertos divisor/espejo, rechazo fuera del dominio y distancias inferiores exactas al intervalo. Son controles matemáticos, no pruebas GPU ni réplicas independientes.

## Límite científico

Este análisis convierte el acuerdo aproximado anterior en cotas verificables de **los datos archivados bajo el modelo algebraico indicado**. No certifica captura Blender float32, selección/completitud de triángulosRT, régimen Maxwell, incertidumbre física, generalización, coste total ni superioridad. Tampoco prueba originalidad: suma compleja e intervalos son conocidos.

La revisión del punto1 utiliza este resultado para precisar el certificado candidato; la implementación desde geometría real y su diferencia científica siguen pendientes. Los ensayos confirmatorios futuros siguen sujetos a resolver el registro prospectivo solicitado al propietario.
