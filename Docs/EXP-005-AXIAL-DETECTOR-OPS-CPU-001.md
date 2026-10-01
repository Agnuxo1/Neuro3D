# AXIAL-DETECTOR-OPS-001: lectura de intensidad RN32 CPU modelada

Base6292da3. Opt-in `hilo-square-13op-rn32-v1`, SOLO simulador CPU,
NO GPU/ALU/detector físico. Lee informe AXIAL-QUARTER-SOURCE-OPS-001 SHA
c3a54d51c47f901d4c0520216499c027a24c9579742e9b28a57073c72053d2a0
y sus45huellas antes de cálculo. No acepta escena/campos/report sustituto;
no repetir productor/reducción/certificador/Taylor/suites/barridos.

Para componente expansion h+l, cada nodo redondea RN32 ties-even:
s=RN(h*h); t=RN(h*l); u=RN(l*l); v=RN(t+t);
w=RN(s+v); z=RN(w+u). Seis nodos/componente, luego
Qgrupo=RN(zRe+zIm):13nodos/grupo. Puerto suma Qgrupo en orden explícito
con RN32, comenzando0. Grupos incoherentes NOsumar campos. Mantener
sourceID/group/port/gauge/binding original y decodificado/cobertura completa.

delta de cada nodo=resultado-exacto(input), observado con oráculo racional.
z-(h+l)²=e_s+2e_t+e_u+e_v+e_w+e_z. Cota componente sumaabs con peso2
para error del producto cruzado; grupo suma dos cotas+errorRNgrupo;
puerto suma cotas grupos+sumabs errores acumuladorRN. Verificar identidad
exacta por caso, NO teorema hardware no comprobado ni racional gratis.

Bpotencia_original=Bpropagación_reducción_retenida+BdetectorNuevo.
Presupuesto absoluto del mismo snapshot retenido y relativo del mismo
puerto: bound/lower con lower=max(0,QdetRN32-B)>0, sinfloor/epsilon/0div0.
PASS previo requerido además de los nuevos gates; no convertir FAILprevios
enPASS ni sustituir referencia original por potencia representada diferente.
Cuadrados/potencia de referencia EXACTOS racionales son solo ORÁCULO,
NO lectura terminal nueva hasta pasar TODOS los nodosRN32.

Inputs/intermedios/output normal o0; NaN/Inf/overflow/subnormal seleccionado
rechazan SIN FTZ. RN32 bajo medio mínimo subnormal puede resultar0:
cobrar pérdida exacta y exigir relativo; cero no certifica señal nozero.
Potencia final negativa rechaza, nunca clip a0. Signo de0 no es avalnativo.

Costes13ops/grupo+una suma/grupo-puerto, oráculo CPU/packing/geometría/
productor/transferencias/memoria/energía/guard/detector físico EXCLUIDOS;
tiempos de tests NO benchmark/costes completos/comparación equivalente.
Todo native/auth/GPU/ALUexecuted=false. Runners/shaders/fixtures/bounds/
conf1/gates/fallos anteriores intactos. Un hilo/hijo60s.
Skills contrato/reuso guiaron salidas existentes, no repetición de cargas.
Claude acuseID/SHA y SOLOartifacts0337 geometry/limbs/bindings/backend/
guard YAexistentes/igualtrabajo-costes; no nuevaGPU/suite/barrido/guardreview.
006/013/0337FAIL intactos; JEVfallback local sin reintento/aval.

## Resultado verificado (CPU sintética, no hardware)

Ocho tests PASS, rc0; hijo de un hilo con límite60s terminó en
0,3651956s (tests internos0,066s). Se reutilizaron18casos retenidos:
ocho aceptados y diez FAIL anteriores conservados. Trece casos llegaron
al detector:14grupos coherentes,13puertos y196nodos RN32 modelados
(14*13+14sumas de puerto). Tres primitivas adicionales:39nodos.
No se volvió a calcular escena, productor ni reducción. Validador
independiente de palabras, nearest/ties-even, identidades, cotas, bindings,
referencias y presupuestos:0,0393437s; no importa el helper de redondeo.

En la escena oscura retenida, referencia original de campo=-2^-30 y
potencia ideal=2^-60. Lectura RN32 modelada=(2^22-1)/2^82;
error real de potencia=2^-82, relativo real=2^-22 (aprox.2,38419e-7).
Cota nueva del detector=2^-106; cota total original=33554433/2^106;
relativo certificado=11184811/23456231282005 (aprox.4,7684e-7):
PASS al presupuesto existente1e-6, SOLO para este modelo CPU.
No se cambió la referencia a la potencia representada de los limbs.

Control NUEVO, únicamente primitiva sintética de detector, no escena:
campo real normal32=2^-80, parte imaginaria0; potencia exacta=2^-160.
El cuadrado RN32 resulta0; pérdida real y cota=2^-160, pérdida relativa
100%. Denominador inferior0: relativo RECHAZADO aun con error absoluto
minúsculo. No implica FTZ, fallo de driver ni detector físico observado.
Campo normal2^-70 selecciona cuadrado subnormal2^-140 y se rechaza;
overflow, word subnormal/bool, sustitución SHA, selección inválida,
gauge/cobertura/decodificación alteradas y budgets0 también rechazan.
Controles cruzados comprobaron el peso2 sin crédito por cancelación.

Raw stdout79311bytes SHA
22c0ddef7cecc0b656b577ccae28aed64224af26d177737805880cfb95da7b7d,
conservado comprimido en informe propio. Ningún fallo inicial del hijo.
45pins previos+informe retenido=46pins congelados;49huellas actuales
(más45previas), sin incluir la huella autorreferente del informe nuevo.
GPUq sin holder/tickets fue solo lectura de metadata, NOtelemetría ni
admisión GPU. Sin carga/reserva/cancelación/peerwriter; deadline histórico
intacto. Sin aval JEV remoto. Pendiente evidencia nativa y fase general;
este resultado no demuestra velocidad, energía ni costes completos.
