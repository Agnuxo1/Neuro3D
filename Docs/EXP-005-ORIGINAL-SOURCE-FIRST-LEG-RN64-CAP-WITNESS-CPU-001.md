# Primer tramo RN64: testigo de límite de precisión, no fallo nativo

ID `PRECISION-ORIGINAL-SOURCE-FIRST-LEG-RN64-CAP-WITNESS-CPU-001`, Codex P1.
Modelo opt-in CPU. No ejecuta geometría, backends ni productores congelados y
no evalúa sqrt/isqrt/libm: selecciona el resultado RN64 mediante álgebra sobre
extremos binary64 adyacentes ya capturados y comparación del radicando con el
cuadrado del punto medio. En empates se demuestra la paridad ties-even.

El modelo anterior dejó abiertas hipótesis RN64/sqrt/FMA y presupuesto de
ingreso SOURCE. Esta unidad demuestra una limitación numérica de **ese modelo**:
en seis primeros tramos (oblique, direction_scaled y shared_ref1000 × S0/S1),
incluso un sqrt RN64 correcto tiene una discrepancia geométrica no nula cuyo
término aislado supera numéricamente la escala literal de 2⁻⁸⁰ rad. Pero ese
literal es un **cap de ancho geométrico**, no un presupuesto de error puntual
nativo. La comparación no es equivalente: no demuestra fallo del cap original.
Un resultado RN determinista tiene intervalo puntual de ancho cero y aun así
difiere de la raíz exacta. Certificar ancho o redondeo correcto no basta para
certificar exactitud; hace falta un presupuesto explícito del backend.

Entradas SOURCE/P singleton ligadas a escena/consulta/fila/primitivas y SHA.
Las 8 operaciones previas a sqrt son exactas en esos fixtures; se comprueban
componentes, cuadrados y sumas capturados, sin reevaluar sus grafos. Los dos
extremos adyacentes y sus cuadrados prueban qué binary64 queda más cerca de la
raíz. No se confunde RN con elegir arbitrariamente un extremo de un intervalo.

Para tiny_gap se escalan los dos candidatos de oblique por 2⁻⁶⁰, y se demuestra
otra vez su adyacencia y su bracket cuadrado contra el radicando tiny exacto.
Es una transformación dyádica, no un cálculo nuevo de raíz ni una equivalencia
de consultas. La rejilla geométrica capturada 2⁻⁹⁶ permanece sin cambios: allí
la cota del término aislado queda por debajo de esa escala, pero no prueba
exactitud nativa ni admisión del contrato completo.

Sea r el resultado RN seleccionado y L=[a,b] la raíz geométrica capturada.
El error firmado está en [r−b,r−a]. Su magnitud está entre δlo y δhi, con
δlo=0 si ese intervalo contiene cero. Como 6<2π<8 y λ>0, el término geométrico
aislado cumple `6·δlo/λ ≤ |Δφ_tramo| ≤ 8·δhi/λ`. Se usan λ y caps originales,
no una tolerancia nueva ni umbrales elevados para lograr PASS.

**Alcance limitado:** el cap SOURCE original limita ancho/radio geométrico
según el consumidor, NO error respecto de un resultado RN. Tampoco es una
asignación de presupuesto al primer tramo. Compararlo con este término es sólo
un diagnóstico de escala, no fallo de protocolo. No se ha demostrado
incumplimiento del cap de ancho ni del camino total:
otros términos pueden cancelar errores, pero no existe aquí una garantía de
esa cancelación. Fases SOURCE/material originales siguen desconocidas; no se
ponen a cero. No evalúa reducción/encoding de fase, referencia nativa, detector
ni óptica física. La identidad de un backend real sigue sin verificarse.

Resultado esperado: 28 filas, 6 errores del término aislado por encima de la
escala de ancho, 2 cotas tiny por debajo y 20 STOP upstream preservados. Los
ocho resultados RN singleton tienen ancho cero sin convertirse en error cero:
en los ocho se prueba r²≠q exactamente, incluso si la cota tiny contiene cero.
Todas mantienen
promoción STOP/native=false/GPU0/costes completos UNKNOWN; ingreso SOURCE y
presupuesto nativo de primer tramo null, no cero. QA de CPU 1 hilo/RAM128 MiB
dejando >=4 GiB/timeout30/deadline35 nuevo. No hay benchmark de motores.
Tests cubren paridad ties-even, raíz exacta, inputs negativos, ligadura por SHA,
cap lift rechazado y pin de captura incorrecto. Oráculo independiente verifica álgebra
y resultados capturados; no repite barridos ni raíces anteriores.

Claude: ACK por ID+SHA y artifacts EXISTENTES M03/M04/M05/M08/M13 o ausencia;
indicar ABI/grafo real SOURCE/primer tramo, prueba de redondeo/orden/FMA,
presupuestos de exactitud y tratamiento justificado del término, guard fail-closed
con deadline por job e igual trabajo/costes completos. Sin nuevas cargas de
relleno. Runners/shaders/fixtures/128-512/rejilla96 y caps intactos. JEV fallback
LOCAL bloqueado por seguridad, sin reintento ni aval remoto. Boards/cache sin stage.
