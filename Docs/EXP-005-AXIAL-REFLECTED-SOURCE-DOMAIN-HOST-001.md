# EXP005 — reflexión ideal ligada al dominio de fuente fija

ID AXIAL-REFLECTED-SOURCE-DOMAIN-HOST-001; base f17e61ab42f134048dd112b2afe0aa1bd9dec525.
Acuse ZERO-SOURCE-DOMAIN-HOST-001/reporte SHA
c5acabf3e19284bf44a33bb69b80b6945768ecd607aa3fd97dcac4eaacdee0dc.

## Modelo y contrato

Opt-in axial-ideal-mirror-zero-fixed-source-domain-HOST-v1.
API pública: casos retenidos únicos/acotados y modelo explícito;
no caller resultados, escenas, perfiles, certificados, cupos ni allocations.
278 pins heredados; 282 incluyendo cuatro archivos propios.

Perfil EXISTENTE: un mirror M ideal con coeficiente -exp(i*phase) y
detector D, ambos declarados en ORIGINAL. Fase ORIGINAL binary64 fija
exactamente +0 o -0: coeficiente -1+0i, error cero, sin trigonometría.
No convertir fases pequeñas/subnormales no cero a cero, ni FTZ.
No nuevo Fresnel, incidencia/polarización, material físico certificado,
incertidumbre de fase o implementación del buffer material nativo.

El perfil se liga a INPUT, snapshot, fuente/gauges, eventos/departure y
al dominio axial de selector uniforme ya probado: M primero, D después,
dos segmentos positivos, mismas primitivas interiores YZ y skip sólo
tras root aceptado. No repetir selector ni aceptar owner anterior del caller.

## Prueba restringida

SOURCE ORIGINAL fija + unidad constante en el dominio cero -> producto
bare acotado por 1/2^55 L1/fuente. La negación simultánea de ambas
componentes es isometría L1 respecto a ORIGINAL también negada:
|(-Fhost)-(-Foriginal)|_1=|Fhost-Foriginal|_1.

Se comprueban 24 identidades XOR retenidas (2 palabras, 4 esquinas,
3 fuentes). Incluyen +0 -> -0 final exactamente: no ocultar su signo.
No se llama a productores, negate_product_words anterior, encoder ni RN;
no nuevas salidas de escena. Bound hi-lo NO cero y charges permanecen
idénticos; el enlace uniforme procede del dominio constancia previo,
NO de interpolación/muestreo de esquinas.

Flag NUEVO restricted_ideal_reflected_fixed_source_error_to_ORIGINAL_proved
sólo negative/s, positive/s, two_sources/s. La falta de asignación
explícita de presupuesto permanece STOP y el gate previo no se promueve.
No comparar cupo de fase en radianes con L1 ni inventar default allocation.
14 STOP retenidos, dos dominios no cero sin refinamiento, other/two_sources
sin suma parcial. Sourceuniform GENERAL, amplitudegate, reducción,
detector, fullpipeline, native/signzero graph, GPU/RT/auth/general3D/óptica
física continúan falsos. No se cambia ningún contrato/runner congelado.

## Verificación y seguridad

Cuatro tests stdlib nuevos: auditoría, perfiles sintéticos ±0,
identidad de palabras y 41 controles fail-closed. Oráculo independiente
stdlib sin imports producción: 282 pins, cadena de dominio/input/eventos,
24 identidades, isometría ORIGINAL, cargos y STOPallocation intactos.
Captura íntegra con SHA/timing en reporte. CPU un hilo/hijo timeout60s.

Incidente de orientación: una búsqueda de pin escogió primero la
documentación MIRROR-ZERO y se intentó parsear como JSON. Se conserva el
JSONDecodeError como error de lectura, no numérico; después se leyó por
ruta exacta el recibo correcto. No replay de cómputo ni caprelax.

JEV bloqueado por seguridad: LOCAL sin aval/retry/elusión.
Sin GPU/Blender/SDK/DrJit/Kaggle/push/merge. Sólo cinco propios revisados
en commit local; cuatro boards/checkpoint SINstage. Ventana 0337 cerrada,
deadline intacto; futuras GPU sólo reserva Claude/telemetría/guardfailclosed/
deadline nuevo y límites originales completos.

## Siguiente

Cerrar grupo y reducción/potencia uniforme sin suma parcial; cubrir
dominios no cero y restantes contratos físicos/nativos separadamente.
Claude: ACK ID/reporte SHA y sólo certificados/backendguard YA existentes
matching INPUT/escena/ABI/fuentes/gauges e igualtrabajo/salidas/costes
completos. Sin RT duplicado/relleno, claims de velocidad/eficiencia/ganador,
o U/GEMM compilada sustituyendo silenciosamente inferencia desde escena.
