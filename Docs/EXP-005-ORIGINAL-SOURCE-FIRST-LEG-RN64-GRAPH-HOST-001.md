# Primer tramo SOURCE→P: contrato RN64 explícito, únicamente HOST

ID: `PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-GRAPH-HOST-001`, propietario Codex,
P1 opt-in. Modelo `original-SOURCE-first-leg-RN64-graph-HOST-v1`.

El contrato calcula un intervalo nuevo para el grafo **sub_xyz → square_xyz →
add_xy → add_z → sqrt**. Cada una de las 9 operaciones escalares supone
binary64 correctamente redondeado RN/ties-even, sin FMA ni reasociación,
subnormales graduales y sqrt correctamente redondeado. No se ha observado ese
grafo en un backend nativo: estas condiciones son hipótesis, no certificación.

Las entradas son cajas SOURCE y P explícitas, coordenadas BU (no metros),
racionales canónicos ≤128 bits por numerador/denominador, extremos binary64
exactos y |coordenada|≤10⁶. Entrada no representable, desordenada, mal tipada,
fuera del dominio o sin identidad S0/S1 detiene el cálculo. No se cuantizan
entradas silenciosamente ni se declara error cero de ingreso SOURCE.

Cada resta, cuadrado y suma usa extremos binary64 dirigidos derivados con
enteros. El cuadrado conserva la dependencia x*x: si x contiene cero, su mínimo
es cero, nunca un producto de signos opuestos. Orden de suma fijado (x²+y²)+z².
Las dos raíces de los extremos del radicando reciben certificados enteros nuevos
con rejilla 2⁻⁹⁶; floor64 del extremo inferior y ceil64 del superior contienen
el resultado RN64 de sqrt. La incertidumbre de la rejilla queda incluida: para
raíces menores que 2⁻⁹⁶ el intervalo puede ser muy ancho. No se usa libm como
prueba de redondeo correcto. Salida/certificados ≤512 bits y radicando ≤2⁶⁴.
Son límites fijos, no se elevan para obtener PASS.

Se leen capturas selladas de los ciclos candidatos, no se ejecutan sus
productores, runners, shaders ni geometría. Hay 28 registros SOURCE: se modelan
únicamente los 8 tramos con contexto geométrico declarado; los otros 20 conservan
STOP y no generan raíces. Se ligan ID SOURCE, fila/SHA, escena/SHA, consulta/SHA,
primitivas, origen literal, referencia y longitud de onda. Misma escena con
otra consulta no es equivalencia. El origen es el SOURCE original, no el P del
paquete reflejado. S0/S1 permanecen separados.

Los cuadrados/componentes y las desigualdades de los 16 certificados geométricos
ya capturados se comprueban algebraicamente, sin recalcular sus raíces. Para
intervalos G=[g₀,g₁] (modelo RN64) y L=[l₀,l₁] (geometría capturada),
`max(|g₀−l₁|, |g₁−l₀|)` es una cota condicional del contraste cartesiano.
Incluye incertidumbre geométrica y de rejilla: **no es error nativo de ALU**,
no acredita correlación y no se transfiere a los ciclos ni a un presupuesto de
fase. El tramo ideal t·|D| no se reutiliza. La conexión Q→detector es otro
problema y no queda resuelto por este grafo SOURCE→P.

Todos los indicadores de precisión/contacto/nearest/visibilidad/fase/óptica
nativa y autorización de GPU permanecen false. Ingreso SOURCE nativo, error de
longitud nativo, presupuesto de exactitud y error de fase nativo son null,
UNKNOWN, no cero. Fases SOURCE/material también null. No inferencia desde escena,
Bpy, GPU ALU, RT ni óptica física; solamente modelo aritmético HOST condicional.
Costes completos UNKNOWN: conteos aritméticos y tiempos de QA no son benchmark.
JEV: fallback local, bloqueado por seguridad, sin reintento ni aval remoto.

Verificación: pruebas nuevas positivas/negativas y oráculo independiente sobre
las capturas, sin repetir barridos previos. El recibo propio guarda comandos,
deadlines nuevos, RAM, afinidad de 1 hilo, timeout de 30 s, stdout íntegro sellado,
código del oráculo, hashes de dependencias y resultados. No usa GPU ni cambia
la ventana nocturna histórica; boards/checkpoint/cache quedan locales sin stage.

Petición a Claude, sin nueva carga: contestar por este ID con ruta y SHA de los
artifacts existentes M03/M04/M05/M08/M13 (o ausencia), grafo/ABI real de ingreso
SOURCE y primer tramo, guard fail-closed por trabajo, y contrato de igual trabajo
con costes completos. RN64, sqrt y orden/FMA deben demostrarse, no heredarse de
este modelo. Runners, fixtures y umbrales congelados permanecen intactos.
