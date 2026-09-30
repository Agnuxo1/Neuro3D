# Reproducción propia de reimpactos sobre el mismo triángulo

Estado: auditoría CPU de consultas geométricas sintéticas float64, sin GPU,
Blender ni prueba de red completa. El resultado confirma un riesgo de dominio,
no un defecto medido del shader nativo ni una solución implementada.

## Método independiente

Se parte de la advertencia F1 de PRECISION-004, pero no se ejecuta código de
Claude. El script propio usa la biblioteca estándar, un generador determinista
y la intersección escalar del oráculo triangular ya existente.

Cada fixture contiene cuatro vértices y dos triángulos de un espejo nominalmente
plano. Se intersecta el rayo incidente, se calcula el punto y la dirección
reflejada y se vuelve a consultar el triángulo concreto recién alcanzado.
El origen no se desplaza y se conserva t_min=1e-9. La variante local resta el
mismo origen incidente a los vértices y al rayo antes de repetir las consultas.

Solo se contabiliza el retorno inmediato al MISMO triángulo. No se clasifican
los impactos sobre otra cara como falsos: una malla representada ligeramente
no coplanar puede tener retornos reales sobre otra cara. No se implementa ni
autoriza una exclusión por identidad del objeto completo.

## Resultado retenido

192 ensayos por perfil, todos con impacto inicial válido en ambos frames:

| Escala de coordenadas | Ángulo rasante | Reimpactos mismo triángulo, mundo | Reimpactos, local |
|---|---|---|---|
| 1 BU | 1e-4 rad | 0 | 0 |
| 100 BU | 1e-7 rad | 83 | 28 |
| 1e4 BU | 1e-5 rad | 90 | 0 |

Las coordenadas locales ayudan en estos perfiles, pero el segundo conserva
28 reimpactos. Por tanto no debe presentarse la traslación como reparación
general de autointersecciones al eliminar el bias. El propio oráculo float64
también necesita controles de robustez; la coincidencia con él no prueba por
sí sola que una escena cumpla el ideal físico.

Se retienen doce adversarios completos con vértices, caras, rayo de entrada,
primer impacto, rayo reflejado y consultas mundo/local. Cuatro tests enfocados
verifican control, riesgo residual, reproducción exacta e inmutabilidad.

## Evidencia y alcance

`D:/PROJECTS/.cognition/neuro3d/exp005_self_hit_cpu_20260930_0804.json`

SHA256 `534d2c14b5ab1738f00192068c70600ae94f60b3d601eda60ddb557206eedd71`.
El informe conserva los dos hashes de código usados.

```powershell
python -B -m unittest discover -s Blender/tests -p test_exp005_self_hit.py
```

No reproduce las cifras exactas de Claude, cuyo generador y cálculo son
distintos. No equivale a readback Bpy float32 ni al transporte GPU hi-lo.
No se han modificado oráculo, shaders, runners, t_min, contratos congelados
ni bounds. Las habilidades de continuidad y pruebas enfocadas han servido
para preservar el contraejemplo, no convertirlo en un PASS mediante exclusión.

Siguiente paso: Claude contrasta los registros retenidos dentro de PRECISION-005.
Especificar manejo de retorno inmediato por primitiva, error de punto y rechazo
de ambigüedad antes de una variante nueva. Cualquier reparación requerirá
controles positivos (incluidos retornos legítimos a otras caras), negativos y
contrato antes de integración/GPU. Generalización de V3 sigue bloqueada.
JEV bloqueado por seguridad: fallback local explícito, sin aval remoto.
