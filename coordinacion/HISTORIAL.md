# Historial de experimentos

## EXP-000 · Circuito de una reflexión · 2026-09-28

- **Hipótesis:** posición, orientación, reflectancia RGB y frecuencia de
  objetos Blender cambian la señal y la activación del receptor.
- **Baseline:** emisor, reflector y receptor alineados; sin otros caminos.
- **Variables:** receptor desplazado, espejo girado, filtro azul y frecuencia
  modificada, cada una comprobada por separado.
- **Datos/partición:** escena sintética de tres objetos, sin dataset externo.
- **Métricas:** hit, potencia/intensidad RGB, fase y activación.
- **Presupuesto:** background CPU, un hilo, 45 s por fase, umbrales de memoria
  del ejecutor.
- **Resultado:** pruebas superadas; intensidad baseline 0,7053474966 y
  activación 0,3657724623; guardar/reabrir reprodujo el estado.
- **Artefactos/logs:** `Docs/BLENDER_RUNTIME_REPORT.md`; `.blend` y logs
  locales en `D:\PROJECTS\.artifacts\neuro3d-blender-smoke-v2`.
- **Limitación:** un solo camino; sin interferencia ni GPU.
- **Decisión:** conservar como baseline. No promocionar como red multirrayo.
- **Reproducción:** `Blender/tests/run_blender_smoke.py`, con ruta explícita al
  Blender portátil y directorio de artefactos en D:.

## Próximo experimento

La prueba confirmatoria Blender no se inicia hasta registrar hipótesis,
control monorrayo, variable principal, métrica, presupuesto, parada y criterio
de promoción para `OPT-002/003`. Las comprobaciones CPU posteriores se
etiquetan exploratorias, como se indica abajo.

## OPT-002 · Comprobaciones exploratorias CPU · 2026-09-28

- **Hipótesis provisional:** un circuito de dos puertos con campos complejos
  redistribuye la potencia sin crearla y distingue fase relativa de potencia.
- **Cambio respecto de EXP-000:** siete objetos y dos caminos; no se ha
  sustituido ni modificado el circuito monocamino verificado en Blender.
- **Datos:** escena sintética `default_scene()` del nuevo motor CPU; ningún
  archivo `.blend` nuevo se creó ni se abrió Blender.
- **Controles:** fase 0 y π, divisor asimétrico, reflectancia/absorción,
  camino roto, receptividad y solape fallido. Entradas extremas finitas
  provocan resultado finito o rechazo explícito.
- **Resultado:** 28/28 pruebas CPU/estáticas en 0,026 s, incluidas 10 nuevas;
  144 comparaciones con el oráculo separado de Claude, error máximo 4,72e-15.
  Estas coincidencias comparten supuestos y no validan física real.
- **Balance:** residuo por canal <1e-12 en los casos ensayados. La potencia
  que llega sin solape queda `unresolved` y bloquea la afirmación de
  interferencia; no se presenta como pérdida material.
- **Límite y decisión:** el adaptador Blender solo se importó, no se ejecutó;
  el control incoherente y una variación geométrica con recombinación válida
  siguen pendientes. Mantener EXP-001 como borrador y pedir OPT-008 a Claude.
- **Reproducción:** `python -m unittest discover -s Blender/tests -p 'test_*.py' -q`.
