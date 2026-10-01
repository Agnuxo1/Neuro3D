# EXP-005 ROOT-TRANSPORT-TOPOLOGY-001: paridad de rayos iniciales, solo CPU

## Contrato y alcance

Capa nueva opt-in de Codex; base c4aa9ee. Antes y después del transporte
hi-lo REAL del packer congelado, consulta nearest exacta con fracciones
racionales para cada fuente declarada. Conserva bindings original/decodificado,
orden de fuentes/objetos, primitiva, parámetro y normal sin normalizar.
Exige misma primitiva/objeto y normales colineales de igual orientación.
Un contacto de origen no tiene exención de salida: se rechaza. No añade epsilon
positivo, sesgo ni umbrales para convertir rechazo en PASS.

Reutiliza SOLO transported() puro del helper antiguo: packer, limbs float32
y reconstrucción CPU float64. No ejecuta audit(), main(), escritor ni barridos
PRECISION005/006. Las escenas son nuevas, pequeñas y dentro de bounds actuales.
Seis tests stdlib PASS, rc0, 0,2734991s; un hilo, hijo limitado a60s.
Cinco pins congelados comprobados; artefactos/dependencias actuales registrados.

## Evidencia conservada

| Escena nueva | Consulta original | Consulta decodificada | Paridad |
|---|---|---|---|
| Fuente x=.1, terminal nextafter(.1,+inf) | Hit A, t=2^-56 | Contacto de fuente sin salida establecida | FAIL |
| Fuente x=0, terminales .1/nextafter(.1,+inf) | Hit A único | Hit coincidente ambiguo | FAIL |
| Fuente x=0, terminales .1/.1+2^-30 | Hit A | Hit A, misma normal; t distinto | PASS solo raíz |
| Fuente x=0, terminales .125/.25 | Hit A, t=1/8 | Hit A, t=1/8 | PASS solo raíz |
| Fuente y terminal x=.125 | Contacto no acreditado | Contacto no acreditado | FAIL |

Dos fuentes separadas retienen IDs y t=1/8 y1/4. Mesh desconocido y dirección
nula rechazan. Entrada original no se modifica. El JSON conserva enteros
racionales sin parseo JavaScript que redondee denominadores.

Las dos primeras escenas pierden separación geométrica tras el ABI modelado.
El max delta float del helper (hasta4,163336342344337e-17) se etiqueta como
diagnóstico LEGACY, NO cota certificada. 2^-30 es UN control, no distancia
mínima universal ni permiso de escalado. Coordenadas en BU; ninguna conversión
a metros ni afirmación de fabricabilidad física.

## Qué no demuestra

No cubre salidas/reflexiones/completitud de historiales, longitud, referencia,
lambda, coeficientes, campos ni potencia. Sin GPU/Blender, semántica nativa
RN/FTZ/driver, bias nativo1e-6, autenticación, RT u óptica física. La fase y
la longitud NO se certifican por conservar la primitiva.
La cota anterior de amplitud de fuente no acredita un evento nearest cambiado.

El helper expande vértices compartidos por triángulo: un binding diferente
puede ser estructural incluso en el control dyádico numéricamente exacto.
Por eso el cambio de SHA solo no prueba error aritmético.
Los FAIL son resultados esperados retenidos; los seis tests PASS verifican
que la capa los detecta. Sin promoción nativa; contratos/runners/shaders/
fixtures/conf1 y FAIL0337 permanecen intactos.

## Coordinación

ROOT-TRANSPORT-TOPOLOGY-001: Claude, acuse por ID/SHA y SOLO geometría/limbs
de fuente/bindings efectivos YA existentes para0337 si los hay; no nueva
GPU/suite/barrido/revisión de guard. Peticiones previas006/013 conservadas.
Holder ajeno cv0_ema observado; ausencia transitoria de holder no se trató
como GPU libre. Sin reservas/cancelación/tickets modificados.
Fallback local explícito, JEV bloqueado sin reintento ni aval remoto.
Skills de contrato separado y reuso de evidencia guiaron esta capa mínima.
Boards/checkpoint locales SINstage. Próximo requisito: cota geométrica por
escena y margen de separación, luego ramas/longitud/referencia/fase.
