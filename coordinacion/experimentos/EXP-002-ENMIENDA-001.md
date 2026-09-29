# EXP-002 · Enmienda 001, antes de cualquier ejecución Blender

Fecha: 2026-09-29. Complementa, sin ocultar ni reescribir,
`EXP-002-PREINSCRIPCION.md`. Ninguna corrida EXP-002 en Blender/GPU se
había iniciado cuando se adoptó. Se conservan los dos objetivos, dominio
de `u`, paso, diferencias finitas y umbrales originales.

## Motivo verificable

La revisión independiente `respuestas/EXP-002-REVISION.json` reprodujo en
el motor CPU que `P_A(u)` coincide con `sin²(πu/2)` a 7,2e-14. Un evaluador
defectuoso que **ignora los objetos** y devuelve esa fórmula pasa las dos
carreras, el control de geometría congelada y el de coherencia nula. El
éxito numérico anterior no distingue escena real de atajo.

## Gates adicionales, fijados ahora

1. **Control sham causal.** Restaurar A. Ejecutar el mismo optimizador y
   ambos objetivos, pero asignar `u` solo a una edición que debe ser
   ópticamente nula: trasladar el empty del combinador
   `0,3u·(1,1,0)/√2 BU` en el plano de BS2, con M1 y todas las
   propiedades ópticas fijas. Ni 0,75 ni 0,25 deben converger en
   ≤50 actualizaciones. Registrar status, solape y balance en cada
   evaluación. Si la versión Blender pierde alineación o cambia potencia
   de forma relevante por redondeo, el control falla y se informa; no se
   reetiqueta como éxito. En CPU el motor honesto no converge, mientras
   que la fórmula filtrada converge en ambos casos.
2. **Vínculo final objeto–parámetro.** Al guardar y reabrir cada escena final,
   la traslación mundial de M1 y la del grupo del combinador deben ser
   iguales a las de A más `u_final` por los respectivos deltas de
   `B-geo`, con error euclídeo ≤1e-6 BU por objeto. El resultado óptico
   retrazado desde la escena reabierta debe quedar a ≤1e-9 del último
   `P_A` registrado para `u_final`. Esto evita aceptar un archivo
   persistido en la posición `u+h` de una sonda.
3. **Trayectoria visible, diagnóstico no gate nuevo.** Conservar la secuencia
   completa de `u`, `P_A`, `P_B`, escape, status, solape y balance para
   cada evaluación, incluidas las sondas de gradiente; comparar con una
   trayectoria CPU calculada antes de Blender. No fijar por ahora un
   umbral paso a paso: JEV tuvo confianza 0,38 al elegir el gate mínimo y
   la cuantización float32 aún no se midió en este bucle.

Ningún error o excepción autoriza guardar como resultado válido la última
sonda. El ejecutor debe registrar el último `u` evaluado y conservar
artefactos parciales en fallo. La validación del contrato por Claude y estas
enmiendas no sustituyen autorización ni comprobación de recursos para una
corrida real. Un resultado exitoso seguirá siendo un **bucle de calibración
geométrica de una celda**, no una red neuronal.
