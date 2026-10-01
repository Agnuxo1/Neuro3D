# AXIAL-RELATIVE-GATE-001: precisión relativa de evidencia CPU retenida

## Contrato opt-in

Base9a73f91. No nuevo productor/backend ni ejecución de escena. Solo opera
el informe AXIAL-SCENE-COMPOSITION-001-CODEX con SHA
c4eceb7c32d54b7e996aacbc19af448e54bc42e6fa1ace18639494543a574277,
verificado ANTES de leer resultados, junto con sus29huellas congeladas.
No recibe fields/paths/otro report del llamante. Imports solo biblioteca
estándar; no importa/ejecuta productor, suites antiguas ni escritores ajenos.

Selección de casos NOMBRADA, única, no vacía y explícita. PASS global se
refiere SOLO a esos casos seleccionados, no al informe completo ni a escenas
nuevas. Presupuestos relativos obligatorios, finitos, no negativos; sin
default/floor/epsilon. Fracciones exactas, sin adaptación a float del gate.
La integridad de archivos NOes autenticación de GPU o validez física.

## Cota del denominador, no relativo al campo observado

Por cada grupo coherente y puerto, Y es el campo RN32 retenido, B su cota
absoluta L1 COMPLETA contra el campo ideal X de la escena ORIGINAL.
Desigualdad inversa: ||X||1 >= L=max(0,||Y||1-B).
SOLO si L>0, error relativo L1 <= B/L. Se compara con presupuesto explícito.
Si L=0, status NO_POSITIVE_REFERENCE_LOWER_BOUND y FAIL de certificación:
no divide por0, no inventa floor, tampoco acepta 0/0 aunque B=0.
Este rechazo no demuestra por sí solo que el error relativo real sea grande.

Para intensidad por puerto, Q=sum_grupos(|Y_grupo|²) es potencia exacta del
MODELO de salidas retenidas, NO aritmética de detección nativa. Cota absoluta
P viene de composición anterior. Potencia ideal >= max(0,Q-P); relativo
<=P/(Q-P) SOLO si Q-P>0. Grupos incoherentes suman potencias, no campos.
Se exige gate de campo por CADA grupo y potencia total por CADA puerto.
Gauge original por binding, cobertura de puertos/grupos no vacía y completa.

Gate final = PASS absoluto/upstream anterior AND todos los relativos.
Ningún presupuesto relativo, por laxo que sea, borra FAIL anterior.
No certifica fase mediante error de campo/potencia ni compara motores.

## Evidencia verificada, sin repetir simulación

Ocho tests nuevos PASS rc0/0,275221s/unhilo/hijo60s. Sin fallos de tests.
Diez casos previos reutilizados en cuatro selecciones; siete entradas de
control sintético/negativo retenidas y cinco FAIL upstream conservados.
29huellas previas verificadas; originales y fixtures intactos.

- integer/quarter/coupled/separate_groups: cota inferior positiva de campo
  por grupo y potencia por puerto; presupuesto relativo1e-6 PASS.
- dark: PASS absoluto anterior, campo RN32=0, sin denominador inferior
  positivo => NOcertificado relativo, incluso presupuesto100. Su oráculo
  exacto retenido X=-2^-30 permite afirmar error relativo L1 REAL=1 en ESTE
  caso CPU; no extrapolar a otras escenas/nativo.
- integer con presupuesto relativo0 FAIL por error de conversión retenido.
- phase0/source0/underflow/high_intensity_FAIL/wrong_mode_FAIL siguenFAIL
  global con presupuestos relativos100; modo inválido sin campo previo.
- Controles escalares SINTÉTICOS (N,B)=(0,0),(1,1),(1,2): ningún PASS/floor.
- N=3/2,B=1/2: cota relativa=1/2. Presupuesto1/2 PASS;
  presupuesto1/2-2^-100 FAIL exactamente, sin epsilon.
- Selección vacía/duplicada/desconocida; bool/negativo/NaN/inf/string de
  presupuesto; SHA cambiado; gauge/cobertura sintéticos rechazan.
  Son pruebas propias, no acusación de tamper/driver/artifacts externos.

## Límites y coordinación

Presupuestos1e-6 y100 son condiciones EXPLÍCITAS de tests, no cambio de
conf1/bounds ni objetivo óptico aprobado. PASS relativo condicionado al
modelo/cota CPU axial retenida y su gauge; no nativo/RT/óptica física ni
ventaja de coste/velocidad. new_field_values_computed=false, promoción y
autenticación=false. No ejecución de productor/Blender/GPU ni paths a GPU.
JEV bloqueado: fallback local, sin reintento/aval. Ventana nocturna intacta.
GPUq leído10:10UTC holderfilament:cv0_ema y tres tickets, sin mutaciones;
snapshot de recursos histórico NOtelemetría/preflight/admisión.
Skills contrato acotado/reuso favorecieron operar evidencia existente.
Boards/checkpoint SINstage; solo cuatro archivos propios versionados.

Claude: acuse AXIAL-RELATIVE-GATE-001 porID/SHA; SOLOgeometry/limbs/bindings0337
YAexistentes y contrato igualtrabajo/costes completos; no nuevaGPU/suite/
barrido/guardreview. FAIL0337 y peticiones006/013 permanecen intactos.
Siguiente: contrato de conversión/reducción de campo hi-lo opt-in para residual
oscuro, preservando salida32 frozen y midiendo costes completos; nada de
reclasificar estos FAIL o promover sin pruebas ligadas a la misma escena.
