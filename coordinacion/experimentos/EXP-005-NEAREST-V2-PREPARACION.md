# EXP-005: nearest-hit independiente del orden — preparación V2

30/09/2026, Codex. Fallback local; JEV bloqueado. NO contrato de lanzamiento
GPU congelado todavía; CPU specification y variante GLSL opt-in nuevas.

## Problema y conducta requerida

CE3 retenido: tres superficies a 5, 5−0,9e−9 y 5−1,8e−9 BU. V1 puede borrar
la ambigüedad al encontrar un impacto posterior. Se reprodujo en emulador
independiente CPU, NO en GPU runtime. El oráculo triangular rechaza los seis
órdenes de objetos. No ampliar conf1/bounds ni certificar generalización.

V2 obtiene primero el mínimo global exacto entre impactos válidos. Después
revisa TODOS los candidatos dentro de ±1e−9 BU del mínimo final. Rechaza si
alguno pertenece a otro objeto o tiene normal no paralela (|dot|<1−1e−9).
Triángulos coplanares del mismo objeto con winding opuesto no se rechazan.
Empates de distancia exactos seleccionan normal canónica (signo del primer
componente no nulo positivo; mínimo lexicográfico), no el primer triángulo.
Esto evita dependencia del orden cuando normales casi paralelas rodean el
umbral angular. No implica ortogonalidad física ni continuidad de modos.
Una ambigüedad lejana no contamina un impacto anterior único. No usar grupos
transitivos de distancia: la referencia es el mínimo global, no cada vecino.
En el borde EXACTO la banda es inclusiva: rechazo conservador; el oráculo
histórico usa comparación estricta. Registrar esta diferencia, no ocultarla.

GPU recorre triángulos crudos DOS veces; no recibe listas de impactos CPU ni
readback intermedio. Hay más tests de triángulos por consulta: los contadores
históricos de casts cuentan consultas, NO pruebas de intersección. NO RT/BVH,
ni velocidad/eficiencia demostrada. Es una corrección de seguridad numérica.

## Preservación y límites

El shared shader V1 SHA914bf296...ebdfcd1 queda intacto. Composición verifica
SHA, reemplaza solamente nearest y conserva main/amplitudes/ledger/flags.
Los runners anteriores NO seleccionan V2 automáticamente. Bias1e−6,
epsilon1e−9, terminal tolerancia1e−6 y perfiles/caps siguen SIN corregir:
esta versión sola no resuelve CE1/CE2/hi-lo/overflow ni modos físicos.
Regresiones CPU adicionales RETIENEN las limitaciones: una superficie a1e−8
BU se pierde con bias1e−6; llegada normalizada(1,4e−4,0) es aceptada por el
umbral GPU1e−6 y rechazada por oráculo1e−9. Son contraejemplos pendientes,
no funcionalidades reparadas. Geometría CE3 tiene todas las partes high
FP32 iguales; el split high+low distingue tres planos a error<1e−14CPU.
Eso NO mide precisión del hardwareRT ni del kernel compilado.

## Antes de GPU

Preparar runner nuevo con rawscene adversarial CE3: seis órdenes de objetos
y triángulos, status2 y campos cero. Controles unique-nearest frente a
ambigüedad lejana, coplanar edge válido, miss y near-band; conservar oráculo
independiente y bandera inclusiva exacta. Revalidar fixtures existentes
sin alterar sus resultados/hashes. Registrar compuesto/hash del snippet,
gate fail-closed, guard, límites y tiempos antes del primer lanzamiento.
Solo gpuq exclusivo, deadline06UTC, piloto120s, RAM4GiB tras presupuesto,
VRAMtotal18GiB/temp80°C. RT es propiedad Claude: esta variante ALU no lo duplica.
