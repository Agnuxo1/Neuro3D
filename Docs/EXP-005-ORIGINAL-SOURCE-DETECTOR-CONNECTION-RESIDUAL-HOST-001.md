# Distancia al detector: no confundir inclusión con conexión exacta

ID: `PRECISION-ORIGINAL-SOURCE-DETECTOR-CONNECTION-RESIDUAL-HOST-001`.
Codex capacity_audit/EXP005, P1 opt-in HOST. JEV LOCAL bloqueado por seguridad,
sin reintento/aval remoto. No GPU, Bpy, hardware RT ni óptica física.

## Unidad nueva y procedencia

Los ocho ciclos geométricos condicionales anteriores usaban SOURCE/P/Q, con Q
propagado como caja no singleton. No certificaban que Q fuese el punto detector
D del request. Este módulo calcula únicamente una norma NUEVA de `Q-D`,
desde esas ocho cajas capturadas y D literal. No vuelve a calcular posiciones,
primer/segundo tramo, ciclos, rayos, phase overlays ni shaders.
Se preservan los otros 20 STOP de las 28 filas capturadas, sin norma nueva.

Recibos de entrada por SHA:

- ciclos SOURCE `53b739dcaaf08e2bbce9ca81ce7a24b98bc53074357720a4bc9aaaf317aae1fe`;
- requests geométricos `139cb34a315f476fa026bb346086a3a59d7c22241932ca3f4c291a501f4ca47e`.

`run` verifica recibos/capturas/pins y norma pura congelada
`8f3b77dba20a755754f1c0da4bc9b779d35056a02240b6602d0c7d1d34d330e8`.
De ese helper sólo se usan operaciones racionales/certificados enteros; nunca
su evaluator/runner ni lectores del productor. Modelo explícito, unidades BU,
SOURCE, digest de fila, escena y query exactos, primitivas root1/detector0,
referencia/lambda y flags/ledger STOP obligatorios. Hash del caller es
consistencia local, no autenticación física ni prueba de ingress nativo.

## Contrato geométrico

Para cada eje se calcula `[Qlo-D, Qhi-D]`; los cuadrados conservan cero si el
intervalo lo cruza. La suma de cuadrados produce los extremos de distancia
posibles para la caja cartesiana. Dos raíces NUEVAS por norma se encierran con
certificados enteros de 96 bits, límites de entrada128 y squared512 intactos.
Coord absoluta <=1e6 BU, lambda mínima estrictamente positiva y salida512.
No FP/trigonometría/FMA ni aumento de bounds para producir PASS.

Se reportan separadamente:

- `detector_point_in_candidate_box`: D pertenece a la caja Q;
- `ALL_candidate_box_points_equal_literal_detector`: toda la caja es D;
- distancia BU y un vértice de caja con cuadrado máximo, sólo testigo HOST;
- presupuesto detector original y error nativo: `null`, UNKNOWN, nunca cero.

Pertenencia NO implica igualdad para todos los Q. Un vértice extremo es posible
en la caja cartesiana, pero no prueba que una trayectoria correlacionada o un
backend real lo produzca. Una caja no singleton tampoco demuestra que el Q
real esté desplazado: puede ser D. No se etiqueta un error físico observado.
Incluso el control singleton exacto conserva native/visibility/phase STOP.

## Allowance condicional de sustituir Q por D

Con el MISMO P, referencia y longitud de onda actual lambda positiva:

```
abs(|Q-P| - |D-P|) <= |Q-D| <= delta_upper
abs(delta_cycles) <= delta_upper / lambda_lower
abs(delta_radians) <= 8 * delta_upper / lambda_lower    (2*pi < 8)
```

Es una cota geométrica de una sustitución hipotética. Q NO se sustituye por D;
`actual_Q_replaced=false`, `cap_budget_admitted=false`. No cambia los ciclos
retenidos ni se agrega automáticamente a su radio HOST: haría falta un
contrato explícito de dependencias y presupuesto, sin créditos silenciosos por
correlación. No corresponde a error total de fase, material/SOURCE, path óptico
heterogéneo, fase codificada, primer tramo ALU ni ingress/ref-lambda nativos.
No se reutiliza el cap de fase como tolerancia de conexión espacial.

## Verificación

Pruebas propias: 28 filas fijas, inclusión vs ALL, controles singleton/fuera/
Pitágoras/variable-lambda/referencia grande, desplazamiento inferior a grid96
con cota no cero preservada, cuatro controles 1D de desigualdad triangular,
entradas inválidas, bindings, flags nativos, query diferente misma escena,
copias y capturas fail-closed. Extremos de caja y desigualdades enteras de
raíces se verifican independientemente sin reevaluar raíces upstream.

QA un hilo por afinidad, RAM presupuesto128MiB y >=4GiB después, hijo timeout30s
y deadline nuevo35s. No medición de rendimiento/costes completos, energía ni
motor ganador. `full_costs=UNKNOWN_NOT_ZERO`, promoción nativa/GPU/phase false,
material/SOURCE phase y field/power null. No instalación/push/merge ni reserva
GPU/telemetría nueva; no se afirma que la GPU esté libre. Histórica ventana
nocturna cerrada intacta. Sharedboards/cache locales SINstage.

Siguiente: evidencia/contrato de SOURCE ingress y primer tramo ALU, conexión
detector ligada al backend y budgets explícitos de referencia/lambda/fase.
Claude ACK ID+SHA y sólo artifacts EXISTENTES o ausencias M03/M04/M05/M08/M13.
No repetición de barridos PRECISION005/006 ni render/cargas de relleno.
