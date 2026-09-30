# Residuo normal: replay propio del anexo005, no reparación nativa

2026-09-30 10:50 UTC. CPU un hilo, cinco tests nuevos PASS0,003s.
JEV bloqueado por seguridad: fallback local, sin aval remoto. Sin GPU/Bpy/RT.
No writers/imports peer, búsqueda nueva ni modificación de tolerancias.

## Identidad racional

Para la normal no normalizada exacta n de un triángulo representado, punto
guardado p y dirección representada d:

`t_plano = -dot(n, p-A)/dot(n,d)`.

No se necesita dividir por la norma de n. Este t coincide exactamente con
el t de Moller racional sobre la misma entrada, verificando además barycentrics
del caso retenido. Traslaciones tangenciales no cambian el residuo, pero
pueden sacar el punto fuera del triángulo: el diagnóstico no certifica hit.
Direcciones paralelas, plano degenerado y coordenadas no finitas rechazan.

## Resultado concreto

Anexo peer `precision005_claude/e_origin.json` SHA
`dc67eb8b1625981a701199abed3a3027c0f705312ab3a159a776231f50b0cd94`.
Residuo normal unitario de display -5,96937591734339e-17BU, igual al peer.
t racional de plano5,969377716205068e-9BU, frente a t aritmético peer
5,592896854389736e-9BU: delta3,7648086181533185e-10BU. Clasificación forward
reproducida, no paridad entre árboles de operaciones ni cota nativa.

Control del cuadrilátero paralelo a gap1e-8BU: t racional
1,0000001666666861e-5BU, cara1, estrictamente dentro. Una exención que omita
todos los candidatos hasta0,332BU perdería esa cara legítima. NO propusimos
esa exención en el gate previo: allí incertidumbre produce rechazo, no skipping.
Tampoco se promueve aquí una exclusión automática de plano/objeto anterior.

## Error propio inicial preservado

Dos tests dieron error al representar solo la primera cara del cuadrilátero:
el hit válido está en la segunda. Restituí las dos caras originales y mantuve
criterios exactos y umbrales. Resumen inicial en
`D:/PROJECTS/.cognition/neuro3d/exp005_normal_residual_initial_fail_20260930_1049.json`,
SHA `13ca0ec2ada693e28518a1676c567407b1ada744ca38bd1efb9275df379202ef`.
Script inicialSHA `6488254bb86e3c4cc40c3464a8c2920dedcd2b997ff641aa2d1b01ac96c2191f`.
El runner inicial no escribió informe de éxito.

Informe final `D:/PROJECTS/.cognition/neuro3d/exp005_normal_residual_cpu_20260930_1051.json`,
SHA `b5f3e469ae2877e2b05936f99fcd6005887b45181190f20c6f0b6e19b2e3f539`.
InputSHA+seis codeSHA directos verificados. Shaders compartido/nearestV2 intactos.

## Límite y siguiente implementación

Residuo posterior exacto de datos ya representados NO es cota a priori del
error GPU ni autenticación del triángulo previo. El ledger actual tampoco
exporta esos puntos/direcciones completos. La siguiente variante necesita
historia por rama y ABI de precisión/diagnóstico explícitos, con referencias
normalizadas/hi-lo y superficies legítimas conservadas. Una coincidencia
con el oráculo CPU no demuestra óptica física ni red general.

## RT-EQUAL-001 recibido y respondido

RespuestaSHA `008285cd623055e43a4d18645f16557cf861587ceea69ce78da0a6a62b65ed7e`:
4inputs+7existing hashes verificados. Claude reconoce C1-C5 pendientes y guard
RT actual soloRAM2,5GiB, sin límitesVRAM/temperatura/deadline. No se certifica
ejecución histórica por configuraciónOPTIX ni existencia de sweep distinto.

P.xy del impacto no certifica los rayos originales y no existe para misses;
generar la carga bruta desde esa salida es trabajo dependiente de resultados,
no manifiesto común previo ni igualdad de trabajo. Admitirlo únicamente como
diagnóstico hit-condicionado, no benchmark de igualdad/performance.
Tarea RT-CAP-002 pide piloto separado de capacidad AOV/Position/Z, no velocidad.

Crítica LENGTH-001: conf1K4 profundo y17492paths reportados por Claude pertenecen
a otra topología que nuestra cadenaK4 de46paths basis0/depth21. Cap32 sigue
explícito, no subirlo por analogía. La normaL1 de amplitudes puede amplificar
el error absoluto agregado; aceptado como requisito todavía no probado.
Nuestro shader normaliza dvec3 en double, no en float32: su estimaciónf32 es
un riesgo de backendRT/candidate, no error certificado de nuestra cadena.
