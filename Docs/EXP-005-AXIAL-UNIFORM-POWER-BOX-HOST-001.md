# EXP005 — AXIAL-UNIFORM-POWER-BOX-HOST-001

Modelo opt-in: axial-uniform-power-encoded-box-RN64-HOST-v1.
Propietario Codex, capacity_audit. Base c869ff728fd745b6bfbc9399ecc17ac9c3e91665.
Predecesor STAGE-CLOSURE-HOST-001 SHA dbdd33989b452690272a942c31214bf9ed9af0b577dac26b04c685fae2039e27.
Fallback LOCAL: JEV bloqueado por seguridad; no reintento ni aval remoto.

## Teorema limitado al dominio declarado

Se declara una caja rectangular cerrada de componentes codificadas [rlo,rhi] x [ilo,ihi].
Extremos racionales canónicos, ordenados, finitos y acotados en longitud (4096 bits).
El modelo asume binario64 nearest-even con subnormales graduales, sin FTZ ni FMA.
No demuestra que un dispositivo ejecute ese modelo.

u=2^-53, eta=2^-1075. Si todo argumento exacto cumple |x|<=M<=MAX_FINITE:
E(M)=u*M+eta, con E(0)=0. En cada binade normal el error RN es como máximo media separación <=u*|x|;
en subnormales es como máximo eta. La restricción conservadora M<=MAX_FINITE excluye overflow.
Esto prueba una cota analítica uniforme; las muestras no son la demostración del continuo.

R=max(|rlo|,|rhi|), I=max(|ilo|,|ihi|).
Mr=R^2, Mi=I^2; Er=E(Mr), Ei=E(Mi).
S=Mr+Er+Mi+Ei; Es=E(S); potencia RN uniforme <=Er+Ei+Es.
Mr, Mi y S deben ser <=MAX_FINITE; si no, ValueError/STOP, sin clamping.
Grafo fijo: RN64(r*r), RN64(i*i), RN64(sq_r+sq_i).
Las cotas incluyen todo redondeo de este grafo, no fuente/reducción/transporte/otras etapas.

## Referencia ORIGINAL: sólo teorema condicionado

Sean mr y mi los mínimos de |r|,|i| sobre la caja, cero cuando el intervalo cruza cero.
Suponiendo adicionalmente un B uniforme L1 entre campo codificado y ORIGINAL:
lower_field=max(0,mr+mi-B); lower_power=max(0,max(mr,mi)-B)^2.
Propagación field->power <=2*max(R,I)*B+B^2, con unidades de potencia.
Relativos: B/lower_field y (prop+Er+Ei+Es)/lower_power.
Denominador cero deja relativo None y STOP; no epsilon ni denominador observado.

La primitiva permite B como hipótesis SINTÉTICA explícita, no certificado ni claim de escena.
API de escenas sólo acepta selección de casos/variante/modelo fijados por recibos SHA.
NO acepta caja/B/cupo/scope/certificado del caller. B uniforme permanece None en TODOS los casos retenidos.
La cota de esquina existente no se recicla silenciosamente como B uniforme.

## Integración conservadora

Se verifican pins y contexto fresco de seis buffers, scene/ABI/gauges/grupos/fuentes y diamonds de recibos.
Para grupos de campo elegibles se construye la envolvente de sus palabras de esquina retenidas.
Prueba RN para ESA caja, pero scene_image_enclosed=false: falta demostrar que toda la imagen de escena esté contenida.
Compara contra power_RN64_cap_abs INPUT ya retenido: no autosplit ni aumento de cupos/fixtures.
Se conservan status/razones de FAIL previos y STOP de fuentes/grupos; no suma parcial multifuente.
Obligaciones del ledger previo quedan pendientes: este teorema limitado no las cierra por sí solo.
Fullpipeline, restante, detector, native, GPU, auth y ORIGINAL global de escena permanecen false.

## Verificación y costes

Una suite de seis tests, captura stdout íntegra comprimida y SHA en el reporte. No repetir para guardarla.
Cuatro variantes enlazadas a recibos anteriores; comprobaciones de hueco de referencia/cero/subnormal/overflow/inyección.
Tres contraejemplos anteriores reutilizados por SHA; cero replay de sus ocho nodos RN.
12 controles SINTÉTICOS nuevos, 36 nodos RN HOST, más 36 contrastes del oráculo entero independiente.
Cero cálculo numérico nuevo de geometría/fase/campo/potencia de escena; sólo cotas racionales nuevas.
Oráculo stdlib sin imports de producción: pins, caja, fórmula, contexto, cupos, STOP/FAIL y cada nuevo nodo.
Tiempos son CPU ligera de tests/checker, NO costes completos del pipeline ni comparación GPU/RT/óptica.
CPU un hilo por entorno numérico, hijo limitado a60s; sin cargas GPU/Blender.

Siguiente: checker explícito de enclosure y B de fuente/reducción uniforme ligado al MISMO INPUT/escena/ABI.
Claude: ACK ID/SHA y sólo artifacts YA existentes matching backend/guard/dominio; contrato igualtrabajo/salidas/costes completos.
0337 histórico cerrado/deadline intacto. Frozen/runners/shaders/fixtures intactos; boards locales SIN stage.
No SDK/DrJit/Kaggle/push/merge/escritores ajenos ni afirmaciones de velocidad/eficiencia/motor ganador.
