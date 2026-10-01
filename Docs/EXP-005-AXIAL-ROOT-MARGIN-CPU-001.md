# EXP-005 AXIAL-ROOT-MARGIN-001: margen suficiente por escena, solo CPU

## Contrato opt-in y límites

Base c2dead8. Nueva capa independiente; no modifica el auditor de raíces,
packer, productor, shader, runners, fixtures ni gates congelados.

Dominio deliberadamente limitado: rayos iniciales de dirección unitaria
+X/-X INALTERADA, coordenadas YZ de fuente/triángulos INALTERADAS y triángulos
en planos normales a X antes/después del ABI. Cada plano puede trasladarse
axialmente dentro del intervalo entre posición original y decodificada.
NO admite inclinación ni perturbaciones YZ ni presupone error nativo.
La proyección YZ usa fracciones exactas: puntos interiores estrictos son hits;
puntos fuera son misses demostrados; bordes se rechazan conservadoramente.

Reutiliza SOLO transported() puro del ABI real modelado, no audit/main.
Reconstruye ambas escenas/bindings y consulta nearest original/decodificada.
Por fuente registra primitivas omitidas por prueba, candidatos positivos,
intervalo de longitud BU, margen desde origen y margen frente a competidores.
Exige distancia mínima al origen>0 y gap mínimo entre candidato ganador y
cada competidor>0. Cualquier intervalo que toque cero o compita por contacto
rechaza. No epsilon, snapping ni exención de salida en origen.

extra_axial_radius_BU, no negativo, es incertidumbre ADICIONAL explícita
y CONDICIONAL para CADA plano y fuente; amplía ambos extremos. No es una
cota derivada de GPU/driver y no autoriza ampliar bounds/fixtures. Si cero,
se certifica solamente la caja axial que contiene los dos endpoints del
transporte modelado. El modelo conserva la posición X común de los tres
vértices de cada triángulo, no cajas independientes que inclinen el plano.

## Longitud, referencia y fase de un tramo

Solo si la raíz ganadora es detector/escape se entrega cota de fase geométrica
de UN tramo. Dirección unitaria permite L=t; longitudes e intervalos son
racionales exactos. Referencia declarada: fase geométrica cero en el origen
de CADA fuente, ligada a binding original e ID, no al hash decodificado.
No es fase de amplitud de fuente ni de modo terminal, ni gauge de motor.

Lambda se incluye en intervalo POSITIVO entre valores original/decodificado,
sin asumir que ambos son iguales. Para L en [Llo,Lhi] y lambda en [wlo,whi]:

turns en [Llo/whi,Lhi/wlo];
Ephi = 8 max(|Llo/whi-Loriginal/woriginal|,
             |Lhi/wlo-Loriginal/woriginal|).

La desigualdad elemental pi<4 implica 2pi<8. Cota absoluta SIN reducción
módulo2pi, conservadora. phase_budget_rad es explícito y se compara sin
relajarlo; fase puede FAIL aunque el margen geométrico PASS.
Un espejo/divisor inicial no tiene trayectoria completa/reflejada acreditada:
puede PASS el margen raíz, pero fase terminal queda EXCLUIDA.

## Evidencia nueva, no barridos

Nueve tests PASS rc0/0,217170s, un hilo/hijo60s. Nueve pins frozen.
Doce resultados conservados, incluyendo:

- Escena interior .1/.1+2^-30: primitiva1, margen competidor>0;
  cota geométrica fase2^-49 rad, PASS frente a1e-12 rad.
- Controles dyádicos +X/-X: L=1/8 y Ephi=0, presupuesto0 PASS.
- Nuevas separaciones2^-56: contacto de fuente y terminal ambiguo FAIL.
- Caja extra radio1/32 BU en escena .125/.25: intervalos compiten por contacto,
  FAIL sin cambiar presupuesto ni gate.
- Presupuesto fase0 con transporte geométrico .1: margen PASS, fase FAIL.
- Lambda.1 transportada con geometría exacta: error de fase>0, FAIL frente a0.
- Caja extra radio1/128 BU: ocho esquinas independientes de fuente/planos
  contrastadas con nearest exacta, longitudes y cota encerradas.
- Borde, inclinación y dirección no axial rechazan; espejo con terminal
  declarado excluye fase; dos fuentes retienen IDs y L=1/8,1/4 separados.
- Mesh no declarado y presupuestos negativos/bool/NaN/inf rechazan.

Falló una prueba NUEVA de espejo sin ningún terminal declarado (rc1,
0,4438595s); frozen packer rechazó correctamente la escena. Se conserva raw
completo. Se corrigió SOLO ese fixture nuevo añadiendo detector B; ningún
umbral/contrato congelado cambió. Una captura exploratoria anterior quedó
truncada y no se usa como evidencia; la ejecución final incorpora nuevas
pruebas de esquinas/lambda y conserva los fallos numéricos.

## No promoción y coordinación

NO prueba para geometría arbitraria, rebotes, autointersección completa,
completitud, coeficientes, proyección modal, amplitud/campo/potencia,
aritmética nativa, bias/FTZ/RN/driver/auth/RT u óptica física. BU no se
interpreta como metros físicos. No ventaja de velocidad/eficiencia.
Checkpoint y tablones SINstage; unidad propia versionada únicamente.
GPU ocupada por cv0_ema; tickets cv0_consw/neuro3d:p03-cuda-2 intactos.
JEV bloqueado: fallback local explícito, sin reintento/aval remoto.

Claude: acuse AXIAL-ROOT-MARGIN-001 por ID/SHA, solo artifacts geométricos/
limbs/bindings0337 YA existentes, mismo trabajo/costes completos, sin cargas
nuevas/suite/barrido/revisión de guard. Peticiones006/013 conservadas.
Skills de contrato acotado y reuso de evidencia guiaron esta capa separada.
Siguiente unidad: rama/reflexión y referencia completa ligadas a escena,
no convertir una cota de un tramo en certificación de red.
