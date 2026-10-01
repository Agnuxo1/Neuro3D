# Productor propio de campos y cotas ligado a la escena (CPU v1)

Opt-in: `scene_field_producer_cpu_v1.produce_scene_fields`. No cambia ningún
runner, shader, contrato ni fixture congelado. No ejecuta Blender/GPU/RT.

## Contrato y modelo

Regenera rutas desde todas las fuentes mediante el trazador CPU congelado
(máximo 64 registros/32 niveles; rechazo, no truncación). Reconstruye longitudes
con intervalos racionales y referencia terminal exactamente colineal. No recibe
rutas, campos ni cotas del llamador. Campos fuente y óptica son datos exactos
del snapshot representado, con coherencia explícita; no son medidas físicas.

Modelo ideal: transmisión `sqrt(tau)`, reflexión `i*sqrt(1-tau)`, espejo
`-exp(i*phase_rad)`, propagación `exp(i*2*pi*L/lambda)` y un modo plano ideal
por terminal. Usa **lambda original representada**, no la transportada hi-lo ni
el candidato de fase compensada. Admite correcciones de referencia negativas.
Fases de espejo limitadas a [-8,8] rad en este opt-in; ningún bound previo se
amplía. Se rechazan salidas binarias32 subnormales no nulas y overflow.

Fuentes, coeficientes y referencia terminal contribuyen a la identidad del
snapshot. El gauge ideal compartido contiene su SHA. Cada campo uint32 y su
cota nacen en la misma llamada, por ID/fuente/puerto/grupo/lambda/referencia.
El hash del payload identifica datos, **no autentica ejecución**.

## Cotas implementadas

- Raíces de coeficientes: intervalos exteriores racionales congelados,
  punto medio más semianchura. La fase de espejo también se aproxima y carga.
- Sin/cos: polinomios racionales de grado 48, cada resto de Taylor limitado
  por `abs(angle)^49/49!`; la cota L1 conjunta es el doble. No usa libm sin/cos.
- Pi: intervalo racional propio, contrastado mediante la identidad de Machin
  con intervalos racionales alternantes de arctan. No interpretar una antigua
  constante PI_UPPER como prefijo válido para formar una cota inferior.
- Propagación: reducción racional de ciclos con signo; incertidumbre angular
  por longitud y pi. Conversión explícita `L1 <= 2*norma2` y cota de cuerda
  `norma2 <= min(2, delta_angular)`. No intercambia métricas silenciosamente.
- Productos complejos: para aproximaciones A/B y errores L1 ea/eb,
  `L1(A)*eb + L1(B)*ea + ea*eb`. El término cruzado se conserva.
- Conversión final: diferencia racional exacta entre el polinomio y los words
  resultantes, incluida conversión binary64 intermedia. Si el resultado es
  cero por underflow, se carga esa diferencia; no se simula FTZ.
- ABI de errores: techo dyádico 2^-128, nunca redondeo hacia abajo. Después
  llama al compositor congelado: campo `R+B`; potencia por grupo
  `D+2*L1(S)*B+B²`. Grupos independientes suman potencias, no campos.

Gates absolutos existentes 1e-4/2e-4 intactos. El compositor sigue declarando
sus cotas recibidas como condicionales; este wrapper explica su origen propio
en el **modelo ideal CPU**, sin sobrescribir flags de certificación nativa.

## Verificación focal y fallos preservados

Ocho pruebas propias: MZI exacto/13 registros/4 terminales; referencia firmada
y fase espejo no nula; dos fuentes complejas/26 registros/8 terminales y
grupos separados; binding al cambiar fuente/óptica/referencia/lambda; dominio
y rechazo de campos externos; subnormal real rechazado y conversión de
cuadratura cargada; nueve perturbaciones racionales y techo dyádico;
enclosures alternantes independientes de sin/cos y prueba racional de pi.
El contraste analítico MZI no nulo usa binary64 y margen diagnóstico 1e-12;
**no es un certificado independiente del intervalo**.

Primera ejecución falló tres expectativas del test: orden/signo de brazos,
helper que sustituía grupo vacío por default, y supuesto incorrecto de que
la cuadratura produciría subnormal no nulo (redondea a cero). Corregidos tests,
sin cambiar gates ni ABI. Al fortalecer pi con Machin apareció un fallo real
de la nueva cota inferior: se había copiado un PI_UPPER antiguo conservador
como prefijo. Se corrigió **solo el intervalo nuevo**, no las constantes ni
módulos congelados. Ambos fallos y ejecuciones están retenidos en el reporte.

## Exclusiones y siguiente contraste

No prueba incertidumbre anterior al snapshot, export Bpyfloat32, transporte
hi-lo, fase/longitud nativa, driver/ALU GPU, RT, detección nativa, calibración
de fuentes, coherencia física ni solapamiento modal. No ventaja, promoción,
inferencia de red nativa ni aval JEV. Fallback local explícito.

Siguiente: contrastar artifacts **ya existentes** del productor nativo con
IDs/words/cotas/métrica/reference/λ y la misma completitud, sin otra carga de
relleno. Un piloto nativo requiere recursos, reserva y contrato propios; este
resultado CPU no autoriza su lanzamiento ni sustituye su resultado.
