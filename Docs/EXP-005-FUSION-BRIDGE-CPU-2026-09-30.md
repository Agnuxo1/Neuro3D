# Contraste CPU del puente entre fusión y estados en dispositivo

Unidad propia P0-FUSION-BRIDGE-001-CODEX. Contrato escrito antes de este
contraste, sin cambiar contratos ni módulos de Claude. JEV bloqueado para
Codex: fallback local, no se adopta un aval remoto sin procedencia verificada.

## Pregunta y controles fijados

¿El arreglo opt-in `statefuse.quant='auto'` llega a `gpu_states.trace`?
Los archivos son bibliotecas puras revisadas, importadas solo en CPU;
ningún arnés escritor, barrido grande, Blender, CUDA o RT se ejecuta.

Cinco MZI sintéticos axiales/diagonales diádicos, un hilo, hijo <=60s.
Datos representados exactos; no se simula readback Bpy float32.
Se regenera el árbol completo mediante el trazador racional propio y se
calculan campos ideales desde sus longitudes, sin usar U de Claude como
referencia. Para cada escena: sin fusión, fusión por defecto, auto en CPU,
estados torch en CPU por defecto y override escalar de quant como diagnóstico.

Casos fijos (longitudes en BU):

- Control exacto: lambda=2^-17, desplazamiento=0.
- Adversario nuevo: lambda=2^-17, desplazamiento del espejo MB=2^-31.
- Misma geometría con lambda=0,125.
- Sham no subcuantizado: lambda=2^-17, desplazamiento=2^-27.
- Misma geometría con lambda=2^-10.

Gate de campo del proyecto 1e-4 intacto. Controles de referencia/auto/
override deben discrepar <=1e-8 del oráculo CPU independiente; no se utiliza
ese umbral para relajar el gate de campo. El adversario busca error >1e-4
aceptado por la fusión por defecto, no solo colisión de hash.
Cada árbol debe contener 13 registros y cuatro campos por camino.

## Límites y seguimiento

El override de quant es un diagnóstico monoescena, NO implementación
adaptativa por escena para lotes con distintas lambda. Tampoco demuestra
una cota uniforme de fusión: faltan error angular con longitud restante,
márgenes topológicos, coherencia/referencias y acumulación entre fusiones.
No se promueve conf1/bounds ni se atribuye fallo a CUDA sin ejecutarla.

Acusar las entregas P0-1/P0-3/P0-4 por SHA y revisar primero artefactos
retenidos; no repetir sus 104/300 escenas, 60 000 escalares ni raycasts RT.
La preinscripción histórica es declarada por el autor, no certificada por
este auditor; las cabeceras horarias deben aclararse antes de atribuirla.
No repetir/instalar Mitsuba o DrJit ni otorgar aquí permisos de instalación.

Claude: si se confirma el adversario, añadirlo como gate CPU retenido antes
de promover la fase B; variante nueva, quant dependiente de cada escena
o rechazo explícito de entradas no cubiertas, sin tocar fallos congelados.
RT-CAP-006 mantiene prioridad de cola y piso RAM; este contraste no
autoriza otro job ni exige esperar pasivamente mientras faltan recursos.
