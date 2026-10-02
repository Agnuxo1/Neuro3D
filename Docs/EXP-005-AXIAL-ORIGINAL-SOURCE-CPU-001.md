# EXP005 — AXIAL-ORIGINAL-SOURCE-CPU-001

Modelo opt-in `axial-ORIGINAL-source-hi-lo32-IEEE-RN64-prefix-CPU-v1`, Codex/P1. Predecesor AXIAL-ORIGINAL-UNIT-CPU-001 / SHA0132858e34ca29a91ae8f91974531c706f7d973e0bbbeab1dba04f544f3c9fe3.

## Contrato

Únicamente dos fuentes nonexact_geometry_phase_PASS/s ythin_resolved/s. Desde el snapshot ORIGINAL binary64 fijado por INPUT: referencia/selector racional exactos y argumento/unit CPU nuevos con primitivas propias anteriores. Crosscheck sólo DESPUÉS de ejecutar, nunca usar unidad/ángulo retenidos como inputs. Fuente compleja field_reim ORIGINAL ligada a sus dos palabras binary64 del mismo stride/ABI y orden/gauges.

Nuevo encoder CPU: high=RN32(original); residual=RN64(original-high); low=RN32(residual). Guardar cuatro palabras uint32,16bytes little-endian/base64/SHA y errores exactos por componente. Cast32 IEEE nearest-even con cuatro probes; seis probes64 aparte. Perfil seleccionado: ORIGINAL normal-o-cero y limbs normal-o-cero, overflow/subnormal no admitido por este contrato; no FTZ/clamp. Política nueva explícita IEEE de signo por nodo, sin canonicalización. -0 original conserva high=-0, residual/low según operación IEEE; el signo no se inventa desde Fraction.

Decode: dos sumas RN64. Producto: ac,bd,ad,bc,real=ac+(-bd),imag=ad+bc, seis operaciones sinFMA. Todos los nodos observados en bits ydelta racional; normal-o-cero/finito. Signos -0 intermedios preservados. Este modelo NUEVO no exige equivalencia con el grafo HOST canonical+0: sus ocho FAIL/12signos históricos se mantienen INTACTOS, sin sobrescribir o fabricar PASS. El oráculo integer IEEE verifica el nuevo grafo, no reinterpreta el viejo.

Cargos L1 separados hacia bare sORIGINAL*uORIGINAL:
E <= Eencoding*|uCPU|L1 + Edecode*|uCPU|L1 + |sORIGINAL|L1*Eunit + Eproduct.
Eencoding es el error del sumatorio exacto high+low; incluye el residual64 ylow32, no se oculta. Edecode suma delta de dos adds; Eproduct suma cuatro mul ydos adds. Eunit es la cota puntual ORIGINAL fijada por fase+Horner, no un radian convertido silenciosamente a presupuesto de amplitud. Se verifica aparte el error del producto RN hacia decoded-source*represented-unit.

No presupuesto por fuente/etapa inventado. El cap INPUT de fase1e-12rad de UNIT permanece intacto; NO es presupuesto L1 de SOURCE ni cota de fase de fuente cerca de cero. Esta salida es sólo PREFIJO fuente*unidad ANTES de reflexión/material/fieldsum/potencia/detector, no campo terminal ni inferencia física completa. Geometría ORIGINAL sigue racional, NO transporte geométrico hi-lo ejecutado. 17fuentes STOP/two_sources sin parcial/todos flags amplios false.

## Verificación y seguridad

Suite propia con dos fuentes, controles primitivos de fuente -0 ycomponente imaginaria nozero, rechazos de modelo/contexto/pin/ABI/encoder/casts/guard. Oráculo stdlib sin importsproducción: RN32/RN64 enteros nearest-even/signos, bytes/SHA, nodos ycuatro cargos exactos; verifica referencia/unit con código independiente propio, no suites previas.

Por fuente principal:8RN64decode/product+4RN32casts+2RN64subtractions, además26Horner+1cast1mul argumento yreferencia racional. Controles/rechazos separados. IO/pins/setup/racional/restante UNMEASURED, no cero; no comparación de velocidad/eficiencia/igualtrabajo/ganador. CPU1hilo/afinidad1/hijo60s; sinGPUBlenderSDKDrJitKagglepushmerge. JEV LOCALsinaval/noretry, deadline histórico intacto. Contratos/runners/shaders/fixturesconf1-v0-v4-0119-0315-nearestV2 yfallos previos sin cambios; boards/checkpoint SINstage.
