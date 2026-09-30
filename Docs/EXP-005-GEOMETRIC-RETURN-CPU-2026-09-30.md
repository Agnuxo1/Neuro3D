# Retorno por primitiva: conexión con consultas geométricas CPU

La regla candidata de empates ya se aplica a TODOS los impactos calculados
sobre los triángulos de los doce adversarios retenidos, no solo a un candidato
de primitiva previa inyectado manualmente. Es un auditor CPU de fixtures
sintéticos, NO Blender, GPU, red con campos ni reparación nativa.

24 consultas después de reflexión: doce en coordenadas mundo y doce trasladadas
al frame del origen inicial. Se conserva la aritmética de los rayos retenidos,
sin normalizarlos de nuevo; se verifica replay numérico exacto de ambos frames.
Cada consulta examina ambos triángulos, permuta sus órdenes y conserva el mismo
resultado. Mínimo y banda global siguen inmutables en la regla candidata.

Resultados de ESTE subconjunto, seleccionado por self-hit mundo:

| Frame | Abort | Continue | Miss |
|---|---:|---:|---:|
| Mundo | 12 | 0 | 0 |
| Local | 3 | 0 | 9 |

Los 12 retornos mundo y 3 locales quedan en la banda de la primitiva previa y
abortan. Los nueve miss locales NO son salidas de campo válidas ni prueba de
que el frame repara el problema. No extrapolar tasas a las 192 muestras anteriores.
Otra cara del mismo objeto sigue accesible: tres pasos geométricos A→B→A del
objeto plegado pasan, con una única huella geométrica para sus cambios de rayo.

Seis tests enfocados PASS0,008s: control plegado, 24 órdenes de cuatro triángulos,
invariancia de huella al cambiar el rayo, invalidación al cambiar un vértice,
consulta incompleta/duplicada y corrupción/no mutación de inputs.
El primer test de corrupción intentó mutar una tupla del fixture y falló;
se corrigió únicamente su construcción, sin cambiar umbrales, oráculo o gates.
El report0844 provisional se conserva con su hash del test previo; no usarlo
como entrega certificada después de ese cambio.

Evidencia final: D:/PROJECTS/.cognition/neuro3d/exp005_geometric_return_cpu_20260930_0845.json
SHA `23cbb50a6a987b1f3ffb52c95f27730f28261debe6961077cab9d6c58319c0a6`;
input0804 congelado SHA `534d2c14b5ab1738f00192068c70600ae94f60b3d601eda60ddb557206eedd71`.
Doce SHAcode; registros, candidatos, distancias y resultados por orden retenidos.

La huella calculada solo cubre vertices/faces/IDs del fixture; no certifica
snapshot óptico completo, exportador Bpy, ABI GPU o estado por rama nativo.
El mismo oráculo escalar también tiene errores numéricos: no es certificación
independiente Maxwell. t_min, errores de otras caras, fase/modos, campos/ledger,
readback y revisión independiente siguen pendientes. No alterar kernels/contratos
congelados, ni ampliar conf1/bounds. JEV bloqueado: fallback local sin aval remoto.
