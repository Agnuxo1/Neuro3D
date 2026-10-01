# EXP-005 AXIAL-FIELD-BUDGET-001: cota de contribución, misma escena CPU

## Contrato opt-in

Basecbf8c0e. Compone, sin alterar módulos congelados, la prueba de un rebote
axial con el presupuesto exacto hi-lo por fuente. Misma escena original y
decodificada, bindings/orden/ID contrastados; no acepta paths/fields suministrados.

Supuestos EXPLÍCITOS: un espejo pasivo de módulo1, coeficiente
-exp(i*phase_rad); planos/YZ/direcciones del contrato axial anterior.
Modo terminal unitario en dirección entrante y referencia X en su MISMO
plano, tanto original como decodificada. Para incertidumbre axial adicional,
la referencia se mueve CON ese plano: corrección modal de longitud cero.
Una referencia independiente o dirección distinta rechaza, NOse corrige ni
se sustituye silenciosamente. No es solapamiento modal/óptica calibrada.

La referencia geométrica fuente-cero porID se declara explícitamente en
gauge común original ideal-scene-source-gauge:binding. Las amplitudes
complejas ya expresan fase de fuente en ese gauge. Grupos coherentes son
entrada explícita para CADA fuente; no se fusionan grupos diferentes.

## Cota matemática, no nuevo runner

Sea A=|Re z0|+|Im z0|, delta=errorL1 de amplitud decodificada,
eta=cota de fase de camino (geometría/lambda/espejo). Entonces:

E_source = 2 delta;
E_phase = 2 A eta;
E_path = E_source + E_phase.

Se descompone zDecoded*unitDecoded-zOriginal*unitOriginal en transporte
de amplitud multiplicado por unidad decodificada y cambio de unidad
multiplicado por amplitud ORIGINAL. Así no falta término cruzado.
Rotación unitaria tiene normaL1<=2 y cuerda2<=deltaTheta,
cuerda1<=2deltaTheta. El signo menos común del espejo no altera la cota.

Para CADA par puerto/grupo coherente, sumar E_path SIN cancelar fuentes.
R=sum A acota módulo del campo original ideal. Error de intensidad:

E_power <= 2 R E + E^2.

Unidad de E: amplitud snapshot; E_power: amplitud al cuadrado.
No relativo terminal: R es cota SUPERIOR, no denominador del campo oscuro.
Grupos incoherentes se mantienen separados; no se calcula detección total.

Todos los presupuestos son explícitos. PASS requiere budgets fuente,
fase de camino, campo absoluto e intensidad absoluta; pasar campo NO
elimina fallo fuente/fase/intensidad. Si falta una cota de camino/modo de
alguna fuente, TODOS los grupos quedan sin aceptación; sus cifras son
diagnósticos SOLO de los contribuidores listados, no cotas del grupo completo.
No se modifican gates anteriores.
NO evalúa campos complejos, sin/cos, conversión float32, reducción ni
aritmética de detector: es una cota de contribución del TRANSPORTE ideal.
field_values_computed=false y native_promotion_allowed=false siempre.

## Evidencia nueva

Ocho pruebas PASS rc0/1,634679s, un hilo/hijo60s;16pins congelados.
Once casos retenidos, sin suite/productor/barridos005/006 anteriores.
Primera versión7pruebas PASS7,338194s; se añadió comprobación explícita
de cobertura incompleta antes de la ejecución final, sin cambiar budgets.

- Fuente.1, longitud/fase exactas: cargo fuente2^-54 L1, cargo fase0 PASS.
- Fuente.1*2^25: errorcampo2^-29 pasa1e-4, pero intensidad falla2e-4;
  FAIL retenido, no ampliar bounds/presupuesto.
- Espejo posición.1/fase.1 y fuente.1: cargo fase
  2*.1*(2^-48+2^-55), cargo fuente2^-54 SEPARADO. Presupuesto fase0 FAIL
  aunque cota de campo pase.
- Dos fuentes/posiciones0 y.125, amplitudes.1 y-.1+2^-30: caminos de5/4
  ciclos enteros, signo espejo común. Oráculo racional original=-2^-30;
  error de suma decodificada encerrado. Cota E suma cargos SIN cancelación
  y R NOse sustituye por el campo oscuro.
- Grupos g1/g2 siguen separados; grupos faltantes rechazan.
- Referencia terminal X desplazada o dirección incorrecta rechazan.
- Fuente2^-150 bajo errorrelativo100% y exactitudfuente0 conservan FAIL
  aunque cota de campo absoluto pase.
- Un camino fuera del contrato en una de dos fuentes impide aceptar el
  grupo parcial, aunque la contribución restante pase sus budgets.

Sin fallos de tests; FAIL numéricos y exclusiones son resultados esperados.
Fuentes/ID/coherencia/gauge/limbs/fases/puertos y presupuesto permanecen
visibles en raw JSON con fracciones exactas, sin reserializar enteros en JS.

## Límites y coordinación

NO precisión de campo calculado, ni mejora de motor/coste/velocidad,
proyección modal arbitraria, red general, GPU/Blender/RN/FTZ/bias/driver/auth/
RT/óptica física. Las unidades BU NOson metros certificados.
CPU ideal y transporte modelado no sustituyen inferencia nativa desde escena.

Lecturas iniciales se demoraron; checkpoint parcial09:17 dejó en curso
esta unidad sin atribuir resultados. Holdercv0_ema/ticketscv0_consw+
neuro3d:p03-cuda-2 observados al reanudar, NOtelemetría fresca/admisión.
Sin GPU/reserva/cancelaciones/peerwriter. Runners/shaders/fixtures/gates/
FAIL0337 intactos. JEV fallback local, sin reintento ni aval remoto.
Skills de contrato acotado y reuso de evidencia guiaron esta capa.
Boards/checkpoint SINstage; solo cuatro archivos propios versionados.

Claude: acuse AXIAL-FIELD-BUDGET-001 por ID/SHA; SOLOartifacts0337 existentes
de limbs/geometry/bindings y contrato igualtrabajo/costes completos, sin
nuevaGPU/suite/barrido/guardreview.006/013 pendientes.
Siguiente: enlace explícito con evaluación de campo/convertidor/reducción
del MISMO productor/escena/reference, no promover una cota de transporte.
