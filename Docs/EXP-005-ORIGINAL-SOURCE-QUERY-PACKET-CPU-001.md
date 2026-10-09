# Paquete de consulta SOURCE original — candidato CPU, no ABI nativa

ID PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001; Codex capacity_audit/EXP005. Base ba87272570be38188cb0bee7ae8bbc7fcd08a3f6. Reanudación de dos archivos propios incompletos, sin resultados anteriores asumidos.

## Contrato opt-in CPU

Modelo explícito original-SOURCE-query-packet-CPU-candidate-v1. make_packet(point,direction,model=...) compone dos filas de evidencia retenida correspondientes al MISMO case/SOURCE/scene/query/input/previous_primitive/triángulo/bounds/source_record. Verifica enlace de dirección a la identidad CPU del punto, tipos uint32, endpoints racionales canónicos y correspondencia exacta entre palabras hi-lo y ambos extremos guardados. Los hashes son identidades de contenido CPU, NO firmas ni autenticación de escena. El llamador debe fijar sus recibos; el componente no autentica ni busca archivos.

| Offset bytes | Contenido | Tamaño |
| --- | --- | --- |
| 0 | Punto xyz, hi-lo uint32 por eje | 24 |
| 24 | Dirección xyz, hi-lo por endpoint inferior/superior | 48 |
| 72 | previous_primitive_id uint32 | 4 |

Wire little-endian19uint32/76bytes. SOURCE y hashes permanecen en envelope separado; doce envelopes para seis casos S0/S1, SIN deduplicar por wire igual.912bytes sólo payload lógico, excluye envelopes, alineación, memoria/temporales y costes. Es un layout CANDIDATO CPU, no promesa de compatibilidad con shader, OptiX, Blender o cualquier GPU.

audit_packet(packet,expected=...,model=...) exige esquema cerrado y consistencia interna incluso si expected fue suministrado por el llamador; además compara contra el slot CPU fijo. Copia su resultado para no compartir estructuras mutables. Todas las seis banderas de permiso/certificación quedan False; cotas de origen/fase=None y costesUNKNOWN_NOT_ZERO. No API de lanzamiento.

## Evidencia y corrección retenidas

Primer control4tests PASS para12paquetes/96NEG. Nueva regresión de consistencia produjo FAIL en5tests: slot punto contradictorio podía ser aceptado si packet y expected se resellaban juntos. Fallo/fuentes/stdout/stderr preservados en recibo; no se cambió tolerancia ni fixture. Se añadió validación independiente de slot/wire en el nuevo módulo. La regresión quedó inalterada tras FAIL.

Resultado final5tests PASS/113registros:12paquetes,48mezclas de filas rechazadas,48sustituciones reselladas rechazadas,5contradicciones internas rechazadas; además5assertions de previous inválido/no finito, sin filas adicionales. Stdout34522bytes SHA8b9b5ede220592740bab7f127840a0c4934484812e9ff57e9adb162fffbede06 losslesszlib/base64. Afinidad1/CPUbudget64MiB/timeout30s/deadlineUTCnuevo35s/RAMantes7963209728bytes; ejecución07:02:48..49UTC, tiempoQA no rendimiento.

Un intento post-fix se detuvo ANTES de crear el hijo por RAM insuficiente tras64MiB; no se obtuvo su valor exacto. STOP y errorretención conservados. Tras observar recuperación RAM7133179904bytes, se reintentó con comprobación independiente fresca y deadline nuevo. No se redujo presupuesto ni cotaRAM.

Se conservaron12anchos x de dirección no nulos:3/2^51 en direction_scaled y3/2^52 en los otros casos. Exactitud de transporte no significa incertidumbre geométrica cero. previous_primitive_id transportado NOprueba exclusión de autointersección. Etiquetas tiny_gap_2m60/outside_segment conservadas, NO nueva cobertura de huecos ni nearest ni raytrace.

## Límite y continuación

Componente: Blender/benchmarks/capacity_audit/original_SOURCE_query_packet_CPU_v1.py SHAbd39e42cdb59941470b0b37b662a003a22ea261f98aeba22829098d15642fc8b.
Test: Blender/tests/test_original_SOURCE_query_packet_CPU_v1.py SHAdcde0639fa2f2a79b1c836f1623de77e9253b9ec8c03a2320c5ffc1003e8f322.
Recibo: coordinacion/respuestas/PRECISION-ORIGINAL-SOURCE-QUERY-PACKET-CPU-001-CODEX.json.

Padres POINTe3d4a3e5f431b97fb83e121d4a9f06c9454e9f9849437721a7ed3e9b488fce07 yDIRECTION789c41b770050d1cdd25146e7efbcc9eb3216b17e3a730cc54f80012cb2a2a45 leídos/decodificados, NO productores antiguos reejecutados.461pins y35recibosCLAUDE en scope intactos. Cero queriesgeométricas nuevas/cero joinsnativos. NoGPU/Bpy/RT/SDK/cola/reserva/killajeno/publicación/push/merge. Runners/shaders/contratos/fixtures/bounds/FAILs intactos.

Skills resume-interrupted-task y feature-testing guiaron reconstrucción factual y regresión nueva; no heredaron un PASS del borrador. JEV bloqueado, fallbackLOCALsinaval/sinretry. Cuatro propios candidatos en revisión/versionado pendiente; sharedboards SINstage. Claude conserva RT/research: ACK ID+SHA y artifacts YA existentes consumerABI/input/previous/ALLcoverage/longitud-referencia-fase/guard/igualtrabajo-costes o faltantes concretos. M01..M14 retenidos, sin petición de nuevo render. No promover ni escalar antes de evidencia nativa/guard/reserva.
