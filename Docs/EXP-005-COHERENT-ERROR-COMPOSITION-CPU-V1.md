# Composición condicional del error de campo y de reducción

Unidad CPU nueva, separada de módulos/shaders/pilotos congelados. Usa campos
float32 suministrados y una cota L1 racional no negativa por camino suministrado.
Cada cota debe enlazar ID, fuente, puerto, palabras uint32, longitud de onda, grupo y referencia de
fase exactos. Máximo64 registros; racionales canónicos de hasta256bits.
Fuentes coherentes comparten longitud de onda representada y referencia de fase.
El etiquetado no prueba que un productor físico/nativo haya realizado ese transporte.
No reutilizar una cota previa de norma compleja como si fuera L1: debe derivarse
por componentes o convertirse conservadoramente (L1<=sqrt(2)*norma2<=2*norma2).
Este módulo exige L1 ya justificada; aún no enlaza las cotas previas de fase.

Contrato antes de las pruebas: campo absoluto1e-4 por grupo y potencia2e-4 por
puerto, sin relajación. Para suma representada exacta S, resultado RN32 Y,
ideal desconocido X y B=suma de cotas previas por camino:

- Campo: |Y-X| <= R+B, con R=error L1 exacto de reducción respecto a S.
- Potencia: ||Y|²-|X|²| <= D+2*L1(S)*B+B², donde
  D=||Y|²-|S|²| se calcula exactamente con racionales.
- Grupos incoherentes suman cotas de potencia, nunca sus campos.

La segunda desigualdad procede de la identidad del cuadrado y de
|S|<=L1(S), |X-S|<=B. Usa las cotas suministradas como hipótesis; no las
certifica. Una cota demasiado grande produce rechazo conservador, no una
demostración de que la salida real sea errónea.

Pruebas nuevas: seis órdenes A+1-A sintético de amplitud alta con compensación
exacta pero cota previa que agota el presupuesto; control de amplitud1 cuyo gate
de campo pasa mientras potencia falla;25 perturbaciones complejas racionales;
grupos independientes; cero error previo; cobertura, bindings, referencias,
frecuencias y racionales inválidos. No reeditar ni repetir suites congeladas.

NO escena/inferenciaGPU, libm/FTZ/driver, aritmética nativa de detección, modos
físicos, cota de precisión total ni ventaja de velocidad. Cotas previas aún no
vinculadas a un productor nativo/escena completo. No cambiar backend a matrices.
JEV bloqueado por seguridad: fallback local explícito, sin aval remoto.

Siguiente: enlazar cotas anteriores retenidas por ID/referencia a los campos del
mismo productor, preservando la completitud de la escena y sin confundir esta
composición condicional con autenticación. Piloto escalar GPU sigue separado.
