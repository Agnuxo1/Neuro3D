# EXP-005 — AXIAL-NATIVE-SIGNED512-001

Primitivas opt-in signed512 sobre16limbs uint32 little-endian:
compare/add/sub/mul checked, decode binary32 normal-or-zero a escala2^149
y suma de hi-lo. Header GLSL nuevo y espejo CPU sin Fraction/float/int512
en el núcleo: sólo carry/borrow/32x32→64 y producto temporal unsigned1024.
Overflow/signo fail-closed, no wrap/saturación/FTZ.
En GLSL false significa output inválido: el caller debe propagarlo y NO
consumir limbs. No main/SSBO/admisión o dispatch en este header.

Builtin multiplicación64 como hi/lo está documentado por
[Khronos GLSL4.60](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html).
Header requiere GLSL>=4.00; no extensión uint64 ni FMA.
No glslangValidator disponible localmente: **NOcompilado y NOejecutado**.
CPUmirror/tests y checks textuales NOvalidan semántica del compilador/driver.

Consumo nuevo desde inputpacket pin: coordenadas X hi-lo, radios signed512,
sourceIDs/dirección±X, planos compartidos porowner M/D. Calcula intervalos
fuente/espejo/detector y longitud geométrica σ(2M−S−D) exclusivamente usando
limbs, NO longitud suministrada/cache/GEMM. Radialenclosures inalteradas.
Esta longitud NO Lref de modo ORIGINAL; no inferir fase de Lgeom.

Gate conservador adicional sobre ambos planos X iniciales: espejo estrictamente
adelante; D estrictamente detrás de cero o separado después de todo el intervalo
M. Contacto con cero, empate y solape rechazan. No usa coberturas YZ; puede
rechazar un plano cuya cara no cruce el rayo. NO selecciona eventos completos.

**Límite explícito:** YZ/interiores/competidores geométricos/árbol/selección de eventos
y aplicación GLSL a escena todavía NO implementados. Xpositivo NOgeometríaPASS.
boundaryFAIL puede tener Xpositivo: mantener global accepted_complete_geometry
false; los FAILs y gates congelados no se reemplazan ni se relajan.
No conf1/v0/v4/0119/0315/nearestV2/runners/shaders antiguos modificados.
NO fullpipeline/native-ALU GPU/coherenciafísica/auth/promoción/RT/óptica/
ventaja/costescomparativos. No replay de productores: sólo comparar intervalos
ya retenidos disponibles en tests; oráculo independiente verifica nueva aritmética.

SOURCE-ENCODER-001 SHAa116d831b7ddd48b1f00046c3c705e16e378a87ef01410ba9ba25b2211386474
es dependencia; ingreso frozen SHAc20ddf4f856b8932c9394d1d60c6c4e44b3170bac72e4a3922a673c778dfb855.
CPU1hilo/hijo<=60s/sinGPU; JEVbloqueado/fallbackLOCALsinaval.
Skills feature-tests y inputs factuales reutilizados; boardsSINstage.

## Evidencia

Primera ejecución propia: 8 tests, rc1, 6 PASS y 2 FAIL; stdout completo retenido
en el reporte. Dos supuestos de tests eran incorrectos: hay nueve filas disponibles,
no diez; contacto de D puede ocurrir aunque distancias M y M→D sean positivas.
Se conserva ese positivo parcial; se implementa gate separado de clearance de
ambos planos y controles estrictos de contacto/solape. No cambia geometría
retenida, radios, caps ni convierte FAIL científico en PASS.
9 tests propios PASS rc0/0,2462808s; 13 casos, 14 fuentes. Las nueve filas
disponibles de ocho casos coinciden exactamente en ambos segmentos y Lgeom.
Reporte raw334643bytes SHA f15775be732685aacac931fcf0024c36deb791dd60765f4c07cebe87d1fdc725.
Primer verificador independiente rc1: serialización JSON inicial convirtió tuple
inválida en lista; una negativa de tipo inicial queda NO verificable a partir
del raw. Se conserva FAIL y raw inicial, se añade recibo de tipos de contenedor
al trace nuevo; ninguna fórmula/cota/resultado numérico cambia por ese arreglo.
Oráculo independiente stdlib/enteros ordinarios, sin imports de productores:
rc0/0,2066604s, 167 huellas (163 heredadas + 4 propias), 13 casos/14 fuentes,
9 matches de intervalos/8 casos retenidos disponibles. Diez filas pasan el
perfil de planos X conservador: incluye boundaryFAIL; **ninguna** obtiene
geometría completa o admisión GPU. Cuatro contactos/solapes quedan negativos.
Checks aritméticos finales: 1235 llamadas nuevas incluyendo controles,
300 add/245 sub/49 mul/174 compare/467 decode32; 21 rechazos esperados.
Estos son conteos semánticos CPU, NO costes GPU/hardware/fullpipeline/energía.
En raw inicial verifica 1084 llamadas salvo una negativa de tipo no recuperable
tras tuple→JSONlist; esa limitación permanece declarada. Header sólo revisión
textual/manual, sin evidencia de compilación/ejecución. GPU sigue pendiente
de contrato, driver, escena completa y protocolo exclusivo por job.
