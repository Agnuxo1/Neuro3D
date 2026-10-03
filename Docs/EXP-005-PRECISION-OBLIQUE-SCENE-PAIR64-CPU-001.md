# EXP005 — PRECISION-OBLIQUE-SCENE-PAIR64-CPU-001

Estado: módulo opt-in de transporte/recentrado CPU; promoción y predicado posteriores STOP.
Base e5dd807de78843ad4dac5c6a0cc7aa5ae4e28c67. No GPU, Bpy, RT, óptica física ni JEV remoto.

## Contrato cerrado

Snapshot HOST sintético original y query SOURCE0/DETECTOR0/TRIANGLE0/segmento cerrado
inmutables. Política ALL15_EXACT_PAIR_WORDS_COMMON_SOURCE0_CONSTANT_KEEP_RADII.
Paquete canónico de 240 bytes: 15 coordenadas en orden origin,detector,A,B,C y xyz;
cada coordenada contiene hi y lo binary64 little-endian (16 bytes). Hash de TODOS
los bytes ligado al request y snapshot, que incluye los 15 radios independientes.
Normal/zero solamente; rechazo de NaN/Inf/subnormal, paquetes incompletos,
escena/query/política no correspondientes o suma exacta de limbs distinta del
nominal original. No se reduce ni aumenta ningún radio ni dominio congelado.

El productor NO codifica nominales ni reemplaza restas por resultados HOST.
Preparación de pruebas: 30 casts binary64 más residuales HOST por escena;
esto NO es encoder nativo. El módulo decodifica ambos limbs y verifica su valor
exacto frente al nominal. Restar el MISMO par SOURCE0 de cada coordenada mediante
el grafo nativo congelado de 26 operaciones RN64 y 2 inversiones de signo exactas.
ALL15: 390 operaciones RN64, 30 cambios de signo, 60 lecturas de limbs como
operandos del grafo (referencia repetida), 30 decodificaciones de entrada.
Los 4 EFT por coordenada y operaciones auxiliares HOST de auditoría se conservan.
No usar FastTwoSum con supuestos implícitos ni colapsar a un único float.

Salida: pares nativos y nominal racional decodificado de ESOS pares, sólo cuando
representación y resta tienen error exacto cero. Auditoría de diferencias exactas
HOST no suministra la salida. Error no nulo => STOP_NATIVE con ledger completo,
sin frame ni cota geométrica positiva. No existe rescate por umbral/radio ajustado.
Todos los radios originales se copian, también origen0±radioSOURCE0:
referencia elegida constante geométrica, NO SOURCE físico exacto ni referencia de fase.
Validación del frame con el MISMO dominio 128 bits y magnitud2^32.

## Evidencia y límites

Leer seis escenas traducidas2^30 del recibo sellado COMMON-FRAME
d17a781897aeef1289d0e1c0682462e5f9263e8c8a7f1ecf2bd26170acb2603a
(181436 bytes). NO repetir suites/ejecuciones de productores retenidos.
Nuevo transporte nativo sobre las seis escenas, sin llamar al clasificador.
Comparar puntos y radios con el marco HOST ya sellado y ligar los fallos directos
previos por hash de cada record; no borrarlos ni convertirlos a PASS.
Nueve entradas inválidas deben STOP antes del grafo. Nuevo control nativo
tres escalas 1+2^-60 menos2^-120: resta inexacta preservada y STOP.
Control nominal1/3 no representable exactamente en dos limbs: STOP_INPUT.

Oráculo independiente sólo captura/bitpatterns/racionales: reconstruir el DAG
completo, operandos, RN más cercano/ties-even y 4 EFT por resta; comprobar ambos
limbs de salida y radios. Ocho mutaciones deben rechazarse. Sin productores
en el oráculo, sin inferir visibilidad/fase del transporte.

Costes parciales registrados: bytes, decodes, RN64, inversiones de signo,
auditoría HOST, preparación de controles, integridad/parse/tests. Fullcost
UNKNOWN_NOT_ZERO: NO equivalencia igual trabajo, velocidad, eficiencia ni ganador.
Los tiempos del proceso incluyen captura/pruebas; NO throughput del motor.
Retener incidencias/fallos en recibo sin cambiar umbrales.
Ejecución CPU1hilo/afinidad1/hijo<=60s; GPU/Blender0. Frozen intactos;
boards/checkpoint locales SINstage; sólo own4 revisados en commit LOCAL.
Skills de cognición extendida y feature-development: reutilización focalizada
de evidencia y separación del nuevo contrato/pruebas; fallback local explícito.
