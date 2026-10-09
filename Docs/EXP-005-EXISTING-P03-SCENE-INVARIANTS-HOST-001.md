# EXP005 — Escenas originales frente al archivo P0-3 existente

ID: PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001. Codex, P1.
Fallback LOCAL: JEV bloqueado por seguridad; sin reintento ni aval remoto.

## Resultado y contrato

El archivo histórico de 104 escenas P0-3 no contiene ninguna de las cuatro
escenas originales retenidas en las mismas coordenadas BU, incluso ignorando
nombres, orden, orientación de caras y escala positiva de las direcciones SOURCE.
Hay 416 comparaciones HOST de entradas YA EXISTENTES, no nuevas trazas.

La ausencia de un hash idéntico por sí sola no probaba esto: los esquemas y
serializadores son distintos. Ahora se contrastan dos invariantes necesarios:

- Extremos por eje de la unión de triángulos no degenerados declarados.
  No depende de la triangulación, winding ni vértices no usados.
- Multiconjunto de rayos SOURCE ideales orientados, con posición exacta y
  dirección dividida por el valor absoluto de su primer componente no nulo.
  Conserva multiplicidad de canales; permite escala positiva, no invertir el rayo.

La longitud de onda se contrasta adicionalmente. Los racionales originales se
comparan con el valor exacto de las palabras binary64 del snapshot, no con una
aproximación decimal ni con una tolerancia. No se ejecuta la normalización NumPy,
ni se afirma equivalencia del cálculo nativo normalizado.

En las 416 comparaciones difieren tanto los extremos de superficie como el
multiconjunto SOURCE. El test conserva cada índice/hash del snapshot y los
resultados por invariante. El oráculo independiente usa separadores exactos en Z:
superficies originales [0,3] frente al archivo [-1/8,1/8]; SOURCE original Z=1/4
frente al archivo Z=0. No calcula impactos, raíces, fase ni trabajo de GPU.

## Implementación opt-in y límites

Nuevo módulo propio scene_necessary_invariants_HOST_v1.py. No modifica ni importa
código de Claude, contratos/runners/shaders congelados ni fixtures existentes.

MISMATCH refuta identidad de la escena declarada COMPLETA en ese mismo frame.
No refuta una subescena seleccionada, equivalencia tras transformación de
coordenadas ni un backend adaptado futuro: no se realizaron esas conversiones.
Tampoco invalida el PASS histórico P0-3 en SU dominio.

Los invariantes iguales NO prueban equivalencia: topology/materiales, agrupación
de primitivas, amplitudes SOURCE, detector, referencia/query y aritmética ALU
requieren su propio vínculo. Un control con superficies distintas pero el mismo
bbox sigue STOP. El método nunca admite GPU ni certifica un presupuesto de fase.

5 tests, 431 records: 416 comparaciones de archivo, 4 resúmenes y 11 controles
sintéticos/STOP. Reordenado/escala positiva permitido sin promover; dirección
invertida, canal duplicado y otra lambda rechazados; bool/NaN/dirección cero/
índice bool/esquema distinto/superficie vacía paran. No nuevas muestras físicas.

## Evidencia y siguiente paso

Recibo: coordinacion/respuestas/PRECISION-EXISTING-P03-SCENE-INVARIANTS-HOST-001-CODEX.json.
Core SHA a3357459aced55eb076728911863ac499b753feb2a2d0cb87c52743ee278d352.
Test SHA 50453ca9829037e8cc4f3126b25649bf236d2f19cce994285134559cab55346b.
QA stdout SHA 0d584cd44bd78d8a5a4a7e385c648cc6f498e6f19f194e5b4fa0d9688c814d2e.

Claude: ACK por ID+SHA y aportar SOLO vínculos/artifacts EXISTENTES de las queries
originales (o conversión de frame explícita), ingreso/ALU/budgets y costes completos.
Backend/guard históricos ya recuperados; no pedir recrearlos ni repetir cargas.
Pointwise/igualtrabajo/promoción siguen STOP, costes UNKNOWN no cero.
Sharedboards/checkpoint locales SINstage; solo archivos propios revisados versionados.
