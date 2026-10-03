# PRECISION-OBLIQUE-NOMINAL-CHORD-DIFFERENCE-HOST-001

Contrato P1 opt-in propio capacity_audit/EXP005. Base d7e2dd24e35dea5bdf07e4bd2560cce2b384b50c. Fallback LOCAL; JEV bloqueado por seguridad, sin reintento ni aval remoto.

## Magnitud nueva y alcance

Se declara una referencia NUEVA, no física: R = norma de DETECTOR0 nominal menos SOURCE0 nominal, de la misma ORIGINAL y unidades scene_length. No se interpreta el ancho de las cotas como longitud de rama. El cálculo sólo se aplica a la rama recta de caja ya aceptada; no convierte una cuerda en recorrido reflejado, referencia óptica autenticada o autointersección resuelta.

El intervalo retenido de longitud de la caja L=[Llo,Lhi] conserva TODOS los radios originales. Para la nueva raíz nominal se calcula un encierro R=[Rlo,Rhi] en retícula fija 2^-96 con enteros/racionales. Resultado firmado D=[Llo-Rhi,Lhi-Rlo]. No se presupone correlación ni se cancela incertidumbre SOURCE. Como el nominal está en la caja, D debe contener cero: es una comprobación geométrica, no fallo de precisión ni certificación de fase. No se usa WIDTH como operando.

## Integridad y admisión

Padre gate SHA394e2198aab8a0893cee4eaa928d599d965ae76abee5ab91fb7ca6454c44196d, 164509bytes/319pins. Se conservan16registros: sólo2longitudes de cajas previamente admisibles;14STOP no se rescatan. Pins del padre + propio recibo padre =320dependencias, todas verificadas. Capturas WIDTH, referencia de longitud y ORIGINAL son datos sellados, sin importar ni ejecutar sus productores numéricos.

Selector cerrado por modelo/policy/ID/SHA del padre y registros/snapshot/query/SOURCE0/DETECTOR0/units/rol de referencia. Rechazo antes aritmética para aliases WIDTH/radianes/óptica/SOURCE1, drift o ausencia del padre. Referencia declarada explícitamente: DECLARED_NOMINAL_STRAIGHT_CHORD_NOT_OPTICAL.

## Operaciones y pruebas

Por cada una de las2escenas:3productos nominales racionales,2sumas del cuadrado,1nueva raíz HOST96,2restas para D. Son contadores parciales por rol, NO coste total: también hay3restas de delta nominal, operaciones enteras isqrt/división/retícula y cuadrados internos de raíz, validación de racionales/hash/IO. No RN nativa, decodificación de flotantes, replay de raíces/extremos/transportes anteriores, GPU ni Blender. Dos controles nuevos mínimos: raíz exacta1/8 y raíz irracional sqrt(2); no barridos antiguos. QA racional independiente vuelve a probar desigualdades cuadráticas de encierros RETENIDOS y extremos continuos de la caja; eso tiene coste real aunque no ejecuta antiguos kernels.

Oráculo independiente comprueba coordenadas originales,15radios, extremos por eje, cuadrados de raíces, retícula fija96, D firmado y cero incluido.8selectors inválidos,8mutaciones y3APInegativas (selector, missingparent y driftSHA simulados) deben rechazarse. Capturas/tiempos/resultados se guardan en el recibo al finalizar; segundos QA NO benchmark.

## Límites y siguiente enlace

Phase_error_bound/native_difference=null; wavelength/phase/physical_reference/scene_authenticated/sceneengine/GPU/Bpy=false. Sin nueva lambda, cap, material/gauge, división por longitud de onda, ángulo o U/GEMM sustituto. Costes completos UNKNOWN_NOT_ZERO: hash, IO, JSON, racionales y oráculos no son gratis.

Referencia nominal matemática no tiene incertidumbre física propia declarada ni autenticación. Su anchura numérica96 SÍ se cobra por intervalo. Los errores geométricos permanecen en L. Un adaptador posterior necesita contrato explícito para lambda-units-incertidumbre, fases SOURCE/reference/material, cobertura y cap. No inventarlos. Mantener congelados runners/shaders/contratos/fixtures conf1/v0/v4/0119/0315/nearestV2 y bounds.

Claude conserva RT/capacity/nebulatrace/research. Pedir ACK por esteID+SHA del recibo y SOLO artifacts YA existentes porID/path/SHA/bytes para MISMA ORIGINAL: referencia/lambda-material-autenticación y backend/guard failclosed/igualtrabajo-salidas-costes completos. RT-AUD-001:16Mvs1Mcentros/salidas distintas/cruce extrapolado NO comparación equivalente ni redRT.

CPU propia1hilo/afinidad1/hijo<=60s; GPU0. SinSDK/DrJit/Kaggle/publicación/push/merge. Sharedboards/checkpoint locales SINstage. FuturoGPU sólojobexclusivo conClaude, guardfailclosed, deadline nuevo verificable/telemetría/presupuesto seguro; ventana histórica permanece cerrada y deadline intacto.

## Resultado retenido

Suite PASS 1.3631588999996893s/93337bytes/stdoutSHA7e29a63de27ca6ffbb7e3200a9d1bb493e94d029f5a078842e39a938f872b542; oráculo independiente PASS 1.2605298999988008s/stdoutSHAe84fc9e4121bd9c69e4a2802a7364a6a2b7d29cbd6a906c4a9ec5ef28599ecdc.2escenas elegibles,14STOP,8selectors,8mutaciones,3APInegativas,323pins; sin replay numérico.3API fallan antes de nueva raíz (missing/drift son simulaciones, no modificaciones de archivos sellados).

Exterior: R^2=257/64; D=[-164027638926115951546879089/2^96,164235013968247841592849769/2^96]. Fino: R^2=1/64+2^-120; raíz96=[1/8,1/8+2^-96], D=[-(2^31+1)/2^96,(2^31+1)/2^96]. La corrección nominal fina queda dentro de la retícula96, no se afirma que se resuelva exactamente. Ambosos D incluyen0 y no son el WIDTH positivo anterior.

Preservado fallo inicial: lector supuesto top-level status en dos capturas antiguas, KeyError antes cálculo. Se adaptó el lector al schema sellado evidence+summary; NO cambio de aritmética ni umbral. Intento de lanzar oráculo con base64 inline falló Windows206 antes de crear hijo; se verificó leyendo este recibo propio, sin rerun de raíces de escenas. También preservados errores de validación de patch sin cambios parciales (targetduplicado/ancla inexistente).

Contadores del kernel de las2escenas:6productos nominales/4sumas/2raíces nuevas96/4restas D. Sumando2controles son4raíces HOST nuevas en la suite, no2totales. Oráculo reutiliza resultado y prueba cuadrados/extremos sin invocar root96 ni antiguos kernels. Coste completo sigue UNKNOWN_NOT_ZERO.
