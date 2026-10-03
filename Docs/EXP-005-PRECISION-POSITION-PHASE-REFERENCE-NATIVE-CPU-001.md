# PRECISION-POSITION-PHASE-REFERENCE-NATIVE-CPU-001

P1 Codex, capacity_audit/EXP005. Base 8ad6f7b07682e46f4acaf8aa509a8489ec4ba8a0.
Fallback LOCAL explícito: JEV bloqueado por seguridad; sin consulta ni aval remoto.
CPU sintética declarada; NO fase total física, Bpyfloat32, GPU ALU, RT u óptica física.

## Contrato opt-in

Modelo precision-position-phase-reference-native-CPU-v1. API audit(model,request,raw_frame).
Selector cerrado: ID, SHA del recibo y registro padre, parámetros, contexto SOURCE,
ORIGINAL, overlay, representación e intención. Recibo padre OVERLAY-HOST-001:
SHA 7c52f61504e126628ff54d76686ba6585abe9d0cf1a5ff8bf99a87d6fe686e14, 196856 bytes.
No repetir productores, raíces ni suites ancestrales: consumir capturas verificadas.

Conservar 336 registros padre; solo 39 admitidos. Los 297 STOP no se rescatan.
Comparar TODOS los 16 bytes geométricos antes de decode, conversión o ALU.
Salida nativa: dos palabras binary64 separadas, nunca suma escalar de fase.
Contexto CPU_SYNTHETIC_ONLY_NOT_SEALED_SCENE y referencia declarada destino3-extremo1,
frame DECLARED_COMMON_TURNS_FRAME_NOT_CALIBRATED. No injertar contexto oblique S0/S1.

Cuatro términos separados, en orden: SOURCE destino, SOURCE referencia,
MATERIAL destino, MATERIAL referencia. Radios no se cancelan.
Cada midpoint: dos conversiones RN64 con residual HOST exacto, usando SOLO convert/internal
del encoder congelado. 8 casts por contraste; 2048 bits solo para racionales internos
derivados, no aumenta entradas geométricas/longitud de onda/componentes de 128 bits.
Rechazar midpoint subnormal antes de HIGH y residual subnormal después de HIGH,
preservando casts parciales. Palabras y nodos: finitos normales o ceros, incluidos -0.
Referencia: invertir bit de signo de ambas palabras (4 inversiones exactas, sin confundir
con sumas RN). Cuatro plus congelados de 26 nodos: 104 sumas/restas RN64 por contraste.
Reutilizar algoritmo puro NO reutiliza semántica de la escena oblique.

Cota fija en radianes:
8*(radio_geom + error_encoding_geom + error_normalize_geom + suma4radios_fase
 + suma4errores_encoding_nuevo + suma4errores_suma_nativa) <= 1e-4.
Todos los errores medidos con HOST exacto; no descuento por cancelación.
El factor 8 es la envolvente ancestral conservadora, no una modificación de cap.
Contrastar además contra extremos del intervalo heredado; errores directos dominados
por la cota conservadora. No aumentar bounds ni cambiar umbrales para PASS.

## Evidencia y verificación

Suite propia: PASS, 482 principales = 39 CPU + 443 STOP; 297 STOP padre,
128 corrupciones de bit, 5 formatos inválidos y 13 controles selector/modelo.
4056 nodos RN64, 312 conversiones, 156 inversiones de signo principales.
Decodificaciones: 78 palabras geométricas y 312 palabras de términos principales,
2/8 adicionales en API duplicada, separadas de casts RN y costes aún no medidos.
API pública duplicada: 104 nodos, 8 casts, 4 inversiones adicionales, contados aparte.
Capturas íntegras acotadas a 2097152 bytes y SHA en el recibo.
Primer PASS 1938366 bytes/SHA cc698862aadb933e9d8a633ca249c2435dc355fbf9f7cc2ac1f446aafbd0c114,
retenido antes de añadir SOLO contador explícito de decodes de términos, sin
cambiar algoritmo, cap ni veredictos; captura final y comparación en recibo.
Hijo único: afinidad1, bibliotecas1hilo, timeout60s; 5.3775428000008105s observado,
no benchmark end-to-end ni comparación de eficiencia.

Oráculo independiente ejecutable conservado en recibo: sin importar implementación,
IEEE754 decode por enteros y redondeo ties-to-even racional para cada cast y nodo.
Reconstruye operandos/topología de los 4 grafos, comprueba EFT observado de cada two_sum,
signos de cero, inversiones XOR, errores etapa a etapa, cota y vínculo padre/contexto.
Preserva capturas/fallos. La identidad EFT observada no se convierte en prueba universal.
El recibo registra resultado del oráculo y pins; no se infiere PASS del nombre del archivo.

Autenticación de escena/incertidumbre/material/longitud de onda/referencia óptica,
completitud física, fase total y GPU siguen False. Field/amplitude/power=None,
promotion=STOP; upstream/I/O/hash/setup/ingress/fence/readback/memoria/energía y costes
completos UNMEASURED_NOT_ZERO. No ganador, rapidez, eficiencia ni red RT inferidos.

## Coordinación y límites

Sharedboards/checkpoint locales SINstage; versionar solo own4 revisados.
Sin GPU/Blender, sin cambios de ventana nocturna/deadline, sin CIM/telemetría retry,
sin SDK/DrJit, publicación/push/merge/Kaggle/procesos ajenos.
Fixtures conf1/v0/v4/0119/0315/nearestV2, runners/shaders/contratos congelados intactos.
RT-AUD-001 16M vs 1M, salidas distintas/cruce extrapolado NO equivalencia ni red RT.

Pedir a Claude ACK por ID+SHA del recibo y SOLO artefactos YA existentes del mismo
ORIGINAL/contexto/referencia-gauge/calibración, incertidumbre/autenticación/completitud,
backend-error total, guard fail-closed e ingress-fence-readback, igual trabajo/salidas
y costes completos por ID/path/SHA/bytes. No inventar ACK ni repetir cargas de relleno.
