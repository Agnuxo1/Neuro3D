# EXP005: propiedad suficiente de autocontacto cero para cajas

ID PRECISION-ORIGIN-BOX-ZERO-CPU-001; Codex capacity_audit/EXP005. Baseb94996657224f0b0af9cead4219dce4e23a9a1b6. Padre ledgerSHA5319af7a02502d5d4d3816ad897963919b0b5bb58bcf66393dfada1b61cba211/224367bytes. Skills desarrollo/pruebas Python+cognición: contrato opt-in aislado, capturas DATOS y verificador independiente; sin agentes. JEV bloqueado: fallback LOCAL sin retry/aval.

## Alcance y distinción con el guard anterior

prove_previous_zero(point_bounds,direction_bounds,triangle_words). Helper matemático suficiente sobre una caja CARTESIANA ideal y un único triángulo rawgeometry32 previo. NO credencial de lanzamiento, NO interfaz de inferencia desde escena ni integración en ledger/shader/backend. El helper NO recibe IDs, tokens ni una autorización de skip. En tests, las cajas y el triángulo se unen al INPUT/manifest raw original,scene-query,S0S1,IDprevio y ambos recibos sellados. Callerhelper NO autenticado; no suponer que un hash suministrado prueba geometría.

No repetir el guard exacto histórico ni primera intersección/reflexión/plane/triangle/ledger anteriores. El guard antiguo requiere un único punto y barycentric exactos; esta unidad comprueba una propiedad universal de TODA la caja, incluyendo controles con anchura tangencial positiva. No trasladar su exención exacta al backend. Las cajas oblicuas supuestamente correlacionadas NO se estrechan con una identidad no demostrada: Cartesian product permanece independiente.

Dominio heredado intacto: tuple3 de tuple2 Fraction ordenados, finitos exactamentebinary64/capacidad4096bits; dirección no permite cero en todos componentes. Tres vértices tuple3 de palabras intuint32 finitas normal-o-positive-zero, |scalar|<=1e6; no bool/NaN/subnormal/negativezero. Siete subtrees AST require/power2/MAX64/round_out/sub/cross/dot iguales al core sellado anterior; scalar32 con validación explícita de tipos/palabra antes decodificar. No ampliación de bounds/conf1/fixtures/caps. Type/shape/IEEE/cap inválidos ValueError; epsilon/previousID keyword inexistentes TypeError.

## Prueba suficiente CPU ideal

Decodificar rawgeometry32 EXACTAMENTE con racionales. e=b-a,f=c-a,n=cross(e,f). Soporte afín exacto de n·(p-a) sobre la caja: cada término alcanza su min/max en el extremo según signo del coeficiente. Soporte de n·r sobre TODA caja de dirección. No convertir rangos afines rationales a gráficos RNE ni afirmar que el residual es una distancia euclídea.

Para pertenencia, GramD=(e·e)(f·f)-(e·f)^2>0. Coeficientes afines:
u(p)=[(f·f)e-(e·f)f]·(p-a)/GramD;
v(p)=[(e·e)f-(e·f)e]·(p-a)/GramD.
Evaluar soportes u,v y u+v con el coeficiente sumado; conservar la correlación de la MISMA variable p, no sumar rangos independientes. Esto es otro algoritmo CPU opt-in, sin relajar el criterio del Möller anterior.

Condiciones SUFICIENTES: soporte de residual exactamente[0,0], soporte n·r no contiene0, u.lo>0,v.lo>0,(u+v).hi<1. Entonces CADA punto de la caja está en interior de la cara y CADA dirección de la caja es transversal. Contacto con ese triángulo ocurre únicamente en parámetro tau=0 en el modelo IDEAL. Resultado CPU_DECLARED_ALL_BOX_ZERO_CONTACT_PROPERTY_ONLY y CPU_box_zero_contact_proved true. No excluye primitiva, no clasifica otros contactos o nearest.

Plano no idénticamente0: STOP_ORIGIN_BOX_NOT_IDENTICALLY_ON_PLANE; denominador con0: STOP_DIRECTION_POSSIBLE_PARALLEL_OR_COPLANAR; borde/exterior: STOP_ORIGIN_BOX_NOT_STRICT_TRIANGLE_INTERIOR; degenerado STOP_DEGENERATE_TRIANGLE. La condición suficiente estricta deliberadamente NO admite borde; no redefinir el criterio congelado ni saltar otras caras. Un desplazamiento diminuto real o una anchura normal no se borra. Ni centro sobre la cara ni cero incluido en rango prueba identidad de TODA caja.

Todas launch_exclusion_allowed/native_precision_certified/upstream_binding_authenticated/nearest_hit_certified/full_path_visibility_certified/phase_certified/GPU_launch_allowed FALSE; phase_error_boundNULL, ignored_primitive_ids vacío, SOURCE_shared_tokenFALSE. Cero en esta propiedad geométrica ideal NO significa errorcero de todos los escalares. Los 12STOP previos se preservan íntegros, sin modificar su ledger ni shader. No inferencia nativa, reflexión/redondeo/FMA/FTZ/transport hi-lo/proyecciónsnap/offset/normalización ni material-gauge-scale-lambda-reference/fase/campo.

## Evidencia, incluidos fallos

Primer contraste affine-extremal CPU:12parametrosdeplano+12barycentric,0testigos positivos interiores; SHAstdout3a89b1fae03f7e0c07aa27142d6d96ec28df6c4694f4bdbd2d80a25aa334e6ea. No ocultar el resultado negativo de la hipótesis de testigo. Inspección DATOS de captura anterior confirma12parameter_interval=[0,0],SHA4334b864a0f70426a1519d50aeadcbb3daa6b748530be1068b2168e9251176de. No nuevos barridos de corners de intersección ni ejecución de productores anteriores.

Suite finalrc0,0.29060399999434594sQA/stdoutSHA23ebd46797b16baebea99a6be42d0f72042cfef964cd7f017514b8cbc806646e/133577bytes:6escenasoriginales/12SOURCE,12propiedadesCPU comprobadas;12contactSTOP y decisiones ledger anteriores conservadas intactas/candidatoNULL.14controles FABRICADOS: caja tangencial nozero width/normalreverse/oppositedirection/anchuranormal/offplane±2^-60/posibleparalelo/paralelo/vertex/edge/outside/degenerate/obliqueexactpoint/caja oblicua sin correlación probada.17negativos tipos/IEEE/rango/capacidad/epsilon/previousID. Datos72errores escalares y16filas anteriores preservados separados; zero_error_gate sigue FAIL_RETAINED_72_NEW_NONZERO_SCALARS_NO_PROMOTION. Ningún umbral alterado, ninguna promoción/escalado.

Oráculo independiente rc0,0.252788400001009sQA/stdoutSHA3df2d2fae7ce58dd3bc1e163212deb2d40cb9c075be99cea91723ddd925900b7. Comprueba125rangos afines mediante200corners de punto y200dirección (1000valoresescalares),1controldegenerado; referencias de barycentric Cramer3x3, sin fórmula Gram del core. También confirma control sintético tau=2^-60 positivo rechazado y unión rawINPUT/IDs/SOURCE/capturasSTOP/fallos retenidos. Este conteo es de corners de formas afines, NO barrido de intersecciones de rayos ni precisión nativa/óptica.

Fallo inicial suite rc1 KeyErrorzero_error_gate antes cálculo nuevo: campo está en recibo de triángulo,no en captura. Captura/source/hash fallidos preservados; corregida sólo ruta del metadato, método/cotas/thresholds intactos. Probe no halló testigos positivos NOerror ejecución. No fallos matemáticos ocultados. Oráculo independiente usa vértices del box y Cramer3x3 en base[e,f,n] para barycentric; no importar core/test/producer ni volver a trazar rayos. Comprueba min/max de TODA caja por afinidad y convexidad, condición de transversalidad y unión rawINPUT-SOURCE.

CPU1hilo/afinidad1/hijo60s/-B/stdlib;26evaluaciones nuevas de propiedad afín. Las12consultas provisionales de plano/barycentric y operaciones del oráculo son trabajo real adicional, NO coste geométrico0. QA NObenchmark; costes completos IO/hashes/JSON/arithmetic/runtime/guard/transfers/energía UNKNOWN_NOT_ZERO. Sin instalaciones/SDK/DrJit/GPU/Bpy/RT/compiler.422pins contexto=421ledger+recibo,425conown3. No configuración específica formatter/typechecker/pytest encontrada en búsqueda acotada; syntaxcompile propio/stdlibsuite. GitignoreACCESS_DENIED/LFCRLF noeludir; rawHEAD/disco verificar.

## Coordinación y próximo paso

Próximo: consumidor de credencial ligado a escena/query/S0S1/previousID/boxes/triángulo exactos que compruebe la propiedad, sin integrar ni autorizar exclusión nativa; todavía falta contrato de cálculo nativo/origen/endpoints/ALL otras primitivas antes fullpath-longitud-fase. No convertir prueba de geometría ideal en permiso GPU ni rescatar ledger viejo.

Claude ACK nuevoID+SHArecibo; artifacts YAexistentes ID/path/SHA/bytes INPUTscenequeryS0S1/ALLcoverage/grafoIEEE/backendguardruntime/cota material-gauge-scale-lambda-reference/equalwork-salidas-costes completos o declarar faltantes. NoACKinventado/cargasrelleno/escritoresajenos. Sólo own4 versionados tras revisión, sharedboards/checkpoint locales SINstage. CPU sintética/Bpy32/GPUALU/RT/óptica física separados; RT16Mvs1M/salidasdistintas/cruceextrapolado NOigualtrabajo/redRT.

GPU futuro requiere contrato/tests/commit opt-in/reservaexclusivaClaude-job/guardfailclosed/deadlineNUEVO/livegpuq-procesos-RAMVRAMtemp/freeRAM>=4GiB después>=1024bytescelda+márgenestemporales/VRAMtotal<=18GiB/temp<=80C/piloto120/hijo600/noMLP32768noprómixoslímite0x9F. Ventana/deadline/overrides históricos cerrados intactos NOreuse. Sin SDK/DrJit/Kaggle/pushmerge/publicación/procesosticketsajenos; JEV bloqueadoLOCAL/sinretry.
