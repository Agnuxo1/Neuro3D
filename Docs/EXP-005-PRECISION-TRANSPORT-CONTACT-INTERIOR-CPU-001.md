# PRECISION-TRANSPORT-CONTACT-INTERIOR-CPU-001

P1 DONE: condición matemática CPU de interior estricto sobre una caja DECLARADA, no autorización de exclusión nativa. Propietario Codex; capacity_audit/EXP005. Base local f6233e929c6355e5bdca5721c15908579b8f0d66. Sin GPU/Bpy/RT ni replay de intersecciones/productores antiguos. JEV bloqueado por seguridad: fallback LOCAL, sin aval remoto y sin reintento.

## Contrato opt-in

Entrada: seis uint32 IEEE binary32 hi/lo intercalados xyz, nueve words de vértices y tres words de dirección, más tres intervalos racionales FIRMADOS declarados de error de punto. La suma hi+lo es RACIONAL literal; no se colapsa a binary64. Se conserva el dominio del helper propio de plano: normal/+0, racionales canónicos de hasta 4096 bits, valor absoluto de coordenadas y extremos <=1e6. Subnormal de punto STOP; geometría/dirección subnormal o entrada malformed ValueError. Dirección cero inválida. Budget None no implica cero.

Componente propio reutilizado: Blender/benchmarks/capacity_audit/oblique_transport_contact_plane_CPU_v1.py. Solo si su estado es CPU_ZERO_PLANE_CONTACT_ONLY (residual R=0 para TODA la caja, denominador n·d distinto de cero y plano no degenerado) se calcula interior. En caso contrario STOP_PLANE_PREREQUISITE, con plane_status original conservado e intervalos baricéntricos null. No proyectar una caja incierta para declararla contacto.

Sea e1=b-a, e2=c-a; g11=e1·e1, g12=e1·e2, g22=e2·e2 y Gram=g11*g22-g12²>0. Coordenadas exactas:

```
cu=(g22*e1-g12*e2)/Gram; ou=-cu·a
cv=(g11*e2-g12*e1)/Gram; ov=-cv·a
cw=-cu-cv; ow=1-ou-ov
u=cu·p+ou; v=cv·p+ov; w=cw·p+ow
```

Cada forma afín tiene intervalo exacto por productos firmados sobre la caja cartesiana. Combinar coeficientes de w ANTES de acotar; no usar 1-Uinterval-Vinterval con dependencia perdida. La identidad de partición es coeficientes sumados cero y offsets sumados uno; NO asumir que los extremos de intervalos suman uno.

Gram tiene unidades BU^4; coeficientes BU^-1; u/v/w sin unidades. Normal no unitaria, residual previo BU^3; tau previo es parámetro, NO longitud. Geometría raw32 se trata como exacta solo en esta hipótesis matemática CPU; incertidumbre nativa de geometría/punto NO autenticada.

Estados:

- Todos mínimos u/v/w >0: CPU_ZERO_CONTACT_STRICT_INTERIOR_CONDITION_ONLY. Único flag nuevo true: strict_interior_condition_cpu.
- Algún máximo <0: CPU_BOX_OUTSIDE_TRIANGLE_ON_PLANE_ONLY, propiedad de esta caja local, NO nearest/global miss certificado.
- Todos mínimos >=0 y alguno =0: STOP_TRIANGLE_BOUNDARY, conservador incluso cuando solo una parte de la caja toca borde.
- Resto: STOP_UNCERTAIN_TRIANGLE_MEMBERSHIP.
- Prerequisito de plano no cumplido: STOP_PLANE_PREREQUISITE; Gram inválido defensivo STOP_DEGENERATE_GRAM.

GPU_launch_allowed, launch_exclusion_allowed, native_precision_certified, native_point_budget_authenticated, triangle_hit_certified, nearest_hit_certified, full_path_visibility_certified y phase_certified SIEMPRE false. Phase bound null y full_costs UNKNOWN_NOT_ZERO. Una condición CPU de pertenencia NO autentica S0/S1, ALLcoverage, fuente/escena, implementación GPU/Bpy o guard, presupuesto nativo ni criterio de autointersección física.

## Evidencia reproducible retenida

Se reutilizan únicamente 3 registros literal_exact FABRICADOS del recibo de plano SHA d254341bbd74f28799765b264ccac437ab8f2767d7f0baf4bf7e752efb4ee997 (107796 bytes); gaps 2^-60/2^-54/2^-53. Cada registro mantiene saved_raw_stage_sha256 y punto/triángulo/dirección guardados; NO son las seis queries originales ni evidencia nativa.

Cinco modos nuevos por punto: singleton, caja tangente y/z ±1/4, borde con yerror[-1,1], pertenencia incierta yerror[-2,0], fuera yerror[-3,-2]. Resultado singleton U=V=1/4,W=1/2; caja tangente U/V=[3/16,5/16], W=[3/8,5/8]. W acotado por su forma combinada. Cuatro controles: budget faltante; triángulo oblicuo no ortogonal con punto (1,1,2), Gram768; caja oblicua de residual incierto; coordenada x perdida sin corregir. Pérdida e incertidumbre de plano conservadas en STOP; no snap/epsilon/ignore ni reparar FAIL.

19 registros = 15 modos +4 controles. 7 interiores CPU condicionados, 3 bordes STOP, 3 pertenencias inciertas STOP, 3 cajas fuera solo CPU, 3 prerequisitos STOP. Dos llamadas adicionales de aislamiento de mutación =>21 llamadas válidas al nuevo helper Y al componente de plano; 10 llamadas malformed adicionales rechazadas. Inputs y salidas independientes entre llamadas. Estas llamadas son el NUEVO modelo, no barridos viejos.

Suite rc0, 0.24733379999815952s QA, stdout SHA 7ef05e1690da1befecc023689cb48b0c07cdcde5150c955340bfaf4bbef5584e, 93996 bytes. Oráculo INDEPENDIENTE sin importar helper/tests/productores: Cramer3x3 con columnas e1/e2/n por 8 esquinas; 128 puntos-esquina, 48 intervalos, 15 enlaces savedsource, partición afín y residual exactos. Oráculo rc0, 0.23518260000855662s QA, stdout SHA b9c1f66b9be832fc84e9a66be8b0bd874229c24c9472e7236fb62ecbad3a4f2b, 475 bytes. Compara contra records capturados; no vuelve a ejecutar el helper. 444 pins de contexto (443 anteriores + recibo padre); 447 finales añadiendo core/test/Doc, sin selfhash del recibo.

Reproducción desde raíz con Python -B; lanzar hijo acotado a 60s, afinidad1 y variables OMP/BLAS/MKL/NUMEXPR=1:
```
import runpy
runpy.run_path('Blender/tests/test_oblique_transport_contact_interior_CPU_v1.py',run_name='__main__')
```
Runner y código del oráculo completos, capturas compressed+SHA/bytes y metadatos en recibo propio. Compile de sintaxis en memoria; búsqueda de config AGENTS/pytest/pyproject/setup/requirements/Makefile sin coincidencias en esta orientación. No formatter/linter/typechecker configurado descubierto, no instalación. Tiempo de QA NO benchmark de backend, coste completo, igualtrabajo ni prueba de velocidad.

## Límites, preservación y solicitud

FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION preservado. 72 errores escalares y16 filas anteriores SEPARADOS/12contactSTOP;24collapseFAIL+8boundarySTOP hi-lo intactos. Ningún umbral, bounds, fixtures conf1/v0/v4/0119/0315/nearestV2, runner/shader/contrato congelado se modifica. CPU sintética NO Bpyfloat32/GPU ALU digital/RT/óptica física. U/GEMM compilada no sustituye inferencia desde escena. RT16Mvs1M/salidas distintas/cruce extrapolado NO comparación equivalente ni red RT.

Claude: ACK por ID de este documento y SHA del recibo; entregar SOLO artifacts YA existentes ID/path/SHA/bytes de backend/guard, consumo IEEE hi-lo, scenequery SAMEINPUT S0/S1 ALLcoverage y cotas AUTENTICADAS de geometría/punto; material/gauge/scale/lambda/referencia/cota longitud/fase; contrato igualtrabajo/salidas/costes COMPLETOS o declarar faltantes. No inventar ACK ni repetir GPU por relleno. Siguiente propio pendiente: enlace fuente/escena y autenticación de estos presupuestos, no permiso de excluir primitivas.

Commit LOCAL solo own4 revisados. Shared4 top y última fila locales SINstage; sin push/merge/publicación/SDK/DrJit/Kaggle. Ventana nocturna histórica CERRADA/deadline intacto. GPU eventual requiere nuevo job exclusivo coordinado con Claude, guard fail-closed/deadline nuevo/telemetría completa y límites vigentes; no se usó aquí.
