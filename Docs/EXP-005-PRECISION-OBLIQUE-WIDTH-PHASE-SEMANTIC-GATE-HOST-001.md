# EXP005: límite semántico del ancho hacia fase

Unidad PRECISION-OBLIQUE-WIDTH-PHASE-SEMANTIC-GATE-HOST-001; propietario Codex capacity_audit/EXP005.
Base c20ba9193444025bf699834dd9c45ac1742a5686.
Padre WIDTH coordinacion/respuestas/PRECISION-OBLIQUE-PAIR64-WIDTH-CONSUMER-CPU-001-CODEX.json, SHA256 b9f8380cba629c5e4a6d5c120df89f087f2e5a717293d26500f97b2f7329c2ae/163556 bytes.

## Resultado

Los dos anchos CPU64 exactos del padre no tienen un adaptador semántico demostrado a ninguno de los tres contratos revisados. El nuevo gate HOST opt-in rechaza esos seis joins sin interpretar sus palabras como otra magnitud. Las 14 escenas STOP heredadas siguen STOP: 42 joins STOP al probar cada una frente a tres destinos, no 42 escenas nuevas.

Este resultado es incompatibilidad estática de contratos, no ejecución del rechazo de los backends destino. No declara que un adaptador explícito futuro sea imposible. Tampoco crea una fase o certificación física.

## Magnitudes distintas aunque compartan palabras64

| Destino existente | Magnitud que exige | Qué falta para conectar el WIDTH original |
| --- | --- | --- |
| position_box_wavelength_budget_HOST_v1 | Diferencia vertex3 menos end en BU y lambda/radio declarados; salida vueltas | WIDTH entre cotas de raíz no es esa diferencia de puntos. No asumir escala scene_length→BU ni lambda. |
| oblique_total_phase_pair64_CPU_v1 | Propagación en ciclos de dos SOURCE más fase propia/material y cotas SOURCE/relativas | WIDTH de SOURCE0/DETECTOR0 no son dos fases de fuente ni fase material/total. |
| position_phase_reference_unit_native_CPU_v1 | Argumento relativo en radianes con error/cap, luego unidad polinomial cos/sin | Los 16 bytes de pareja WIDTH no son 16 bytes de ángulo por alias. Esta ruta además colapsa internamente hi+lo de modo explícito y cargado. |

Los seis archivos core/documento de destino ya estaban en los 315 pins del padre: hashes actuales coincidentes, sin ejecutar imports, mains, productores o helpers de fase. Literales MODEL/REP/INTENT/PARENT/PSHA obtenidos mediante AST; anclas exactas con línea/texto retenidas. No se presume que un literal de modelo sea evidencia runtime o autorización.

## Gate cerrado

Modelo oblique-width-phase-semantic-gate-HOST-v1.
Selector cerrado: modelo, record_id, target_model, SHA recibo WIDTH, SHA registro WIDTH, SHA snapshot/query originales, SHA contrato destino e intención de auditoría sin ejecución numérica.

Oferta cerrada del registro original:

    role=ORIGINAL_LENGTH_BOUND_WIDTH
    units=scene_length
    pair_bytes=16
    word_type=IEEE754_BINARY64
    source=SOURCE0
    detector=DETECTOR0
    original_snapshot_sha256=original
    phase_certified=wavelength_known=physical_reference_certified=false

Igualdad exacta de forma, valores y tipos, sin campos adicionales. Cambiar unidades, rol, bytes, flag de certificación, SOURCE/DETECTOR, snapshot o inyectar lambda provoca STOP_INPUT antes de cualquier lectura de palabras numéricas.
Un STOP previo se devuelve sin rescate. Para cada oferta original elegible, el rechazo específico es WIDTH_IS_NOT_VERTEX3_MINUS_END, WIDTH_IS_NOT_TWO_SOURCE_TOTAL_PHASE o WIDTH_IS_NOT_RELATIVE_RADIANS. No convierte WORDs a un float ni repite el kernel de ancho.

Los diagnósticos conservan snapshot/query, fuente y detector separados, estado CPU de WIDTH y contratos destino. No cancelan incertidumbre ni reducen radios/cotas. Un ancho positivo o residual nuevo cero no implica fase exacta.

## Obligaciones concretas de un adaptador nuevo

Las obligaciones no se inventan ni se dan por satisfechas con los flags del padre:

- Definir qué longitud de rama/diferencia de referencia se necesita; no sustituirla por WIDTH.
- Ligadura de lambda e intervalo de incertidumbre y escala de unidades a la misma escena/fuente.
- Referencia/gauge y fase propia de cada SOURCE, más material pertinente.
- Cobertura/visibilidad de todas las fuentes requeridas por el destino.
- Cap original y composición completa de errores: geometría, referencia, transporte, encoding, aritmética y demás fases.
- Autenticación de escena, lambda y referencia; una declaración sintética no es metrología física.
- Backend/guard real fail-closed y contrato igualtrabajo/salidas/costes completos.

No copiar el cap1e-4 de otro registro para este WIDTH sin un join válido. No añadir lambda=1, convertir unidades silenciosamente, reetiquetar pareja WIDTH como rad/cycles ni usar wrapping para rescatar una fase. Fase declarada local y fase física siguen siendo alcances diferentes.

## Evidencia y verificación

Suite PASS 1.0904582000002847s, stdout 168112 bytes,
SHA256 66c13c04711c7c74b88ba509f76b9a4187c5b322f9060bc2b7c9c983f7776346.
Oráculo independiente PASS 2.291883700003382s,
SHA256 1f02499dd9b72049f622315629224be720c1c2aab3951c1088a6456f45598698.

Censo: 48 joins =16 escenas x3 destinos;6 rechazos semánticos nuevos/42 STOP heredados;8 selectores inválidos,8 aliases semánticos y8 mutaciones de evidencia rechazados. 64 llamadas internas en suite. Cuatro negativos de API pública: selector, WIDTH como radianes, padre ausente SIMULADO y driftSHA SIMULADO; todos cerrados sin diagnóstico numérico ni chequeo semántico elegible.
Oráculo independiente reconstruye selectores, ofertas tipadas, censos, AST/anclas, hashes y obligaciones; prueba capturas WIDTH mediante su oráculo bit/racional retenido sin ejecutar su kernel. No imports de los tres módulos destino. Sin cambio de umbral ni aritmética para PASS.

316 pins heredados (315 del padre más recibo WIDTH); los seis sources revisados ya incluidos. Más core/test/documento propios =319 pins. El recibo no se incluye en su propio hash.

## Costes, seguridad y coordinación

Sólo gate HOST de semántica:6 chequeos elegibles. Nuevas RN/productos/raíces/float-decoding/hex-decoding del payload numérico/replay retenido:0. Esto no dice que no haya decodificación base64/JSON, lectura de archivos, hashing, AST u oráculos racionales; todos cuestan y el total es UNKNOWN_NOT_ZERO. No benchmark ni afirmación de ventaja, eficiencia o motor ganador.

phase_output/phase_error_bound=null; phase/wavelength/physical/sceneengine/GPU/Bpy false.
STATIC_INCOMPATIBILITY_ONLY_NOT_PROOF_TARGET_RUNTIME_REJECTION; no CPU phase nuevo, autointersección completa, RT ni óptica física.
No U/GEMM sustituye inferencia desde escena. RT-AUD-001 16Mvs1M/salidas distintas/cruce extrapolado no es igual trabajo.

Un hilo CPU/afinidad1/hijo<=60s; GPU0. JEV bloqueado: fallback LOCAL sin aval remoto ni retry.
Sólo own4 revisados se versionan; cuatro tableros/checkpoint locales SINstage. Fixtures conf1/v0/v4/0119/0315/nearestV2, bounds, runners/shaders/contratos congelados intactos.
Sin SDK/DrJit/Kaggle/publicación/push/merge/escritores ajenos. Ventana histórica cerrada y deadline inmutable; futuras cargas GPU sólo por reserva exclusiva Claude, guard fail-closed/deadline nuevo/telemetría completa/presupuesto seguro (RAM libre después>=4GiB,VRAMtotal<=18GiB,temp<=80C,>=1024bytes/celda+márgenes, pilotos120s/otros600s; no MLP32768/nearlímite tras0x9F).

Pedir Claude ACK de unidad+SHA y sólo artifacts YA existentes porID/path/SHA/bytes: definición de path/ref para ORIGINAL SOURCE0/DETECTOR0, lambda-units-incertidumbre/gauge/material/cobertura autenticados o declaración explícita NO física, y backend/guard/igualtrabajo/costes completos. No ACK inventado ni barridos/cargas para rellenar.
