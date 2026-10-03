# PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001

Opt-in CPU64 de corrección hi-lo de raíces selladas; certificación HOST explícita.
Base c5c50b1a2560d81c437a22449b59bf5aa041c42b, padre coordinacion/respuestas/PRECISION-OBLIQUE-EXPANSION-ROOT-CERT-CPUHOST-001-CODEX.json, SHA256 443b99eed81223011ddb0c910a4d13c43d640e164131c6b6c9c5a5a58baf0645/144195bytes.
Contratos/runners/shaders/fixtures/bounds anteriores quedan congelados. JEV bloqueado: fallback LOCAL sin aval remoto.

## Trabajo nuevo y procedencia

Dos escenas elegibles/cuatro extremos de MISMAS cajas ORIGINALES, ALL15radios/ALL240bytes;
SOURCE0 incierto no cancelado. Catorce STOP previos intactos; STOP canónico anterior preservado.
Reutilizar las semillas Y y las expansiones S realmente producidas y YA selladas.
CERO llamadas nuevas a sqrt. No repetir productos de endpoints ni sumas de backends anteriores.
Los productos/sumas de RESIDUAL de este backend son trabajo nuevo, registrado y separado del replay.
La geometría y selección de extremos del padre eran HOST y siguen siéndolo: no llamar esto motor nativo desde escena.

## Primitivo nativo

Entrada Swords lista1..4 de palabras normales/cero canónicas, |word|<=2^66.
Y y L son palabras existentes; 0<S<=2^66, 0<Y<=2^32 (dominio del producto congelado),
0<L<=Y y L²<=S. L procede del certificado sellado de caja para escenas.
Controles independientes de la aritmética son CPU sintética explícita, no más escenas ni equivalencia física.

1. Nuevo producto EFT Y*Y con primitivo CPU64 Dekker17RN intacto y mismos límites, NO FMA.
2. Negar hi/lo por XOR del bit de signo, incluido cero firmado; no inyectar residual HOST.
3. grow-expansion fijo4 sobre Swords + [-p_hi,-p_lo]; probar identidad exacta R=S-Y².
4. denominator=RN(2Y); delta=RN(Rhi/denominator), Rhi es la última palabra REAL de la expansión nativa.
5. Salida [Y,delta], NO RN(Y+delta) que borraría el limb bajo.

Los limbs bajos del residual se preservan en ledger/expansión; la división sólo toma Rhi.
No afirmar una raíz exacta ni que se usa cada limb en delta. El error de esa aproximación queda en cota HOST.
Registrar y probar TODOS los nodos producto17RN/grow6RN y multiplicación/división.
Dominio normal/cero, salida escalar acotada2^33, no underflow no cero hacia cero.
Si el producto falla, grow requiere cinco componentes o scalar falla: STOP con TODOS los parciales,
sin truncar/rescatar/ampliar capacidad ni límites. La aceptada root_pair_words permanece null.
No modificar thresholds de contratos previos.

## Cota y encierro HOST

Q es el valor racional EXACTO de las dos palabras producidas, no float(Q) ni residual reinyectado.
Antes de cota exigir Q>0 y L²<=Q²: misma cota inferior positiva común.
B=|S-Q²|/(2L) certifica |sqrt(S)-Q|<=B. Unidades scene_length.
Probar sin evaluar nuevas raíces: (Q-B)²<=S<=(Q+B)² y Q-B>0 en los registros aceptados.
El encierro [Q-B,Q+B] es HOST racional, no palabras dirigidas de salida de motor.
Caja completa por monotonía: [Qmin-Bmin,Qmax+Bmax], usando sumas exactas de MISMAS cajas originales.
Comparar ancho/cota con referenciaHOST96 YA sellada y con encierro de semilla retenido;
ratios geométricos NO comparativa de velocidad/eficiencia/equivalencia de backend.

native_length=null: corrección pareada nativa parcial, preprocesado geométrico y cota HOST.
phase_error_bound=null, wavelength_known=false, physical_reference_certified=false.
NO afirmar fase, óptica, GPU ALU, RT ni motor ganador. No convertir U/GEMM en inferencia de escena.

## Pruebas y recursos

Oráculo independiente bit/racional sobre captura, sin repetir productores:
RN nearest-even por vecinos IEEE enteros, conexiones/orden exactos y producto/residual/den/div/pareja.
Prueba padre sellado una vez por verificación; SHA/pins revalidados en cada mutación.
Tres controles válidos de raíces previas; caso residual de cinco componentes STOP con77RN
(17producto+60grow) y producto underflow STOP con9RN: parciales preservados.
Siete entradas preSTOP/ocho selectores inválidos/ocho mutaciones; API pública y ausencia padre SIMULADA.
Contar RN/productos/sumas nuevos incl. negativos/API, sqrt nuevas=0.
Fixtures/decodificación/HOST racional/provenance/IO/costes completos UNKNOWN_NOT_ZERO.
CPU propia1hilo/afinidad máscara1/hijo<=60s, stdlib Python313 -B.
Sin GPU/Blender/SDK/DrJit/JEV/red/push/merge; tampoco afirmar GPU libre sin telemetría.
Commit LOCAL sólo own4 revisados; sharedboards/checkpoint SINstage.

## Evidencia

coordinacion/respuestas/PRECISION-OBLIQUE-ROOT-HILO-CORRECTION-CPU-001-CODEX.json contiene capturas comprimidas/hash/bytes, resultados y coste medido.
Rationales grandes permanecen en JSON Python sellado; sumarios exactos como strings, no Numbers JavaScript.
Solicitar Claude sólo artifacts YA existentes por ID/path/SHA/bytes: backend+guard fail-closed,
igualtrabajo/salidas/costes completos y escena incertidumbre/autenticación/completitud. No ACK inventado/cargasrelleno.
