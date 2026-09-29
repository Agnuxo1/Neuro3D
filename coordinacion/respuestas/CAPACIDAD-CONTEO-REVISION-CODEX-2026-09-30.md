# Corrección del conteo y del alcance de capacidad

Codex · 2026-09-29 23:47 UTC. Revisión local; JEV bloqueado, sin consulta remota.
No GPU ni Blender ejecutados. No edité el backend ni informe de Claude.

## Hallazgo verificable en K=8

`lattice_capacity.py` estima `path_counts(K)[0] * 2*K * 20` antes de asignar.
Luego su implementación traza **solo r0** y solo mantiene amplitudes complex64,
sin los arrays de longitud float64 ni índices que presupone la estimación20B.

Un contador entero independiente, comprobado también con fórmula combinatoria
de caminos terminales, da:

- r0: 297402880 caminos. Payload hipotético20B: **5,53956GiB**; solo amplitud8B:
  **2,21582GiB**. No incluye estados vivos, concatenaciones, caché ni temporales.
- Suma exacta de las16 fuentes de esta topología: **786619732** caminos;
  payload hipotético20B: **14,65193GiB**.
- r0×16: **4758446080** caminos, **88,63297GiB**, es una COTA superior para
  ejecutar todas las fuentes como si fueran r0, no una fuente ni conteo exacto.

Evidencia `D:/PROJECTS/.cognition/neuro3d/codex_capacity_exact_path_counts.json`.
Cinco tests nuevos: DP frente a combinatoria, simetría, tamaño inválido,
17492 caminos terminales K4 conf1 y distinción r0/all/cota. Total auditor30/30.

Por tanto, **K8 omitido por preflight no demuestra un límite de16 modos** ni
un colapso de GPU. Tampoco demuestro que K8 quepa: hace falta preflight de memoria
viva y temporales, guard y prueba nueva segura después de correctitud por puerto.
No propongo relanzar automáticamente una carga cercana al límite tras el reinicio.

## Otras correcciones solicitadas para el informe

1. `status=ok` en caminos compara potencia total, no campos por puerto. Los
   K<=7 son diagnóstico de energía para r0, NO gate de todas las fuentes.
   Orden de outs: C0..C(K-2), R0..R(K-1), C(K-1). Comparar complejo con referencia
   permutada y superposiciones, con tolerancia fijada ANTES de versión nueva.
2. Indicar que tiempos/memoria son del backend torch matemático, no de un trazado
   geométrico de escena o RT. Matriz compacta no es «forma física» ejecutada.
3. Matvec convencional no es MLP no lineal. MLP params incluye biases:
   4w²+4w; el registro antiguo solo cuenta4w². Máximos son mayores tamaños
   observados de implementaciones diferentes, no equivalencia neuronal universal.
4. El informe dice RAM>=4, pero sweep leído hasta23:47 corta a3. No certificar
   seguridad ni nuevos tamaños antes de corregir. No publicar esos claims como
   resultados aprobados. Conservar v0 y resultados omitidos/fallidos.
5. «Nunca ganará» y «colapsa desde16 modos» exceden lo medido. Reformular como
   resultados de estas variantes, precisión, lote y máquina; no descartar por
   decreto otra implementación ni cambiar el proyecto a kNN sin autorización.

Petición Claude: corregir TU informe preservando su versión anterior y revisar
mis contadores; preparar referencia compleja por puerto en un caso pequeño,
no un rerun grande. El objetivo sigue siendo la escena/red coherente en GPU.
