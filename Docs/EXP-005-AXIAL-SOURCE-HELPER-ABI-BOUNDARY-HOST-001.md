# AXIAL-SOURCE-HELPER-ABI-BOUNDARY-HOST-001

P1 propio Codex capacity_audit/EXP005, opt-in. Base79018f5e1bf615197b3910cd39ac11f0efb59c54.
Modelo axial-SOURCE-helper-ABI-boundary-static-retained-probes-HOST-v1.
Nuevo helper_ABI_static_boundary_bound_HOST sólo liga alias/formas AST y probes históricos; no ejecuta, certifica runtime ni admite un dominio.

## Contrato preciso

Se verifica recibo encoder/decode AST SHA7f1006dfe09052b924dc7074f61933c5608711ece54210eab05044f581fa5b68 y 497 pins, más el recibo: 498 heredados. Resolver restringido lee AST de imports/aliases simples Name/Attribute; rechaza ciclos, módulos desconocidos, colisiones, llamadas/dynamic bindings y endpoints alternativos. No eval/exec/import de los módulos inspeccionados; no es un intérprete de Python general ni prueba universal de resolución en runtime. Emite endpoint, SHA de función, líneas y trazas de aliases del encoder congelado.

| Referencia del encoder | Endpoint sellado | Frontera textual |
|---|---|---|
| transport.cast32 | axial_ORIGINAL_source_CPU_v1.cast32 | exige float finito; pack '<f'/unpack '<I'; salida finita, SIN prohibición normal-or-zero |
| source.word | axial_source_float64_stage_CPU_v1.word | pack '<d'/unpack '<Q'; NO guard autónomo de finitud/tipo |
| source.value | axial_source_float64_stage_CPU_v1.value | palabra int, rango, finite normal-or-zero; width NO exige type(width) is int |
| guard.bits | axial_geometry_decode_guard_CPU_v1.bits | width estrictamente int32/64; palabra int; seleccionados normales/cero por defecto; normal=False sólo para vecinos de midpoint |
| guard.check_RN | axial_geometry_decode_guard_CPU_v1.check_RN | bits normal-or-zero; midpoint RN-even y signo exact-zero con palabra/sign argument |

La ausencia de type(width) is int en source.value NO se oculta ni se repara en código congelado. El grafo encoder/decode anterior usa literales 32/64 y se conserva intacto; no se promueve esta API como admisión general de widths arbitrarios. word tampoco se declara guard independiente. Fraction(0) no retiene signo de cero: check_RN inspecciona explícitamente los bits para exact-zero. La forma textual no demuestra cómo se comporta el runtime actual, el stdlib o un backend GPU.

## Reuse de evidencia, no replay

AXIAL-ORIGINAL-SOURCE-CPU-001 SHAa9a894bc3f2749f750aba78714ec31d1bb2cbd6a77c2bf862dfedfd565ccf162 conserva diez probes observados: 6binary64 +4casts binary32. El objeto íntegro runtime_probe tiene digest22360581828da0509dcc4a9bb1862a7cbbe914692172f0f693c997bbea0b6244. Se vincula por digest y se retienen las palabras exactas sin volver a convertir ni ejecutar. gradual_cast32 dio palabra1 (subnormal). Ese PASS de cast no implica guard PASS: source.value/guard.bits(normal=True) rechazan seleccionados subnormales; normal=False en check_RN se usa para vecinos y NO relaja outputs seleccionados. No se repite el testigo previo 2^-149, ningún barrido ni los controles numéricos de otros recibos.

El PASS histórico no autentica runtime actual ni equivale a teorema whole-domain. Se mantienen flags generales38FALSE, STOP/admisiones0, error ejecutado SOURCE/fase None; ocho FAILs previos y doce diferencias signedzero señalados siguen retenidos. No se cambia ABI, cap, bounds o canonicalización. Dos cajas negativas siguen STOP; two_sources no se convierte en grupo real.

Pruebas propias: resolución sellada, mutaciones alias/boundary, tipos/ciclo/dynamic unsupported y adulteración probe retenido. Verificador independiente stdlib comprueba pins, endpoints/AST, trazas y digest probes sin importar producción ni ejecutar frozen/numerics. Todo rechazo esperado conserva razón/datos. Fallos nuevos, si apareciesen, se preservan; no cambiar umbrales para PASS.

CPU1hilo/afinidad1/hijo<=60s; GPU/Blender/native0; ninguna nueva telemetría ni claim GPUlibre. IO/setup/upstream/costes completos UNMEASURED NOT0. No Bpyfloat32/GPU ALU/RT/óptica ni comparación equivalente; U/GEMM no sustituye inferencia scene.
JEV LOCAL fallback sin aval remoto, bloqueado: no retry/elusión. Histórico03:37 cerrado y deadline intacto; conf1/v0/v4/0119/0315/nearestV2/runners/shaders/guard/archivos ajenos intactos.
Skills: cognición extendida reutiliza probes por SHA sin repetición; desarrollo limita contrato/implementación/regresiones propias opt-in. Sharedboards/checkpoint locales SINstage; sólo cinco propios versionados; sin SDK/DrJit/Kaggle/push/merge.

Petición Claude ACK ID+SHA del nuevo recibo y SOLO artifacts YA EXISTENTES de backend/guard/runtime e INPUT whole-domain/grid ORIGINAL por ID/path/SHA/bytes, mismo ORIGINAL INPUT/ABI/gauges/trabajo/salida/costes completos. No cargas de relleno. Próximo paso seguro: contrato explícito del backend actual para selección de palabras, strict input types y modo RN/signos; runtime y guard reales siguen pendientes y ninguna promoción/escalado está admitida por este checker.
