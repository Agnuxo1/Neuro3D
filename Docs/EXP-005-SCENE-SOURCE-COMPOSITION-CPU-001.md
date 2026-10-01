# Error de fuente antes de coeficientes y fase, contrato solo CPU

P1 / SCENE-SOURCE-COMPOSITION-001-CODEX. Nueva capa opt-in sobre el productor
ideal congelado; no reemplaza ningún runner/shader/contrato existente. El
productor recibe una NUEVA escena: solo field_reim se reconstruye con el
split hi-lo y el modelo CPU64. Geometría, direcciones, óptica, lambda y
referencias siguen siendo los valores originales representados. No se
repiten la suite antigua ni barridos PRECISION005/006.

El resultado conserva dos bindings distintos: escena original (referencia
del error final) y escena con amplitudes decodificadas (entrada real del
productor). También conserva el SHA del payload del productor, palabras
uint32, IDs de ruta/fuente/puerto y cada componente de la cota.

## Contrato de composición

Para cada fuente s, delta_s es la normaL1 del error exacto de reconstrucción
hi-lo CPU de su campo. La escena ideal admitida es pasiva: cada transmisión
o reflexión de splitter tiene módulo sqrt(T) o sqrt(1-T), con T en[0,1];
espejos y fase son factores unitarios. Los modos terminales son ondas planas
unitarias. Por tanto, para C_p el coeficiente complejo ideal de una ruta:

`|C_p| <= 1`

`error_L1(ruta por transporte fuente) <= sqrt(2)*delta_s <= 2*delta_s`

La nueva cota por ruta es la cota del productor contra la escena decodificada
más2*delta_s, comprimida solamente hacia arriba al ABI racional congelado.
Se recomponen reducción32 e intensidad con el compositor existente y los
mismos gates1e-4/2e-4. No se acredita cancelación entre fuentes, no hay ganancia
activa ni proyección de modo no unitaria, y no se corrige fase de geometría
o lambda transportadas. Este factor conservador no es un error GPU medido.

El gauge de la cota se vuelve a identificar con el binding ORIGINAL: es una
rebase deliberada y explícita, válida aquí porque solo cambia amplitud de
fuente, no coordenadas ni referencia/phase gauge. No se mezclan payloads.
La aceptación CPU requiere conjuntamente presupuesto absoluto/relativo de
TODAS las fuentes y gates de campo/intensidad recompuestos.

## Evidencia

Seis tests PASS, rc0, 0,3029505s, un hilo/hijo60s. Seis pins congelados
verificados. Tres escenas originales se leen del artifact retenido, pero
las ejecuciones son NUEVAS amplitudes decodificadas, no replay de su productor.
Los oráculos racionales originales encierran error de campo y potencia de
la nueva salida. El caso de campo alto conserva rechazo de intensidad.

Dos fuentes casi oscuras reciben cargas2^-54 y3*2^-54 por ruta, separadas.
Presupuesto de fuente0 rechaza incluso si pasan los gates terminales.
Fuente2^-150 colapsada también rechaza por error relativo100%, aunque pase
el presupuesto absoluto terminal. Los FAIL numéricos esperados se conservan.

Una entrada NUEVA de MZI pasivo, amplitud.1 en lugar de1, regenera13 registros
y4 rutas sin usar el ledger suministrado por la fixture. Contraste racional
independiente: Dx=-i*.1 y Dy=0. Entrada del usuario intacta tras la llamada.
Salida subnormal2^-149 sigue rechazada por el productor normal-or-zero;
T=1,01 rechaza, no se amplían perfiles/bounds/conf1 ni se cambia un gate.

## Límites y continuidad

Sin Blender/GPU/RT, autenticación, óptica física, ejecución de writers ajenos
o publicación. No certifica transporte de geometría, autointersección/huecos,
longitud/referencia/lambda, fase GPU/libm/FTZ/RN/FMA, detección nativa ni la
causa del FAIL0337. Native promotion y execution_authenticated siguen false.

GPU ocupada por holder ajeno FIL-ENS3 observado al reanudar; no se tocó cola.
Fallback local sin aval JEV y sin reintentos. Skills de implementación y
cognition mantuvieron contratos separados y reutilizaron oráculos retenidos.
Boards/checkpoint locales sin stage; solo versionar los cuatro archivos propios.

Claude: acuse por ID/SHA; mantener petición de limbs/bindings/semántica
efectiva YA existentes de0337, sin nuevaGPU/suite/barrido/guardreview.
Siguiente requisito distinto: contraste de entradas geométricas y
referencias transportadas dentro del contrato de escena, con evidencias
existentes o nueva unidad CPU justificada; no promover este modelo a nativo.
