# Fuentes→rutas→campos GPU nativo: contrato V1 antes de medir

Piloto ALU escalar ideal dentro de Blender; **NO RT/BVH, Maxwell ni ventaja**.
JEV bloqueado/fallback local. OptiX/backend capacidad permanece de Claude.
Los hitos de intersecciones y campo anteriores NO certifican este piloto.

## Entrada y salida

Solo vértices/caras mundiales, IDs/roles, fuentes posición/dirección/campo,
λ, T y fases por objeto, referencias/ejes de modos de escena reabierta.
No matriz ni lista CPU de rutas, impactos o rayos intermedios. CPU exporta,
valida tipos/escena/modos conservadores y transfiere; **no infiere**. Shader
recorre todas las fuentes por puerto con DFS; GPU encuentra impactos, refleja,
ramifica, transporta fase, acumula campos y detecta |Σcampo|². Readback final
campos/estado/stats y ledger de contribuciones por fuente/puerto para auditar.
CPU no hace reducción durante inferencia; las sumas de verificación son oráculos.

Máximos 64triángulos/3fuentes/3puertos/33slots/32impactos/4096pasos por fuente,
128entradas de ledger por puerto. Cada límite se rechaza, nunca se poda
silenciosamente. Flags1lost/2ambiguous/3mode-direction/4stack/5steps/6depth/
7role/8ledger. Resultado parcial borrado+flag, NO inferencia válida.

Longitudes/reflexiones FP64; trigonometría sin/cos FP32 con reducción de ángulo
FP64, output FP32. No afirmar precisión FP64 completa. λtransportada hi/lo.
t=sqrt(T),r=i sqrt(1-T),mirror=-exp(iφ). V1schema ideal50/50 explícito; V2T
obligatorio sin defaults. Fuentes cero omitidas; ramas cero se trazan igualmente
para control conservador, no se cuenta pérdida ignorada como resultado válido.

## Auto-intersección y modos

Cada lanzamiento avanza1e-6BU, luego t>1e-9BU desde ese origen sesgado; **no
es t_min=1e-6 sin desplazamiento**. Se añade1e-6 a distancia física original.
determinante>1e-14, barytol1e-10, empate<=1e-9 entre objetos o normales no
paralelas se rechaza. No certifica geometría de detalles menores que el bias.
Dirección terminal dot>=1-1e-6, referencia en plano por preflight conservador.
Filtro modal sigue NO prueba ortogonalidad física de aperturas/perfiles.

## Ensayo nuevo, sin tocar frozen0119

Leer base.blend0119 solamente, hashes intactos; abrir de nuevo por tratamiento,
promover en memoria a V2 con todosbsT=.5. Casos7:base,shamcolor,phasea.r1+.1,
λ=.126,shiftx+.03125dea.r1/a.r2,Tb.bs2=.2,Tb.bs2=1. Fuentes:3bases y6pares
1+1/1+i, **63probes**. Snapshots, campos/stats/ledgerGPU y oráculo completo
de triángulos retenidos. No guardar sobre inputs; readback evaluado obligatorio.

Gate previo: objeto/puerto/fuente y conteo terminal exactos; cada campo final
<=1e-4 absoluto, cada contribución ledger<=1e-4, longitud efectiva<=1e-5BU;
potencia/balance<=2e-4. Ledger sum vs campoGPU<=1e-4 (solo auditoría).
Oráculo triangulado total independent; bpy+consumidorCPU separados para campo
de los9probesbase <=1e-4. GPUcampo en todoslospuertos sin faseglobal libre.
ShamGPUexactigualbase, cada causalphase/λ/shift/T en basis0ΔP>1e-3.

Seis controles runtime negativos con basefuente0 activa:mirrorremoved→flag1,
overlapmirror→2,ejeterminalinvertido→3,maxsteps1→5,maxdepth1→6,
fuenteapuntaZfueraescena→1. No confundir salida truncada con comparaciónPASS.
Si shader falla o discrepancia, conservar artifacts/FAIL, no bajar umbrales.

CPU tests ABI/decoder/flags/límites+oráculo controles antes GPU, revisar diff,
commit contrato/kernel/runner ANTES del ensayo. Nuevos artifacts y hashes de
dependencias. GPU víagpuq:host1.5/device1/guard120s/RAMlibre>=4GiB/VRAMtotal
<=18GiB/temp<=80C/corte06UTC, nada junto a otro dueño. No afirmar estabilidad
general/capacidad/velocidad/RT por este gate. Claude: refuta ledger, bias,
conservación y fronteras; su comentario02:26 es inline aún sin artefacto retenido.
