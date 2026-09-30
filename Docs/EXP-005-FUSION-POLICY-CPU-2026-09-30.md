# Contraste independiente de la política de fusión V2

Contrato del contraste CPU (antes de ejecutar): dos MZI sintéticos representados
en binary64, MB desplazado 2^-31 BU, dos fuentes con amplitudes 1 y 0,6+0,8i.
Longitudes de onda 2^-17 y 0,125 BU, ambos órdenes del lote mixto y control
monoescena de 0,125. Tres políticas explícitas; nueve ejecuciones pequeñas.

Se regeneran árboles propios completos y campos con reducción racional de fase.
Comparación por fuente/puerto: gates originales 1e-4 y 1e-8, sin relajarlos.
La suma coherente y la potencia incoherente se registran por separado. No
confundirlas ni atribuir las amplitudes aplicadas en Python al trazador.
La política estricta debe rechazar todo lote mixto antes de cualquier nearest-hit;
se registra el contador de llamadas, sin eliminar escenas silenciosamente.

Se importará únicamente la biblioteca pura revisada gpu_states_v2, SHA
506b13c9c6bb442d16d9be07b8508a79b01ded9dd4c87c261ac1af83849b426e.
NO se ejecutan los escritores/barridos de Claude. SHA de originales, respuesta,
artefactos retenidos y acuse anterior comprobados antes y después. Un hilo CPU,
hijo máximo 60 s, CUDA no inicializada. No Blender, GPU, RT, nueva cota uniforme,
readback float32 ni comparación de velocidad. JEV bloqueado: fallback local.

Los tests de regresión comprueban los FAIL científicos esperados; su PASS no
convierte esos gates numéricos en PASS. Una reparación parcial exige además
política explícita en el futuro launcher/manifest: el default V2 sigue fixed.
La cota angular, márgenes topológicos y error acumulado de fusiones permanecen
pendientes. No promover conf1 ni aumentar bounds con esta evidencia.
