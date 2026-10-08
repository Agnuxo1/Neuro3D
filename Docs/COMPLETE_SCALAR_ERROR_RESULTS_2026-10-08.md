# Punto 4: resultado del certificado integral

**Cerrado para el motor CPU completo de óptica escalar ideal y para las cajas de entrada que superan las condiciones de certificación.** No se declara una cota física sin mediciones ni se certifica automáticamente otra implementación GPU/RT. La red completa GPU permanece en el punto 6.

## Evidencia final

- 14 pruebas PASS, incluyendo raíces comprobadas con enteros, pi/trig contrastados diagnósticamente con mpmath1.3.0 a90dígitos, todas las 41 entradas K3/K4 y cajas no nulas.
- 41 certificados completos: cota máxima del error L1 de campo <=1.550e-13; cota máxima de intensidad <=1.418e-13. Son cotas respecto al modelo escalar representado exacto y a los valores flotantes efectivamente producidos, no medidas de precisión física.
- 9 ejecuciones de la interfaz JSON PASS: cuatro cajas K3/K4, escena exacta y cuatro rechazos explícitos (incertidumbre angular, cota ausente, orden de hueco diminuto y presupuesto JSONnull). UNKNOWN devuelve código2 y no emite un campo completo certificado.

Recibos finales: [aceptación](validation/multipath-error-2026-10-08/attempt07/receipt.json), [interfaz y cajas completas](validation/multipath-error-2026-10-08/cli03/receipt.json). Entradas, certificados, fuentes y resultados anteriores se conservan. Los siete intentos son revisiones de implementación, no réplicas estadísticas independientes.

## Utilidad y limitación de las cajas perturbadas

La misma caja de radio1e-8BU en posiciones y traslaciones rígidas de objetos, con error axial de escala de dirección1e-8, produce las siguientes cotas finales. El radio de dirección conserva el signo y no introduce incertidumbre angular.

| Escena | Caminos | Error L1 de campo máximo | Error de intensidad máximo |
|---|---:|---:|---:|
| K3, row | 22 | 0.000257360 | 0.000333969 |
| K3, todos los modos | 58 | 0.000686124 | 0.000972495 |
| K4, row | 46 | 0.000438316 | 0.000543511 |
| K4, todos los modos | 128 | 0.001302882 | 0.002181428 |

Las cotas iniciales K4/todos eran3.1373 y6.2301: válidas pero poco útiles. La mejora conserva las mismas entradas y usa dependencias demostradas (invariancia de escala de dirección, mapa afín del impacto, reflexión matricial exacta y Lipschitz de seno/coseno). Los resultados iniciales permanecen en cli01. No se presenta este estrechamiento como mejor tolerancia de hardware. La caja final tampoco acredita precisión1e-11 bajo esas perturbaciones: distingue claramente error numérico y error de entradas.

## Cadena cerrada y reproducción

El [documento de prueba](COMPLETE_SCALAR_ERROR_PROOF_2026-10-08.md) cubre: entradas → cobertura/orden/reflectancia geométrica → longitudes y referencia → fase → coeficientes complejos → suma coherente completa → intensidad → cota de las salidas flotantes reales. Rechaza topología, soporte o modalidad no demostrados. Los [protocolos prospectivos locales](ERROR_CERTIFICATE_PREREGISTRATION_2026-10-08.md) y sus enmiendas no equivalen a un registro externo ni a revisión por pares.

```text
python -I -B Blender/tests/run_multipath_error_validation_v1.py --out <directorio_nuevo>
python -I -B Blender/tests/record_error_certificate_cli_v1.py --out <otro_directorio_nuevo>
python -I -B Blender/benchmarks/capacity_audit/certify_exact_scene_v1.py --scene escena.json --out certificado.json
python -I -B Blender/benchmarks/capacity_audit/certify_exact_scene_v1.py --scene escena.json --radii radios.json --out certificado_caja.json
```

El certificado de producción usa sólo biblioteca estándar. mpmath1.3.0 interviene en la prueba diagnóstica, no en la garantía de inclusión. Las escenas con entradas físicas desconocidas continúan `UNKNOWN_NOT_ZERO`. Un presupuesto explícito ausente/null se rechaza; omitir `--radii` selecciona exclusivamente el modelo representado exacto.
