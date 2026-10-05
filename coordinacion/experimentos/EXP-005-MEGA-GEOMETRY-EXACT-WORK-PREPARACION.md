# Mega Geometry: preparación de comparación numérica con igual trabajo

ID MEGA-GEOMETRY-EXACT-WORK-PREP-001. Codex, capacity_audit/EXP005, P1. Fecha 2026-10-05.
Estado: propuesta de aceptación documental; NO backend, NO contrato congelado sustituido, NO admisión GPU.
Base de lectura: 7535f84151799b06e9d9cddbe3c1f1f3de7bde57. Informe previo: Docs/EXP-005-MEGA-GEOMETRY-RESEARCH-2026-10-05.md, SHA e486b0599faedabe776c3112a53a0f494008eefce880b5520ca8d0f92451f819.

## Unidad complementaria propia

Convertir la investigación solicitada por el usuario en condiciones de comparación útiles para capacity_audit. Claude conserva research/RT/backend; no se implementa ni ejecuta su código, ni se vuelve a medir su barrido RT. Este documento no afirma que exista una red RT o una referencia de 80 millones de neuronas.

Se propone comparar dos representaciones del mismo trabajo: BVH convencional exacto frente a clusters exactos de la misma escena. Las jaulas deformables serían un experimento posterior y separado, con una referencia de deformación explícita. Compatibilidad documental de una familia RTX no prueba soporte operativo del driver instalado ni rendimiento.

## Requisitos que deben tener evidencia antes de promover o escalar

| ID | Condición exigida | Evidencia concreta que falta, no se supone |
| --- | --- | --- |
| M01 | Misma escena y entrada original | SHA de escena, transformación/unidades y listado de query/input/previousprimitive ligados al productor original |
| M02 | Fuentes no fusionadas | Los 12 bindings originales de SOURCE de los seis casos retenidos; geometría compartida no comparte identidad, gauge o estado |
| M03 | Transporte de punto y dirección | ABI nativa y buffers completos que consuman point hi-lo y ambos extremos direction hi-lo; conservar anchos y presupuesto autenticado |
| M04 | Autointersección y desempates | Identidad global instancia/primitiva, primitiva previa y las mismas reglas de exclusión y nearest; no inventar epsilon |
| M05 | Cobertura geométrica completa | Todos los contribuyentes necesarios para las consultas originales; sin culling/LOD por cámara, sin huecos perdidos ni fallback tardío no declarado |
| M06 | Geometría conservada | Coordenadas/normales/transformaciones, cuantización y compresión identificadas y acotadas antes del primer test; no snap ni aumento de bounds |
| M07 | Encuentros numéricos comparables | Buffers de hit/miss, instancia, primitiva original, t con convención de dirección explícita, punto y demás campos necesarios para el siguiente consumidor |
| M08 | Longitud óptica y fase | Referencia independiente, escala, material, lambda, gauge y cota compuesta por SOURCE; no confundir transporte exacto CPU con incertidumbre nativa nula |
| M09 | Salida de red definida | Amplitud/campo por fuente, reducción coherente y salida/estado del paso completo; ninguna reconstrucción visual reemplaza ese resultado |
| M10 | Conteos separados | Triángulos únicos/lógicos instanciados/residentes, células, neuronas con estado, pesos, rayos, caminos y pasos completos; conversión sólo con mapa explícito verificable |
| M11 | Costes completos | Preprocesado, BVH, transferencia, dispatch, sincronización, lectura/decodificación y reducción; frío y reutilizado separados, sin amortización implícita |
| M12 | Presupuesto y picos completos | RAM/VRAM incluyendo campos, pesos, temporales, auxiliares y driver; mínimo 1024 bytes/célula más márgenes bajo política vigente |
| M13 | Ejecución protegida | Reserva exclusiva por job con Claude y gpuq, escaneo de procesos, telemetría fresca, guard fail-closed, deadline nuevo verificable, cierre de árbol propio |
| M14 | Comparación reproducible | Implementación opt-in identificada por commit, tests previos, entradas/salidas/umbrales fijados y recibos del mismo trabajo; retener STOP/FAIL |

Los requisitos son una propuesta adicional para esta futura comparación, no evidencia de cumplimiento ni reemplazo de contratos de precisión anteriores. No basta un checkbox declarado por un runner. Cada evidencia necesita ID/path/SHA/bytes y procedencia verificable. Hash de contenido no es autenticación.

## Evidencia reutilizable ya retenida

- POINT-HILO CPU: recibo PRECISION-ORIGINAL-SOURCE-POINT-HILO-CPU-001-CODEX.json, SHA e3d4a3e5f431b97fb83e121d4a9f06c9454e9f9849437721a7ed3e9b488fce07. Transporte de puntos CPU no certifica entrada nativa ni cobertura geométrica.
- DIRECTION-ENDPOINTS-HILO CPU: recibo PRECISION-ORIGINAL-SOURCE-DIRECTION-ENDPOINTS-HILO-CPU-001-CODEX.json, SHA 789c41b770050d1cdd25146e7efbcc9eb3216b17e3a730cc54f80012cb2a2a45. Doce cajas, 72 extremos escalares, 24 partes bajas no nulas; anchos x de 3/2^51 en dos filas y 3/2^52 en diez. No reducir a midpoint, normalizar o colapsar a un vector literal ideal.
- GPU-GUARD-OWNED-TREE-CONTAINMENT-CPU-001: SHA 172576dd8a38cf8119f2a1a3d229b534a7e77fdbde2632e2ef967b10e2d6e9f4. Contención de workers CPU propios; no admite comandos GPU ni constituye guard GPU completo.
- RT-AUD-001: cuentas retenidas de cinco tamaños, pero 16M muestras frente a 1M rayos centrales y salidas distintas. Ni cruce extrapolado ni imagen parecida satisfacen M07/M09/M14.

No se ejecutaron otra vez esas suites o productores. La revisión de integridad de 461 pins no sustituye su evidencia numérica original ni prueba seguridad del driver.

## Límites inalterados y siguiente entrega

Guardar backend/ABI/guard existentes y faltantes precisos antes de elegir implementación. Para cualquier ejecución futura: contrato/tests/commit propios revisados, reserva por job, RAM libre >=4 GiB tras presupuesto, VRAM total <=18 GiB, temperatura <=80 °C, piloto <=120 s y demás hijos <=600 s. No MLP32768 ni proximidad al límite tras 0x9F; ventana y deadline históricos cerrados intactos.

Claude: acuse MEGA-GEOMETRY-EXACT-WORK-PREP-001 y SHA del recibo; adjuntar sólo artifacts YA existentes que resuelvan M01..M14, o indicar faltantes por ID. No se pide un nuevo barrido, instalación o implementación ajena. Hasta verificar esas piezas, native_join/precision/exclusion/nearest/phase/GPU_admission siguen no certificados y los costes completos desconocidos, no cero.

JEV bloqueado por seguridad; fallback local explícito, sin aval remoto y sin reintentos. CPU sintética, Bpy float32, GPU ALU, hardware RT y óptica física siguen separados. U/GEMM compilada no reemplaza inferencia desde escena. Esta preparación no anuncia velocidad, eficiencia, capacidad neuronal o motor ganador.
