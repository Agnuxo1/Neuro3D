# Repetición CPU en un entorno Linux de GitHub

Estado: REPRODUCCIÓN CPU EN LINUX GITHUB COMPLETADA con el perfil v2. El primer workflow fallido permanece archivado. Se ejecutó nuestro código en un entorno externo al ordenador de desarrollo; la réplica realizada e interpretada por un investigador independiente sigue pendiente.

## Perfil y límites fijados

[Perfil](research/external_cpu_reproduction_profile_2026-10-09.json), UUID `313e31a5-f555-4ce2-9652-f753f05dee6a`, SHA-256 `ecb48f85f0785572bedc91a4254381ef5ca9683e3aaca7e9355a6db62b131385`, 38 fuentes/artefactos. La [autorización humana GitHub](research/external_cpu_reproduction_registration_2026-10-09.json) permite esta continuidad prospectivamente publicada. Registro externo/IPFS pendiente, sin identificadores emitidos.

Plataforma declarada: GitHub Actions Ubuntu 24.04 x86_64, Python 3.12.12, NumPy 2.2.6, psutil 7.0.0 y mpmath 1.3.0. Las ruedas Linux de [PyPI](research/external_cpu_dependency_primary_receipt_2026-10-09.json) se verifican mediante SHA-256 y `--require-hashes --only-binary=:all:`. Los commits de checkout/setup-python/upload-artifact se verificaron contra las etiquetas primarias de sus repositorios GitHub y se fijan completos en el workflow. La [versión de Python](https://www.python.org/downloads/release/python-31212/) es deliberadamente reproducible; no se afirma que sea la más reciente.

Antes de cualquier cómputo científico, el ejecutor exige igualdad de HEAD con el evento GitHub y comprueba que las 38 fuentes, el perfil y el recibo son exactamente los blobs publicados. El checkout sólo descarga las familias de archivos necesarias. El workflow sólo tiene permiso `contents: read`, no expone credenciales y conserva siempre los resultados disponibles.

Etapas:

1. Cinco módulos de controles adversos CPU: índice exacto, grafo coherente, derivadas geométricas, vecindades independientes e intervalos con referencias de alta precisión.
2. Recomposición racional independiente del certificado del grafo capturado ya observado. Es repetición del cálculo de ese certificado, no una observación nueva de GPU o de Blender.
3. Repetición del entrenamiento Iris original sin modificar entradas, división 120/30, 60 actualizaciones, controles de gradiente, 61 auditorías ni reconstrucción final. Su supervisor original conserva el límite de 900 s.

El resultado informa pérdida, aciertos y diferencias de potencias/predicciones frente a la ejecución local. Las trayectorias entre plataformas no tienen que ser idénticas bit a bit; cualquier diferencia se conserva. No se elige el mejor resultado ni se cambia un umbral después de verlo. Un fallo válido de descenso de pérdida mantiene métrica 0; una interrupción ambiental o fuente/runtime inválido conserva métrica nula.

Presupuesto exterior: 1500 s, un núcleo CPU, sin GPU, RAM libre inicial ≥4000 MiB/suelo ≥2500 MiB, RSS agregado propio ≤1500 MiB y evidencia ≤128 MiB. Controles y certificado tienen 120 s cada uno; entrenamiento conserva sus 900 s. El job completo tiene un límite de 35 minutos, incluidos instalación y archivo de artefactos. La supervisión externa termina sólo sus procesos creados.

## Alcance y reproducción

[Workflow](../.github/workflows/external-cpu-reproduction-20261009.yml). Se inicia al publicar cambios en ese workflow/perfil/ejecutor en la rama autorizada o mediante ejecución manual. Artefactos brutos se conservan diez días en GitHub y luego se archivarán con hashes en el repositorio.

```bash
python -X utf8 Tools/run_external_cpu_reproduction_v1.py --profile Docs/research/external_cpu_reproduction_profile_2026-10-09.json --registration Docs/research/external_cpu_reproduction_registration_2026-10-09.json --verify-only
python -m pip install --require-hashes --only-binary=:all: -r Docs/research/external_cpu_requirements_2026-10-09.txt
python -X utf8 Tools/run_external_cpu_reproduction_v1.py --profile Docs/research/external_cpu_reproduction_profile_2026-10-09.json --registration Docs/research/external_cpu_reproduction_registration_2026-10-09.json --out reproduction-evidence
```

Esta receta no ejecuta Blender nativo ni CUDA/AMD y no puede validar hardware fotónico. La descarga oficial de Blender Linux no pudo verificarse desde este entorno, por lo que no se sustituye esa ausencia por una afirmación de instalación Linux satisfactoria. La crítica especializada y réplica independiente humana permanecen pendientes.

## Fallo de infraestructura conservado

Publicado `62c9c5d5194d81382793d5f06a25871d37e16447`, fuentes/perfil/recibo byte a byte verificados localmente. El [run GitHub 37886493361](https://github.com/Agnuxo1/Neuro3D/actions/runs/37886493361) terminó inmediatamente con fallo y cero jobs/artefactos. El parser YAML local identifica `--only-binary=:all:` dentro de un escalar de comando sin bloque: el último `:` seguido de espacio provoca sintaxis inválida. Se conservan [metadatos primarios, preimágenes Git y recibo del operador](validation/external-cpu-reproduction-2026-10-09/attempt01/evidence_index.json), con métrica nula y sin ejecución científica. La corrección usará bloque literal de comando y un perfil nuevo publicado; no se considerará este intento reproducción externa.

## Perfil v2 con sintaxis corregida y resultado completo

[Perfil v2](research/external_cpu_reproduction_profile_v2_2026-10-09.json), UUID `67ba33d3-4006-43d9-b3cf-e0eae2fc1d6a`, SHA-256 `cee34399e9d6a0529cdae293677551ae8341640853a0e60c628fe510ded42fef`. Cambia únicamente el hash del workflow por el uso de bloques literales y rutas de perfil/recibo versionadas. Los otros 37 pins, datos, controles, software científico, ruedas de dependencias, versiones y límites son los mismos. Un parser YAML confirma ahora la sintaxis antes de publicar. La ejecución sigue exigiendo igualdad con todos los blobs Git antes de obtener datos.

Publicado antes del ensayo en `bbc06c3ace138d98873df9ba0a4d83252ebfefc8`. El [run 37886830249](https://github.com/Agnuxo1/Neuro3D/actions/runs/37886830249), job `113678593248`, verificó los 40 blobs —38 pins, perfil y autorización— antes de ejecutar la ciencia. El recibo local de las 05:05:45 UTC se obtuvo después del inicio del run y no se usa como prueba de ese orden: la comprobación autoritativa es la etapa del propio runner.

| Medida observada | Resultado |
|---|---:|
| Controles adversos CPU | 34/34 pasan |
| Recomposición racional independiente | Certificado reproducido |
| Estados geométricos del entrenamiento auditados | 61/61 |
| Aciertos entrenamiento / evaluación | 110/120 / 27/30 |
| Predicciones iguales a referencia Windows | 150/150 |
| Máxima diferencia de potencia entre runtimes | 3,885780586188048×10⁻¹⁶ |
| Tiempo total del ejecutor científico | 367,366 s |
| RSS agregado propio máximo | 88,289 MiB |

El entorno real fue Linux x86_64, kernel `6.17.0-1022-azure`, Python 3.12.12 y las tres versiones fijadas. Los tiempos incluyen controles, certificado y entrenamiento dentro del worker; el checkout, instalación y subida del artefacto se miden separadamente en los metadatos del job y no se ocultan como cómputo neuronal.

Se descargó el artefacto GitHub `11596084252`, cuyo ZIP tiene SHA-256 `84691994ad4c34285f14a032998da461c817d31bcc7e893d5f9b8f5dd7fdbae8`, y se verificaron todos los hashes internos. [Archivo permanente de resultados, logs, metadatos primarios y preimágenes](validation/external-cpu-reproduction-2026-10-09/attempt02/evidence_index.json). El estado es `VALID_EXTERNAL_CPU_REPRODUCTION_RESULT`, métrica 1. Un fallo temporal HTTP403 del enlace de descarga del conector se resolvió usando el acceso GitHub existente; no altera el resultado ni los bytes de evidencia.

Para repetir exactamente este perfil, utilice el commit fijado anterior y sustituya en los comandos las rutas originales por `external_cpu_reproduction_profile_v2_2026-10-09.json` y `external_cpu_reproduction_registration_v2_2026-10-09.json`. Cualquier modificación científica exige un perfil nuevo publicado. No se ejecutó Blender nativo ni GPU en Linux y no se obtuvo revisión especializada, calibración física o registro externo/IPFS.
