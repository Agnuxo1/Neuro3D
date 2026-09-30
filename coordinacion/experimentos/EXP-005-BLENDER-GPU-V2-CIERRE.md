# Enmienda operativa v2 · cierre del contexto

2026-09-30 01:04 UTC. V1 conserva números y fallo:54casos correctos y JSON
written antes de EXCEPTION_ACCESS_VIOLATION al llamar quit_blender. El proceso
NO salió limpio; no certificar estabilidad por passed=true del JSON.

Hipótesis acotada: shader Python permanece vivo al apagar contextoGPU. Cambio:
destruir dueño shader y recoger objetos ANTES de quit. No se modifica kernel,
ABI, entradas ni umbrales. Regresión estática del orden de liberación; nueva
ejecución completa54cases bajo guard, exige también retorno0 y proceso propio
finalizado. Si vuelve a fallar, seguir diagnóstico y no promover resultado.

TEMP/TMP propios en D: para conservar archivos de crash; sin borrar temp ajeno.
Esto corrige falta de acceso al tempC: observada pero no se afirma causa del crash.
V1artefactos originales intactos. Guard120s y resto de límites/contrato v1 iguales.
