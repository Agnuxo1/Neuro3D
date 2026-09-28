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

No se inicia hasta registrar hipótesis, control monorrayo, variable principal,
métrica, presupuesto, parada y criterio de promoción para `OPT-002/003`.
