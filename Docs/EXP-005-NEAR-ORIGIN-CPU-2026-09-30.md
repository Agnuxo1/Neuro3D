# Rechazo del intervalo cercano: referencia y contrato CPU

Preparación NO integrada. Después de confirmar F5, se añadió una referencia
racional pequeña que conserva intersecciones firmadas, incluidos t=0 y t<0,
antes del filtro. No cambia el corte congelado t_min=1e-9 ni el trazador anterior.
No ejecuta GPU, Blender, campos de red, entrenamiento o código de Claude.

El candidato aborta si el intervalo declarado [t-e,t+e] puede intersectar
(0,t_min]. Los dos gaps problemáticos 5e-10/1e-9 abortan; los controles2e-9/1e-8
pasan SOLO este criterio cuando e=0. Tres consultas representadas del objeto
plegado A→B→A también pasan, sin veto por identidad. No es equivalencia nativa.

La incertidumbre es obligatoria y no se sustituye silenciosamente por cero.
Una muestra con e=1.1e-9 aborta, incluidos impactos de partida cuyo intervalo
cruza0. Esto expone posibles falsos rechazos, no demuestra un guard robusto general.
La cota e todavía NO se ha derivado de transporte/Bpy/cálculo GPU.

Ocho testsPASS0,015s: parámetros racionales de planos, fronteras/signos,
incertidumbre obligatoria/inválida, control plegado, paralelo vs coplanar,
degeneración/bounds y no mutación. Máximo8triángulos/64vértices y componentes
acotadas1e6 para esta referencia. No elevar el dominio de la arquitectura.
El parámetro exacto corresponde al rayo numérico suministrado, no longitud/fase
de una propagación física certificada. Pertenencia triangular estricta exacta
NO certifica la tolerancia barycentrics del shader.

Report D:/PROJECTS/.cognition/neuro3d/exp005_near_origin_cpu_20260930_0908.json
SHA `f527df7998b6f74db44c8f1d1c87c00b41496cafb46e2dd6494f446d9b221167`;
catorce hashes de código, casos e intervalos racionales completos retenidos.
Contrato prospectivo: coordinacion/experimentos/EXP-005-NEAR-ORIGIN-PREPARACION.md.

Pendiente: crítica005, intervalos demostrados de cálculo nativo y barycentrics,
partida/identidad/snapshot, flags por rama y fields/ledger/gates completos. La
referencia CPU puede definir pruebas falsables, no reemplaza inferencia desde
escena con cálculos CPU ni justifica velocidad/ventaja. JEV bloqueado/fallback local.
