# PRECISION-OBLIQUE-TOTAL-PHASE-SHADERC-001

P0 opt-in capacity_audit/EXP005. Candidato nuevo; no integración ni ejecución GPU.
Base 24de7d9f4588af9ace0c6c21f3cbc0f1ca734dd8. JEV LOCAL, bloqueado por seguridad, sin retry.
Skills de desarrollo/pruebas y cognición extendida: reutilización de capturas, pruebas acotadas y fallo conservado, sin delegación.

## Contrato de entrada y salida

Entrada little-endian 96 bytes: cuatro uint32 (TAG=0x54504731, count=10, fuentes=2, marcador=1), luego diez binary64 en orden:
P0.hi/lo, P1.hi/lo, gamma0.hi/lo, gamma1.hi/lo, mu.hi/lo.
Son pares CODIFICADOS capturados, no inferencia de caminos o parámetros desde escena.
Salida 64 bytes: mismo TAG, count=6, fuentes=2, marcador=1; seis binary64:
TOTAL0.hi/lo, TOTAL1.hi/lo, RELATIVE.hi/lo.
Este TAG no es el CPU_TAG=0x43545031 ni V2=0x4f444632. Expected_output retaguea explícitamente CONTROL CPU, nunca readback de dispositivo.
La API prepare(model,request) carga evidencia sellada interna; no parámetro público de evidencia.

TOTAL0=plus(plus(P0,gamma0),mu); TOTAL1=plus(plus(P1,gamma1),mu); RELATIVE=plus(TOTAL0,-TOTAL1).
Cada plus usa cuatro twoSum y dos adiciones: 26 operaciones, cinco plus=130 nodos topológicos.
Capturas de once casos nativos admitidos verifican cada arista y los nodos de salida 46/51/98/103/124/129.
No se recalculan RN, longitudes, geometría, encoding ni productores. Se conservan 35 STOP heredados, incluido borde de cota; no se amplían caps.
Mismo mu no rescata presupuesto SOURCE ni elimina errores de redondeo de sumas SOURCE.

## Guard y límites de evidencia

Una sola invocación gid=(0,0,0), tamaños exactamente 24/16 uint32. Cabecera se invalida antes de leer componentes cuando los tamaños son válidos.
Todos los diez exponentes crudos se comprueban ANTES de cualquier packDouble2x32.
Después del pack, los diez valores se comprueban finitos y |x|<=2^40. Igual dominio conservador V2, no ampliado.
Seis componentes de salida se comprueban finitos y |x|<=2^40 antes de escribir payload. Header TAG se escribe al final.
El marcador final es orden lógico del código: NO atomicidad del dispositivo, barrera, fence, visibilidad de memoria o contrato host certificado.
La salida STOP tiene TAG=0 y count=0 si el tamaño permitió invalidar cabecera; en gid/tamaño inválido no se escribe.
HOST debe inicializar salida, garantizar exclusividad y rechazar cabecera incompleta. Un output previo no es nueva evidencia.
Shader no demuestra cotas de fase; requiere validación independiente ALLSOURCE/relative del readback antes de toda promoción.

Compilación CPU con DLL existente sellada d62717becac57380539f099f844e38171a84dad544d86550fc1889224318ab6b.
Vulkan1.0/shader_kind2/main/optimización0; versión textual UNKNOWN, identidad SHA verificada. No SDK, DrJit ni instalación.
Extractor aritmético ignora ramas: 130 nodos Float64/NoContraction, 25 llamadas desenrolladas. No prueba RNE ni validez SPIRV-Tools.
Modelo de prefijo recorre CFG solo hasta primera operación de pares. 78 escenarios: 39 por dos políticas explícitas de pack.
Treinta entradas Inf/-Inf/NaN, diez componentes, se rechazan sin ningún pack bajo ambas políticas; controles de cabecera, tamaños, gid y dominio.
Modelo CPU de bits y control NO prueba guard GPU. Salida postaritmética se revisa estructuralmente, no se simula ejecución FP64.
Verificador independiente inline (sin importar core) decodifica SPIRV, exige capability Float64 y ocho instrucciones estáticas aritméticas NoContraction; reconstruye CFG y dominadores: diez máscaras crudas dominan primer pack y cada comparación positiva termina en return. Reconstruye 130 aristas y comprueba bits/payload/11 casos/35 STOP/pins. Esto es propiedad estructural del binario sellado, no garantía de driver/dispositivo/RNE.

## Resultados y fallo conservado

Primera prueba terminó rc1 KeyError native_wrong_model: control de selector no tenía entrada registry. Ya había dos llamadas compiler; sus artifacts no se capturaron debido a excepción.
Reparación SOLO separa selector negativo sellado de caso geométrico; exige STOP previo y no crea packet.
Captura inicial completa del stderr conservada en recibo. No se cambian umbrales ni resultados parent.
Suite final tres grupos PASS: 46 preparaciones (11 CONTROL/35 STOP), once trazas x130 aristas, 78 prefijos y controles de selector.
Dos llamadas compiler en suite final: candidato válido y fuente propia con token inválido que conserva error, salida SPIRV vacía.
TOTAL REAL del turno CUATRO llamadas compiler CPU; no declarar dos como total del turno. Ninguna recompilación de shader frozen.
Primer verificador independiente rc1 por comparar tuple/list de referencias simbólicas. Conservado íntegro; corrección solo normaliza contenedores en esa comparación, sin cambiar aristas, caps o criterio. Segundo verificador PASS. Los dos fallos administrativos permanecen en el recibo.
Tiempos de suite/compile son QA local, NO costes completos de motor. Costes desconocidos siguen UNMEASURED_NOT_ZERO.

GPU/Blender0, CPU1hilo/afinidad1/hijo<=60s. CIM RAM ACCESS_DENIED/UNKNOWN histórico conservado sin retry/elevación/bypass.
GPU launch, native promotion, scene/material/device/physical authentication: False/STOP.
No Bpyfloat32, RT ni óptica física, ninguna inferencia silenciosamente sustituida por U/GEMM.
Fixtures conf1/v0/v4/0119/0315/nearestV2, bounds, caps, runners/shaders/contratos frozen y archivos Claude intactos.
Boards/checkpoint LOCAL SINstage. Versionar solo cinco propios.
Pedir Claude ACK por ID/SHA y artifacts YA existentes backend/guard fail-closed/Float64-float-controls/ingress-fence-readback/material-amplitud-completitud con ID/path/SHA/bytes e igual ORIGINAL-overlay-caps-trabajo-salidas/costes completos. No cargas de relleno ni ACK inventado.
