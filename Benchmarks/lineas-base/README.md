# Lineas base con igual numero de parametros (P0-4)

Estado: ejecutado segun el preregistro `PREREGISTRO-P0-4.md` (commit 5fbed71, publicado antes de ejecutar). Extension con mas semillas: exploratoria, post hoc. Auditoria independiente: cifras reproducidas con diferencia 0.

## Resultado primario (preregistrado)

| Conjunto | Optico | Lineal (15 coef.) | Cuadratica (45 coef.) | Optico menos lineal | Optico menos cuadratica | Clasificacion |
|---|---:|---:|---:|---|---|---|
| Iris, 10 particiones 120/30 | 0,9500 | 0,9467 | 0,9467 | +0,0033 [-0,0067; +0,0133] | +0,0033 [-0,0067; +0,0133] | equivalente |
| Wine, 10 particiones 141/37, semilla 1049 | 0,8622 | 0,8541 | 0,8622 | +0,0081 [-0,0054; +0,0243] | 0,0000 [-0,0108; +0,0108] | inconcluso frente a lineal; equivalente frente a cuadratica |

Iris con la media de los 4 reinicios (en vez del mejor reinicio): +0,0017 [-0,0092; +0,0142], equivalente (`resultados/SENSIBILIDAD_IRIS.md`).

Ningun conjunto muestra superioridad del optico (Holm p = 1,0).

## Extension post hoc (exploratoria, decidida tras observar la particion k=0)

Wine con tres semillas de inicializacion (1049, 1050, 1051), promediadas por particion:

| Modelo | Media | Diferencia frente a lineal | Diferencia frente a cuadratica |
|---|---:|---|---|
| Optico (3 semillas) | 0,7910 | -0,0631 [-0,0838; -0,0414], Holm p = 0,0039 | -0,0712 [-0,0910; -0,0486], Holm p = 0,0039 |

Sensibilidad a la semilla: 1049 da 0,8622; 1050 da 0,8270; 1051 da 0,6838. La desviacion media entre semillas dentro de una particion es 0,096.

## Lectura

- **Iris:** el optico es estadisticamente equivalente a las lineas base de igual numero de parametros. No hay evidencia de superioridad.
- **Wine:** el resultado primario depende de la semilla. Con tres semillas el optico queda por debajo de ambas lineas base. El resultado primario ("equivalente a la cuadratica") es optimista y no debe citarse sin la extension.
- **Conclusion:** no se demuestra que el optico iguale a las lineas base en Wine de forma robusta a la inicializacion, ni que las supere en ningun conjunto.

## Limitaciones

- Wine usa 4 de 13 caracteristicas; Iris tiene 150 ejemplos. Las conclusiones valen para este codificado y estos conjuntos.
- Las 10 particiones se solapan entre si; los IC subestiman la incertidumbre. Con 10 particiones, Wilcoxon tiene poca potencia.
- Wine: el plan de respaldo redujo el analisis primario a una semilla, porque el entrenamiento completo superaba marginalmente 6 minutos de CPU.
- Los hiperparametros del perfil se fijaron con resultados observados en un intento previo sobre la particion original.
- El modelo guardado de Iris (`trained_lattice.json`) no se reproduce exactamente con `train(seed=0)` en esta maquina. La reproduccion exacta se comprobo en esta maquina (numpy 2.2.6, scipy 1.15.1).

## Archivos

- `PREREGISTRO-P0-4.md`: protocolo fijado antes de ejecutar.
- `INFORME-EJECUCION.md`: desviaciones, tiempos de CPU y auditoria.
- `resultados/RESULTADOS.md` y `.json`: analisis primario.
- `resultados/RESULTADOS_EXTENSION.md` y `.json`: extension exploratoria.
- `resultados/SENSIBILIDAD_IRIS.md` y `.json`: media de reinicios.
- `resultados/SHA256SUMS.txt`: hashes de todos los resultados (`verificar_hashes.py --check`).
- `auditoria/AUDIT-P0-4.md`: auditoria independiente de las cifras y del analisis.
