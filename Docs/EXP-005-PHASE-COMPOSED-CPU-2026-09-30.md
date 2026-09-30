# Composición condicional de precisión de fase ligada a escena (CPU)

## Resultado y alcance

Auditor retenido `PHASE-COMPOSED-001-CODEX`, 30/09/2026 17:12:50 UTC:
6 pruebas nuevas PASS en 0,5942 s, un hilo, hijo limitado a 60 s.
Cinco escenarios pequeños regeneran 13/26/26/13/13 registros y
4/8/8/4/4 caminos terminales desde fuentes y triángulos representados.
No leen historias precalculadas del fixture ni suministran caminos a GPU.

La nueva variante opt-in compone las cotas de longitud efectiva del trazador
CPU congelado, el transporte de longitud de onda y la cota racional puntual
de la aritmética de fase compensada. Esto NO certifica geometría nativa,
transporte hi-lo real de escena, acumulación GPU, sin/cos del driver,
coeficientes/fases de fuentes, modos físicos ni error nativo total.
`native_promotion_allowed` y `native_precision_certified` siguen false.
No hay prueba Blender, RT, rendimiento, energía ni ampliación a conf1.

## Contrato matemático

Para un camino, L pertenece a [Llo,Lhi], lambda pertenece a [wlo,whi]
con wlo>0. Frente a los valores representados L0,w0 utilizados en la traza,
d=max |Li/wj-L0/w0| en las cuatro esquinas. La desviación NO se reduce
módulo una vuelta: hacerlo en extremos puede esconder el interior.
La cota del fasor ideal es min(2, b_aritmetica + 2*pi_superior*d).
La envolvente lambda aquí es el valor original representado en la escena;
w0 es la reconstrucción del transporte hi-lo validado por el helper previo.
Las envolventes genéricas aportadas por otro llamante son condicionales:
esta función no autentica por sí sola su procedencia ni validez física.

Por puerto y grupo coherente: epsilon=sum(Ap*bp), A=sum(Ap),
error de intensidad <=2*A*epsilon+epsilon². Las intensidades de grupos
independientes se suman; sus campos complejos nunca se mezclan.
Las amplitudes ideales se acotan hacia fuera; no se podan fuentes/caminos.
Las decisiones usan Fraction y umbrales intactos: campo 1e-4, potencia 2e-4.

## Controles retenidos

- Una fuente y lambda=0,1: campo por puerto <=6,97574e-14;
  potencia <=1,39515e-13. Son cotas, NO errores GPU medidos.
- Dos fuentes idénticas: la cota de potencia coherente es exactamente
  cuatro veces la de una fuente; con dos grupos independientes, dos veces.
  La prueba exige una cota estrictamente positiva para evitar comparar ceros.
- F1 trasladado a la referencia de detector de una escena CPU: campo
  <=5,82819e-8 y potencia <=1,16564e-7, máximos de los dos puertos.
- L en [0,2], lambda=1: la envolvente debe permitir error 2 aunque
  los extremos tengan fase equivalente; tres intervalos inválidos rechazan.
- Lambda general ~1e-12 y longitud efectiva ~1e6 rechaza q>=2^52;
  no se declara reparado ese fallo ni se relaja el dominio del candidato.

La representación de geometría es sintética CPU, no readback Bpy float32.
Las referencias terminales pertenecen al modelo representado, no certifican
incertidumbre previa de exportación. Las fases de coeficientes y fuentes
se mantienen ideales e idénticas en ambos modelos comparados.

## Evidencia y reproducción

Ejecutar solo `Blender/tests/test_history_compensated_phase_budget_cpu.py`
con Python que tenga math.fma real, `-B`, un hilo y timeout de 60 s.
El reporte guarda opciones, binding de escena, ocho pins antes/después,
cuatro pins congelados del candidato/cota circular, cotas superiores
redondeadas hacia fuera y SHA del resultado completo y cotas exactas.
Los SHA permiten reproducir los racionales; el reporte compacto NO contiene
todo el ledger. Dos salidas previas truncadas no se usan como artefactos.

Se conservan candidato, trazador, presupuestos y shaders anteriores intactos.
JEV permanece bloqueado por seguridad: fallback local explícito, sin aval remoto.
GPU externa ocupada y RAM escasa: ningún Blender/GPU ni reserva propia.

Claude: incluir esta composición en la MISMA crítica opcional de fase,
si encuentra una omisión concreta o un contraejemplo de intervalo; sin
nuevo barrido/revisión de guard/carga. RT-CAP-006 mantiene prioridad.
Siguiente Codex: ligar datos/longitudes observados y referencia a un contrato
nativo separado antes de promover; no confundir esta cota CPU con GPU.
