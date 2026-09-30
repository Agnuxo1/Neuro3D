# Aplicabilidad del testigo exacto a impactos redondeados

2026-09-30 09:41 UTC. Solo CPU, fallback local; sin consulta JEV bloqueada.

El testigo f527e93 funcionaba sobre partidas representadas exactamente en el
plano. Ahora se contrasta, sin modificarlo, con los doce casos congelados de
autointersección, tanto en coordenadas mundo como locales. Se reproducen solo
sus 24 consultas guardadas; no se regenera el muestreo de 192 rayos.

## Resultado

Las 24 partidas redondeadas son rechazadas por el testigo exacto:

| Frame CPU | t racional positivo | t racional negativo | t exactamente cero | Aceptadas |
|---|---:|---:|---:|---:|
| Mundo | 12 | 0 | 0 | 0 |
| Local | 8 | 4 | 0 | 0 |

t es distancia firmada desde el punto redondeado hasta la misma primitiva
anterior, usando el rayo reflejado representado. En mundo abarca
1,5991282436e-9 a 5,2089744187e-8 BU; en local, -9,2120939891e-10 a
2,8845591502e-9 BU. Trasladar el frame no hace exacto el punto de salida.

Esto limita la aplicabilidad del testigo, NO demuestra 24 fallos físicos ni
una tasa general: los doce fixtures se seleccionaron por reimpacto en mundo,
y la primera intersección/reflexión ya usa aritmética CPU redondeada. Los owners
son etiquetas sintéticas explícitas, no metadatos ópticos recuperados.

Cinco tests PASS en 0,024s: cobertura completa, input intacto, parámetros
racionales encerrados en intervalos CPU cuando det está resuelto, rechazo de
consultas guardadas alteradas y de cobertura parcial. No se cambia epsilon,
se proyecta el punto, se fuerza t=0 ni se ocultan rechazos para conseguir PASS.

## Evidencia

- Input0804 SHA256 `534d2c14b5ab1738f00192068c70600ae94f60b3d601eda60ddb557206eedd71`.
- Report nuevo `D:/PROJECTS/.cognition/neuro3d/exp005_departure_replay_cpu_20260930_0942.json`.
  SHA256 `d7bb937fca9c70bb2c371a2e8259fa9f2d3efe5f8f096cc0562fc88354d4e34d`.
- Report previo0934 intacto; 16 hashes de código verificados, incluyendo los
  shaders congelados. No ejecución ni cambios de código ajeno.
- Reproducción: `python -m unittest discover -s Blender/tests -p test_exp005_departure_replay.py -v`.

## Consecuencia para el contrato

No integrar este testigo como solución general de partida. Se necesita un
presupuesto de error del origen reconstruido y continuidad por rama verificable,
además de la cota de intersección. Si la banda espacial de la propia superficie
se solapa con otra superficie válida, debe abortar de forma explícita; un ID
previo no justifica saltarse todos sus candidatos positivos ni el objeto entero.
Esta es una obligación prospectiva, no un algoritmo nativo implementado.

Claude: dentro de PRECISION-005 contrasta un registro local positivo y uno
negativo, y critica cómo justificar la banda del origen sin eliminar el gap F5
o retornos legítimos a otra cara. 006 sigue después; sin nuevo encargo paralelo.
Sin GPU, Blender, campos, RT, transporte nativo o ventaja de eficiencia probada.
