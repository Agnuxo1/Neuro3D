# Turno nocturno: capacidad GPU, Blender y RT

Autorización humana: trabajar coordinadamente hasta **30/09/2026 08:00 Europe/Madrid**
(06:00 UTC), sin cargas GPU simultáneas y objetivo de no dejar huecos mayores de
15 minutos cuando existan pruebas útiles, preparadas y seguras. No ocupar la GPU
con renders decorativos para aparentar actividad. Antes del cierre no iniciar
cargas que no puedan terminar; cortar solo procesos propios con plazo explícito.

## Reparto confirmado por Claude en tablón 21:21 UTC

- Claude: propietario de `.cognition/neuro3d/capacity/` (ya existe su
  `probe_optix.py`): backend Blender/RT y ejecución del banco de capacidad,
  baseline convencional. Confirmar qué está haciendo antes de duplicar código.
- Codex: `Blender/benchmarks/capacity_audit/`: contrato de comparación,
  validación independiente de evidencia GPU, oráculos de campos/energía,
  inspección de ruta RT y diagnóstico de dependencias. No tocar sus scripts.
- Ambos usan exclusivamente `gpuq.py run`; anuncian tarea y recursos en tablón.
  No reservar GPU toda la noche: cada job libera turno al finalizar. Jobs de
  hasta 10 minutos con límite y checkpoint; alternar cuando ambos tengan trabajo.
  Si el otro no tiene job listo, tomar el siguiente propio sin esperar permiso
  indefinidamente. No matar procesos ajenos ni eludir el detector de carga externa.

Claude propone además render de multiplicador INCOHERENTE Cycles/OptiX:
mantenerlo como variante adicional, no reemplazar la arquitectura coherente.
Modo `cells` usa suma CPU tras render y es parcial; modo `integrate` requiere
auditar que la integración sea del propio render y su error estadístico.
Ni color ni render RT prueban interferencia de ondas.

## Gates antes de llamar a algo capacidad de nuestra arquitectura

1. Backend disponible: Blender identifica RTX 3090 / OptiX y ejecuta una sonda
   acotada. Esto SOLO demuestra render RT disponible, no inferencia de la red.
2. Ruta RT funcional: intersecciones de la geometría de escena ocurren en backend
   hardware RT, con evidencia de dispositivo/API/código y readback de impactos.
   `scene.ray_cast` más un render OptiX NO satisface este gate.
3. Campo en GPU: registro de acumulación compleja y detección ejecutadas en GPU,
   propiedades/geométricas procedentes de escena reabierta; sin intensidades
   precalculadas ni Python sumando interferencia durante la inferencia medida.
4. Correctitud: comparar campos de todos los puertos, energía y superposiciones
   1+1/1+i con oráculo independiente. Fase/lambda/espejo/sham/escape causal.
   Para primer prototipo usar límites del smoke (campo 2e-3, potencia 1e-4),
   sin relajar tras medir; cambios de contrato se registran como nueva versión.
   Ortogonalidad de fuentes/puertos requiere justificación geométrica, no IDs.
5. Escalar SOLO backend que pasó correctitud. Si RT no llega a estar integrado,
   informar resultados separadamente (render RT, CUDA/GLSL, matriz y CPU híbrido)
   y dejar la prueba RT de arquitectura como no conseguida, no sustituirla en secreto.

## Comparación de capacidad y seguridad

Congelar antes de medir cada variante: topología, profundidad, precisión,
tamaño de lote, inferencia vs entrenamiento, tolerancia, semillas e inputs.
Informar neuronas/canales/MZI/conexiones/parámetros por separado; NO equivalencia
1:1 por nombre. Mismo presupuesto y, cuando sea posible, misma operación/precisión.
Una matriz lineal no equivale en funcionalidad a un MLP no lineal.

Medir memoria pico asignada/reservada/dispositivo, tiempo kernel y extremo a extremo
(exportar, BVH/retrazar, compilar, transferir, lanzar, sincronizar, leer), warmup,
mediana/p95 y muestras/s. La capacidad incluye resultado correcto, no solo reservar
memoria de nodos. Tamaños crecientes con búsqueda acotada; reportar mayor probado
estable y primer rechazo por memoria/tiempo/precisión, no un máximo teórico.

Cap inicial: **18 GiB de VRAM total usada**, mantener >=4 GiB RAM disponible,
temperatura GPU <=80 °C, timeout <=600 s/job y cierre absoluto 06:00 UTC.
Si uso externo o memoria impiden esos márgenes, esperar cola y registrar causa;
no forzar colapso, no probar deliberadamente un reset del driver ni subir TDR.
Ninguna carga larga sin reserva/checkpoint; instalar dependencias solo en D:/E:,
sin aceptar licencias/registro de SDK sin autorización específica.

## Continuidad

Heartbeat cada 5 minutos revisa progreso y GPU: prepara/ejecuta unidad útil si
hay margen. Si GPU lleva >10 minutos libre y no hay job validado listo, prioriza
el siguiente smoke/profiling real pendiente; si >15 min sin acción segura,
documenta el motivo y notifica si requiere intervención, sin trabajo artificial.
Al llegar 08:00 Madrid: no nuevas cargas, verificar procesos propios finalizados,
informe de resultados y límites, pausar el seguimiento nocturno hasta nueva orden.
JEV bloqueado por revisión de seguridad: decisiones locales identificadas;
no eludirlo ni atribuir provenance=jev sin respuesta remota verificada.
