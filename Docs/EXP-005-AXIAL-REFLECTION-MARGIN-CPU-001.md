# EXP-005 AXIAL-REFLECTION-MARGIN-001: un espejo y referencia de camino CPU

## Contrato nuevo y suficiente

Base5ff5161, opt-in separado. Rayos unitarios ±X, YZ de fuentes/triángulos
inalterados y planos normales a X. Cada OBJETO tiene una sola variable X,
compartida por TODOS sus triángulos, antes/después del ABI y en la caja
condicional. Se rechaza agrupar planos diferentes bajo el mismo propietario.
Cajas entre posiciones original/decodificada; radio adicional no negativo
explícito, supuesto CONDICIONAL, no cota nativa ni ampliación de bounds.

El camino se reconstruye desde cada fuente, no se acepta ledger suministrado:
nearest exacta, punto de impacto derivado, reflexión por normal racional,
segunda nearest y terminación. Exige exactamente espejo->detector/escape,
mismos IDs/primitivas en ambas escenas. No splitters ni más rebotes.
Proyección YZ interior estricta/miss demostrado; bordes rechazan.

## Salida propia, autointersección y separación

En la salida del espejo, el origen X es la MISMA variable del objeto espejo.
Por tanto el contacto consigo mismo es idénticamente cero, no diferencia
de dos errores independientes. Se registra qué primitiva se omite por esta
identidad. No recibe previous_pid externo ni epsilon/snap/bias positivo.
El helper nearest congelado verifica además los dos endpoints con su
prueba exacta de salida por primitiva/coplananidad.

Otro propietario NO obtiene esa exención. Un contacto desde la FUENTE
tampoco tiene salida establecida y se rechaza. Distancias estrictamente
positivas y gaps entre planos de competidores separan cada evento.
Al comparar competidores se cancela el origen compartido: el margen es
entre sus planos, no entre cajas independientes del mismo origen.

## Longitud y fase de camino, referencia explícita

Para signo s=±1, espejo M, fuente S y terminal D:

L = s*(2M-S-D).

Intervalo racional exacto preserva la misma variable M en ambos segmentos;
la perturbación del espejo se carga DOS veces, no solo una.
Referencia: fase geométrica cero en el origen de cada fuente declarada,
ligada a binding ORIGINAL e ID. No es gauge de motor ni proyección modal.

Lambda en intervalo positivo entre endpoints original/decodificado.
Con vueltas originales L0/w0 y caja [Llo/wmax,Lhi/wmin], pi<4 permite:

Egeom = 8 max(|Llo/wmax-L0/w0|, |Lhi/wmin-L0/w0|);
Etotal = Egeom + |phiMirrorDecoded-phiMirrorOriginal|.

Mirror.phase_rad se transporta y se carga separadamente, no se omite.
Cota absoluta sin reducción módulo2pi; presupuesto explícito y sin relajar.
Amplitud de fuente, fase modal y coeficientes/campos/potencia NO certificados.

## Evidencia nueva

Ocho pruebas PASS, rc0/6,4397302s, un hilo/hijo60s, doce pins congelados.
Doce casos retenidos, sin ejecutar suite anterior/productor/barridos005/006.

- Controles ±X: primitiva espejo1 y terminal3, L=5/8 BU, faseerror0;
  salida propia omitida por identidad exacta y presupuesto0 PASS.
- Espejo x=.1 y fase óptica.1: Egeom=2^-48 rad, carga espejo=2^-55 rad;
  frente1e-12 PASS y frente0 FAIL aun con topología PASS.
- Radio1/128 BU: ocho esquinas independientes de fuente/espejo/terminal
  contrastadas con nearest/reflexión racional; L en[19/32,21/32] BU,
  Egeom<=2 rad. Radio1/16 llega a contacto de fuente y FAIL.
- Contacto fuente-terminal original rechaza; otra superficie con cero
  NO obtiene exención de espejo en prueba acotada del selector.
- Separación fuente-espejo2^-56 colapsa tras ABI y sigue FAIL.
- Dos planos diferentes del mismo objeto rechazan; splitter excluido.
- Dos fuentes mantienen IDs/gauges y L=5/8,11/16 separados; no suma coherente.
- Lambda.1 transportada carga error de fase, FAIL frente presupuesto0.

No hubo fallos de pruebas en esta unidad; los FAIL numéricos/exclusiones
son resultados esperados CONSERVADOS, no gates convertidos a PASS.

## Alcance y coordinación

Completo SOLO para un camino axial de un espejo bajo el contrato condicional,
no completitud de una escena arbitraria/red óptica. No tilt/YZ/dirección,
bounces múltiples, splitters ni transporte modal/amplitud/campos/potencia.
Sin GPU/Blender/RN/FTZ/bias/driver/auth/RT/óptica física ni ventaja de motor.
BU no se convierte a metros. Runners/shaders/fixtures/gates/FAIL0337 intactos.

GPU ocupada por cv0_ema; tickets cv0_consw/neuro3d:p03-cuda-2 intactos.
Sin reservas/cancelación/peerwriter. JEV bloqueado: fallback local sinaval,
sin reintento. Skills de contrato limitado y evidencia reusable guiaron la
implementación. Boards/checkpoint locales SINstage; solo propios versionados.

Claude: acuse AXIAL-REFLECTION-MARGIN-001 por ID/SHA; SOLOlimbs/geometry/
bindings0337 YA existentes y contrato igualtrabajo/costes completos.
No nuevaGPU/suite/barrido/guardreview; pendientes006/013 conservados.
Siguiente requisito: composición explícita de amplitud/fase/campo en el
MISMO contrato de escena, sin promover esta prueba axial a nativa.
