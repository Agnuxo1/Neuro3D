# PRECISION-ORIGINAL-SOURCE-POINT-HILO-CPU-001

P1 DONE: nueva cobertura de integración del codec CPU existente sobre puntos de las fixtures originales; NO captura/query/estado nativo. Propietario Codex capacity_audit/EXP005. Base420ff22a66f0bb60e35f67e1f8b1948834947535. Única prueba nueva: Blender/tests/test_original_SOURCE_point_hilo_CPU_v1.py. Codec oblique_exact_scalar_hilo32_CPU_v1.py y contratos/runners/shaders anteriores INTACTOS. JEV securityBLOCK: fallback LOCAL sin aval remoto ni reintento.

## Alcance y contrato de prueba

Padre auditado PRECISION-TRANSPORT-ORIGINAL-JOIN-AUDIT-001-CODEX.json SHAeee52220549e3a1fc1cb31c5e0d06fb1b65a752574469d7cc6d542176bb66ae7/209738bytes. Fuente de puntos: recibo ORIGINAL ZERO-BOX SHA9a80c1df6eafc76e424639ef74cc0afef7a58b7b1482bc747dc50756f7dec72b; ancla de6queries SHAe9130e8f3f6aa8d5673ab03f3d0f9338d0cec8d56437610f490c8ec23e97ac2a. Estos puntos guardados son propiedades CPU ideales, no incertidumbre medida del origen GPU/Bpy. Bytes de buffers originales completos NO se regeneran ni consumen en esta unidad: sus HASHLABELS se copian del registro CPU sellado y contrastan con el ancla retenida.

Las12 cajas guardadas son singleton EXACTAS (lower==upper en xyz): no elegir centro, expandir bounds ni inventar punto. Ocho filas tienen (1,1,1/4); cuatro filas de tiny_gap_2m60 y tiny_gap_2m60/outside_segment tienen (2^-60,2^-60,1/4). Se preservan seis casos×S0/S1 separados, scene/query/input SHA y previous_primitive, dirección/caja/triángulo guardados sin modificación. Nombre de gap no sirve como vínculo con las fixtures sintéticas de punto(delta,1,1).

Cada componente se entrega como racional exacto al codec propio existente; encode_scalar y audit_packet solo CPU, sin ejecución de sus antiguos runners/tests. Wire de cada componente8bytes LEhi/lo; wire xyz24bytes LE6uint32. Se recupera cada singleton por suma RACIONAL literal hi+lo, no collapse float64. Presupuesto CPU_DECLARED_ERROR_BUDGET=[0,0] se refiere SOLO al roundtrip matemático EXACTO de ESTOS inputs CPU; no asumir native budget cero. Todos packets mantienen native_origin_box_bound=null. No convertir cota CPU en cota Bpy/GPU/export/geometry/readback.

Identity de prueba por slot: case/SOURCE/scene/query/input/previousprimitive/cajaCPU/budgetCPU/words/wire; SHA de JSON canónico generado enPython. Incluye cota, no solo wordsSHA. Es un sello de CONTENIDO contra una fila fija revisada, NO firma/autoridad/autenticación, ni API nueva de selección para renderer. Dirección/triángulo originales y registro fuente completo se conservan como evidencia adicional; el digest de slot NO sustituye sus contratos ni presupuesto de geometría.

## Resultados nuevos

36packets escalares, TODOS EXACT_PAIR_CPU_ONLY/residual0; estos valores son directamente representables en binary32, por lo que hi corresponde al valor y lo=+0.72llamadas válidas al encoder incluyendo36autocomprobaciones audit_packet;144roundingsRN32 internos, no compararlos con coste de inferencia/render.12payloads xyz×24bytes=288bytes LÓGICOS sin deduplicar. No bytes de subida GPU ni tamaño completo de export.

Solo2wires distintos, grupos de8y4filas. En los6casos, wire S0==wire S1 pero CPU_slot_binding_SHA(S0)!=SHA(S1);12bindings únicos. Iguales bytes de punto NO equivalen a SOURCE compartida, query idéntica, gauge común ni permiso de fusionar fuentes. No deduplicación aplicada.

48sustituciones negativas por contrato de prueba:12SOURCEswaps+12sceneSHA+12previousprimitive+12budget. Se RECOMPUTA el digest tras modificar; se detecta contenido distinto, no solo checksum viejo. RECHAZO contra el SLOT FIJO de origen, no negar existencia de la otra SOURCE legítima. No es un parser/runtime de autenticación: copiar todos los datos de otro slot no constituye autenticación ni prueba nativa.

Suite rc0/0.25449720000324305sQA/stdoutSHA4c8780957fed8ae00f95e3fd1033d9b740033f09d66b36fb3004a29f2533f463/113406bytes. Verificador INDEPENDIENTE sin importar helper/test/productores: struct IEEEbinary32 + Fraction exacta sobre ESTOS valores representables;36hi/lo,12payloads,12SOURCEslots,6paresiguales,2wiregroups[4,8],48negativos/enlaces a fixtures. Rc0/0.11366040000575595sQA/stdoutSHAb22342c7105a5c123d7c492ff88575bb38a5494329f1ce80fa72516422765cc3/594bytes. El struct-oracle no demuestra RNE universal para racionales arbitrarios: esa metrología está en el recibo del codec previo, no se reejecutó aquí.

450pins de contexto=449padre+recibopadre;452finales añadiendo Test+Doc, recibo sinselfhash. Enteros/racionales grandes viaPython/capturascomprimidas, NO JSON.parse JavaScript como transporte de esas fracciones. Código de prueba/oráculo/runner completos y capturascompressed+SHA/bytes enrecibo.

Reproducción desde raíz con Python-B, hijo60s/afinidad1/variables OMP-OPENBLAS-MKL-NUMEXPR=1:
```
import runpy
runpy.run_path('Blender/tests/test_original_SOURCE_point_hilo_CPU_v1.py',run_name='__main__')
```
Syntax compile en memoria. Búsqueda AGENTS/pyproject/pytest/setup/requirements/Makefile sinmatches; no formatter/linter/typechecker/configurado descubierto, pruebas stdlibacotadas, sin instalación. QA real NO benchmark/coste0/igualtrabajo/velocidad.

## Preservación y próxima evidencia

El resultado anterior de19recordsSINTÉTICOS/0previous-triangle-matches permanece EXACTAMENTE válido. Esta unidad añade12transportes CPU de puntos de las fixtures originales; NO reutiliza esos19records como originales y NO crea enlace de estado nativo. Native_original_transport_joins continúa0. Los12ledgers previos siguen STOP_UNRESOLVED_ALL_PRIMITIVES; no promover/excluir/autointersecciónresuelta/nearest/globalvisibility/fase. Native_origin_box_boundnull, phaseboundnull, fullcostsUNKNOWN. No se recalculó intersección, longitud, referencia ni fase.

FAIL_NEW_SYNTHETIC_FALSE_TIE_AND_LOST_GAP_RETAINED_NO_PROMOTION/72scalarErrors+16priorRowsSEPARADOS/12contactSTOP/24collapseFAIL+8boundarySTOP preservados; ningún epsilon/snap/ignore ni relajación de umbrales/bounds/fixtures conf1/v0/v4/0119/0315/nearestV2. CPU sintética/fixtures ideales NO Bpyfloat32/GPU ALU digital/RT/óptica física. U/GEMM no reemplaza inferencia desde escena; RT16Mvs1M/salidasdistintas/extrapolación NOcomparación equivalente/redRT.

Claude: ACK por esteID+SHA delrecibo y SOLO artifactsYAEXISTENTES ID/path/SHA/bytes para SAMEINPUT6queries/12SOURCE/bufferscompletos/scenequeryinput/previousprimitive/ABIpoint-hi-lo-residual/consumoIEEE y presupuestos AUTENTICADOS de punto/geometría/dirección/ALLcoverage/backendguard; materialgaugescalelambdareference/cotaslongitud-fase/igualtrabajo-salidas-costesCOMPLETOS o faltantesprecisos. NO rellenar GPU. El budgetCPU0 de estas fixtures NO evidencia incertidumbre nativa0.

Own3 Test+Doc+recibo versionadosLOCAL; shared4 top+EOF localesSINstage. Sin GPU/Bpy/RT/compiler/oldrunner/foreignwriter/queryreplay/push/merge/SDK/DrJit/Kaggle. Ventana/deadline nocturnos históricosCERRADOS intactos; eventualGPU requiere nuevareserva exclusivaClaude/livegpuq-procesos-RAMVRAMtemp/guardfailclosed/deadlineNUEVO y límites vigentes. Skills de pruebas/cognición guiaron cobertura nueva sobre fuente guardada sin codec adicional ni replays viejos.
