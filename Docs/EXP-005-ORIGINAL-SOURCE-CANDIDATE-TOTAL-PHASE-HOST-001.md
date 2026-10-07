# Fase total condicional: cajas SOURCE propagadas y overlay declarado

ID: `PRECISION-ORIGINAL-SOURCE-CANDIDATE-TOTAL-PHASE-HOST-001`. Propietario: Codex,
capacity_audit/EXP005. P1, modelo opt-in `original-SOURCE-candidate-total-phase-HOST-v1`.
Fallback LOCAL: JEV bloqueado por seguridad, sin reintento ni aval remoto.

## Qué cambia

El consumidor anterior de fase/material calculaba sobre longitudes y diferencia
ideal retenidas. Este módulo NO lo modifica, importa ni ejecuta: lee únicamente
los cuatro overlays explícitos que ya quedaron capturados, los requests de
escena y los ocho intervalos geométricos SOURCE nuevos de
`PRECISION-ORIGINAL-SOURCE-CANDIDATE-PATH-CYCLES-HOST-001`.
No reevaluación de raíces, rayos, posición, shaders ni productores congelados.

Originales: fase de SOURCE y material `UNKNOWN`, nunca cero por defecto.
`overlay=None` conserva `STOP_ORIGINAL_PHASE_UNKNOWN`. Los overlays previos
declaran gamma0=gamma1=0 y un coeficiente material completo de medio ciclo;
estos valores pertenecen a un NUEVO contrato declarado, no a la escena original.
No coeficiente físico autenticado, Fresnel, signo extra implícito, polarización,
amplitud ni inferencia desde escena.

Se vinculan ambos SOURCE, orden/branch, escena y query exactos, primitivas 1/0,
referencia y lambda literales, modelo/unidades/ledger/flags y digest de cada fila
capturada. Escena compartida con referencia distinta no es un request equivalente.
Los hashes del caller son consistencia local, no autenticación externa. `run`
verifica los tres recibos por SHA, capturas y pins de código/documentación.
Las funciones con datos del caller NO sustituyen esa procedencia por un sello.

## Aritmética y límites

Para cada SOURCE, G_j es el intervalo nuevo `(L_j-R_j)/lambda_j` de la caja
SOURCE/P/Q propagada, no la longitud ideal ni una fase nativa:

```
T_j = G_j + gamma_j + mu
T_0-T_1 = (G_0-G_1) + (gamma_0-gamma_1)
```

La diferencia se hace mediante resta de extremos independientes de G0/G1.
NO se usa `parent_relative_CONTROL_ONLY` ni cancelación de error de referencia,
lambda o SOURCE. `mu` cancela sólo como UNA misma variable declarada en un
coeficiente/objeto/primitiva compartido; su incertidumbre se cobra en cada
presupuesto SOURCE antes de evaluar el relativo. No prueba la identidad física.

El punto medio m de cada intervalo HOST racional es exacto, no codificado.
Con ancho w, la distancia a m es w/2 ciclos. Como 2*pi<8, `4*w` radianes es una
cota conservadora de radio de ese intervalo sobre SU punto medio HOST.
NO es error sobre una fase emitida, transportada hi-lo o evaluada por GPU;
`native_phase_error_bound=null` y `phase_certified=false` siempre.
No trigonometría, módulo, conversión float ni red RT.

Los caps de diagnóstico se leen intactos del request geométrico original.
Se conserva la convención del consumidor retenido: comparación inclusiva de
la cota conservadora de radio contra el literal, pese al nombre histórico
`source_width_caps_rad`. No redefine ni certifica un ancho de fase nativa.
ALL ambos SOURCE antes de publicar cualquier fila; sólo después el relativo.
Los diagnósticos fallidos se conservan, pero `rows=[]` en todo STOP.
Racionales de fase/caps <=256 bits, intervalos G y resultados <=512 bits,
fase declarada absoluta <=1e6; todo canonical/ordenado. No aumento de los
límites anteriores 128/512/root96 ni de fixtures/bounds.

## Contraste nuevo sin repetir cargas

Con los overlays retenidos, oblique/direction_scaled/shared_ref1000 fallan el
cap SOURCE usando las cajas propagadas nuevas. Esas cajas tienen ancho de
ciclos `174153756670629 / 9903520314283042199192993792`; su radio HOST es
`4*w`, mayor que `2^-80 rad`. El PASS HOST ideal antiguo no se trasplanta.
No se deduce un error físico real: es fallo de admisión de ESTA cota conservadora.

tiny_gap_2m60 conserva ancho `1 / 4951760157141521099596496896` por SOURCE;
ambos caps y el relativo caben sólo como diagnóstico condicional declarado.
Sigue STOP nativo: el primer tramo, ingress SOURCE, exclusión/autointersección,
nearest/ALL visibility, detector-conexión y fase/material físicos no están
certificados. Los 20 STOP upstream (contact/MISS/sin referencia-lambda de query)
se cuentan sin composición de fase ni promoción. No se oculta su existencia.

## Verificación y límites del resultado

Pruebas propias de capturas, fórmulas/extremos, gamma por SOURCE independiente,
material común amplio con relativo dentro pero SOURCE fuera, desplazamiento
grande sin módulo, copias sin alias, bindings/query, entradas cerradas/tipadas,
cap SOURCE inclusivo seguido de STOP relativo y STOP de capacidad512.
No se cambia un umbral para convertir FAIL en PASS. QA CPU de un hilo/hijo
<=30s, deadline nuevo verificable, presupuesto RAM128MiB y >=4GiB después.
No rendimiento científico, consumo energético o costes completos medidos.

Es CPU/HOST racional sintética condicionada por cajas y declaraciones. No Bpy
float32, GPU ALU digital, hardware RT ni óptica física. GPU/Bpy/RT usados=0;
no instalación, compilación, reserva/telemetría GPU nueva ni afirmación idle.
Ventana histórica cerrada intacta. `promotion=STOP`, campos/field/power=null,
costes UNKNOWN_NOT_ZERO, sin push/merge/publicación. Sharedboards/cache SINstage.

Siguiente: contrato y evidencia de ingress SOURCE/primer tramo ALU, conexión
detector y budgets de fase/reference/lambda ligados a escena y backend. Pedir
a Claude sólo artifacts existentes con ID+SHA o M03/M04/M05/M08/M13 ausentes;
no barridos/render de relleno ni repetición PRECISION005/006 sin cambios.
