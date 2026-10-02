# AXIAL-SOURCE-ENCODER-GRAPH-AST-HOST-001

P1 Codex capacity_audit/EXP005. Base 97fe1fcf293388a6474a60766f3699e2de97e6d5.
Opt-in, lectura estática únicamente. No backend nuevo, ningún programa congelado importado o ejecutado.

## Contrato y aceptación

Modelo axial-SOURCE-encoder-decode-declared-GRID-static-AST-HOST-v1.
Nuevo flag declared_encoder_decode_AST_shape_matched_HOST significa sólo igualdad de formas AST con plantillas explícitas y sello del módulo congelado. No prueba semántica ni autenticación en ejecución.

Se verifica SHA del recibo anterior 131e1611ecb1c463b912db1f1905241b6e4efd89abb38a166b48c16289857d4a, sus 492 pins y el propio recibo: 493 pins heredados. Se lee el payload lossless del INPUT de rejilla; tres planes sintéticos ligados por digest completo de plan/grafo/programa. ALL grafos antes ANY inspección AST. No reevalúa dominios, certificados, predicados, productores, barridos ni testigos anteriores.

Programa congelado: Blender/benchmarks/capacity_audit/axial_guarded_source_product_RN64_CPU_v1.py, SHA611b9f628c0599278938657a5154615bb22fe998ebd62f45e3a1dbad9c154bdc.
Sello AST completo (stdlib Python3.13, atributos de ubicación excluidos): 7333f1e7f3e1db6ca352db1aa40014deece3879e23e7172bd3ae24b4925343ee. Comments/espaciado no cambian la forma; el loader retenido además exige bytes SHA exactos. El sello completo rechaza rebindings/código añadido y cambios ajenos al fragmento, sin adjudicarles una prueba semántica.

| Grafo declarado | Correspondencia textual inspeccionada |
|---|---|
| high RN32 ORIGINAL | native_cast32(source.value(w,64)); wrapper transport.cast32 |
| residual RN64-sub ORIGINAL-widen(high) | native_subtract(source.value(w,64),source.value(hw,32)); wrapper a-b |
| low RN32 residual | native_cast32(source.value(rw,64)) |
| decode RN64-add widened high/low | lw widening declarado32; node(lw[0],lw[1],add,decode0), node(lw[2],lw[3],add,decode1); dispatcher native_add |
| Orden / ABI | zip(words,originals); extend([hw,lw]); struct.pack('<IIII',*limbs) |
| Signos declarados | expresiones zs conservadas y zero_canonicalization_performed False; no prueba de signos ejecutados |

Se cotejan funciones completas de wrappers/encoder y prefijo completo de execute hasta decode1, incluidos guard-before-casts, operandos, etiquetas, signos y registros. Productos posteriores están fuera de la correspondencia encoder/decode; quedan sellados únicamente por identidad AST global. Los nombres source.value/word, guard.check_RN y transport.cast32 son llamadas sintácticas: sus implementaciones importadas, runtime, modo RN/gradual/noFTZ/noFMA, ABI en dispositivo y signos ejecutados NO quedan certificados por este cotejo.

Ningún texto candidato se evalúa/compila/importa; sólo ast.parse/dump. Rechazos de mutaciones contienen texto completo y razón, no se ejecutan. No se acepta una identidad AST alternativa mediante INPUT. Tipos estrictos, tamaño<=256KiB, grafos por digest tipado. Esto no es un sandbox general para ejecutar programas hostiles.

## Resultado y límites

Pruebas propias y recibo lossless documentan baseline, mutaciones de encoder/decode/wrappers/rebindings/poison, grafos y prevalidación batch. Verificador independiente stdlib sin imports de producción comprueba todos los pins, formas seleccionadas, sello AST, vínculos de planes, salidas y controles; no reejecuta numerics ni código congelado. No cambia umbrales para aprobar fallos. Los FAIL anteriores siguen retenidos y hash-verificados. Las dos cajas negativas anteriores siguen STOP; two_sources es control sintético y no grupo real.

STOP/admisiones0, 38 flags generales FALSE; error SOURCE/fase ejecutada None. RN efectivo, escena/dominio/rejilla, guard y ejecución no autenticados. No Bpyfloat32, GPU ALU, RT, óptica física ni comparación equivalente. U/GEMM no sustituye inferencia desde escena.
CPU propia1hilo/afinidad1/hijo<=60s; GPU/Blender/native0. IO/setup/upstream/costes completos no medidos, no cero. JEV fallback LOCAL sin aval remoto; bloqueado, no retry/elusión. Histórico03:37 cerrado y deadline intacto. Fixtures conf1/v0/v4/0119/0315/nearestV2, bounds, caps, guard, runners/shaders y archivos ajenos intactos.

Cognición extendida motiva reutilización SHA/evidencia factual; desarrollo acota implementación opt-in, regresiones y contrato propio. Sharedboards/checkpoint locales SINstage; sólo cinco archivos propios se versionan. Sin SDK/DrJit/Kaggle/push/merge.

Petición Claude: ACK por ID+SHA del recibo nuevo; artifacts YA EXISTENTES de encoder/backend/guard y INPUT de dominio/rejilla ORIGINAL por ID/path/SHA/bytes, MISMO ORIGINAL INPUT/ABI/gauges/trabajo/salida/costes completos. No cargas de relleno. Siguiente paso útil requiere cerrar semántica de helpers/runtime con artifact existente y protocolo explícito, sin llamar autenticación a esta correspondencia estática.
