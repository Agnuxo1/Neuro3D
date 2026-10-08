# OpticNeuroBlender: contribución operativa y revisión de novedad

La revisión permite descartar las reivindicaciones amplias de novedad. La contribución candidata se limita a un cálculo neuronal coherente desde una escena capturada, con una cadena verificable de identidad, completitud y cotas hasta la decisión. Su implementación completa y su originalidad todavía están pendientes. Esta conclusión permite desarrollar el instrumento sin presentar la integración como un descubrimiento demostrado.

Este hito amplía la [revisión histórica](LITERATURE_AND_NOVELTY_AUDIT_2026-10-08.md) y concreta el contrato v2; no sustituye su evidencia, la formulación v1 ni el piloto publicado. La nueva lectura primaria y sus hashes están en [el recibo de fuentes](research/operational_contribution_sources_v1.json). El corpus histórico conserva 194 registros, 175 únicos, 30 extracciones y 106 antecedentes sin extracción completa. La revisión dirigida adicional no cierra esa cobertura ni constituye una búsqueda exhaustiva.

## Problema y objeto comprobable

Sea Q la escena representada admitida: mallas evaluadas, transformaciones afines, unidades, fuentes, parámetros ópticos y modos terminales. Para una entrada compleja x y parámetros theta, la referencia es el conjunto completo de caminos pertinentes P(Q, theta), con

`E_d = sum_p a_p(x, theta) exp(i phi_p)`

`phi_p = 2 pi sum_s(n_s L_s / lambda_vac) + sum_j phi_j`.

En el modelo inicial n=1, las longitudes y la longitud de onda usan BU, y todos los puertos comparten portadora y referencia de fase. La intensidad normalizada es `q_d = |E_d|²`. No se atribuyen vatios sin una potencia de referencia explícita. Las decisiones proceden del readout declarado, no del brillo del render.

Para parámetros y geometría fijos, el transporte escalar pasivo es lineal en x. La detección cuadrática no convierte ese operador en una capa óptica no lineal ni acredita capacidad universal. El [análisis algebraico anterior](IRIS_LINEAR_FIELD_QUADRATIC_DECISION_2026-10-08.md) obliga a incluir una implementación matricial equivalente como baseline.

Una salida CERTIFIED exige simultáneamente:

1. Identidad del Q consumido, código, parámetros e input, incluyendo la representación realmente empleada por el backend.
2. Caminos completos o una cota de todas las contribuciones omitidas. Alcanzar un límite de profundidad no demuestra completitud.
3. Inclusión del campo exacto del Q admitido en el conjunto complejo publicado. La coincidencia entre dos programas en coma flotante no basta como prueba.
4. Cotas derivadas para intensidad, readout y decisión. Una decisión certificada requiere un margen estricto frente a todas las alternativas; un empate conserva estado indeterminado.

H1 se refuta con un único certificado falso independientemente verificado. Una ejecución incompleta sin certificado no refuta inclusión: refuta la utilidad en un miembro admitido de la familia fijada. La familia útil, sus tolerancias y los criterios de cobertura deben congelarse antes de su evaluación. No se ha congelado ni evaluado una familia confirmatoria nueva de H1 en este hito.

## Separar errores y rechazos

El error de aritmética se refiere a Q. La diferencia entre Q y una geometría original anterior a cuantización necesita una cota propia. La diferencia frente a un experimento físico necesita validación del modelo y mediciones. Ninguna de estas diferencias recibe cero por omisión.

Si las etapas comparten modelo, referencia de fase y norma, sus cotas de campo pueden componerse por desigualdad triangular. Una cota de caminos omitidos es `sum_p |a_p|`; un cutoff individual de potencia no la sustituye. Con `|E-E_hat| <= b`, se obtiene `||E|²-|E_hat|²| <= 2|E_hat|b+b²`. Este argumento es conocido; nuestra obligación es verificar sus hipótesis y enlazar los recibos de cada etapa.

Un presupuesto no conocido produce UNKNOWN_MISSING_BOUND. Un recorrido ambiguo o incompleto produce INCOMPLETE. No se transforma ninguno en cero, una predicción certificada, una máscara física ni un resultado exitoso. La exactitud de la captura por hash prueba integridad de datos, no fidelidad óptica.

## Contraste dirigido de antecedentes

| Fuente primaria | Solapamiento comprobado o documentado | Comparación que aún falta |
|---|---|---|
| [PBRT 4, §6.8](https://pbr-book.org/4ed/Shapes/Managing_Rounding_Error) y predicados exactos del catálogo histórico | Cotas de redondeo, intersección y origen de rayos; evitar un epsilon arbitrario tiene antecedentes | Mostrar qué evidencia adicional conecta esa geometría con campos coherentes y decisiones de nuestra red |
| [Sionna RT, conceptos y modelos](https://nvlabs.github.io/sionna/rt/tech-report/S2.html) | Escena, caminos y campos electromagnéticos; no podemos reivindicar esa combinación por sí sola | Igualar modelo, precisión, input y readout; diferenciar una estimación de un certificado determinista de inclusión |
| [Blender Optics Simulator, alcance fijado](https://github.com/emircbngl/blender-optics-simulator/blob/2b488e2e99dff4f56d67f57f9674bd00f812dda1/docs/OPTICS_SCOPE.md) | Física/interferencia, banco Blender y capa ondulatoria con límites declarados | Resolver grupos coherentes, modo detector y tolerancias antes de ejecutar una comparación equivalente |
| [BlenderPhotonics, versión fijada](https://github.com/NeuroJSON/BlenderPhotonics/tree/732799f9e3ebe10e013e316b8a21d88452755dc8) | Instrumento Blender, mallas, materiales y simulación científica | Su flujo de fluencia inspeccionado no proporciona el campo complejo de nuestro banco interferométrico |
| [OptiBench, README fijado](https://github.com/thepacket/optibench/blob/bceb97b640bc4cd70780f9a3fcc8dcd2c3fcd5c7/README.md) | Laboratorio abierto con caminos plegados, suma de campos y límites explícitos; antecedente adicional de integración | Inspección documental, sin ejecución ni auditoría completa aquí. Sus diagnósticos no deben equipararse a nuestras cotas; tampoco se presupone ausencia universal de certificados |
| LAMP, Ashtiani, Shen, Hughes y Pai, en el [catálogo primario](research/literature_catalog_v1.json) | Redes coherentes, 3D y entrenamiento fotónico tienen antecedentes directos | Una simulación Blender no constituye una nueva demostración física ni prueba superioridad neuronal |

La documentación de OptiBench fue recuperada en el commit de 2026-09-16. La solicitud inicial de `docs/validation.md` devolvió error; no se presenta como documento leído. Se conserva ese fallo y la lectura del README. Ningún software externo fue instalado, ejecutado o copiado.

## Criterio de cierre de la prioridad 1

La formulación operativa queda escrita y el resultado de la revisión dirigida es **NOVELTY_NOT_ESTABLISHED**. La prioridad científica completa permanece ABIERTA: faltan un algoritmo/certificado implementado de extremo a extremo, comparación verificable con los métodos próximos y revisión de los candidatos pendientes. No puede cerrarse positivamente mediante la mera ausencia de una frase en unos abstracts.

Las demás prioridades conservan sus gates propios: un test de software no valida precisión nativa; precisión numérica no valida fidelidad física; acierto histórico no valida generalización; una ejecución local repetida no es reproducción externa. El [estado actual de diez prioridades](research/optic_neuro_blender_acceptance_v1.json) registra resultados observables y bloqueos sin sustituir el historial de 26 puntos.
