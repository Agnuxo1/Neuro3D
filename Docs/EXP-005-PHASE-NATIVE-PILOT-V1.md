# Piloto de fase compensada en Blender GPU: contrato preparado V1

## Estado congelado antes de GPU

PHASE-NATIVE-PREP-001-CODEX, 30/09/2026 17:36:51 UTC: seis pruebas CPU
PASS en 0,0065235 s, un hilo/timeout de hijo 60 s, ocho pins antes/después.
ABI de palabras exactas, decoder, rechazo de trazas manipuladas y revisión
textual de shader verificados. GLSL NO compilado, GPU NO ejecutada,
Blender NO abierto. El shader anterior 914bf296...dfcd1 sigue intacto.
Esta preparación no constituye un resultado GPU ni una red en escena.

## Trabajo y entradas

Shader nuevo opt-in `exp005_phase_compensated_probe.glsl`: cada invocación
recibe SOLO un par L/lambda representado en binary64. Textura RGBA32UI
contiene cuatro uint32, dos por escalar en orden little-endian; pack/unpack
Double2x32 reconstruyen bits, no una aproximación hi-lo float32.
Esto aísla la aritmética de fase: NO valida transporte geométrico hi-lo,
no exporta escena ni sigue rayos, no reemplaza la red por una matriz.

Seis controles congelados en reporte: cero, cuarto de vuelta, F1 lejano,
lambda general dentro de dominio y dos fronteras de media vuelta.
El código admite 1..16 pares, pero un piloto solo usa esta lista y
negativos preregistrados: L=-1/λ=0/NaN/subnormal (status1),
q=2^52 y L=1e6,lambda=1e-12 (status2). Serializar negativos no finitos
por sus palabras uint, nunca por JSON NaN ni aceptar cambios post-medida.

GPU calcula q=L/lambda, residual=fma(-q,lambda,L), correction=residual/lambda,
ciclos reducidos, producto TAU y cast float32, luego cos/sin float32.
`precise` exige conservar puntos de redondeo: su efecto real debe comprobarse
en readback. No fallback multiply-subtract ni cálculo CPU de salida.
Un compilador que rechace FMA/FP64/resources aborta; no se declara reparación.

## Salida y gates falsables

Siete píxeles RGBA32UI por caso: cinco pasos aritméticos en binary64
por sus bits, un par cos/sin promovido a binary64, status+ID+padding.
Abortos limpian TODOS los campos/trazas y conservan status/ID.
Status: 0 éxito, 1 entradas inválidas, 2 cociente fuera de dominio,
3 residuo no normal, 4 corrección inválida. Lista de status esperados
obligatoria: abortar un control válido NO se contabiliza como éxito.

Decoder exige forma/tipos/IDs/padding/status y pasos RN frente a Fraction,
sin umbral relajado para la traza. Campo unitario se contrasta con referencia
CPU a 1e-4 y cota aritmética ideal <=1e-4. CPU libm de referencia no es
certificado uniforme del driver ni cota de error de una red completa.
No se atribuye el error sintético CPU 8,742278e-8 a GPU.

El readback desnudo NO autentica la ejecución: se mantiene
`runtime_execution_authenticated=false` y `native_promotion_allowed=false`.
El futuro wrapper debe conservar compilador/backend/ejecutable, job/deadline,
guard+envelope+cierre, shader/inputs/outputSHA y trazas originales. Estas
evidencias son necesarias además de la consistencia numérica, no alternativas.

## Ejecución futura: NO autorizador implícito

`dispatch_probe` no tiene CLI ni crea reservas. Solo se llama dentro de
un Blender privado, escondido, por wrapper con exclusividad gpuq real y
guard fail-closed. Callback de deadline obligatorio antes de compilación,
alloc, dispatch y readback; timeout externo <=90 s y deadline nuevo UTC
por trabajo. No reutilizar ni ampliar la ventana nocturna cerrada.
RAM presupuestada 2 GiB + 4 GiB libres después; VRAM total <=18 GiB,
temperatura <=80 C, procesos/cola/telemetría comprobados antes de lanzar.
No cancelar ticket006, matar procesos ajenos ni reducir márgenes por esta sonda.

No prueba de velocidad, energía, RT, geometría, autointersección, malla general
ni capacidad máxima; no aumento de bounds/conf1. Siguiente unidad: wrapper
privado y manifest de negativos por bits, luego un job único si recursos libres.
Claude conserva RT/006; incluir una objeción pequeña ABI/redondeo en MISMA
crítica opcional de fase, sin duplicar su backend ni nuevo barrido/guardreview.
JEV sigue bloqueado: fallback local explícito, sin aval remoto.
