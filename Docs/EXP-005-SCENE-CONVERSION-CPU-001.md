# Conversión de campo desde escena: tres controles CPU exactos

Unidad independiente P1; productor `scene_field_producer_cpu_v1` del commit
b83b2ae permanece intacto. Escena nueva y pequeña: fuente a detector directo,
longitud 3 BU, lambda original 1/8 BU, 24 ciclos enteros, sin coeficientes.
El oráculo independiente es la **suma racional exacta de campos fuente del
snapshot**, no un ledger ni una cota aportados al productor. Todos los datos
son sintéticos CPU; no hay Bpy, GPU ALU, RT ni óptica física.

Se generan solo tres escenas, una vez cada una en las pruebas nuevas:

| Escena | Error de campo L1 exacto | Gates absolutos campo/potencia |
|---|---:|---|
| Fuente real 0,1 representada | 53687091 / 36028797018963968 | PASS/PASS |
| Fuente real 0,1 * 2^25 representada | 53687091 / 1073741824 (aprox. 0,05) | FAIL/FAIL |
| Dos fuentes coherentes 0,1 y -0,1+2^-30 | 2^-30, error relativo 100% | PASS/PASS |

En la segunda escena, el error **real del modelo CPU** de conversión excede
1e-4 y el error exacto de potencia excede 2e-4; no es únicamente rechazo de
una cota conservadora. La reducción tiene error cero: compensar la suma no
recupera bits ya perdidos al convertir el campo a binary32. El productor
carga esa conversión y rechaza correctamente el presupuesto total.

En la tercera, el campo ideal exacto es 2^-30 y la salida modelada es cero.
Cumplir gates ABSOLUTOS no acredita precisión relativa cerca de un puerto
oscuro; no se modifica el contrato ni se añade un umbral relativo posthoc.
El productor cuenta cuatro registros/dos terminales desde ambas fuentes.

Tres tests nuevos: control ordinario, fallo antes de reducción contra oráculo
exacto, y puerto casi oscuro. No se repite la suite anterior ni los barridos
PRECISION005/006; no se ejecutan writers ajenos. El reporte conserva snapshots,
words, cotas y errores como fracciones JSON exactas (no convertir enteros
grandes vía float/JavaScript al transportar evidencia).

Este alto campo es un contraejemplo pequeño **CPU sintético**, no permiso para
escalar cargas GPU ni un error de red nativa observado. Gates, source/geometry
profiles y fixtures congelados permanecen intactos. Sigue pendiente comparar
artifacts nativos ya existentes con iguales campos/IDs/métrica/reference/λ y
costes completos; no pedir otra carga para rellenar esta evidencia. Fallback
local sin aval JEV; ningún push, merge o publicación.
