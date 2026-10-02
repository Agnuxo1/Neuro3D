# EXP005 — prueba exacta del singleton cero (HOST)

ID AXIAL-ZERO-SINGLETON-UNIT-HOST-001. Base 1d1adf8079862bfb512edb011025a25465fe7466.
Acuse SCENE-PARAMETER-DOMAIN-HOST-001, reporte SHA
c81d8e34b11d73db75470096f95bec6ca738cd08af030e3977da077bf4a9df97.

## Contrato y alcance

Opt-in axial-zero-singleton-canonical-HOST-Horner26-v1. API pública admite
sólo nombres de casos retenidos y modelo explícito. No admite resultados,
coeficientes, contextos, certificados ni cupos suministrados por el caller.
Los helpers internos sirven a controles negativos, no son certificados de escena.

Se leen 268 pins heredados; no se ejecutan productores, selectors, RN,
barridos PRECISION005/006 ni tests anteriores. Todos los inputs, orden de
fuentes, gauges, radios y cupos se enlazan con recibos SHA y buffers INPUT.
Sólo dominios axiales restringidos ya probados con YZ exacta y X compartida;
no geometría 3D general ni incertidumbre física.

Tres fuentes (negative/s, positive/s, two_sources/s) tienen imagen
representada [0,0], residual ORIGINAL cero, cuarto constante y cargos previos
de parámetro/argumento cero. La cota genérica Horner anterior sigue positiva
y su NONfit con cupo cero permanece sin modificar. Una NUEVA identidad
exacta restringida prueba error L1 y fase cero con EL MISMO cupo cero.
No es una relajación de umbral ni un arreglo de fallo numérico.

## Prueba

Para x=0, z=x*x=0. En cada etapa de Horner, h*z=0 y 0+c_j=c_j
exactamente representable. Finalmente cos=1 y sin=1*0=0.
Los coeficientes superiores no aportan error al resultado en este dominio.
Taylor en cero es exacto; la permutación por cuarto entero produce ±1/±0.
Se contrastan 26 identidades de cada recibo (ORIGINAL y cuatro esquinas);
la igualdad exacta en TODO el singleton, no muestreo, sustenta la prueba.

Limitación explícita: el productor HOST rationaliza los intermedios y
canonicaliza cero a +0. Seis multiplicaciones por grafo que IEEE-754 daría
como -0 quedan como +0 en el recibo. La permutación final sí conserva XOR
de signo, incluidos ceros. El valor matemático y los resultados finales
son exactos, pero NO se certifica equivalencia de todos los bits/signos
del grafo nativo. No se modifica el runner congelado para ocultarlo.

Flag NUEVO restricted_exact_unit_error_to_ORIGINAL_proved sólo en tres
fuentes y bajo ese dominio/modelo. Flags generales uniform_unit,
uniform_source, fullpipeline, native, signedzero-native, GPU, RT y
autenticación permanecen falsos. Las otras dos imágenes no cero quedan
sin refinamiento; 14 STOP heredados intactos, other/two_sources sin suma
parcial ni promoción del caso.

## Verificación y seguridad

Cuatro tests stdlib propios: auditoría completa, identidades, permutaciones,
37 rechazos fail-closed (palabras, bool, intervalo, coeficiente, traza,
operando, delta, ABI, ORIGINAL, cargo, cupo y SHA). Oráculo independiente
stdlib sin imports producción comprueba 272 pins y 390 identidades
retenidas; no redondea ni genera nuevos resultados de escena.
Captura completa, tiempos y hashes en reporte propio. CPU un hilo,
timeout duro 60s por hijo. Fallos se conservan si los hay.

JEV bloqueado por seguridad: fallback LOCAL explícito, sin aval remoto,
sin retry ni elusión. Sin GPU/Blender/SDK/DrJit/Kaggle/push/merge.
Boards/checkpoint locales SINstage. Sólo cinco archivos propios nuevos
versionados. Ventana histórica 0337 cerrada/deadline intacto; cargas
futuras exigirían reserva Claude, telemetría, guard fail-closed y nuevo
deadline/límites originales completos.

## Siguiente unidad

Cerrar error complejo de fuente y reducción/potencia uniformes conservando
el campo de ORIGINAL; no sustituirlo por U/GEMM. Pedir a Claude acuse ID/SHA
y únicamente artifacts YA existentes de backend/guard/certificado matching
INPUT/scene/ABI/source/gauge e igual trabajo/salida/costes completos.
No declarar velocidad, eficiencia, motor ganador, red RT ni óptica física.
