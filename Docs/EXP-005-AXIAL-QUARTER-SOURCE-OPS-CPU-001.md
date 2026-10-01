# AXIAL-QUARTER-SOURCE-OPS-001: terminal desde limbs de fuente de escena

Base54378fa. Backend opt-in `axial-quarter-source-words-v1`, SOLO CPU
modelada; no GPU/ALU ejecutada. Admitir exactamente un espejo axial ±X,
referencia terminal co-móvil y modo unitario entrante certificados por
helpers congelados. Longitud decodificada/lambda debe satisfacer
4*L/lambda ENTERO exacto; fase espejo ORIGINAL ydecodificada0 exacto.
Otros ciclos/espejosfase/topologías rechazan ANTES del productor de campos,
sin Taylor/trig/fallback/umbral aproximado; no sustituye fase general.

Entrada únicamente snapshot original y presupuestos/coherencia explícitos,
no paths/campos/terminales suministrados. ABI source_transport real MODELADO
provee words hi/lo de Re/Im por sourceID/offsets3,7 y bindings originales.
Rechaza subnormal/NaN/Inf por limb, conserva fuentes separadas y orden.
Para k=(4L/lambda) mod4, incluyendo espejo -1:
0:(-Re,-Im),1:(Im,-Re),2:(Re,Im),3:(-Im,Re).
Implementar XOR de bit signo por limb y swap; no evaluación racional del
campo, producto/trig ni codificación de un residual racional nuevo.
Signos de cero NO garantía nativa/física.

Suma de limbs se usa solo como oráculo/decodificación del MODELO. Puede
diferir del decodeCPU64 congelado; cobrar L1 esa diferencia POR fuente,
además de transporte2delta_fuente+2Aoriginal*eta geométrica/fase/referencia.
No aprovechar cancelación entre fuentes para reducir errores. FuenteABI
no implica autenticación del runtime/readback/driver.

Reducción con grafo `five-twosum-32op-v1` congelado:64RN32 CPU simuladas
por fuente compleja. Se reutiliza compositor privado de casos `_case`
mediante ADAPTADOR PROPIO: su campo previous_case_accepted se etiqueta
explicitamente como admisión de TRANSPORTE nuevo, NO PASS de reporteprevio.
El flag field_values_regenerated del helper retenido también se reemplaza
por reads_new_scene_generated_source_word_terminals=true: aquí SÍ se
generan terminales NUEVOS desde fuenteABI. No aparentar reutilización de
terminales anteriores. Gates de transporte y abs/relativos todos requeridos.
Campo=sumcargasfuente+transporte+boundRN32; potencia expansión exacta
modelada<=2normaL1(Y)B+B², lower positivo sinfloor/epsilon/0div0.
NO detector/intensidadRN32 implementado; no motor fasegeneral.

Conteos de bitxor/swap/RN32 explícitos, sin prometer costes completos:
excluye certificación CPU exacta, packing/preprocessing, geometría/trace,
uploads/downloads/memoria/energía/detector. Ningún kernel/runner/fixture/
conf1/bounds/umbral congelado modificado. native/auth/GPU/ALUexecuted false.
Un hilo/hijo60s. Skills contrato/reuso guiaron opt-in limitado; JEV
fallback local sin reintento/aval. Claude acuseID/SHA y SOLO artifacts0337
geometry/limbs/bindings/backend/guard YAexistentes/igualtrabajo-costes;
no nuevas cargas/suites/barridos/guardreview.006/013/0337FAIL intactos.

## Resultado verificado, SOLO perfil exacto de cuartos de ciclo

Ocho tests PASS rc0/0,396509s (internos0,104s)/un hilo/hijo60s;18casos,
ocho aceptados/diez FAIL.42pins previas verificadas antes de nueva carga
CPU ligera. Validador independiente0,0397171s: fuente words/offsets/gauge,
permutación/cargos/bindings,1088nodos RN32 con vecinos/ties-even/cotas,
relativos/potencia y oráculos originales exactos. No repetir batería.

Cuatro cuartos de ciclo calculados desde geometría nueva con Re=.1/Im=.075
contrastados con oráculos (-Re,-Im),(Im,-Re),(Re,Im),(-Im,Re).
Oscuro MISMAS bindings anteriores y orden inverso: ideal=-2^-30,
Y=-8388607/2^53/error absoluto2^-53; bound2^-52/relativo2/8388605,
PASS1e-6 SOLOCPUmodelada. Fuente.1 original: Y=-900719925474099/2^53,
error2^-55/bound2^-54. Fuente limbs y decodeCPU64 se cobran por separado;
en estos casos diferencia limbs-decodeCPU64=0, NO omisión de charge.

source0/relative0/high_intensity/underflow/exact_dark_zero conservanFAIL.
Nonquarter/mirrorphase/mode rechazan ANTES de permutación. Desvío terminal
2^-30 respecto a cuarto exacto rechaza sin tolerancia; faseespejo ORIGINAL
2^-150 rechaza aunque decodifique0. Fuentes subnormal2^-149 rechazan.
Coherencia distinta suma potencias, no campos. 32Y0/FAIL y todos artifacts
anteriores intactos; no comparativa de fasegeneral, conf1 o red completa.

Salida terminal usa únicamente sourcewords originales del MODELOABI:
4reads/fuente, XORsigno0/2/4 y swapcomponentes0/1 por quarter; reducción
64nodos/fuente. Selector geométrico de fase/certificación todavía CPU
racional, NOimplementado nativo; cero operaciones productoRN32 en esta
permutación NO significa coste total cero ni inferencia completaGPU.

Fallo de SPAWN del primer validador inline Windows206 (comando demasiado
largo), antes de iniciar hijo, retenido por código/causa/reparación. No
fallo de tests/driver ni motivo para instalar stack. Resultado raw guardado
primero con apply_patch en artifact propio, luego validación por lectura
de archivo: ningún test repetido ni umbral cambiado. Observaciones completas
zlib/base64+SHA256 UTF8 preservan enteros exactos, no JSONfloat64intermedio.

SinGPU/Blender/reservas/cancelaciones/peerwriter. Holder/tickets ausentes en
lectura de GPUq de esta unidad, NOtelemetría/preflight/admisión. Ventana
nocturna cerrada intacta. Boards/checkpoint SINstage; cuatro propios al
commit local. Siguiente: fase general explícita y detector con errores/
costes completos; NOescala/GPU mientras falten selector nativo y contrato
guard/reserva por trabajo. Pedir artifacts existentes antes nueva carga.
