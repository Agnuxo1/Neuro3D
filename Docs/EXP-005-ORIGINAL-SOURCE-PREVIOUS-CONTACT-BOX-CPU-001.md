# Contacto previo SOURCE con toda la caja de dirección — sólo CPU

ID PRECISION-ORIGINAL-SOURCE-PREVIOUS-CONTACT-BOX-CPU-001; Codex capacity_audit/EXP005. Base LOCAL19f71b3b6e22eabab92961573735e613c2ad6279. P1 opt-in nuevo; no cambia módulos, runners, shaders, contratos, fixtures, bounds ni criterios anteriores.

## Resultado que entrega

Los12 slots SOURCE originales guardados, seis casos S0/S1, satisfacen la condición matemática de contacto previo en interior estricto para TODAS sus direcciones declaradas. Se mantienen ambos extremos hi-lo de dirección; no se sustituyen por dirección ideal o midpoint. A diferencia de la antigua comprobación de interior sobre19registros fabricados con dirección raw32 puntual, aquí la caja de dirección no singleton está ligada al paquete SOURCE original retenido.

Esto NO resuelve ni revoca los12autocontactos STOP del ledger siguiente: éstos siguen sin exclusión, nearest, salida de camino, permiso de GPU ni autenticación de presupuesto nativo. La condición demuestra contacto, no permiso para ignorarlo. Cotas de origen/dirección del backend, identidad global de instancia/primitiva y credencial de exclusión efectiva siguen pendientes. No produce nueva longitud o fase ni transfiere cotas del consumidor ideal.

## Contrato y prueba matemática

Modelo original-SOURCE-previous-contact-direction-box-CPU-v1, API condition(point_bounds,direction_bounds,triangle_words,model=...), evaluate_packet(packet,model=...) y run(case,source_id,model=...). Cajas3×2 de racionales canónicos firmados, positivos denominadores, capacidad4096bits y valor absoluto<=1e6; geometría raw32 finita normal/+0, sin subnormal/negativezero. Modelo explícito y datos malformados rechazan; sin parámetros epsilon, offset o ignoredID. No amplía dominios anteriores.

Sean e1=b-a, e2=c-a y n=e1×e2, triángulo no degenerado. Se acotan formas afines por signo de coeficientes sobre cajas cartesianas:

```
R(P) = n·(P-a)          D(V) = n·V
tau  = -R/D
```

Si0 pertenece a D(V), STOP aunque el punto parezca exactamente coplanar. Si R(P) no es idénticamente[0,0] sobre TODA la caja, STOP: ni proyección, snap, epsilon ni referencia puntual rescatan la incertidumbre. Sólo cuando R=[0,0] y D excluye0, tau=[0,0] para toda dirección declarada. Tau es parámetro de dirección NO normalizada, NO longitudBU/metros. Normal tiene unidades BU²; residualBU³; denominadorBU²×unidades-dirección.

Se reutiliza únicamente aritmética pura sub/cross/dot/decode/fraction/affine_interval de componentes previos, NO sus audit_plane/audit_interior ni consultas de plano/triángulo. Formas afines de u,v,w por Gram exacto; se verifica partición de coeficientes0/offsets1, y w se combina ANTES de acotar. Todos mínimos>0 implica CPU_STRICT_PREVIOUS_CONTACT_ALL_DECLARED_DIRECTIONS_ONLY. Degeneración, denominador con0, punto no idénticamente coplanar y borde/fuera quedan STOP separados. No división con denominador incierto ni desacreditación de otros oclusores.

run elige exactamente un slot del recibo QUERY-PACKET SHA5f6b3d0ec64df544fc771044796cd88f62967322a879b10fd74fd012a194d272 y verifica fuente/test/codec/purehelpers y captura lossless. evaluate_packet es caller-condicional: parent_receipt_sha256=NULL, hashes de contenido NO autenticación. Sólo run fija el recibo; un caller resellado de otra escena no recibe procedencia del padre. Presupuestos nativos autenticados, precisión nativa, exclusión/nearest/GPU/fase siempreFALSE; phase_error_boundNULL, costesUNKNOWN_NOT_ZERO. SOURCE se conserva, ninguna fusión por wire compartido.

## Evidencia nueva y límites

Suite4tests PASS/35registros:12SOURCE originales,9controles matemáticos nuevos fabricados,9malformed+3selectores rechazados,1aislamiento de copia y1caller resellado sin procedencia fija.768combinaciones de extremos originales (64porSOURCE, incluyen duplicados; NO768muestras únicas).24evaluaciones válidas de condición nuevas y9intentos malformed; no barrido antiguo ni inferencia nueva del siguiente tramo. El loader/codec de contenido se utiliza, NO producer/encoder/trace/contact-evaluator antiguo.

Controles conservan STOP cuando dirección cruza0 o es paralela, incertidumbre normal del punto±2^-59, separación de plano2^-60, vértice/fuera y degeneración. Caja tangente interior y dirección normal diminuta -2^-60 verifican la condición CPU sin introducir epsilon; tampoco autorizan exclusión física o native launch. No modificar fixtures originales para producir dichos controles.

Finalstdout45350bytes SHA040a3639a563c4cd06d5d8ca7e8e79507c55c5a2c7285329d15afe59fd2c9b25; afinidad1/CPU128MiB/RAMantes9286856704bytes/timeout30s/deadline35s nuevo/07:37:31UTC/rc0. Oráculo independiente SINimportar core/tests/productores: determinantes/Cramer y extremos afines,21filas de condición y768combinaciones originales,12SOURCEbindings,6fuentes capturadas y461pins previos. Stdout644bytes SHA982a85f4676c96265a203a72e3c7f15ca1389af4a60c3fa535fa74849acee615/rc0. Código/capturas completas en recibo. Segundos QA NO benchmark ni coste completo.

Dos capturas previas PASS y sus fuentes retenidas: revisión añadió separación de procedencia caller/fixed y negativo de caller resellado, después pin transitivo del codec. Ningún FAIL numérico observado en este helper; los72errores escalares y16filas anteriores, zero-error FAIL sintéticos, contactSTOP y falta de autenticación permanecen intactos, no convertidos enPASS. apply_patch rechazó una sustitución delete/add del mismo recibo sin cambiarlo; reparado mediante Update File, no fallo numérico ni pérdida de archivo.

Skills desarrollo/pruebas/revisión delimitan contrato, negativos y contraste independiente; cognición guarda estado factual/capturas. JEV bloqueado: LOCALsinaval/sinretry. CeroGPU/Bpy/RT/SDK/cola-reserva/foreignwriter/kill/tickets/push/merge; CPU racional condicional NO ALU/RT/óptica física. Sharedboards/checkpoint locales SINstage. Runners/shaders/fixtures conf1/v0/v4/0119/0315/nearestV2/bounds/umbrales inalterados.

## Siguiente entrega

Claude ACK ID+SHA y SOLO artifacts EXISTENTES originalSOURCE/ingress/budgets de punto-dirección/previousprimitive-identidad global/ALLcoverage/guard fail-closed/igualtrabajo-costes completos o campos faltantes precisos. No render ni barrido de relleno. Antes de usar la condición para excluir, hace falta contrato y autenticación de error nativo/credencial de origen; si no existen, seguir STOP y componer cotas direction-to-hit/longitud-referencia-fase sólo condicionalmente, sin reutilizar longitud ideal como cota de error real.

GPU futura únicamente con coordinación/reserva exclusivaClaude+gpuq, procesos/RAM/VRAM/temperatura frescos, guard fail-closed y deadline nuevo porjob; RAM>=4GiB tras>=1024bytes/celda+márgenes, VRAMtotal<=18GiB, temperatura<=80°C, pilotos<=120s/otros<=600s. Ventana histórica cerrada intacta; noMLP32768 ni proximidad al límite tras0x9F. RT16Mvs1M/salidas distintas/cruceextrapolado no es comparación equivalente ni redRT; U/GEMM no reemplaza escena silenciosamente.
