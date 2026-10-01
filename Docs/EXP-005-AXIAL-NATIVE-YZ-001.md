# EXP-005 — AXIAL-NATIVE-YZ-001

Componente opt-in CPU de proyección YZ estricta sobre16limbs signed512.
Consume coordenadas hi-lo del paquete input-only fijado por SHA; preserva
sourceIDs, orden, owner y primitiveID. No consume hit/length/field suministrados.
Usa las primitivas propias SIGNED512-001; no ejecuta productores antiguos.

Contrato: eje de rayo±X, coordenadas YZ EXACTAS en el perfil ABI retenido.
No perfil arbitrario con errores YZ: incertidumbre YZ no implementada.
Exactitud YZ es precondición del caller: coverage verifica el SHA esperado,
pero no convierte un SHA aportado por cualquiera en prueba de esa exactitud.
El oráculo independiente la contrasta contra ORIGINAL para los 13 paquetes
congelados. No extender la aceptación a otra escena sin verificar precondición.
Radios X se preservan en input y NO se reinterpretan como radios YZ.
Por triángulo calcula det,u,v,w con multiplicaciones/diferencias comprobadas.
Winding negativo se normaliza sin wrap; det=0 falla; algún u/v/w<0 es miss;
ninguno negativo y algún cero es boundaryFAIL; todos>0 es interior estricto.
Sin epsilon/snap/aumento de bounds. Intermedio fuera signed512 rechaza,
incluso si cancelación posterior podría dar un valor representable.

NO selección de eventos/raíces, autointersección completa ni árbol. Proyección
válida sólo indica clasificación sin borde/degeneración; no exige un hit.
Eso NO es geometría completa: contactos X deben seguir fallando por el otro
componente. BoundaryFAIL se conserva. Lgeom NO Lref ORIGINAL; no fase/campos.
No componente GLSL nuevo, compilación/driver/GPU, inferencia/RT/óptica física,
auth/fullpipeline/admisión/costes/eficiencia/promoción. Codec SHA no autentica.
CPU1hilo/hijo<=60s. JEV bloqueado/fallback LOCAL sin aval.
Skills feature-tests e inputs reutilizados: tarea propia mínima + oráculo
independiente, no barridos/replay de productores ni cambios a fixtures/runners/
shaders/contratos/cotas. Sharedboards/checkpoint locales SINstage.

Dependencia SIGNED512-001 reportSHA8c609597e36cb9df1324c9e396a47560984ee9bfd93c15e0c32fbf4689f0e5f1.

## Evidencia

8 tests PASS rc0/0,3571186s; 13 casos/14 fuentes/52 triángulos de input.
56 clasificaciones triángulo-fuente:26 interiores/26 misses/4 boundaryFAIL.
Nueve filas disponibles de ocho casos igualan misses y membresía de los
eventos retenidos, NO se recalculan aquellos productores ni se afirma selección.
Oráculo independiente de áreas orientadas de aristas (otro algoritmo): rc0
0,2333960s,171 huellas(168 heredadas+3propias),340 checks exactos contra YZ
ORIGINAL de snapshot de entrada. No gate original modificado, fase ni GPU.
2679 llamadas CPU nuevas incluyendo controles:382add/816sub/423mul/281compare/
777decode32. Dos rechazos de overflow esperados (mul/sub); degeneración,
borde, winding, traslación, tipos, caller-alias y tamper bajo contrato cubiertos.
Conteos semánticos NOcostes hardware/fullpipeline/energía; no benchmark GPU.
Raw584254bytes SHA1a46a363592d6f3d814424c5153bf9529a0a6c76087f0ce0d8f465e6d9eae48f.
Sin fallo numérico ni relajación de umbrales. Frozen boundary/contact/gap FAILs
preservados; outputs parciales no reemplazan gates de cadena completa.
