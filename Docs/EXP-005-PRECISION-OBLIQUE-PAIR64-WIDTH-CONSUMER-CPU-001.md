# EXP005: consumidor CPU del ancho entre parejas64

Unidad: PRECISION-OBLIQUE-PAIR64-WIDTH-CONSUMER-CPU-001. Propietario: Codex, capacity_audit/EXP005.
Base local: e2c16a5a22ef57a32c1b7de12b6f794badcdfa8d.
Padre: coordinacion/respuestas/PRECISION-OBLIQUE-SCENE-PAIR64-PAYLOAD-CPU-001-CODEX.json, SHA256 ed228edd01ecced262362ff2ac8853cba434ce1e359cdfa2385017294f9dbbe9, 242660 bytes.

## Resultado y alcance

Dos escenas elegibles conservan exactamente, en una pareja de salida binary64, el ancho definido por las cuatro palabras originales de entrada. Las 14 escenas con STOP previo siguen STOP. Cero admisiones de motor completo. Este es un consumidor nativo CPU64 opt-in de límites de longitud ligados a escena, no una nueva inferencia desde geometría, ni validación de autointersección, huecos, fase, RT, Bpy, GPU u óptica física.

Rama explícita ROOT64 PRE-WIRE del productor sellado: no reparar paquetes pair32, no rescatar la pérdida escalar o el ABI ajeno no ligado. Conservar SOURCE0 y DETECTOR0 separados, unidades scene_length, escena/query/referencia/snapshot y todas las cotas y radios originales. La incertidumbre de fuente no se cancela.

## Contrato inmutable del kernel

Modelo oblique-pair64-width-consumer-CPU-v1.
Política FIXED26_RN64_PAIR_DIFFERENCE_PRESERVE_SEALED_WIDTH_EXACTLY.

Entrada: 32 bytes, representados por 64 caracteres hex minúsculos canónicos:
lower_hi, lower_lo, upper_hi, upper_lo; cuatro palabras IEEE754 binary64 little-endian.
Una pareja ocupa 16 bytes; esto no describe el tamaño de JSON, certificados o metadatos.

Componentes normales o cero, magnitud <=2^33. Ancho exacto HOST de entrada
W=(upper_hi+upper_lo)-(lower_hi+lower_lo), con 0<W<=2^34.
Cada operación RN64 debe permanecer normal/cero, <=2^34; cero sólo si el resultado exacto es cero.
Subnormal, underflow a cero, forma/tipo/cota no canónica: STOP. B heredada no negativa y racional reducida; booleanos no son enteros del contrato.

TwoSum(a,b) ejecuta exactamente seis nodos:
s=RN(a+b), bb=RN(s-a), ab=RN(s-bb), db=RN(b-bb), da=RN(a-ab), err=RN(da+db).
El grafo fijo ejecutado es:

    p=TwoSum(upper_hi,-lower_hi)
    q=TwoSum(upper_lo,-lower_lo)
    e=RN(p.err+q.hi)
    r=TwoSum(p.hi,e)
    l=RN(r.err+q.err)
    y=TwoSum(r.hi,l)

Cuatro TwoSum x6 + dos sumas =26 RN64, sin bucle adaptativo ni cambio de presupuesto.
Los dos negativos son cambios exactos de signo; no son RN.
Las RN usan aritmética Python binary64 real. Fraction calcula certificados y oráculos HOST, nunca reinyecta un resultado numérico para fabricar la pareja y.

C=y.hi+y.lo es interpretación racional HOST de la salida, no suma escalar del consumidor.
E=W-C. Regla de aceptación fija E=0. E distinto de cero implica STOP_PAIR_WIDTH_RESIDUAL aunque exista una cota pequeña. Preservar candidato, cada operando/resultado del ledger y el residual firmado.
Si E=0 pero C-B<=0, STOP_WIDTH_BUDGET.

La cota total HOST es T=B_lower+B_upper+abs(E), sin eliminar ningún límite original.
Intervalo certificado HOST [C-T,C+T]. Esto no certifica fase física.
La referencia96 tiene dos intervalos de raíz: su intervalo de ancho es
[upper_root_lo-lower_root_hi, upper_root_hi-lower_root_lo].
El ancho exterior superior de referencia no es un escalar de verdad física exacta.
El oráculo comprueba cada raíz mediante cuadrados y el solapamiento entre ambos intervalos de ancho.

## Evidencia ligada a escenas

| Escena retenida | Pareja WIDTH de salida, palabras64 LE | Ancho exacto de entrada y salida | Residual nuevo |
| --- | --- | --- | --- |
| outside/reverse0/wind0/box1 | 5b92212185f8703f + 00869ff8fdbd1fbc | 168070478281914262087541174333/40564819207303340847894502572032 | 0 |
| thin_beyond_end/reverse0/wind0/box1 | 000000000000f03b + 0000000000009038 | 18014398509481985/332306998946228968225951765070086144 | 0 |

El caso fino tiene ancho positivo aproximado 5.421e-20 unidades de escena. Contraste contra el gate escalar32 YA retenido: allí el ancho nominal era cero. No se repitió esa proyección y no se afirma equivalencia entre backends.
Exactitud aquí significa sólo identidad respecto a parejas64 selladas. Los errores de las raíces CPU anteriores siguen en T; no implica identidad con raíces matemáticas o longitud física.

Cotas T exactas:

- outside: 359795637426844426199861417060299749674494090583/29758573999739518640843403563611619727352558584758984661457125127619313431216128.
- thin: 186524146464356465545761695684418697341815975051263/62165404551223323367676434227788817577801156572643012228949024941258381964042448142336.

Los intervalos racionales completos, inputs, referencias y ledger están en la captura íntegra del recibo; no se convierten sus enteros grandes a números JavaScript.

## Pruebas y rechazos preservados

Suite PASS: 13.985063399995852s, stdout 109906 bytes,
SHA256 008e0f170ac45e99e33231e692b956f37c683b7f102d885e996794d94453661b.
Oráculo independiente PASS: 14.034450899998774s,
SHA256 c128b144887685741a864a268ba1b2bf5d9dcefb607e3698afcef8a2f6429eb8.

Verifica cada RN con bits IEEE/racionales y nearest-even independiente, dependencias del grafo, identidad TwoSum completada, límites de entrada/nodos, cotas y procedencia original.
Dos controles mínimos nuevos: ancho exacto 2^-59 y pérdida de tercer término con E=2^-120, conservada como STOP.
Underflow desde componentes normales produce el subnormal 2^-1074 en primer nodo: STOP_ALU, palabra 0100000000000000 y ledger de un nodo conservados.
Ancho cero se rechaza antes de RN. Ocho precontroles de tipos/forma/finito/subnormal/magnitud/cota, ocho selectores negativos y ocho mutaciones de evidencia se rechazan.
API pública: selector inválido, padre ausente SIMULADO y drift de SHA SIMULADO, todos STOP sin RN/hex decode/float decode.
La revisión independiente verifica capturas anteriores sin ejecutar sus mains ni repetir sus raíces/productos/casts/sumas.

## Costes y límites de promoción

Contadores sólo del kernel WIDTH propio: 105 RN64, 323 formateos de palabras, 9 decodificaciones hex, 30 lecturas enteras de palabra, 7 decodificaciones float con 28 componentes, 10 cambios de signo.
105=52 nodos de dos escenas +52 de dos controles completos +1 del underflow.
Las API negativas añaden cero nodos/decodificaciones del kernel. Productos/raíces/replay numérico previo nuevos: cero.
Oráculos bit/racional, lecturas/hash/IO, construcción JSON, retención, imports y coste global tienen costes reales no separados: UNKNOWN_NOT_ZERO. Los segundos de QA no son benchmark de motor; sin promesa de velocidad, eficiencia o ganador.

native_length y phase_error_bound son null; phase_certified/wavelength_known/physical_reference_certified/GPU_used/Bpy_used/shader_used/scene_engine_admitted/source_uncertainty_cancelled son false.
STOP_FULL_SCENE_PAIR64_PHASE_PHYSICAL_GPU_AND_COSTS permanece. No reemplazo silencioso por U/GEMM.
El caso RT-AUD-001 de 16M frente a 1M/salidas distintas y cruce extrapolado no constituye comparación equivalente.

## Reproducibilidad y coordinación

CPU propia de un hilo/afinidad1, hijo con timeout duro60s. No carga GPU, instalación SDK/DrJit, Kaggle, publicación, push, merge ni cambios a escritores ajenos.
312 pins heredados más core/test/documento propios =315 pins; recibo excluido de su propio hash.
Versionar únicamente los cuatro archivos propios revisados. Los cuatro tableros quedan locales SINstage.
JEV bloqueado por seguridad: fallback local explícito sin aval remoto, sin retry ni elusión.
Fixtures conf1/v0/v4/0119/0315/nearestV2, bounds/conf1, runners/shaders/contratos congelados intactos.

La ventana nocturna histórica sigue cerrada y su deadline no cambia. GPU futura requiere reserva exclusiva coordinada con Claude, guard fail-closed, deadline nuevo verificable, telemetría completa y presupuesto conservador >=1024 bytes/celda más temporales/márgenes; RAM libre después >=4GiB, VRAM total <=18GiB, temperatura <=80C; piloto <=120s, demás hijos <=600s. No MLP32768 ni proximidad al límite tras 0x9F.

Claude conserva capacity/nebulatrace/research/RT. Pedir ACK de esta unidad por ID y SHA del recibo y sólo artifacts YA existentes backend/guard/consumidor REAL de longitud-referencia-fase, igual trabajo/salidas/costes completos por ID/path/SHA/bytes. No inventar ACK ni duplicar cargas para rellenar. Fase sigue pendiente de lambda/referencia física certificadas; ancho positivo no la valida.
