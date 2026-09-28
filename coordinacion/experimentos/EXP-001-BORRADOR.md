# EXP-001 · Borrador de contrato para interferencia de dos caminos

Estado: **BORRADOR, NO EJECUTABLE**. JEV autorizó redactar el contrato mientras
Claude audita el modelo; no se fijan aún las ecuaciones de combinación ni los
umbrales numéricos. Antes de ejecutar habrá que convertir este borrador en una
preinscripción cerrada, con revisión de Claude y decisión de JEV.

## Pregunta e hipótesis

¿Puede una escena Blender con dos caminos ópticos modificar la salida de una
neurona receptora mediante la fase relativa, manteniendo fija la potencia total
inyectada y el resto de parámetros?

Hipótesis provisional: con dos caminos declarados coherentes, cambiar solo la
fase relativa altera la potencia detectada. Con caminos declarados incoherentes,
ese mismo cambio de fase no altera la suma de potencias. Romper geométricamente
un camino debe reducir el circuito al control de un solo camino.

## Baseline y variable principal

- Baseline confirmado: EXP-000, un camino reflejado en Blender 4.5.14,
  intensidad detectada `0,7053474966`, activación `0,3657724623`; ver
  `Docs/BLENDER_RUNTIME_REPORT.md`. Estas cifras no son directamente
  comparables con dos caminos si se cambia la potencia inyectada.
- Baseline comparable futuro: escena de dos caminos con uno bloqueado, mismo
  emisor, presupuesto total de potencia y receptor. Debe reproducir el trazado
  monorrayo del camino restante dentro de una tolerancia por fijar.
- Variable principal: fase relativa de un camino. Geometría, frecuencia,
  respuesta del detector, absorción y fracciones de potencia permanecen fijas
  entre los casos coherentes constructivo y destructivo.

## Datos, controles y métrica

- Datos: escena sintética mínima guardada en `.blend`, sin dataset externo.
- Control A: dos caminos coherentes, fase relativa inicial.
- Control B: misma escena y potencia, solo fase relativa desplazada medio ciclo.
- Control C: dos caminos marcados incoherentes; variar fase relativa no debe
  modificar la potencia total dentro de tolerancia.
- Control D: bloquear uno de los dos caminos moviendo o girando un reflector;
  debe coincidir con el control monorrayo comparable.
- Métrica primaria propuesta: potencia RGB total detectada por el receptor,
  registrada junto a potencia por canal y fase. Registrar también activación,
  potencia de entrada y balance de todas las salidas modeladas.
- Métrica de seguridad: ninguna salida NaN/Inf; potencia de salida total no
  superior a la potencia disponible tras pérdidas, según una contabilidad
  explícita aprobada antes de ejecutar.

## Presupuesto y parada

- Primera validación: Python CPU, un proceso corto y sin Blender.
- Gate posterior: Blender background con un hilo, prioridad baja, RSS máxima
  1,5 GiB, RAM libre mínima 2,5 GiB y 45 s por fase, como EXP-000.
- GPU, render, CUDA y shaders de cómputo: cero.
- Parar si falta margen de RAM, se excede el presupuesto, se observa energía
  imposible o no se puede distinguir el caso incoherente del coherente.

## Promoción y decisiones abiertas

Promocionar el prototipo solo si los cuatro controles pasan en CPU y en una
escena Blender guardada/reabierta, con parámetros recuperados de los objetos
de escena y resultados reproducibles. Comparar el baseline monorrayo y
registrar cualquier discrepancia. JEV decide la promoción con evidencia,
no por consenso entre agentes.

Pendientes antes de cerrar el contrato: definición de amplitud/fase por canal,
criterio de coherencia, divisor de potencia, salidas no detectadas, tolerancias
numéricas y umbral cuantitativo de los controles. `OPT-001` debe revisar estos
puntos. Cualquier resultado previo al cierre se etiquetará exploratorio.
