# EXP005: hueco fino conservado en geometría, empate falso al redondear

ID PRECISION-THIN-GAP-FALSE-TIE-CPU-001. Codex capacity_audit/EXP005, base239630adae525a9ad0ef71ac797efda5482a1ecf. Auditoría CPU SINTÉTICA nueva y acotada, NO otro backend/admisión/selector ni barrido de los seis INPUT originales. Skills pruebas Python+cognición: contraejemplo explícito, coste de operaciones y fallos preservados, verificador independiente. JEV bloqueado fallbackLOCAL/sinretry/aval.

## Escenario y grafo declarado

Un rayo fabricado o=(1,1,1),d=(-1,0,0). Dos triángulos con vértices (x,0,0),(x,4,0),(x,0,4), uno en x=delta y otro x=0. Todos sus escalares rawbinary32 son normales o +0, finitos/abs<=1e6; delta=2^-60 es representable binary32 (word0x21800000). No se aumenta dominio/cap/radio/conf1 ni se modifica ninguna fixture original. Son4rays fabricados, NO SOURCE S0/S1 de una escena admitida. Bundle rawstage96bytes por caso, NO INPUT N3DG32V1 ni dispatcher autenticado.

Grafo Möller del candidato first-hit congelado, fuente SHAbe70c31483ddadb6e750741151acd9f4bae26703a0647e314d750fc1af3641b3/5011bytes: edge1=b-a,edge2=c-a,p=cross(d,edge2),det=dot(edge1,p),s=o-a,q=cross(s,edge1),u/v/t divisiones de dots,uv=u+v. Operación por operación RNE binary64 declarada, SIN FMA/contracción, sumas dot (x+y)+z. Auditoría nueva reproduce ese orden con racionales y redondeo por enteros nearest-ties-even; NOejecuta/importa shader/modelos/productores antiguos. No es intérprete SPIRV, validación CFG, garantía del driver, Bpy o GPU.

Por triángulo51nodos RNE64:24mul+15sub+9add+3div.8evaluaciones nuevas (2triángulos×4controles)=408nodos. Reconstrucción ilustrativa posterior o+t*d:6nodos×4casos=24; total432nodos. Este grafo de reconstrucción NOestá emitido por el first-hit congelado (que no calcula reflexión/origen); es un contrato futuro declarado separado, no dato de dispositivo.

## Contraejemplo retenido y controles

delta=2^-60: referencias exactas tA=1-delta,tB=1,u=v=1/4. A es única primera cara en ambos órdenes. En el grafo binary64, s.x=RN64(1-delta)=1 para A; q.z=4 y numerador t=16, luego tA=tB=1. Selección conservadora congelada state5 por empate en ambos órdenes; chosen parcial depende del orden y NOse admite como impacto. No IDtie-break, epsilon o ignore.

Reconstrucción nueva declarada o+tA*d da (0,1,1) en vez de (delta,1,1): error x=-delta BU. Residual del plano x-delta=-delta, no cero; contacto geométrico con caraA no ocurre en tau0 desde ese punto. Un traslado a la caja ideal sobreA no puede justificarse sólo porque sus rawvértices y el primer impacto exacto estén sellados. No se ejecuta ni revoca el helper de propiedad ideal ni su consumidor; sus12STOP y contratos anteriores intactos.

Control delta=2^-54 (word0x24800000): mitad del ULP inferior a1, ties-even redondea1 y produce el mismo empate falso/pérdida de hueco. Control delta=2^-53 (word0x25000000): diferencia representable, parámetros distintos/primeraA y reconstrucción exacta SOLO en ese caso. Control delta=0: triángulos realmente coincidentes, empate verdadero state5 retenido. El contraste distingue empate geométrico real de colapso de parámetros distintos. No tolerancias/umbral/cap alterados para convertirFAIL enPASS.5controles adicionales de ties-even firmados para el redondeador.

Se demuestra un límite del grafo CPU DECLARADO bajo esas operaciones, NO un fallo observado de driver/hardware ni un bug nuevo de un backend certificado. El candidato ya era UNCERTIFIED y bloquea el empate: este control añade una causa concreta de STOP y de por qué un origen ideal no acredita el origen reconstruido. No ejecutar cargas para fabricar readback.

## Evidencia y alcance

Captura primaria rc0/0.2813719999976456sQA/stdoutSHA7f9db8229ff1ae22c8f50a9fd24598ced363eedbdb045eb9efb4fb912bc7832c/135725bytes. Traza432nodos conserva argumentos/preRNE/resultado/error exacto por operación, rawwordbundle/SHA, ambos órdenes, referencias por planos y baryGram.430contextpins=429consumer+recibo, másDoc431. Precisión del nuevo control sigue FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION; padre FAIL_RETAINED_72_NEW_NONZERO_SCALARS_NO_PROMOTION con72scalarErrors+16priorRowsSEPARADOS/12contactSTOP. PASScaptura NOprecisionPASS/no promoción/nearest/fullvisibility/fase.

Oráculo independiente rc0/0.22928390000015497sQA/stdoutSHAff581050f13034f05ca9e4c9a8e2d68c135fa36b7b96ab6c3552ebc506e6397a. No importa ni ejecuta auditoría/test/productores: contrasta432nodos con ALU float binary64 del HOST observado (mantissa53/maxexp1024), rawbinary32 mediante struct y referencias geométricas alternas por plano x=X/y,z. No gráfico del driver ni emulación SPIRV. Conteo24div/204mul/120sub/84add;2errores locales de s.x (+2^-60,+2^-54),2errores de parámetros y2de puntos en LOS MISMOS2casos; métricas distintas NOsumar como6fallos independientes.4bundles rawstage96bytes/5ties-even controls/8selecciones graph y8exactas en ambos órdenes verificados. Las operaciones del oráculo son coste real adicional de QA, NOtrabajo0 ni benchmark; evidencia de redondeo del HOST sólo para estos nodos/controles.

CPU1hilo/afinidad1/hijo<=60s/-B/stdlib.8nuevas referencias exactas y72decodificaciones de words geométricos, más operaciones/boundaryQA/hash/IO/JSON/oráculo con costes completos UNKNOWN_NOT_ZERO; QA NO benchmark ni velocidad/eficiencia/motor ganador. GPU/Bpy/RT/compiler/oldproducers/replaysoriginales0. Sin SDK/DrJit/Kaggle/push/merge/publicación/procesos/tickets/escritoresajenos. GitignoreACCESS_DENIED no eludir. Fallo de búsqueda shellglobWindows fue previo a matemática y se retiene; reparación sólo rg -g sobre carpetas, no criterio.

## Próxima decisión técnica

Antes de promover: contrato nuevo que conserve la distinción entre parámetros y vínculo origen-caja. Un posible cálculo robusto compara cocientes con numeradores/determinantes y lleva residual/hi-lo en reconstrucción; es PROPUESTA, no solución implementada o validada. No parchear el candidato congelado, snap al plano, normalizar d, aumentarepsilon/bounds/conf1 ni excluir porID. Este hito no concede presupuesto de error ni cota óptica.

Claude ACK nuevoID+SHArecibo; pedir SOLO artifactsYAexistentes ID/path/SHA/bytes mismoINPUTscenequeryS0S1ALLcoverage/native-origin-box-grafoIEEE/backendguardruntime/material-gauge-scale-lambda-reference/equalwork-salidas-costes completos o declarar faltantes, sinACKinventado/cargasrelleno. CPU sintética/Bpyfloat32/GPU ALU digital/RT/óptica física separados; RT16Mvs1M/salidasdistintas/cruceextrapolado NOigualtrabajo/redRT; U/GEMM NOsustituto de escena.

Sólo Doc+recibo propios versionados tras revisión; sharedboards/checkpoint locales SINstage. GPU futuro sólo contrato/tests/commit opt-in/jobClaudeexclusivo/guardfailclosed/deadlineNUEVO/gpuq-procesos-RAMVRAMtemp/freeRAM>=4GiB después>=1024bytescelda+márgenestemporales/VRAMtotal<=18GiB/temp<=80C/piloto120/hijo600/noMLP32768 ni límites tras0x9F. Histórica ventana/deadline/overrides cerrados intactos NOreuse.
