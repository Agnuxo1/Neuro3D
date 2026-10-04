# EXP005: consumidor local del recibo CPU sellado

ID PRECISION-ORIGIN-SEALED-CONSUMER-CPU-001; Codex capacity_audit/EXP005. Base df021a9ecfed78dfaf61ea57cdb4a2489178f70e. Padre PRECISION-ORIGIN-BOX-ZERO-CPU-001 SHA9a80c1df6eafc76e424639ef74cc0afef7a58b7b1482bc747dc50756f7dec72b/126063bytes. Opt-in independiente; productores/runners/shaders/contratos/fixtures/bounds/caps anteriores intactos.

## Contrato y confianza

select_cpu_property(receipt_bytes,input_bytes,scene_sha256,query_sha256,source_id,previous_primitive_id,point_bounds,direction_bounds,triangle_words).
Consume DATOS del recibo con digest y tamaño fijos en código revisado; captura interna también anclada SHA23ebd46797b16baebea99a6be42d0f72042cfef964cd7f017514b8cbc806646e/133577bytes y descompresión limitada1MiB. No acepta pin de reemplazo suministrado por caller, override, epsilon, ignore o promoción. Presupone que el propio módulo y su ancla literal se revisan/pinean: NOes firma ni autenticación del renderer/escena nativa, no robustez frente a modificación del módulo. Integridad SHA256 bajo su supuesto habitual, NOprovenance nativa.

Request debe coincidir EXACTAMENTE con un registro original sellado: SHA de INPUT bytes completos, scene/query/S0S1/previousID, todos endpoints racionales de cajas y9rawtrianglewords. Tipos estrictos bytes/str/intnoBool/tuple/Fraction, hash minúsculo64hex, INPUT<=1024bytes, num/den<=4096bits. Ninguna ampliación de dominio geométrico: igualdad con registro fijado, no reevaluación. Incluso otra caja matemáticamente válida o triángulo reordenado equivalente queda bloqueado si no es registro sellado. Identidad S0/S1 separada; no token compartido. Digest supplied sólo etiqueta comprobada contra dato sellado, NOautenticación upstream.

Resultado CPU_RECORD_BOUND_ADVISORY_ONLY_NO_LAUNCH_CREDENTIAL informa integridad LOCAL y coincidencia con evidencia IDEAL CPU, incluye copia nueva del registro y decisiones viejas exactas. Nunca emite credencial/token/skip: launch_exclusion_allowed/GPU_launch_allowed/native_precision_certified/upstream_binding_authenticated/nearest_hit_certified/full_path_visibility_certified/phase_certified FALSE; ignored_ids vacío/phaseboundNULL/costUNKNOWN_NOT_ZERO. Cualquier petición sin coincidencia única STOP_REQUEST_NOT_UNIQUE_SEALED_CPU_RECORD; recibo alterado/rehashed/otra revisión STOP. Mutar resultado no altera próxima selección.

No cálculo geométrico/replay/proof previo/import de producer ni integración al ledger/backend. 12contactSTOP/conditional_first_id=NULL y72errores escalares+16filas previas SEPARADOS permanecen. zero_error_gate FAIL_RETAINED_72_NEW_NONZERO_SCALARS_NO_PROMOTION. Emparejamiento de CPUrecord NOprueba errorcero, IEEE/FMA/FTZ/RNE/hi-lo/native endpoints/ALLvisibility/camino-longitud-fase/óptica.

## Verificación y fallos conservados

Suite propia rc0/0.6485887000017101sQA/stdoutSHAb92f2f8e0d0dc9e4207d2d2ee1087bf709f7ec097af6bd6924f5e9d466fc63c2/145058bytes. 12requests originales,38negativos, matriz completa144 mezclas header INPUT-scene-query-SOURCE vs body previous-boxes-triangles; aceptación sólo si petición completa coincide con registro sellado, no rechazar aliases idénticos por origen del dato. Mutación de retorno aislada. Ningún barrido geométrico. Conteos y oráculo independiente en recibo.

Oráculo independiente rc0/0.2257947000034619sQA/stdoutSHA6dd24ed53a1f3848e1d031bade39b55c64d2845305941094c78985fe17b5bad4: join estructural por claves canónicas (sin importar/ejecutar core/test/productor),144celdas completas/56válidas+88rechazadas. Las56 son peticiones completas equivalentes a registros sellados, no56nuevas escenas/fuentes/certificados ni mezcla incorrecta aceptada. Verifica12registros/anclas literales del módulo/429pins/38negativos/12contactSTOP/72scalarErrors+16priorRowsSEPARADOS/inmutabilidad de capturas y flags nativosFALSE. Ninguna autoridad nativa/signature, ningún cálculo geométrico nuevo.

Fallos de herramienta antes matemática retenidos: Add absolutoD, transporte PowerShell de apply_patch y helperJS btoa ausente. Reparación mismo apply_patch nativo/argumento exacto, sin cambiar código/umbral. Primera suite rc0 produjo captura truncada por presupuesto de salida; JSON.parse falló y no tuvo recibo completo; repetida sólo selección de datos, mismo stdoutSHA/145058bytes, no geometría. Avisos gitignoreACCESS_DENIED/LFCRLF sin bypass; rawHEAD/disco verificar.

Skill desarrollo/pruebas Python+cognición: interfaz opt-in mínima, evidencia previa como datos, negativos de autoridad/vinculación y verificador independiente. CPU1hilo/afinidad1/hijo60s/-B/stdlib/GPU-Bpy-RT-compiler0/oldproducers0/newgeometry0. QA NOcomparación de velocidad/energía/fullcost. JEV bloqueado fallbackLOCAL sinretry/aval. Sin agentes/SDK/DrJit/Kaggle/push/publicación/merge/escritoresajenos.

## Próximo y coordinación

Consumidor local no completa credencial nativa: pedir a Claude artifactsYAexistentes ID/path/SHA/bytes backend/guard/INPUT-scene-queryS0S1/ALLcoverage/grafoIEEE/cotas material-gauge-scale-lambda-reference/equalwork-salidas-costes completos o declarar faltantes. Acuse porID+SHArecibo sin inventarlo; no cargas relleno. Siguiente propio sólo evidencia nueva de enlace entre origen nativo y caja admitida, no otra selección redundante ni reejecución sin cambios.

CPU sintética/Bpyfloat32/GPU ALU digital/RT/óptica física separados. RT16Mvs1M/salidasdistintas/cruceextrapolado NOigualtrabajo/redRT; U/GEMM compilada no sustituye inferencia desde escena. Sharedboards/checkpoint local SINstage, sólo own4 versionados después revisión. GPU futura requiere jobClaudeexclusivo, guardfailclosed, deadlineNUEVO verificable, telemetría gpuq/procesos/RAMVRAMtemp, freeRAM>=4GiB después>=1024bytescelda+márgenes-temporales/VRAMtotal<=18GiB/temp<=80C/piloto<=120s/hijo<=600s/noMLP32768 ni límite tras0x9F. Deadline/ventana históricos cerrados intactos; no procesos/tickets ajenos.
