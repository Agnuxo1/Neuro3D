# Punto 3: protocolo prospectivo de propagación completa

Registrado antes de ejecutar el motor nuevo o sus pruebas. Los recibos históricos y las 20 consultas del punto 2 se conservan intactos.

## Pregunta y alcance

¿Puede un motor de óptica escalar ideal enumerar todos los caminos de una escena triangular representada exactamente, sin sesgo espacial, conservando huecos positivos y retornos, y rechazar explícitamente los casos sin solución geométrica/óptica única?

Este punto integra geometría robusta en **propagación completa CPU de referencia**. La GPU nativa del punto 2 valida selección de primer impacto; la red completa en GPU pertenece al punto 6. La certificación numérica del campo corresponde al punto 4. No se afirma óptica de Maxwell ni comportamiento físico.

## Semántica fijada

- Coordenadas, direcciones, transmisión, fase y longitud de onda son los valores representados, convertidos a racionales exactos. No son mediciones físicas exactas.
- Intersección, orden, punto de llegada y reflexión se calculan con racionales, sin epsilon ni normalización aproximada de la dirección.
- Se excluyen sólo contactos a parámetro cero con el mismo objeto y plano de salida probado. Un retorno a distancia positiva se conserva, incluso a la misma primitiva.
- Dos triángulos coplanares del mismo objeto se consideran una única superficie en una arista interior sólo si comparten exactamente esa arista y sus terceros vértices están en lados opuestos. Un borde exterior, vértice no certificado, pliegue, empate entre objetos o contacto independiente produce estado explícito no resuelto.
- Los segmentos coplanares se recortan contra el triángulo finito. Estar en el plano de un triángulo lejano no demuestra una colisión.
- Se enumeran transmisión y reflexión de cada divisor; sólo se omite una rama de amplitud exactamente cero. No se fusionan historiales, no hay poda por amplitud ni renormalización.
- Todo detector/escape usa un modo común, con referencia de fase y dirección explícitas. Rayos perdidos, límites de recursos y modos incompatibles invalidan el campo completo. Se conservan caminos terminados y diagnósticos; jamás se presentan como una solución completa.

## Criterios de aceptación, antes de observar resultados

1. Cadenas K3 y K4 existentes: todos los 16 y 25 estímulos base, comparación con composición analítica independiente; error de campo y balance <=1e-11. Todas las variantes phase, shift, T, lambda y sham deben alcanzar una salida declarada; phase/shift/T/lambda deben producir el efecto causal existente >1e-3.
2. Hueco positivo de 2^-44 unidades entre superficies: debe conservarse en el historial, sin saltarlo.
3. Fuente sobre superficie independiente: CONTACT; contacto de salida sobre ambos triángulos de su superficie: excluido sólo a cero.
4. Empate de dos objetos: TRUE_TIE; borde exterior: BOUNDARY; arista interior coplanar cubierta: SELECT; pliegue: no resuelto.
5. Retorno posterior al mismo objeto y primitiva: registrado; bucle entre espejos: RESOURCE_LIMIT y campo completo ausente.
6. Divisor con ambas ramas: dos terminales, conservación de potencia; transmisión 0/1: sólo eliminación exacta de rama nula.
7. Coplanaridad finita, geometría degenerada, dirección nula, fuente/terminal incompatibles y rayo perdido: diagnóstico explícito, nunca salida de éxito vacía.
8. Historial y representación simbólica exactos para cada camino. Las magnitudes flotantes sólo son estimaciones hasta el punto 4.

Los fallos se conservan. Una modificación sustancial del criterio exige enmienda prospectiva, sin borrar resultados previos. JEV consultado: connected, provenance=jev, recomienda motor versionado y ambigüedad explícita; su recomendación no prueba corrección.
