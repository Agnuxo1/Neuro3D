# Regresión de reducción de fase con transporte exacto

2026-09-30 16:08:25 UTC. Solo CPU sintética: proxy aritmético de la expresión
GLSL retenida, NO reproducción GPU ni prueba de compilador/libm.
JEV bloqueado; fallback local sin aval remoto.

## Hipótesis y controles

Un presupuesto de lambda, incluso con error de transporte cero, no basta
para certificar el cálculo de fase. Se construyen escenas MZI en el perfil
CPU congelado: dos brazos, 13 registros completos regenerados, geometría
unitaria y referencia Dx grande pero <=1e6 BU. Se reconstruye L efectiva
racionalmente y se exige que sea puntual y exactamente binary64.

El pack_frontier y texture_data/split_double reales dejan idénticos TODOS
los escalares de geometría, fuentes y óptica de las cinco escenas. Esto es
una comprobación CPU del encoder real, NO descarga de texturas GPU ni Bpy.
La referencia racional utiliza lambda YA DECODIFICADA, separando error de
reducción de fase de la diferencia adicional lambda original→codificada.

Shader congelado exp005_shared_frontier.glsl, SHA
`914bf2962ead3c6a7b721a8dc2aa6c1e796af4bde1892db1802c3ca93ebdfcd1`:

    phase = TAU*effective/lambda_decoded
    angle = float(phase - TAU*floor(phase/TAU + 0.5))

El proxy CPU calcula en binary64 ese orden, redondea el ángulo a float32
y compara su cos/sin de biblioteca CPU con la referencia racional reducida
ANTES de convertir a float. No certifica sin/cos float32 del driver, GPU,
FMA, optimizaciones ni errores anteriores de geometría/longitud.

## Resultado

Cuatro tests y cinco casos PASS (validan los controles Y retienen los
fallos esperados), 0,4002 s, un hilo, hijo<=60 s. Gate complejo 1e-4 intacto.

| Caso | Lambda exactamente transportada | Error unitario phase-first CPU | Alternativa cycles-first CPU |
|---|---|---:|---:|
| Control fase entera, lambda 0,125 | sí | 0 | 0 |
| Control cuarto de vuelta, lambda 0,125 | sí | 4,3711e-8 | 4,3711e-8 |
| Lambda 2^-20, L=1000001,8750002384 | sí | 4,92736e-4 | 4,3711e-8 |
| Lambda 2^-30, L=1000001,8750000002 | sí | 0,425917 | 4,3711e-8 |
| Lambda no diádica decodificada, L grande | no | 0,865045 | 0,865045 |

En los dos casos diádicos la referencia racional es EXACTAMENTE 1/4 de
vuelta: los fallos del proxy no provienen del encoder, ni de una longitud
o referencia inexacta en esta representación CPU. Los campos pueden
fallar aunque solo se inspeccione potencia unitaria (siempre uno).

La alternativa reduce primero los ciclos binary64 y después multiplica
por TAU. Mejora esos dos ejemplos, pero FALLA el quinto incluso frente a
lambda decodificada exacta: el cociente binary64 ya perdió la fracción.
Por tanto NO se aplica un parche ingenuo ni se presenta como solución
general. Ningún shader/runner/contrato congelado se modifica.

Reporte:
`D:/PROJECTS/.cognition/neuro3d/exp005_phase_reduction_cpu_20260930_1608.json`
SHA `6ede23289c1a5c071d5652f4d016c9f136fce9740befa13b5df1684ce75e021c`.
Once pins de código intactos. No escritor peer, GPU, RT, Blender ni conf1.
`native_promotion_allowed=False`, `quotient_first_shader_implemented=False`.

## Coordinación y alcance

Estos adversarios complementan la crítica de precisión, NO repiten el
gate K3/K4 ni invalidan sus escenas pequeñas históricas. Una implementación
nueva deberá preservar esta evidencia y demostrar reducción de argumento,
además de lambda/longitud y tolerancias, antes de promover rangos grandes.

Claude: incluir el caso diádico de error de transporte cero y el fallo de
cycles-first en la MISMA revisión CPU de precisión ya pendiente; no nuevo
barrido/benchmark/guardreview ni cambios en 006. El piloto sigue prioridad.
GPU externa ocupada y RAM libre 0,573 GiB a 16:09: no nuevas cargas ni
procesos propios de prueba después de esta unidad; terminar registro.
