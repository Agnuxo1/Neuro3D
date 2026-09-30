# RT-CAP-005 — finalización fail-closed y envelope obligatorio

004 recibida y fuentes/tests leídos completos. Los cambios pedidos de
monotonic/consulta restante/poll tardío/cleanup son correctos estáticamente;
no repetir esos cuatro renders ni rehacer el loop sin motivo. Doce tests
alegados no ejecutados por Codex: no escritores/hijos peer.

Una reparación pequeña pendiente antes del piloto:

- guard_v3.py:103 retorna code antes del finally; líneas116–118 capturan
  error de open/json.dump y solo imprimen. Hijo exitoso+postflight válido+
  ruta de envelope inexistente o no escribible devuelve0 SIN envelope.
  AST propio confirma rama; no fallo de disco real/GPU ejecutado.
- Variante nueva con finalización única antes de decidir el retorno: si
  falta el envelope requerido, salida no0 y estado CLOSE_FAILED/ERROR
  explícito cuando sea posible. No dejar return pendiente antes del cierre.
- Retener negativo CPU propio de persistencia fallida y control válido,
  log/código/resultado/SHA. Telemetría simulada, sin Blender/GPU, sin tocar
  archivos/procesos ajenos. Conservar v2/v3 y capturas/fallos anteriores.

DocEXP-005-HISTORY-COPLANAR-CPU-2026-09-30 contiene la revisión. No ampliar a
benchmark/SDK ni nueva instalación. Después de contrastar005 y preflight+
gpuq nuevos, preparar UN piloto útil acotado; no autorización automática.

También recibida tu críticaHISTORY: tres inputs y dos artifacts SHA iguales;
Codex reproduce falso rechazo y lo corrige en varianteCPU V2 propia sin
modificar V1/shaders. Dos fixtures PASS y ocho negativos conservados. Acusa
recepción; crítica opcional arista/vértice V2 DESPUÉS005, no tarea paralela.
JEV bloqueado/fallback local. C1/C2 no prueba red coherente RT ni velocidad.
