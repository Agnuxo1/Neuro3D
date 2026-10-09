# Diagnóstico de caminos: perfil prospectivo separado

**Resultado:** se completaron las 16 consultas en 2,724788 s supervisados, RSS máximo 31,703125 MiB. El resultado es `INCOMPLETE` válido, con nueve razones `RESOURCE_LIMIT`, campos nulos y métrica 0 del perfil corto. El [auditor categórico](validation/captured-path-diagnostic-2026-10-09/attempt01/supervisor.json) lo acepta como incompleto; no certifica las geometrías parciales ni un campo.

Se probaron 1.664 cajas de objeto y se enviaron 4.736 triángulos frente a 106.496 oportunidades exhaustivas: un recuento de candidatos, no una comparación de tiempos equivalente. Las últimas consultas tienen numeradores/demominadores de 19/17 bits; en este prefijo no se observa una explosión de tamaño racional. Todos los hits de este prefijo son `SELECT`. Se conserva [cada progreso y fuente](validation/captured-path-diagnostic-2026-10-09/artifact_index.json).

El siguiente trabajo es construir un grafo de estados exactamente iguales y sumar **campos complejos** en su referencia común, antes de propagar el operador futuro. Esto puede evitar reenumerar sufijos compartidos sin omitir ramas; la equivalencia deberá verificarse. Los primeros resultados no autorizan a fusionar estados aproximadamente iguales ni sumar sus intensidades.

Dos recorridos anteriores agotaron 90 segundos sin escribir resultado. Este diagnóstico limita explícitamente el trabajo a **16 casts y profundidad 4**, con las mismas garantías de RAM/tiempo, geometría y campos de entrada. No prueba la completitud de la red y no modifica las métricas anteriores. Su propósito es observar los estados geométricos y el crecimiento de la aritmética exacta antes de optimizar más.

El [perfil](research/captured_path_diagnostic_profile_2026-10-09.json), UUID `c230e3e4-c13d-41dc-a4b4-5913b327c7c1`, SHA256 `f15da7e118a2b340f53528bf6207e4fc3c9f0fe5cc2b72228dab2127c0ed9948`, fija fuentes y criterios antes de la ejecución. El [recibo enlazado](research/captured_path_diagnostic_registration_2026-10-09.json) deriva de la autorización humana explícita de continuidad en GitHub; no emite un registro externo.

Se retendrá para cada consulta el número de bits de numeradores/denominadores del origen y dirección, estado de selección, objeto elegido y estadísticas de candidatos. Un resultado incompleto conservará las razones y campos nulos. Se espera que los límites cortos impidan completar la red: `0` en esa métrica no refuta la viabilidad con otro perfil ni sustituye una cota de contribuciones omitidas.

El worker y supervisor nuevos no reemplazan las preimágenes anteriores. Pasan comprobaciones de compilación, pins y vinculación al recibo real; esas comprobaciones no son datos del recorrido.
