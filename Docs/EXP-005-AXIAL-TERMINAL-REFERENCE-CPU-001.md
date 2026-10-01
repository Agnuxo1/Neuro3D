# EXP005 — referencia terminal original (AXIAL-TERMINAL-REFERENCE-001)

Opt-in `axial-fixed-original-terminal-plane-reference-CPU-v1`, base2f40015.
Modo obligatorio explícito: plano ideal unit-X, forward-collinear con la
dirección reflejada. Punto de referencia fijo ORIGINAL en mundo, NOco-móvil.
Snapshot/word-ABI/order/sourceIDs/gauge ligados a geometry-words congelado;
leer CLOSURE/geometry existentes, no invocar productores/branchwriters.

Para dirección incidente σ∈{−1,+1}, longitud geométrica L=σ(2M−S−D).
Dirección terminal =−σ; corrección al punto del modo R: C=−σ(R−D).
Por SAME variableD compartida, Lref=L+C=σ(2M−S−R).
Esto permite cancelar D sólo en longitud referenciada; NO cancelar sus
errores/clearance para decidir hits/contacto/huecos. Geometry FAIL se conserva.
La suma de intervalos independientes L+C se muestra pero NOse usa: ensancha
la cota y pierde correlación. Es un cálculo racional exacto CPU, NOshader.

## Frontera HOST nueva

Mode-X ORIGINAL no formaba parte del ABI geométrico. Se codifica hi-lo32
con la misma fórmula HOSTsplit_double sin ejecutar el writer:2RN32+1restaRN64
por puerto/caso. Se mide |Roriginal−Rdecode| y su radio outward2^-149;
el defecto de la resta HOST también se informa. Todos se cobran por el
radio original en Lref. Modos oblicuos/zero/nonunit/NaN/bool/subnormal limbs
rechazan; YZ originales finitos, no perfil espacial Gaussian/fibra.
Ningún origen de modo exacto entra gratis como dato de un shader nativo.

Intervalo referenciado desde2M−S−R, wavelength hi-lo+radio retenido.
Cota conservadora radianes =8maxcorner|Lref/λ−LrefORIGINAL/λORIGINAL|.
Se conserva MISMOcap de fase original y gauge original por sourceID.
El rechazo phase/geometry anterior NOrevive aunque cota nueva sea pequeña.
La cota HOSTmodeencoding explícita8rR/λmin forma parte del totalintervalo,
no se suma dosveces. No tráficos/campos nuevos en módulos congelados.

Control NUEVO cambia explícitamente mode-X original a0.1 y binding:
no es revalidación de la fixture anterior. Encodingerror2^-55, carga fase>0
ycap0 original RECHAZA; no piso/epsilon/umbralrelajado. Referencia distinta
significa observable/gauge distinto, no mejora numérica equivalente.

## Verificación y límites

Tests CPU1hilo/hijo<=60s, todos13casos/14fuentes y288esquinas correlacionadas;
oráculo independiente debe reconstruir L+C desde variables originales y
enclosures, comprobar signo/cota/gauge/encoding sin imports de producción.
No repetir aritmética geometryword ni shaders/cargas0337. Se mantienen todos
gates de CLOSURE; two_sources relativoFAIL no se convierte enPASS de campo
por una referencia geométrica aceptada.
NOcertificación de árbol general/historias/modos físicos/coherencia física/
nativeABI/runtime/auth/fullpipeline/RT/óptica física ni costescomparativos.
Integrar nueva longitud referenciada en backend opt-in y grafo de operaciones
antes de promover; este módulo no sustituye inferencia desde escena por U/GEMM.
Claude dueñoRT/capacity; aportar sólo artifacts existentes ligados a igual
trabajo/modelo/bindings y costes completos. Sin GPU/reserva/cancelación/
push/merge/SDK/DrJit. JEVbloqueado/fallbackLOCALsinaval.
Skills feature-development contrato/tests yextended-cognition evidenciaretenida.
Sharedboards/checkpoint locales SINstage; versionar sólo cuatro propios revisados.

## Evidencia retenida

8 tests PASS rc0/0,3099939s; raw42633bytes
SHA41f1536f9870dac9aaa73bdefe07c696150deaf38e2144650019483c13dc77cb.
13casos14fuentes,9paths referenciados en8casos geométricos;6gates de
referencia parcialesCPU. HOST nuevos16RN32+8restasRN64 (una por puerto/caso,
no por fuente); controles/test/oráculo contados aparte, no costes comparativos.
5rechazosgeométricos y2phaseFAIL anteriores intactos; CLOSURE8upstreamstops
yrechazo relativo two_sources intactos, aunque referencia geométrica pase.
119pins previos/122huellas con tres propios. Oráculo independiente rc0/
0,2172833s:288esquinas y32control,13bindings/14IDs, modeHOSTround32 alternativo
por racional yties-even, longitud original yL+C correlacionada/fase/caps.
El punto de modo cambiado a0.1 pertenece al control nuevo, no fixture frozen.
Dos fallos iniciales SOLOexpectativas de conteo (10paths/320esquinas vs9/288).
Lectura directa de WORDS retenido confirmó8casos9paths/6gatesphase; corrección
en test/doc propios. Código numérico SHA06d90490 idéntico antes/después,
presupuesto/reglas numéricas/fixtures sin cambios. Fallos conservados en informe.
