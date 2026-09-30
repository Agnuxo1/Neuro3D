# F5 reproducido: el corte de distancia puede ocultar otra superficie

Crítica de Claude F5 contrastada con código propio y referencia analítica.
Consulta CPU sintética de seis triángulos: salida recta desde x=0 hacia +x,
superficie cercana x=gap y lejana x=1. El mínimo positivo exacto es gap. Ambas
superficies son objetos diferentes; el estado previo es una primitiva de x=0.
No se calcula una red completa ni sus campos. No es readback Bpy ni runtime GPU.

| Gap (BU) | Objeto analítico | Objeto elegido por consulta filtrada | Regla de empates |
|---|---|---|---|
| 5e-10 | cercano | lejano, distancia1BU | continue |
| 1e-9 | cercano | lejano, distancia1BU | continue |
| 2e-9 | cercano | cercano | continue |
| 1e-8 | cercano | cercano | continue |

La causa es t<=1e-9 rechazado antes de arbitrar. La primitiva anterior y toda la
banda de empates no pueden rescatar un impacto que no figura entre candidatos.
Continue es permiso de un componente, NO certificación óptica de escena completa.
Seis órdenes cíclicos que consultan los seis triángulos mantienen el primer fallo;
no se han probado todas las720permutaciones ni propagación de campos.

Referencia independiente del trazador: para origen(0,0,0), dirección(1,0,0),
el rayo está en x=t y la primera superficie positiva está en x=gap. Fracciones
retienen el valor exacto del input binary64, sin sustituirlo por decimal ideal.
Cinco tests enfocados PASS0,007s: dos fallos esperados, dos controles superiores,
orden, separación entre fallos/controles e inputs inválidos. Los fallos siguen
registrados como discrepancias; testsPASS NO significa arquitectura reparada.

Report D:/PROJECTS/.cognition/neuro3d/exp005_cutoff_cpu_20260930_0855.json
SHA `0a8249882f08313724ef37e497b7b33ad7e11412728599197aa9950944c470b7`.
Catorce hashes de código/entrada, incluida la respuesta004 leída como evidencia;
no se ejecutan scripts de Claude. Se conservan todos los fixtures anteriores.

Siguiente contrato, todavía pendiente: detectar/rechazar conservadoramente una
superficie positiva dentro del intervalo excluido, distinguirla del origen y
de la incertidumbre de autointersección, o justificar explícitamente un dominio
que impida esos gaps. No bajar t_min, omitir objetos/primitivas, renormalizar
campos ni cambiar el oráculo para convertir el fallo enPASS. Una variante nueva
requiere revisión, contrato antes de compilación y autorización GPU nueva.
Shaders/runners/contratos congelados intactos. No ventaja ni generalización conf1.
JEV bloqueado: fallback local identificado, sin aval remoto.
