# Dos vías de registro: autorización humana recibida

El 2026-10-09 el propietario indicó directamente en este chat: «Vamos a trabajar en las dos vías: “Autorizo el protocolo congelado en GitHub” o “Mantener registro externo/IPFS”». Se acepta la autorización explícita para el piloto ya congelado en GitHub y se mantiene el trabajo de registro externo como vía adicional. No se volverá a solicitar la misma autorización.

## Vía GitHub

El [recibo nuevo de autorización](research/captured_pilot_github_authorization_2026-10-09.json) vincula el mensaje humano real al UUID `957514f2-a233-421f-aa04-50cccd063d97`, SHA256 `5d0cf372f2f66f043c2a219ba6a60f0182ced8a60039348d486ec163be736226` y commit congelado `f22e7a1307e3a3b4c74a507463a0a8055d45fc04`. El protocolo, sus inputs, fuentes y umbrales no cambian. El formulario preparado anterior conserva `approved=false` como documento histórico; no se reescribe como autorización.

La excepción permite ejecutar ese piloto mediante el supervisor preparado y sus límites. El [intento real](CAPTURED_PILOT_EXECUTION_2026-10-09.md) agotó 90 segundos sin resultado y conserva métrica nula; no hay conclusión H1. Esta autorización no equivale a preregId/IPFS externos: ambos siguen nulos.

## Vía externa/IPFS

Se mantiene como objetivo obtener y verificar un registro real. Los antecedentes de acceso autenticado fallido siguen vigentes como límite operativo; no se reintentan credenciales inválidas ni se inventan IDs.

Si un registro externo se obtiene antes del piloto, su orden temporal se conservará con evidencia. Si se obtiene después, no se presentará como preregistración prospectiva de un ensayo ya ejecutado. Los futuros ensayos confirmatorios que utilicen esta vía deben congelarse y registrarse antes de recoger sus datos. El registro externo y la excepción GitHub se documentan por separado.

## Estado científico

Continúan verificadas la captura/admisión de Iris, los contratos y 66 controles de software. El piloto tiene desenlace inconcluso documentado. Siguen pendientes la viabilidad de recorrido completo, la cadena de propagación/cotas/decisión desde la captura, entrenamiento, generalización, comparación/coste, fidelidad física, originalidad y reproducción externa. La fabricación de un procesador es opcional para el instrumento Blender y necesaria solamente para las afirmaciones que dependan de un dispositivo fabricado.
