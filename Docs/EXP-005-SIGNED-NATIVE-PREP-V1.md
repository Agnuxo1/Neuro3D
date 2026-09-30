# Preparación escalar firmada V1, no compilación ni ejecución GPU

Nueva variante opt-in. Shader no-negativo/piloto127efdf y rawscene914bf296
permanecen intactos. Entrada por cuatro uint32: Lefectiva signed binary64 y
lambda binary64. Salida 28 uint32: cuatro pasos sobre |L|, ángulo signed
float32 almacenado en binary64, campo sin/cos y status/ID/padding.

Contrato CPU previo a tests: doce casos fijos exact-word (incluye NaN como
palabras, nunca literal JSON): ocho válidos, cuatro abortos [2,1,1,1]. Tres
negativos previos, referencia -3,03125, frontera negativa, positivos/cero.
|L/lambda|<2^52 y ausencia de subnormales siguen obligatorios; FMA nativa,
RN/precise y gates1e-4 no relajados. L física y referencia no se exportan aquí.

Pruebas CPU solo ABI/decoder: uint exactos, sintéticos que pasan, signo/traza/
padding/ID/status alterados rechazan, abortos sincampo, plazo/captura
obligatorios antesGPU. Shader inspeccionado como texto, NO compilado.

Callable requiere persistir raw ANTESgate/postdeadline. NO es launcher,
supervisor/admisión, guard operacional o autenticación; debe integrarse con
reserva exclusiva+guardfailclosed+deadline NUEVO<=90s y presupuesto2GiB,
RAMlibre>=4GiB después, VRAMtotal<=18GiB/temp<=80C. No GPU mientras Claude006
espera ni RAM<6GiB. Sin instalar herramientas, CPUfallback ni relajar reservas.

El decoder valida solo consistencia de escalares; no scenepropagation,
geometría hi-lo, modos físicos, RT, precisión total, conf1 ni ventaja.
Siguiente: manifest SHA congelado, captura privada/outerguard antes piloto.
JEV bloqueado: fallback local sin aval remoto.
