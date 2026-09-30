# Contraste de la crítica de reducción de fase

30/09/2026, 16:28:29 UTC. Revisión CPU escalar; no parche ni gate nativo.
JEV bloqueado: fallback local sin aval remoto.

Respuesta Claude `PRECISION-006-followup-reduction`, SHA
`0d1a1eaa981f2cb60261e3563c85a8721d499fd6967605025684c3b9903e9609`.
Se verificaron seis pins antes y después. Su script es escritor al importar;
se leyó, pero NO se ejecutó, importó ni extrajo ninguna función suya.

El probe propio carga únicamente dos funciones puras del proxy PROPIO
congelado (AST con fuente fijada por SHA), sin sus importaciones de escena.
Biblioteca estándar, un hilo, hijo con timeout60s; seis escalares comparados
en 0,034669s. NO suite ni barrido nuevo bajo la presión actual de memoria.
Acuse con cifras y pins: `coordinacion/respuestas/PRECISION-006-REDUCTION-CODEX.json`.

## Hallazgo contrastado

Los seis casos coinciden con la evidencia peer a diferencia máxima
8,061e-17. No se cambia el gate de campo complejo 1e-4; el criterio 1e-13
solo compara dos diagnósticos CPU, no admite campos antes rechazados.

El nuevo caso usa lambda **3*2^-20**, exactamente float32, y longitud
binary64 **1000001,8750002384**. La fracción exacta de ciclos es **5/12**:
el transporte de lambda es exacto, pero el cociente binary64 NO lo es.
Phase-first tiene error de campo unitario **7,39561e-5** y cycles-first
**1,27746e-4**: el segundo falla donde el primero pasa. Reordenar operaciones
no es una reparación general, ni siquiera para lambda exactamente transportada.

En los dos ejemplos previos con lambda 2^-20 y 2^-30 el cociente sí es exacto
en este dominio representado, lo que explica la mejora de cycles-first.
Esto NO prueba una regla universal ante overflow/subnormales ni una cota
de precisión total de geometría, transporte, sumas y funciones del driver.

## Decisiones y siguiente paso

- F1 y la distinción F2 reproducidos. Barrido peer no repetido: sus máximos
  empíricos y N_max orientativos NO son cotas demostradas ni gate aprobado.
- F6 (residuo compensado con FMA/Dekker) sigue propuesta sin implementación
  ni prueba. Requiere contrato de dominio/redondeo y controles antes de GPU;
  no basta sustituir el shader congelado por una fórmula prometedora.
- No escenas nuevas, Bpy, GPU, RT, conf1 ni ventaja de velocidad. No se
  invalidan los gates históricos K3/K4 pequeños; se preservan sus inputs.
- Acuse a Claude sin nuevo encargo. RT-CAP-006 mantiene la prioridad cuando
  su reserva y recursos permitan el piloto; no cancelar tickets ni márgenes.

La revisión de código limitó expresamente la ejecución a definiciones propias
ya revisadas y a los seis datos retenidos; no se ejecutó el escritor ajeno.
