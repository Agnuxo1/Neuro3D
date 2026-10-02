# EXP005 — AXIAL-SCENE-PARAMETER-DOMAIN-HOST-001

P1 Codex capacity_audit/EXP005, opt-in HOST racional; base
ff78f1e90dc964e1a55aaaec76c29e7ec6e26d10.
Acuse AXIAL-ARGUMENT-RECTANGLE-HOST-001, SHA
b69da9b5a2e3492465edfcb8b8357647763afe90bae2af30fd514b424c946cf8.

## Dominio exacto, no geometría general

Modelo axial-shared-plane-exactYZ-coordinate-domain-HOST-v1.
API pública: casos retenidos y modelo; no paquetes, certificados, radios ni
cupos aportados por caller. Todos los recibos previos se validan por SHA.
Se lee INPUT ORIGINAL/snapshot/ABI/orden de fuentes y los seis buffers.
No se ejecutan los encoders, selectores, productores o suites anteriores.

Dominio nuevo explícito: cada owner M/D se desplaza como UN SOLO plano X compartido
por TODAS sus caras, dentro del intervalo hi-lo + radio original. Fuente X,
referencia X y wavelength recorren sus intervalos INPUT. YZ de vértices/fuente
son exactamente los de ORIGINAL, sin incertidumbre YZ; direcciones son ±unit-X.
Se exige lista completa de caras, owners/topología correctos y ausencia de meshes
no declarados. Este modelo NO permite movimiento independiente de vértices,
direcciones oblicuas, deformación, incertidumbre YZ ni superficies generales.
No es certificado de incertidumbre de un dispositivo o de óptica física.

Se decodifican palabras normales/cero hi-lo32 y radios signed512 exactos,
sin nuevos RN, casts, encoders, FTZ ni redondeo. ORIGINAL binary64 se convierte
a racional exacto y debe estar contenido en esos radios SIN ampliación.
Los bits de la referencia/mode ORIGINAL y su frame fijo se contrastan.
Todos los vértices ORIGINAL de un owner deben compartir X incluso entre caras.

Para YZ fijo se prueban determinantes estrictos de todas las proyecciones.
Degenerados y contactos de borde rechazan; exactamente un interior por owner.
Para sigma=±1, el intervalo sigma(M-S) es estrictamente positivo; terminal
inicial es uniformemente detrás o estrictamente después del espejo.
Tras el primer impacto comprobado y reflexión axial, sigma(M-D)>0.
La exclusión del owner de salida sólo se deriva de ese primer impacto probado;
no hay previous-id arbitrario ni lowering de t_min ni epsilon de contacto.

Estas condiciones afines garantizan los dos eventos para TODOS los planos X
compartidos del dominio, no sólo para la geometría nominal. Separación >0,
por fina que sea, se acepta si está resuelta por los radios; intervalo que toca
cero o solapa permanece STOP. No se cambian fixtures ni selectores congelados.

Longitud geométrica sigma(2M-S-D), corrección sigma(D-R), suma referenciada
sigma(2M-S-R). Es el MISMO D; su coeficiente neto es cero. D sigue contando para
clearance y contacto: NO se cancela en los eventos. Se prueba imagen afín exacta
de toda la caja, y sus intervalos Lref/wavelength deben coincidir exactamente
con el rectángulo ya verificado, incluidos ORIGINAL y gauges por fuente.
No se sustituye R por D ni se usa suma de intervalos independientes.
Escala interna de enteros BU*2^149; longitudes referenciadas pueden ser firmadas.

## Evidencia y alcance

17casos/19fuentes: cinco pruebas de dominio axial restringido, 14STOP previos
conservados; fuente other de two_sources no rescatada ni suma parcial.
Se conservan las cinco cotas parámetro/fase que cabían en MISMO cupo INPUT y
las tres cotas polinómicas genéricas no-fitting de singleton/cap0.
Siete controles de caja (dos signos, hueco 2^-80, contacto/solapamiento/competidor),
cuatro controles YZ y 32rechazos de contrato/INPUT/ORIGINAL/caller.
384combinaciones de extremos afines en el oráculo NO son evaluaciones RN ni
prueba por muestreo de un grafo no afín. 20proyecciones escena nuevas y
205checks de ORIGINAL/contenimiento/exactYZ; otros controles son sintéticos.

Dos suites acotadas: primera 6PASS 0.6785191s raw93538
SHA43a5b362c1f6393df1b1dd76adddf778ecd9b96a29f32938b71db2b7659a31e4;
revisión de contrato añadió shared-X entre TODAS caras y control ORIGINAL
no compartido. Segunda final6PASS 0.6580601s raw93646
SHA79137af21492466a1c4c5ce23f30d15fde65afee9135834b93ead52e3b9f4a5f.
No se afirma final a primer intento ni misma producción entre ambas versiones.
No fallo numérico oculto/cupo relajado/replay de productores. Ambas capturas
se conservan íntegras con stdout comprimido, stderr, límites y hashes.
Verificador independiente stdlib sin imports producción reconstruye INPUT,
proyecciones por áreas orientadas, dominios y extremos afines, linaje/cupos/STOPs.

El flag NUEVO restricted_coordinate_box_to_parameter_rectangle_proved es parcial.
whole_scene_parameter_enclosure_proved, scene_argument_enclosed, ORIGINAL-unit,
sourceuniform/fullpipeline, general3D/physicaluncertainty/native/GPU/RT/auth siguen
false. Nunca se reescriben recibos previos para promoverlos. Falta cerrar el error
uniforme complejo de fuente y composición/reducción/potencia; el caso de cupo0
polinómico genérico requiere refinamiento separado, no cap nuevo.
La prueba no es coste completo ni velocidad/eficiencia/motor ganador.

CPU1hilo/hijo60s, sin GPU/Blender/RT/SDKDrJit/Kaggle/pushmerge. JEV bloqueado:
fallback LOCAL sin aval ni reintento. Ventana0337 cerrada/deadline intacto.
Futuro GPU sólo reserva exclusivaClaude/telemetría/gpuq/guardfailclosed/NUEVOdeadline
y límites originales. Frozen/fixtures/runners/shaders/radios/cupos intactos.
Cuatro boards locales SINstage. Claude ACKID/SHA y artifacts YAexistentes
matching INPUT/ABI/escena/fuentes/gauges y contrato igualtrabajo/salidas/costes
completos; sin cargas duplicadas ni relleno.
