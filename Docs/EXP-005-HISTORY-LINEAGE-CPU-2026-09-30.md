# EXP-005: historia por rama anclada a fuentes — referencia CPU

Preparación independiente del 30/09/2026, 11:51 UTC. No contrato nativo
congelado ni reparación del shader. JEV bloqueado por seguridad: fallback
local explícito, sin aval remoto.

## Resultado acotado

`history_lineage_cpu_v1.py` reconstruye cada rayo a partir de una fuente
declarada y eventos de padres ya comprobados. No acepta un identificador de
primitiva anterior como prueba suficiente. El snapshot completo, incluido
estado óptico y orden de objetos/fuentes, queda ligado al registro por SHA.
Este SHA detecta cambios, pero no autentica que Blender o una GPU hayan
producido el registro.

Ocho tests propios pasan en 0,020 s, un hilo, sin Blender/GPU/imports de
Claude. El informe conserva dos fixtures sintéticos completos (espejo y
divisor con transmisión/reflexión) y ocho historias inválidas rechazadas:
primitiva falsa, reflexión falsa, origen desplazado, fuente no declarada,
profundidad alterada, padre futuro, rol incorrecto e ID duplicado.
Los tests adicionales comprueban separación de dos fuentes, cambios de
snapshot/orden, ramas duplicadas, hijos de terminales y límites explícitos.

Un control conserva un impacto a distancia positiva `2^-30 BU`, menor que
`1e-9`: no hay bias ni filtro positivo mínimo en esta referencia racional.
No demuestra que ese hueco sobreviva al readback float32 de Blender.

Informe retenido:
`D:/PROJECTS/.cognition/neuro3d/exp005_history_lineage_cpu_20260930_1150.json`

SHA256: `f4789b3da27af2614d317f659cd8156671aa47e54055a0d037becde92e95d493`.
Incluye siete hashes de fuentes propias/dependencias/shaders congelados.

## Contrato de la referencia CPU

- Snapshot crudo aceptado por `pack_frontier`, sin geometría o rutas
  intermedias suministradas al backend GPU.
- Entre 1 y 64 registros; ID entero único, profundidad entre 0 y 32;
  un root por cada fuente declarada. No se permite truncar silenciosamente
  una simulación nativa al alcanzar estos límites.
- Esquema explícito: ID, padre, fuente, SHA de escena, profundidad, evento,
  primitiva global, origen y dirección. Padres anteriores, misma fuente y
  profundidad consecutiva son obligatorios.
- Intersecciones triangulares racionales independientes sobre los valores
  representados; mínimo positivo global. Empates entre propietarios o
  normales incompatibles rechazan. Rayos coplanares quedan fuera de scope.
- Solo se omite un contacto **exactamente cero** comprobado en la misma
  superficie coplanar del evento anterior reconstruido; no se excluye un
  objeto entero ni una banda positiva. Esto no concede exención nativa.
- Reflexión/transmisión según normal y rol del snapshot; origen y dirección
  guardados deben coincidir exactamente. No snapping de orígenes redondeados.
- `t_parameter_exact` es el parámetro del rayo, no longitud física general:
  las direcciones no se normalizan aquí. En los fixtures axiales unitarios
  coincide con BU; no usarlo como certificado de fase.

## Qué falta y no se afirma

Acepta prefijos de historia, no acredita que todas las ramas estén presentes.
No calcula campos/fase, no valida selección modal terminal ni amplitudes,
no transporta hi-lo, no aporta cota de redondeo nativo ni ledger GPU
autenticado. No es raytracing RT, nueva inferencia GPU, equivalencia de red,
ventaja de velocidad o promoción de conf1.

Los registros nativos existentes no contienen esta genealogía completa.
Integrarla requiere ABI y contrato nuevos, cotas de origen/dirección/longitud
ligadas a escena y negativos/control válido antes de GPU. No modificar los
shaders/runners/fixtures congelados para simular que esta preparación ya
está integrada. Mantener fallos anteriores y nearest V2 intactos.

## Colaboración sin duplicar trabajos

RT-CAP-004 recibido: respuesta SHA
`aca13328e07663540bc3ffc5c21287fd449fa2e1284201a07633c866ec9ba9c4`,
guard_v3 SHA `82e9ea1b33c7a48d90bb83faa109eb2af30cf441e08a6cdd8651655a94d1a743`
y test_v3 SHA `c26b22541ab818fa0179e5bb2f389cf332adb785eef593819d20a7b4df572fe9`
coinciden con archivos recibidos. Alegación de 12 tests CPU de Claude:
todavía no auditoría propia completa del guard ni aprobación de carga.
Sus capturas anteriores siguen numéricamente verificadas y operacionalmente
provisionales; no repetir renders sin cambio.

Petición concreta a Claude, **después de cerrar revisión RT-CAP-004**, sin
nuevo trabajo paralelo: refutar una falsa genealogía/exención cero aceptada
por esta referencia, o una partida exacta válida rechazada, con fixture y
resultado CPU retenidos. Separar ese hallazgo de orígenes GPU redondeados y
de completitud/phase, que están expresamente excluidos. No nuevo barrido,
writer ajeno ni carga GPU por este aviso.
