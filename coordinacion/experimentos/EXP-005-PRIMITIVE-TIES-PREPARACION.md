# Identidad y banda de empates: preparación CPU

NO CONGELADO. Candidato de arbitraje de listas sintéticas, no trazador ni ABI
nativo. Usa únicamente CPU ligera. No modifica ningún contrato previo.

## Regla falsable

IDs explícitos únicos por triángulo y snapshot SHA declarado; no confundir el
ID con la posición del candidato en una lista. Remeshing, cambios de geometría
o snapshot requieren estado nuevo: no se hereda la primitiva previa. El módulo
comprueba igualdad de etiquetas, NO autenticidad del SHA ni del exportador.

Primero mínimo global exacto; después banda inclusiva de 1e-9 BU alrededor del
mínimo, conservando distancia exacta. La referencia en empate exacto se escoge
por normal canónica y luego ID estable. Cualquier candidato de la primitiva
previa en la banda ABORTA; no se filtra para elegir otro. Esta condición tiene
precedencia diagnóstica sobre ambigüedad de objeto/normal. Las dos invalidan la
muestra. Una primitiva previa fuera de la banda no veta el impacto más cercano.

Otras caras del mismo objeto siguen permitidas. Sin primitiva previa, el origen
es una fuente. Un miss no inventa impactos válidos. Continue solo indica pasar
este arbitraje, no validación de fase, energía, modo o campo completo.

## Antes de una integración

Exigir contrato nuevo de manifest/hash real, IDs transportados y estado por rama
GPU; resolver empates en GPU desde triángulos crudos, sin lista CPU de impactos.
No leer frontier intermedio. Preservar gates y kernels congelados. Ensayar ID
duplicado, snapshot cambiado, splitting, caras adyacentes, retorno legítimo y
aborto con campos inválidos; revisión independiente antes de congelar. No ampliar
conf1 ni bounds. El t_min y los candidatos que elimina quedan fuera de esta regla.
La etiqueta sintética a*64 de los tests NO es readback Blender ni SHA certificado.
GPU, compilación y Blender requieren nueva autorización: este contrato no la da.
