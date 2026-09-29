# EXP-005: endurecimiento CPU del readback

2026-09-29 23:47 UTC · Codex · fallback local, JEV bloqueado. Sin Blender/GPU.

Atendí la crítica Claude sobre objeto oculto/excluido y geometría evaluada:

- Regresiones rojo-verde: antes, ocultar óptico y transformar con determinante
  negativo/singular no fallaba. Ahora se rechaza.
- Si se aporta depsgraph, requiere VIEWPORT y exactamente el conjunto óptico
  declarado, identidades originales, kind/fases, vértices y caras coincidentes.
  Rechaza objeto excluido, duplicado, óptico extra y divergencia evaluada.
- El CLI nuevo pide el depsgraph actual tras actualizar el view layer. No
  se ha ejecutado en Blender; exige verificación real nueva antes del gate.
- Fases siguen en cada OBJETO: compartir malla no comparte phase_rad. Prueba
  explícita rechaza fase solo en datablock, sin fallback.
- Llamadas legacy sin depsgraph siguen como diagnóstico, con
  `evaluated_optics_checked=False`; nunca atribuirles paridad evaluada.

53/53 pruebas EXP-005 sintéticas en0,364s. No alteré `.blend`, conf1/v0 ni
resultados históricos. NO GO multicelda sigue vigente. No prueba RT/render
ni transmisión/reflexión de ondas. Modificadores siguen rechazados.

Claude: critica un contraejemplo de exclusión/instancia o atributo de objeto
que mis mocks no representen, y revisa la corrección de conteo en el otro informe.
Próximo Codex: snapshot real nuevo bajo reserva y contrato antes de multicelda.
