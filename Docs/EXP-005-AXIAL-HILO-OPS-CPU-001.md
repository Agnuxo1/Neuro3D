# AXIAL-HILO-OPS-001: contrato de operaciones, simulación CPU de RN32

Base1f59e91. Opt-in `five-twosum-32op-v1`; NO implementación GPU/ALU
ejecutada. Solamente informe AXIAL-HILO-TERMINAL-001 SHA
7f82df1358ca2264ada8a39e884615b56845a4265768e20556860fcdbc37200e
y sus37huellas; no campos/escenas/report sustituto suministrados.
No repetir productor/Taylor/suites/barridos ni modificar archivos congelados.

Dos limbs normales/cero por componente. RN32 ties-even tras CADA operación,
sin FMA/fastmath/reasociación/binary64 intermedio como resultado contratado.
Fracciones CPU representan inputs/resultados y oráculo EXACTO de cada RN32;
NO operaciones realmente ejecutadas en hardware32 ni coste gratis racional.
Subnormal en inputs o CUALQUIER intermedio/overflow rechaza, sin asumir FTZ.

TwoSum(a,b): s=RN(a+b), bb=RN(s-a), aa=RN(s-bb), da=RN(a-aa),
db=RN(b-bb), e=RN(da+db). Son6operaciones, no presuponer identidad exacta
sin comprobarla: se cobra |s+e-a-b| mediante oráculo CPU por nodo/caso.
Schedule fijo para (a_hi,a_lo)+(b_hi,b_lo):
s,e=TS(a_hi,b_hi); t,f=TS(a_lo,b_lo); u,g=TS(e,t);
v,h=TS(s,u); w=RN(g+f); z=RN(h+w); hi,lo=TS(v,z).
Cinco TS+dos RN=32operaciones/componente,64/complejo por fuente incluyendo
acumulador inicial0. Conserva orden original, no fusiona grupos incoherentes.

Definir delta_TS=(s+e)-(a+b) y delta_RN=RN(a+b)-(a+b).
Por sustitución en ese grafo, error final local=sum(cinco delta_TS+dos
delta_RN); cota<=sum|deltas|. Registrar todos32nodos/palabras/redondeos,
verificar identidad por oráculo exacto en cada paso. Cota de reducción del
grupo=sum(cotas locales de pasos), sin crédito por cancelación. NO teorema
universal/native TwoSum certificado; únicamente evaluación CPU por caso.

Bgrupo=sumBpath retenidos+B_reducción nueva, potencia<=2normaL1(Y)B+B².
Presupuestos absolutos/relativos del MISMOcaso retenido, lower>0 sinfloor/
epsilon/0div0. Upstream/rechazos previos se mantienen como condición extra.
Gauge/coverage/binding original y decodificado propagados, outputs nuevos
NO mediciones físicas. Potencia por puerto es cuadrado EXACTO modelado de
expansión, NO detector/RN32intensidad implementado.

Costes: terminales4palabras/fuente de artifacts existentes;64ops/fuente,
32entradas de trace por componente/fuente. Excluye productor, preprocessing,
geometría/raytracing, uploads/downloads, memoria/energía y detector. Conteos
NO costes completos, tiempos de tests NO benchmark igualtrabajo/eficiencia.

Nativo/GPU/auth/promoción/ALUexecuted=false SIEMPRE. Racional previo y32
congelado intactos; no ampliación de budgets/conf1/bounds/fixtures paraPASS.
Claude: acuse porID/SHA y SOLOartifacts0337 geometry/limbs/bindings existentes,
backend/guard existentes e igualtrabajo/costes completos; no nueva carga/
suite/barrido/reviewguard.006/013 y0337FAIL intactos. JEV fallback local sin
reintento/aval. Skills contrato/reuso guiaron scope y terminales retenidos.

## Resultado retenido y límites

Ocho tests PASS rc0/0,700371s (tests internos0,137s), un hilo/hijo60s.
13casos escena RETENIDA/1024nodos RN32 modelados y cuatro primitivas nuevas
(128nodos adicionales). Se verificaron37huellas frozen. Validador independiente
de palabras/vecinos/ties-even/grafo/cotas/relativo/potencia0,0265534s;
no llamó productor ni simulador para reconstruir campos nuevos.

Seis casos aceptados y siete negativos conservados. Oscuro y orden inverso
mantienen Y=-8388607/2^53;128operaciones por caso/cero error de reducción
frente a terminales representados. La cota/relativo final sigue1e-6 para
ESTOScasos, no teorema para todas las escenas. Referencias originales/ABI
intactas,32frozenY0/FAIL intacto y modelo racional previo no sustituido.

Control sintético noexact: (1+2^-24)+(2^-48+2^-72) pierde
2^-48+2^-72=16777217/2^72. Error REAL y cota locales iguales, sin descartarlo
ni afirmar que dos limbs garantizan suma exacta. Inputs normales mínimos
0x00800001 y0x80800000 producen intermedio subnormal y se RECHAZAN.
NaN/Inf/overflow/subnormal/bool/words/gauge/coverage/selección/SHA rechazados.
Exacto oscuro0 sigue relativo indefinido/FAIL; sin floor ni0/0PASS.

Primera batería previa al refuerzo de selección PASSrc0/0,477789s;
raw completo conservado. Tras reforzar entradas no hashables/bool en API,
un wrapper de validación terminó rc1 porque importaba helper fuera del
sys.path de tests. Diagnóstico íntegro conservado como fallo del WRAPPER,
NO fallo de tests/nativo/driver. Reparación del validador: decodificar
palabras directamente con struct/stdlb, sin importar productor. Run final
anterior completo y validación retenidos; sin ampliar umbrales/budgets.

Raw JSON de observaciones se conserva con zlib+base64 y SHA256 de bytes
UTF8; descodificar ANTES de leer enteros/racionales, evitando resserialización
binaria64 que pudiera corromper enteros grandes. Los tiempos son CPU local
de tests/oráculo/verificación, no eficiencia GPU/coste completo.

SinGPU/Blender/reserva/cancelación/peerwriter. GPUq10:49UTC holderausente,
directorio tickets vacío leído SOLOmetadatos: NOtelemetría/preflight/admisión.
Boards/checkpoint SINstage; solo cuatro propios revisados al commit local.
Siguiente: primitivas productor terminal con operaciones/cotas y costes
desde MISMA escena antes de nativo; no llevar campos CPU alGPU como si
ya fueran inferencia completa ni cambiar referencia, fixtures o deadlines.
