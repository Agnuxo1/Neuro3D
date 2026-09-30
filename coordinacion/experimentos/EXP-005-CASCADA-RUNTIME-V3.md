# Cascada v3: puertos oscuros explícitos, mismos gates

30/09/2026 00:30UTC. Fallback local, no JEV remoto. V1/v2 conservados FAIL.
V2 ya no pierde los rayos de basis2, pero el consumidor devolvía solo puertos
visitados. La entrada de la segunda celda no alcanza a.Y: su campo debe ser
CERO explícito. El gate de campos COMPLETOS rechazó correctamente esa omisión.

Corrección mínima de consumidor: inicializar TODOS los terminales declarados,
detectores y escapes, a campo0j y contador0 antes de acumular cada camino.
No convierte rayos perdidos en cero: trazador sigue fallando cerrado si pierde
rayos y se exige identidad/multiplicidad completa contra oráculo. No se omiten
puertos ni se renormaliza; conjunto vacío de rutas todavía falla.
Regresión nueva verifica puerto oscuro declarado/campo/potencia/contador y
conserva controles de escape, suma coherente y desconocidos inválidos.

Fixture,54probes y TODOS los umbrales numéricos deV1 siguen intactos.
Reflexión corregida deV2 se conserva; referencia/oráculo no cambiado.
Guardar/reabrir en carpeta NUEVA
`D:/PROJECTS/.cognition/neuro3d/exp005_cascade_cpu_v3_20260930_0031/`.
Guard/cola/120s/1hilo/RAM4/VRAM18/temp80/cierre06UTC sin cambios.
No reescribir resultados anteriores, no declarar PASS por pruebas sintéticas.
Alcance híbrido; no cierra EXP-005completo ni RT/ortogonalidad/modalidad física.
