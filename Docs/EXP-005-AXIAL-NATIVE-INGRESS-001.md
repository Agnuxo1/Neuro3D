# EXP-005 — AXIAL-NATIVE-INGRESS-001

Ingreso HOST opt-in de inputs de escena; no backend ejecutado.
Depende de CONTRACT-001, report SHA
c01575b67e5a097df08d1254247c192d91d737af2c17a727f85f9ef3d8df2948,
plan SHA472ac95b0a30c1bd1674223fc3ab563323cd14590bc4091af494d1d1e412fdb1.

Layout little-endian uint32, sin padding:

| Buffer | Registro |
|---|---|
| triangles | owner + 18 words XYZ hi-lo + 16 limbs radio signed512 = 35 words |
| sources | 6 words origen + 6 dirección + 16 radio + 4 campo ORIGINAL binary64 = 32 words |
| wavelength | 2 words hi-lo + 16 radio = 18 words |
| reference | disponible uint32 + 12 words origen/dirección ORIGINAL binary64; sólo si disponible añadir 2 hi-lo X + 16 radio = 13/31 words |

Cada radio es no negativo menor que2^511, escala BU*2^149. No wrap,
saturación, snap, epsilon, borrado del radio declarado ni defaults por rechazo.
Referencia HOST ausente se conserva como ausente, no equivalente a cero válido.
Cada fuente conserva los bits del campo ORIGINAL incluso en casos STOP.
Original_scene_json contiene sólo el snapshot de entrada original completo
(incluye phase_rad de espejo); input_metadata_json incluye whitelisted ABI,
IDs/orden, gauges/referencia, caps originales y agrupación explícita.
Agrupación sigue HIPÓTESIS CPU, no autenticación de coherencia física.

No outputs/gates/cached units/productos/potencias/U-GEMM/certificados de árbol
en ningún buffer. El SHA del plan completo vincula el contrato para inspección;
NO proporciona respuestas al kernel. Manifest por buffer: bytes/SHA/layout.
verify_packet compara bytes originales exactos incluso si se rehashea la corrupción;
es recibo CPU de inputs, no upload/dispatch ni guard/admisión.

**Pendiente:** encoder HOST campo binary64→hi-lo32 con cargos explícitos,
consumo nativo de signed512/signed256/RN64, geometría/árbol/autointersección/gaps,
fase/referencia/productos/reducción efectivos y costes completos.
Este módulo NO convierte el campo a hi-lo, NO implementa kernel,
NO promociona ninguno de los FAILs ni satisface evidencia nativa CONTRACT-001.
No repetir productores/suites congelados: sólo desempaquetado de bytes retenidos.
CPU1hilo/hijo<=60s; no GPU, Blender, RT, instalación, publicación ni merge.
JEV bloqueado: fallback LOCAL sin aval remoto. Boards/checkpoint SINstage.

## Evidencia

9 tests propios PASS rc0 en0,3635104s, CPU1hilo/hijo60s.
13 casos/14IDs; cinco referencias HOST ausentes preservadas, radio declarado
2^142 transportado sin alterar aunque snapshot/binding original sean iguales.
Controles bytecorruption rehashed/foreignbuffer/endianness/stride/counts,
sourceorder/sourcefield/reference/planexpectedgate swaps rechazados;
signed512 overflow/uint32bool/NaN/duplicateJSON/signedzero verificados.
Verificador independiente stdlib de buffers/layout/radios/bits originales,
fingerprints y whitelist; no importa productores ni recalcula fase/campos.
Independiente rc0/0,1912145s:158huellas13casos14IDs52triángulos,
2815words/45805bytes de inputs (incluye JSONoriginal/metadatos), ocho referencias
HOST disponibles/cinco ausentes. Esto es tamaño de inputs HOST, NO VRAM/RAM,
coste de dispositivo, pico global o rendimiento comparativo.
Raw del test96730bytes; SHA verificable en el report propio. No fallos numéricos.
Extensión de tests detectó por lectura un encabezado duplicado vacío y lo retiró
antes de ejecutar; no cambió raw numérico, límites, fixtures o FAILs congelados.
