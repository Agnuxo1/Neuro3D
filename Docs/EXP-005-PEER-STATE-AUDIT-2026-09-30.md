# Auditoría independiente de fusión por estados: longitudes de onda y claves

30/09/2026 05:28UTC, Codex. Fallback local: JEV bloqueado. Auditoría solo CPU;
no Blender ni inicialización CUDA. No se modificó el código de Claude.

## Procedencia y alcance

Se leyó íntegro `D:/PROJECTS/.cognition/neuro3d/nebulatrace/gpu_states.py` y se
ejecutaron únicamente Batch(dev='cpu'), trace(max_levels=8) y _hash en casos
pequeños propios. No ejecutamos bench_scale.py ni scripts que escriben archivos
de Claude. SHA de peer antes y después:
`3d0bc1127bc86347eab3bec3753090651704178d8da20ea793452dd1acad9061`.
torch2.6.0+cu124 con un hilo; cuda_initialized=False. Cuatro triángulos por
escena, dos escenas, cuatro estados en cada prueba. NO medición GPU ni ventaja
comparativa. U es salida compilada explícita, no inferencia geométrica Blender.

## Fallo reproducido: lambda del primer elemento aplicada a todos

Una fuente a(0,0,0), espejo x=1 y detector x=−1: longitud total3BU, reflexión−1.
Se contrasta el campo contra el oráculo triangular independiente completo.

| Lote | Lambda almacenada por peer | Máx. error complejo | Rechazo |
|---|---:|---:|---|
| 0,125 / 0,125 | 0,125 | 0 | No, control válido |
| 0,125 / 0,14 | 0,125 | 1,9498558244 | No |
| 0,14 / 0,125 | 0,14 | 1,9498558244 | No |

La potencia no delata este error: ambos campos tienen módulo1. Cambiar el orden
del lote cambia qué escena es incorrecta. Causa: Batch.self.lam y self.k se
obtienen solamente de snaps[0]; trace usa el k escalar para todo el lote.
Corrección requerida a Claude: rechazar lambda mixta antes de construir el lote,
o guardar k por escena y usarlo en cada tramo/terminal. No reinterpretar bandas
distintas como una sola longitud de onda silenciosamente. No afecta por sí solo
a la evidencia anterior si todos sus elementos tenían exactamente la misma λ;
hay que contrastar los inputs originales antes de ampliar esa conclusión.

## Cuantización: clave compartida sin igualdad de estado

Para escena0, dirección(1,0,0) y posiciones(5,0,0)/(5+0,4e−9,0,0), _hash da
la misma clave8026870879052046185 aunque delta=4,00000033096e−10BU. Esto es
aliasado por cuantización, no una colisión aleatoria de64bits. Register fusiona
por esa clave sin comparar el estado completo.

Ilustración analítica: con λ1e−6, esa diferencia en longitud de un futuro tramo
produce diferencia de campo0,00251327 para amplitudes locales iguales. Esto NO
es un error de red completa reproducido, ni valida esa λ en Blender/RT. Sí prueba
que una probabilidad baja de colisión hash no controla el error de cuantización.
Requerimos igualdad completa de claves, tolerancia óptica dependiente de λ y
fase/referencia/coherencia/modo, o rechazo explícito cuando no puede garantizarse.
Un hash puede indexar candidatos; no debe certificar igualdad por sí solo.

## Evidencia y siguiente paso

- `D:/PROJECTS/.cognition/neuro3d/exp005_peer_state_audit_20260930_0526.json`.
- SHA `b183f07b4079f7a879b417e343435fc12f3dc9ad9d4d7ce084d12f9e3dc31639`.
- Auditor propio `Blender/tests/exp005_peer_state_audit.py`; tres regresiones
  de fixture/oráculo/readback, total169testsCPU PASS8,546s.
- Mantener el backend de Claude exploratorio; no promocionar generalidad,
  longitudes de onda heterogéneas o aceleración frente a otras redes.
- Pedir a Claude fix y artefactos retenidos; después reauditar versiones nuevas.
  Codex puede preparar el piloto nearestV2 independiente sin esperar ni duplicar.

## Reauditoría CPU del parche, 05:34 UTC

Peer SHA `a39cc506dad29de8e87bc37e875504f5d0c6d5eff1ab228a48c83ac5bcf0a12f`:
el número de onda ahora es por escena. Los dos órdenes del lote mixto coinciden
con el oráculo independiente hasta 7,20e-15; el control uniforme mantiene error0.
Una colisión hash forzada entre claves cuantizadas distintas se rechaza. Esta
prueba modifica únicamente el módulo importado en el proceso auditor; el archivo
peer queda intacto. No se inicializó CUDA y se usó un hilo CPU.

Permanece el aliasado por cuantización: las posiciones5 y5+0,4e-9 comparten
clave6877709230612046977. Comparar claves cuantizadas no demuestra igualdad
óptica del estado original. El ejemplo analítico de fase anterior no equivale
a un fallo de red completa; se solicita a Claude un adversario retenido de dos
ramas y una política de tolerancia dependiente de longitud de onda, modos y
referencia/coherencia antes de promocionar esa fusión.

Evidencia nueva, sin reemplazar la anterior:
`D:/PROJECTS/.cognition/neuro3d/exp005_peer_state_audit_20260930_0534.json`.
Se acepta aquí solo la reparación CPU de lambda mixta y colisiones hash;
no se certifica runtimeGPU, ventaja comparativa ni fusión óptica general.
