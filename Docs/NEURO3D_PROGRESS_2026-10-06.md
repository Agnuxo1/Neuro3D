# Neuro3D Codex-Claude-JEV Santo Grial: estado de ejecución

Fecha: 6 de octubre de 2026. Trabajo realizado en la rama `codex/neuro3d-consolidation-20261006`, dentro de `D:\PROJECTS\Neuro3D-Integration-20261006`.

## Resultado de esta secuencia

**Los puntos 1, 2 y 3 están cerrados con cambios y comprobaciones conservados. El punto 4 sigue abierto: el código candidato y los controles CPU están preparados, y queda pendiente la validación GPU real.** Los puntos siguientes mantienen su orden y no se han declarado completados por anticipado.

Esta numeración es una hoja de trabajo del proyecto. No representa requisitos oficiales del Nobel ni una medida porcentual de proximidad a ese reconocimiento.

## Puntos cerrados

### 1. Consolidar las ramas

Se creó un worktree separado y se integraron las historias local y pública. El merge conserva ambos padres y las evidencias históricas; se recuperaron 50 fuentes y artefactos locales. Se comprobaron 455 referencias históricas relativas y 17 controles CPU, también desde un checkout limpio. El worktree original quedó preservado.

Commit: `63dee34675f0b1de1e032b3b91a87ac09b2eced3`.

Evidencia: `Docs/validation/consolidation-2026-10-06.json`.

### 2. Entregar y verificar el paquete Iris portable

Se regeneró el archivo `.blend` portable y se verificó mediante una apertura en un proceso independiente. La evaluación cubrió las 150 muestras: 117/120 clasificaciones correctas en entrenamiento y 29/30 en la partición de prueba, sin discrepancias de clasificación entre la referencia y la escena comprobada. También se comprobaron los rechazos ante activos ausentes y manifiestos inválidos.

Son resultados de la partición y configuración conservadas. No demuestran todavía generalización amplia ni ejecución de la red completa mediante el backend GPU nativo.

Commit inicial: `5b2e9c5475ddb60fb8d36c15bff270533980f926`; paquete actualizado tras el punto 3 en `8f9a54cb118043ff47d1b09b64e214fa2a676a6f`.

Evidencia: `Docs/validation/iris-portable-2026-10-06.json` y archivo histórico `Docs/validation/iris-portable-point02-2026-10-06/`.

### 3. Corregir reconstrucción interactiva y colisiones de nombres

Se reprodujo el problema: la versión previa falló seis de siete casos de la nueva regresión. La corrección mantiene la pertenencia de colecciones, materiales y detectores a su escena; los sufijos que añade Blender dejan de desviar la selección de componentes.

La versión corregida superó los siete casos, con 230 comprobaciones, además de cinco contratos y los controles existentes. Después se regeneró el paquete portable y se repitió la verificación completa de las 150 muestras. Las salidas conservadas coinciden con las del punto 2.

Commit de la corrección: `7c037702486ae9ab153f605edab432b85c44ba0d`. Cierre y paquete actualizado: `8f9a54cb118043ff47d1b09b64e214fa2a676a6f`.

Evidencia: `Docs/IRIS_REBUILD_VALIDATION_2026-10-06.md` y `Docs/validation/iris-rebuild-2026-10-06.json`.

## Punto 4: precisión CPU en datos de escena y operaciones nativas

El candidato está fijado en `b305043016427d796aff4eb649e090961db026ff`. Se prepararon y reabrieron tres escenas; sus paquetes contienen 847 escalares y 39.072 bytes. Dos son los casos K3/K4 conservados y la tercera es un control numérico explícito.

Han pasado 16 controles del adaptador, la auditoría independiente de los 847 escalares y 17 controles del supervisor. El contrato CPU del oráculo cubre 7.026 componentes previstas, rechaza 18 alteraciones y detecta una entrada superior a 32 KiB. Esos resultados no son lecturas GPU.

El piloto debe ejecutar seis llamadas nativas, devolver todos los bytes e identidades previstos y conservar dos testigos exactos: `1 - 2^-60` y `1 + 2^-30 - 2^-60 - 2^-100`. El control que elimina las partes bajas debe cambiar únicamente los resultados esperados. Un auditor separado recalculará todos los resultados desde los snapshots originales mediante aritmética racional.

Se conserva el primer ensayo fallido del supervisor, así como el borrador de transporte descartado antes de ejecutar GPU por una incompatibilidad de la API de Blender. La compilación y la ejecución del candidato nativo continúan pendientes mientras no se obtenga un turno y se complete la prueba.

Detalle del método y evidencias: `Docs/SCENE_HILO_NATIVE_PLAN_2026-10-06.md`, `Docs/SCENE_HILO_NATIVE_VALIDATION_2026-10-06.md` y `Docs/validation/scene-hilo-native-2026-10-06/`.

## Bloqueo actual y reanudación

Se intentó obtener turno tres veces, con esperas reales de 20,227 s, 120,370 s y 240,618 s. En los tres casos la cola terminó antes de lanzar el supervisor o Blender. A las 22:46:57 UTC, otro trabajo vivo, `villa:legitimate-replay-v15`, conservaba válidamente el turno. No quedaban tickets de estos intentos.

Para continuar tiene que finalizar o liberar su turno ese trabajo. Después corresponde un lanzamiento nuevo, con UUID, plazo, hashes comprobados y destinos nuevos. Las seis lecturas deben pasar tanto el verificador del worker como el auditor independiente; el cierre del proceso y los recursos también deben pasar. Los manifiestos de los intentos anteriores caducan y se conservan como evidencia, no como autorizaciones reutilizables.

No se ha detenido ningún proceso ajeno ni se ha avanzado al punto 5. El estado exacto del punto 4 es `CPU_PREPARED_NATIVE_BLOCKED`.

## Estado de los 24 puntos

| Punto | Trabajo | Estado y condición de cierre |
|---:|---|---|
| 1 | Consolidación de ramas | Cerrado: merge, preservación y controles desde checkout limpio. |
| 2 | Paquete Iris portable | Cerrado: archivo regenerado, apertura independiente y verificación de 150 muestras. |
| 3 | Reconstrucción y nombres | Cerrado: fallo reproducido, corrección y regresión funcional completa. |
| 4 | Integración hi/lo nativa | Abierto: candidato y CPU comprobados; faltan compilación, ejecución y auditoría GPU. |
| 5 | Geometría difícil | Pendiente: integrar y comprobar huecos pequeños, contactos, exclusión de primitivas, empates y tolerancias. |
| 6 | Cotas de longitud, fase y campo | Pendiente: garantía completa de propagación del error hasta la salida. |
| 7 | Equivalencia y reducción de caminos | Pendiente: regla justificada y controles de conservación de coherencia. |
| 8 | Red entrenada sobre GPU nativa | Pendiente: datos, parámetros en escena, propagación, clasificación y evaluación completas. |
| 9 | Ruta RT coherente | Pendiente, si se conserva: campos, fases, referencias y contraste con oráculo. |
| 10 | Unreal | Pendiente, si se conserva: compilación real, lectura de resultados y paridad. |
| 11 | Supervisión GPU completa | Pendiente: el supervisor acotado del punto 4 es una dependencia concreta, no el cierre de toda esta línea. |
| 12 | Reproducción automatizada | Pendiente: ejecución integral desde versión limpia y dependencias declaradas. |
| 13 | Aportación central falsable | Pendiente: formular y contrastar una contribución científica precisa. |
| 14 | Comparación con literatura | Pendiente: revisión de antecedentes primarios y delimitación de la novedad. |
| 15 | Capacidad matemática | Pendiente: expresividad, estabilidad, condicionamiento y límites de la topología. |
| 16 | Generalización | Pendiente: particiones y semillas adicionales, incertidumbre y tareas nuevas. |
| 17 | Comparaciones equivalentes | Pendiente: misma tarea, salidas, precisión y presupuesto. |
| 18 | Coste completo | Pendiente: tiempo, memoria y energía con límites de medición explícitos. |
| 19 | Escalado funcional | Pendiente: crecimiento del trabajo y la calidad con unidades comparables. |
| 20 | Ablaciones | Pendiente: separar el efecto de cada componente del sistema. |
| 21 | Evidencia física | Pendiente: experimentos reales para sostener afirmaciones físicas. |
| 22 | Reproducción externa | Pendiente: ejecución independiente por personas o laboratorios externos. |
| 23 | Artículo científico | Pendiente: argumento, método, resultados, límites y materiales reproducibles. |
| 24 | Consecuencia científica importante | Pendiente: demostrar una aportación de alcance excepcional. |

## Cómo se interpreta esta evidencia

La preparación de software, una simulación verificada, la ejecución de una GPU y un experimento físico son hitos diferentes. Las revisiones internas realizadas aquí tampoco equivalen a reproducción científica externa. Cada conclusión queda limitada por el dispositivo, los datos, la versión y el método que la respaldan.

La próxima acción de esta secuencia es cerrar el experimento del punto 4. Sólo entonces corresponde iniciar el punto 5, respetando el orden solicitado.
