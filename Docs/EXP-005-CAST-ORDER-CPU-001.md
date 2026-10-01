# El ledger cuantizado no reproduce la suma interna del shader

Auditoría P1 propia, sin GPU: lectura del shader compartido congelado
SHA914bf296...dfcd1, del consumidor y del transporte real `split_double`.
Reutiliza los TRES snapshots de SCENE-CONVERSION-001/ad04c656...3fd20;
no vuelve a ejecutar el productor, trazar escenas ni barrer PRECISION005/006.

Hallazgo de contrato: `exp005_shared_frontier.glsl` líneas37/67–69/85–86
acumula campos `dvec2` en doble precisión. Convierte cada ruta a float32
solamente para el ledger diagnóstico; este no realimenta `sum_fields`.
Al final convierte el campo acumulado y, por separado, su potencia a float32.
El productor CPU b83b2ae cuantiza CADA ruta antes de su reducción RN32.
Por tanto no son el mismo contrato de orden ni el mismo productor.

Un modelo CPU AISLADO, con fase identidad asumida y el transporte hi-lo
existente, muestra:

| Control retenido | Suma32 del ledger | Acumular64 y convertir al final |
|---|---:|---:|
| Fuente0,1 | 13421773/134217728 | igual campo final |
| Fuente0,1*2^25 | 13421773/4 | igual campo final; error~0,05 persiste |
| Dos fuentes casi oscuras | 0 | (2^23-1)/2^53, NOcero |

El ideal del último control es 2^-30. Los errores hi-lo de sus dos fuentes
son distintos: 2^-55 y3*2^-55; no se cancelan. El error absoluto modelado
es2^-53 y relativo2^-23, frente al100% del modelo de cuantización previa.
Esto NO demuestra que una ejecución nativa tenga esos valores: quedan fuera
geometría, fase/sin/cos, RN/FMA/FTZ/reasociaciónGPU y autenticación runtime.
El shader incluso usa trigonometría float32; acumular64 no certifica toda
la precisión ni elimina errores de transporte o conversión final.

La potencia debe comparar su propio canal con el oráculo: para0,1, el modelo
del canal de potencia da5368709/536870912, mientras el cuadrado EXACTO del
campo final redondeado es180143990463529/18014398509481984. Diferencia
-9395241/18014398509481984. No sustituir uno por otro silenciosamente.
No se cambia ningún gate ni se reclama fallo del decoder con esta diferencia.

Cuatro pruebas focales pasan. Fallo inicial de expectativa conservado:
se esperaba erróneamente cancelación exacta del transporte; se corrigió la
expectativa con fracciones independientes, sin cambiar algoritmo ni umbrales.
Una salida del segundo intento quedó truncada al transportar el resultado;
se repitió SOLO esta pequeña unidad para conservar evidencia íntegra.

Petición a Claude por CAST-ORDER-001 y SHA: si YA existen capturas del mismo
shader, conservar canal de campo, potencia y ledger separados, orden/fuentes,
snapshot/ref/lambda/backend/guard/costes completos. No pedir otra carga ni
suite/guardreview para responder. Sin archivos ajenos modificados, Bpy, RT,
óptica física, promoción nativa, push o aval JEV. Skills review/cognition
guiaron la separación de contratos y la reutilización factual acotada.
