# EXP005 — Unión de fase total y visibilidad declarada (HOST)

ID: PRECISION-OBLIQUE-TOTAL-PHASE-VISIBILITY-JOIN-HOST-001. Base: 2a60586d493cb120c73b9799845468ce59f1bc3c.
P0 propio Codex, capacity_audit. Nuevo modelo opt-in
`precision-oblique-total-phase-visibility-join-HOST-v1`.
No modifica runners, shaders, contratos congelados ni archivos de Claude.

## Contrato

`compare(model, request, ledger, input_bytes, output_bytes, origin)` usa evidencia
sellada interna; la API pública no permite sustituirla. Origen único
`HOST_UNATTESTED_TOTAL_PHASE_BYTES`. Petición cerrada de ocho campos con tipos
exactos: phase_case, visibility_case, phase_readback_receipt_sha256,
visibility_coverage_receipt_sha256, phase_selector, visibility_selector,
paths_sha256, intent. Los dos selectores anidados también quedan cerrados.

READBACK001 SHA0921d0ead6cfbba22145d3adc908210df22324f1f3b00b8f07ff9e444e456889;
COVERAGE001 SHAdda978eced1bf958c61325e3d29f013b713ad5524ed9f39bc474d9ab9028f45f.
Se verifica su identidad y todos los pins ancestrales. El loader reutiliza
capturas de longitud y fase; no ejecuta sus productores, geometría, sqrt,
RN64, encoding, compiladores ni shader. Conecta cada geometría nativa con una
única entrada exacta de longitud capturada, incluidos caps, lambda, reference,
direcciones, fuentes, primitivas y certificados de segmentos. Se conserva la
rama S0/mirror, S1/mirror y la vinculación del material declarado a la raíz.

Orden de admisión:

1. Modelo/origen/selectores y ambos padres no STOP.
2. Escena ORIGINAL y petición literal idénticas (contenido y SHA); certificados
   completos de trayectos S0/S1 idénticos, no solo hash de posiciones.
3. Cobertura cerrada, única, ordenada y completa del ledger SOURCE/segmento/primitiva.
4. Raw-guard de 10 entradas y 6 salidas binary64, finitud y dominio antes de
   decode; cotas de ambas SOURCE y relativa antes del match exacto de bits.

La unión publica tres filas de fase y ocho filas de cobertura verificadas SOLO
si pasan ambas partes. STOP siempre publica cero filas/contadores y ningún
SHA de salida/escena/literal/trayecto unido; conserva diagnósticos parciales
marcados como tales, que no son una admisión.

## Evidencia acotada

Cinco grupos de pruebas: 246 corridas, 11 MATCH y 235 STOP. Se conservan los
35 STOP de fase y 38 de visibilidad. Otros controles: 55 cruces entre recibos
individualmente válidos pero de contexto diferente, 66 ledgers incompletos/
duplicados/SOURCE incorrecta/orden/valor/campo extra, 11 low-word modificados
que aún caben en todas las cotas y se rechazan por bits, selectores cerrados,
origen/modelo y raw finitud/dominio/tamaños. Hay tres controles adicionales
sobre COPIAS privadas de certificados (orden SOURCE, squared_BU2, endpoint),
un control público positivo y un STOP por ausencia/corrupción simulada de
recibo. No modifica artifacts para simular fallos.

Los 55 controles de AND ingenuo pasan fase y cobertura por separado y
fallan la unión por ORIGINAL o literal distinto. Son contraejemplos de
composición sin contexto, NO bugs atribuidos a los validadores anteriores.
Las dos escenas outside_segment tienen cobertura pero no fase preparada
equivalente: NO se fabrican nuevas entradas de fase para admitirlas.
Las 11 variantes de fase comparten cuatro geometrías selladas, incluido el
hueco 2^-60 BU. Cada overlay mantiene su identidad y sus caps originales.

Suite final: rc0, 1.1923323999508284 s, stdout1105839 bytes,
SHAbaebd4a5154d9727149a250d4c9273464edb156f3cd94416bc44fd64d2075191.
La primera suite también pasó (5.4665326999966055 s); se añadió después la
cobertura explícita de certificados, sin cambios de umbral ni reparaciones
numéricas. Sus dos capturas se preservan en el recibo. Un verificador
independiente sin importar el core comprueba identidad/censos/orden de
rechazo, matrices de cruces, mutaciones, caps de readback y pins.

Fallo administrativo conservado: un signo + literal introducido al insertar
la captura PRE dejó el recibo temporalmente inválido como JSON. Se conserva
el traceback completo de la comprobación repetida (rc1); el primer intento
de metadatos falló y su wrapper no quedó capturado. Reparación de un carácter,
sin alterar código, resultados numéricos, contratos ni umbrales. Revalidación
independiente después de la reparación rc0; no se presenta como fallo GPU.

## Límites y seguridad

MATCH = `HOST_UNATTESTED_SAME_SCENE_PATH_PHASE_VISIBILITY_MATCH`.
NO autentica escena, ledger, material, dispositivo ni fence, no promueve
backend nativo ni campo físico. Amplitud/campo/potencia siguen None,
full_costs UNMEASURED_NOT_ZERO (nunca cero). Es composición de capturas
declaradas CPU/HOST, no inferencia nueva ni GPU ALU/RT/óptica física.
U/GEMM no sustituye inferencia desde escena. No comparación equivalente,
ganador, velocidad o eficiencia a partir de 16M frente a 1M.

CPU un hilo, afinidad1 y deadline duro de cada hijo60s; GPU/Blender/compiler0.
JEV LOCAL sin aval remoto: bloqueo de seguridad sin reintento.
Telemetría histórica CIM_RAM_ACCESS_DENIED/UNKNOWN retenida, sin elevación/
retry/bypass; no se reserva ni lanza GPU. Ventana histórica cerrada intacta.
No SDK/DrJit, Kaggle, publicación/push/merge ni procesos/tickets ajenos.
Fixtures conf1/v0/v4/0119/0315/nearestV2, bounds, caps, fallos y contratos
congelados intactos. Desarrollo/pruebas/cognición guiaron el alcance, las
mutaciones y el contraste independiente; no hubo agentes.

Versionar solo los cuatro archivos nuevos propios revisados; sharedboards y
checkpoint quedan locales SINstage. Pedir a Claude ACK por ID y SHA del recibo,
y SOLO artifacts YA existentes backend TOTAL, guard fail-closed, Float64/float
controls, ingress/fence/readback, material/amplitud/completitud y contrato
igual-trabajo/costes completos por ID/path/SHA/bytes. No inventar acuse ni
repetir cargas. Futuro GPU exige coordinación exclusiva Claude+gpuq,
telemetría válida, presupuesto conservador y nuevo deadline por trabajo.
