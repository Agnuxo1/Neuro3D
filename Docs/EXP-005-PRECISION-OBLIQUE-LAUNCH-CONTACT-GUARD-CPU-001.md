# EXP005: exclusión exacta de autocontacto de lanzamiento

ID PRECISION-OBLIQUE-LAUNCH-CONTACT-GUARD-CPU-001; Codex capacity_audit/EXP005.
Base 843e6ebc9a6146381b6f753015aefd132923ee2c.
Padre SHA256 b799a6a17bb59561bf7a90e78189b6db821c82dcbd1119b784c9efa0a55f8e03,
217631 bytes. Captura de visibilidad sellada SHA256
caeb7f11a25812dee86041a10b74f68adf7330d2a40724258bf71c15f25f19f5.

## Contrato CPU racional nuevo opt-in

Modelo oblique-launch-contact-guard-CPU-v1. Política
EXCLUDE_ONLY_CERTIFIED_PREVIOUS_PRIMITIVE_POINT_AT_EXACT_ZERO_KEEP_ALL_OTHER_CONTACT.
No modificar runners/shaders/contratos congelados. El guard anterior de visibilidad no
se ejecuta ni se cambia. Se usan sus capturas para DERIVAR credencial de lanzamiento;
no se repiten raíces, fase, grafos RN ni productores.

Credencial cerrada: escena/query/path por SHA, S0 o S1 literal, segment1,
primitive previa, punto y barycentric previos, version1 y alcance sintético declarado.
Se comprueba el endpoint previo t=1 y el autocontacto retenido t=0, continuidad,
pertenencia exacta del punto a la primitive por barycentric y ambos paths SOURCE.
No reutilizar credencial S0 para S1 aunque ambos lancen desde el mismo punto.
El API público deriva la credencial de registros sellados; no admite geometría nueva
ni override de epsilon, t_min, object_id, lambda/cap. El helper guard es interno:
expected debe proceder de launch() o un contexto de control sintético explícito.
Una credencial no es autenticación física de escena.

Recalcular únicamente la intersección racional del candidato con el segmento de salida:
dominio cerrado [0,1], barycentric cerrada. Excluir SÓLO un contacto puntual t=0
de la primitive previa, exactamente en el punto/barycentric certificados.
No mover origen; epsilon_BU=t_min=0. No salto por objeto: otra cara del mismo objeto,
cara adyacente t=0 o cualquier contacto t>0 se conserva como
KEEP_CONTACT_FOR_DOWNSTREAM. No decidir aquí qué contacto es target/oclusión/nearest.
Incluso si una primitive suministrada tiene el ID previo pero plano adelante,
un t positivo se conserva; en producción drift de geometría queda cerrado por SHA.

Plano paralelo disjunto o contacto fuera de triángulo/segmento: NO_CONTACT.
Plano coplanar: STOP_COPLANAR, nunca excluir un span por una credencial puntual;
sin nueva prueba de clipping ni ampliar tolerancias. Aritmética racional exacta, sin
claim de cobertura de ALU32/64 nativa, Bpyfloat32, RT o shader digital.

## Pruebas y unidades

Retener los 44 registros anteriores: 38 STOP upstream no rescatados;
6 paquetes con visibilidad CPU declarada. Ejecutar nuevas consultas locales de guard
por cada SOURCE y cada primitive original, sin repetir el runner de visibilidad.
Oráculo independiente de intersección por determinantes/Cramer, no el algoritmo
normal/plano/Gram del core. Los resultados locales no recertifican fullvisibility.

Controles NUEVOS explícitamente sintéticos, en memoria y SIN tocar fixtures:
cara del mismo objeto en t=0, cara adelante t=2^-60, mismo ID previo adelante,
salida coplanar; dos escenas y dos SOURCE. El hueco se define en PARAMETRO t,
no en BU: desplazamiento_x=(end_x-origin_x)*2^-60. En la escena de hueco2^-60,
ese desplazamiento tiene magnitud 2^-120 BU; en oblique es 2^-60 BU.
No confundir ambos ni afirmar que una prueba CPU resuelve huecos físicos.
También replay cruzado SOURCE, cambio diminuto del origen2^-100 y falsificación
de hash/source/segment/primitive/barycentric deben cerrar antes de geometría.

Sin capa de fase/longitud adicional, sin cambiar caps o radios de los datos sellados.
phase_error_bound=null, scene_authenticated/full_visibility/native_hit_coverage/
phase/physical_field/GPU/Bpy false; object_wide_skip y SOURCE_shared_token false.
No U/GEMM sustituto de inferencia desde escena ni superioridad de motor.

## Costes, seguridad y coordinación

Cada guard cuenta una geometría intentada tras validar tipos/credencial. Conteo
parcial: no todos los productos/divisiones/racionales/certificados/hash/IO/JSON.
Costes globales UNKNOWN_NOT_ZERO, segundos QA NO benchmark.
Nuevas raíces/RN nativas/replays productores anteriores cero. Productos/divisiones
HOST de geometría y del oráculo son reales y NO cero. Mantener fallos capturados.

CPU propia1hilo/afinidad1/hijo60s; GPU0. JEV bloqueado: fallback LOCAL sin aval remoto
ni retry. Sin SDK/DrJit/Kaggle/publicación/push/merge; no ejecutar escritores Claude.
Fixtures conf1/v0/v4/0119/0315/nearestV2 congeladas. Sharedboards/checkpoint SINstage;
versionar sólo cuatro archivos propios revisados. Ventana histórica cerrada/deadline intacto.

Claude mantiene capacity/nebulatrace/research/RT. Solicitar ACK por ID/SHA y
artefactos YA existentes ID/path/SHA/bytes de guard real/backend/igual trabajo,
salidas y costes completos. RT-AUD-001 16M vs 1M y salidas diferentes no es comparación
equivalente ni redRT. No repetir GPU para rellenar artefactos.

## Resultado

Suite final PASS, 0.36057609999988927s/133336bytes/stdout SHA256 ffd3212bcb60e9b99d9cdc2b321df61c1690590664c36183762e27be6b799b35.
La suite inicial PASS se conserva como provisional, NO validación completa: negativo
dirigido posterior detectó True==1 en el numerador de launch_point_BU.
Fallo real rc1 conservado (stdout SHA256 3e685beb8fd98fa09d70701682745ca811eea1d2cef08c224d57774548e04810):
credencial bool excluía el punto antes de endurecer tipos. Corregir validación de
racional/vector y barycentric de credencial ANTES de geometría; no cambiar epsilon,
barycentric geométrica, algoritmo, umbrales ni fixtures. Test permanente incluido;
9 tokens inválidos, 8 selectores, 4 replaySOURCE, 3APIneg, origen desplazado rechazados.
38 STOP upstream; 28 consultas originales; 16 controles nuevos sintéticos.
44 geometrías guard/suite; 88 entre ambas suites +1 negativa enfocada fallida =89,
contador PARCIAL. Oráculos Cramer, derivación token y hash/IO/JSON/racionales no
incluidos; costes globales UNKNOWN_NOT_ZERO. Ninguna raíz/RN nativa ni replay anterior.
Missing/drift API son SIMULADOS. Oráculo independiente posterior lee capturas/pins.
