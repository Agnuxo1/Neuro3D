# EXP005 — presupuesto de cajas de posición y diferencia de longitud HOST
ID: PRECISION-POSITION-PAIR-LENGTH-BOX-BUDGET-HOST-001. Propietario: Codex, capacity_audit/EXP005.
Base: 6e2dd779f5362c3c00987acace7dc6caa525515f.
Padre RATIONALIZED001: SHA256 63ee2a87c4609b89a07d1d75a4ba5eff33f92ab094ea42a0d705b98aabb93f61, 88107 bytes.

## Contrato opt-in
Modelo precision-position-pair-length-box-budget-HOST-v1; API audit(model,request,declared_boxes). Selector cerrado de ocho cadenas: record_id, parent_receipt_sha256, parent_record_sha256, original_geometry_sha256, relative_geometry_sha256, declared_boxes_sha256, representation, intent. Solo los veinte registros retenidos; los doce STOP del padre no se rescatan. Todos los quince radios de los cinco puntos se validan, incluidos vértices no usados. Schema DECLARED_INDEPENDENT_COORDINATE_BOXES_ONLY: radios racionales no negativos, controles heredados de 128 bits y magnitud <=1000000 BU. No ampliar fixtures/bounds ni aceptar cajas como medición autenticada.

Se selecciona índice 3 (segundo vértice del triángulo) menos índice 1 (end), ambos desde SOURCE índice 0 y geometría ORIGINAL. Diferencia de longitud euclídea en BU, no referencia óptica ni camino completo. Condicional a cajas de posición independientes declaradas; no escena, incertidumbre o material autenticados.

## Cota exacta conservadora
Para delta nominal d y radio rho=radio_SOURCE+radio_destino, cada coordenada pertenece a [d-rho,d+rho]. El mínimo del cuadrado es cero si contiene cero, de otro modo el mínimo de los cuadrados de extremos; máximo en extremos. Sumando XYZ se obtienen s=[slo,shi] y t=[tlo,thi]. N=[slo-thi,shi-tlo].

E_L=sum(rho_target), E_R=sum(rho_end) son cotas L1 de desplazamiento. La desigualdad triangular acota el cambio de cada norma por E correspondiente. Con suma de raíces nominal retenida [A,B] a 96 bits, D=[max(0,A-E_L-E_R),B+E_L+E_R]. SOURCE se carga a AMBAS normas; no se cancela ni se supone correlación. Si Dlo<=0: STOP sin epsilon y sin divisiones. Si Dlo>0, la identidad (sqrt(s)-sqrt(t))=(s-t)/(sqrt(s)+sqrt(t)) permite el intervalo de las cuatro razones de extremos N/D. Solo lower>0 certifica positividad CONDICIONAL. Las cotas separadas incluyen el caso compartido SOURCE, con sobreaproximación conservadora.

## Evidencia y aceptación
Primera suite propia: 53 casos principales, 10 HOST condicionales y 43 STOP; 20 cajas cero (7 positivas, 1 negativa, 12 STOP heredados), 12 escenarios de incertidumbre en xy/xz/yz (3 positivos y 9 presupuesto agotado), 12 selector/modelo, 8 cajas malformadas, 1 denominador agotado. Fuente con radio 2^-61 BU en eje del hueco o vértice con 2^-60 BU deja Nlo=0; error de end 2^-122 BU agota presupuesto, mientras 2^-125 BU conserva positividad en estos tres fixtures. No es tolerancia universal ni incertidumbre de escena demostrada.

Verificador independiente sin importar el núcleo, sin raíz calculada y sin productores: pines SHA, contexto/geometría originales, celdas nominales 96 por desigualdades de cuadrados, extremos interiores de cajas, L1/triangular y razones. Enumeración adicional de 512 triples de esquinas SOURCE/end/target por escenario con denominador positivo (10240 triples, incluidos duplicados de radios cero), usando desigualdades polinómicas exactas para la diferencia de raíces. Las esquinas solas NO demuestran el interior; la prueba de intervalo y desigualdad triangular lo cubre.

Coste principal contabilizado: 315 radios, 42 cajas de norma cuadrada, 42 cotas L1, 80 divisiones de razones; API pública duplicada separada. Lectura/hash/verificación y coste end-to-end no medidos: UNMEASURED_NOT_ZERO. Cero llamadas root/nativo/compilador/GPU, no replay de productores previos. CPU propia un hilo, afinidad 1, timeout duro 60 s por hijo. Capturas máximo 2 MiB, intacto.

## Límites y continuación
Promotion STOP incluso con resultado condicional positivo. No fase, visibilidad completa, campo/potencia, RT, GPU ALU, Blender float32 u óptica física certificados. Antiguos UNRESOLVED/FAIL/no-nesting preservados transitivamente; roots96/runners/shaders/conf1/v0/v4/0119/0315/nearestV2 intactos. JEV bloqueado: fallback LOCAL explícito, sin retry ni aval remoto. Tableros/checkpoint locales SIN stage; solo own4 revisados en commit local, sin push/merge.
Solicitar a Claude SOLO ACK y artifacts YA existentes de backend/guard fail-closed, incertidumbre autenticada, material/completitud y contrato igual-trabajo/costes completos, por ID/path/SHA/bytes. No repetir cargas ni inventar acuse.
