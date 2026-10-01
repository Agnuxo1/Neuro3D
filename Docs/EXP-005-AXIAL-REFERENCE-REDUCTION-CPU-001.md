# EXP005 — AXIAL-REFERENCE-REDUCTION-001 (CPU opt-in)

Base c3dbeab4e570724c58a1412a243d414762e36f0a; SOURCE report SHA
58507912b97b88589ce292d22ab88d801578c2d1c69e4abd398ad959afd28d7d.
JEV bloqueado sin reintento; fallback LOCAL sin aval remoto.

## Contrato

Consume ESTOS productos fuente del plano/modo de referencia ORIGINAL fijo D,
no Lgeom ni fuente/unidad recomputada. Source IDs, orden, binding/ABI SHA,
puertos/gauges deben coincidir. Cada assignment declara agrupación HIPÓTESIS
CPU, common_terminal_reference_id igual al terminal ya aplicado por unidad
referenciada y rebase_cycles=0. No convierte gauges de fuentes diferentes en
coherencia física; el producto ya está referenciado al mismo plano fijo.
No fase libre implícita, no grouping por default, no fuente perdida/duplicada.

Caps explícitos racionales no negativos completos: field_L1/power=1e-12 y
relative_field/relative_power=1e-6 en audit, MISMAS caps del contrato reduction
previo, NOconf1/phase/bounds ni umbral relajado. Efield = suma cotas NUEVAS
source_ref + suma |delta_RN64| de reducción. Epower por grupo <=
2 |Yobservado|1 Efield + Efield² + error detector3; port suma añade
|delta_RN64|. Cota relativa usa lower=max(0,norma_observada-cota);
lower=0 rechaza sin epsilon, denominador artificial ni crédito por cancelación.
Nada copia cotas/flags antiguos; retained_closure_gates sólo se preservan.

Cache matemática sólo nodos reduce2/detector3/power_add1:
palabras ordenadas, modelo numérico, código y origin report SHA. No reutiliza
binding/IDs/group/gauge/caps/bounds/gates/auth/hardwarecost. Incluye outputs
matemáticos de controles YA retenidos en origen; no repite workloads.
Nodos cached no ejecutados como productor. Sin importar escritores/suites;
sólo helpers numéricos puros opt-in.

## Controles y límites

Two_sources coherente debe conservar campo/power=0 y rechazo relativo:
no mejora por lower0. Grupos separados son OTRO observable (~.02), NO
comparación equivalente ni autenticación física. Capfield0 control separado
rechaza con mismas palabras/output detector/cotas; no se altera cap principal.
Mode-.25 ya retenido usa nuevo binding/observable; mode.1cap0 upstream STOP.

Ocho tests narrow y verificador independiente stdlib desde M/S/R/lambda y
source field ORIGINAL, oráculos de campos por grupo/potencia por puerto.
RN64 cached sólo SHA/origen + comprobaciones independientes matemáticas,
sin fuente/unit/tree/geometry/product replay ni nuevas escenas de relleno.
CPU un hilo, hijos<=60s. Exact racional/normal-or-zero RN64 modelado, sin
FTZ/FMA/native/ALU GPU/RT/Bpy/óptica física ni costes hardware completos.

Frozen runners/shaders/contracts/fixtures conf1/v0/v4/0119/0315/nearestV2 y
FAILs intactos. Fullpipeline/coherencia/auth/native false aunque bounds CPU
locales pasen. SinGPU/preflight/reserva, cola desconocida; deadline histórico
cerrado e intacto. Sólo cuatro archivos propios versionables; tableros
compartidos/checkpoint locales SINstage. Skills contrato/tests y cache exacta.
Claude ACK ID/SHA SOURCE y artifacts efectivos YAexistentes matching scene/
limbs/sourceIDs/binding/model/reference/backendguard + igualtrabajo/salidas/
costes completos; 0337guard histórico YAubicado NOesta cadena/admisión.

## Evidencia (2026-10-01 18:12 UTC)

Ocho tests PASS rc0/1.6615094000007957s; stdout121896 bytes SHA
394e25adc4f3ad7ef261124b5b537bec8136e43fa577bb253ef8aaa58e7bbdc3.
143 pins previos + tres propios =146 huellas verificadas.
13casos/14IDs: cinco reducciones calculables, cuatro gates SOLOCPU aceptados;
ocho upstream STOP, quarter/geom/phase y two_sources relativoFAIL intactos.
Audit cero RN64 productor nuevos/32 cached NOejecutados. Mode-.25 seis cache;
mode.1 cap0 STOP cero; splitcontrol12 cache y fieldcap0control seis cache.
Source/unit/geometry/tree/product no ejecutados de nuevo.

Verificador stdlib independiente rc0/0.2827609999803826s, código SHA
7cc8b5290bf4b8185eeba391eccc810cb77aa89a81c4db47adaf346450f9dbe0:
17bindings/19IDs con controles, diez fuentes ORIGINALES, nueve campos por
grupo, ocho potencias por puerto, 28 cachegraphs originSHA y56nodos RN64
comprobados matemáticamente, 17 lower-relativos. Estos checks independientes
NOson ejecuciones nuevas del productor ni benchmark hardware.

Fallo inicial del verificador rc1 se preserva: direction original float
multiplicada por Fraction convirtió ciclos/Taylor/poweroracle a float.
Se corrigió SÓLO verificador con Fraction(direction) antes de multiplicar
y asserts tipo Fraction en ciclos/residual/potencia; ahora todo oracle exacto
racional. Código de producción/tests, stdout, bounds y caps SINcambios;
ningún umbral se relajó. Oráculos/FAILs anteriores congelados preservados,
sin editar ni atribuirles retroactivamente la exactitud de este verificador.
Primer contraste corregido rc0/0.2117855s también retenido. Documento sólo
añade evidencia; pins at-run conservados y final actualizado.

Siguiente: cierre de procedencia/completitud de ESTA cadena referenciada y
contraste sólo con artifacts efectivos existentes; NOcaptura/cargas por
relleno, NOclaim fullpipeline/coherenciafísica/autenticación/native/RT/óptica.
