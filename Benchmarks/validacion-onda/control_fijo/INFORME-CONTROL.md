# Informe · control P1-7 con dispositivo fijo (lambda/16, n = 2,484992)

Preregistro: PREREGISTRO-P1-7-CONTROL.md (no editado). Scripts: run_control.py, analisis_control.py.

## Resultado
- E_max(16, fijo) = 0,0266 (k = 0, puerto P1). E_max(24) = 0,0275 (JSON: 0,02752). Diferencia = 0,0009 < 0,005.
- Decision del preregistro (H_c): la convergencia con dispositivo fijo queda SOSTENIDA, con dispositivo no calibrado en lambda/16 (|r|^2 = 0,583; el modelo usa r y t del propio solver). Solo comprueba la estabilidad numerica de E_max entre mallas.
- E_max(16, fijo) supera 0,02, igual que E_max(24). No se usa como apoyo a la refutacion de H0: P1-7 exige divisor calibrado (< 0,005) y aqui lo esta solo lambda/24.
- Mismo indice n = 2,484992; |r|^2 = 0,583 en lambda/16 frente a 0,497 en lambda/24, asi que el divisor no es el mismo.
- Referencia: E_max(16, n recalibrado 2,426975) = 0,0269. Que el cambio de n apenas mueva el error es consecuencia del diseno (r y t salen del mismo solver y n), no un hallazgo.

## Calculo
- n = 2,4849920711630684 (n_usado de lambda/24); 12 posiciones k = 0..11 de mzi_fdtd_16_k00..k11, con los mismos pasos (4560) y celdas.
- Se llama a mzi_fdtd.simular sin modificar. r y t del modelo: rt_fdtd (calibracion_fdtd.py) en lambda/16 con ese n, referidos al plano medio.
- E_max con resumen_malla de analisis_validacion.py (importada). Resultados en resultados/ (JSON por punto, RESULTADOS_CONTROL.json/.md, SHA256SUMS.txt).

## Calibracion con n fijo en lambda/16 (sin ajuste)
- |r|^2 = 0,58322 y |t|^2 = 0,41685; diferencia con 0,5: +0,0832 / -0,0832 (> 0,005).
- Dispositivo marcado "no calibrado en lambda/16". Se reporta igual, segun el preregistro.

## Desviaciones (menores; ninguna cambia E_max)
- analisis_control.py (l. 26-28) rellena campos (P1_modelo_dif, pico_memoria_gb = 0, t_por_paso) para poder usar resumen_malla.
- analisis_control.py (l. 17) fija E24_REF = 0,0275 (JSON: 0,02752); la diferencia es 0,0009 con ambos.
- run_control.py (l. 50-51) reutiliza una calibracion en cache (calibracion_n_fijo_16.json); recalculada en la auditoria da r y t identicos.
- Salidas intermedias de simular en D:\PROJECTS\.cognition\neuro3d-audit\p1-7\control\tmp.
- CPU 7536 s en las 12 simulaciones (2 procesos, unos 600 s cada una frente a 323 s del original; la "carga distinta" es una explicacion no medida) y 11,8 s de calibracion.

## Limitaciones adicionales
- E_max mide coherencia entre modelo y solver, no fidelidad del divisor. Con r y t de un divisor 50/50 el E_max sube a 0,0543; con el dispositivo recalibrado del P1-7 original es 0,0269.
- Hipotesis a comprobar, no hecho: la perdida del solver (2,5-3 %) puede explicar gran parte del nivel 0,027 que se compara entre mallas, porque el modelo no tiene perdidas.
- Un solo n y los mismos 12 puntos de malla. E_max esta dominado por k = 0.
- El divisor depende de la malla: |r|^2 = 0,583 en lambda/16 con n fijo frente a 0,497 en lambda/24.
- El error de calibracion de 0,083 indica que con este n la pelicula en lambda/16 no es un divisor 50/50; la prueba no es un divisor calibrado.

## Integridad (SHA-256)
- mzi_fdtd.py c34ec1dc...ada666; analisis_validacion.py 26f49ee8...65bf0 (completos en RESULTADOS_CONTROL.json); coinciden con HEAD.
- fdtd2d.py, archivo de trabajo (CRLF): 34f62ef6935ae6a6981cd1032c7150829e37fa42193fc660dba685e7140f64fa.
- fdtd2d.py normalizado a LF (coincide con el blob de HEAD): d414e102039ac40052f37b1f7dad71a30531961c6041bf7f0ca659fc90e49ba6.

## Origen de las cifras (trazabilidad)
- 0,0543 (E_max con r y t 50/50): `resultados/verificacion_c4.json`, casos, caso B = 0,054283 (solver n fijo, modelo con r y t recalibrados).
- 0,0269 (E_max del dispositivo recalibrado): `resultados/verificacion_c4.json`, campo E16orig = 0,026926 (caso D, original P1-7).
- 0,497 (|r|^2 en lambda/24): `../calibracion_fdtd_45.json`, mallas.24.pasos[0].R = 0,497023 (tambien mallas.24.solver.R). El 0,583 de lambda/16 sale de `verificacion_c4.json`, campo R = 0,583216.
- `verificacion_c4.py` es copia de la auditoria; recalcula |r|^2 con FDTD (rt_fdtd), por lo que no se re-ejecuto: `verificacion_c4.json` es la salida existente de la auditoria.
