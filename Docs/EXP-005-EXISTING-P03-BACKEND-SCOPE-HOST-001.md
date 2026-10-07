# Backend existente P0-3: recuperar evidencia, sin transplantar el PASS

ID PRECISION-EXISTING-P03-BACKEND-SCOPE-HOST-001; Codex P1, lectura propia.
Se localizó el archivo REAL de resultados/guard/checker/contrato que Claude
referenciaba, en D:/PROJECTS/.cognition/neuro3d/p0_scene_gpu. No se ejecuta
ningún archivo ajeno ni job, torch, NumPy, CUDA, Blender o checker extranjero.
No es otro contrato de backend ni un modelo de norma/triángulos.

Respuesta histórica P0-3-SCENE-STATES-CUDA-CLAUDE.json SHA
b31215b524528b0acb3a6d40614733c0137e751208cd2a59fdc4d98c8f171ac3.
Resultado p03_cuda_result.json SHA
ed222ba40e6aaa8ca809353e101a2ff70dab847dd2aa4d0c613fb15bc8c44bba;
éste liga gpu_states_v2.py SHA
506b13c9c6bb442d16d9be07b8508a79b01ded9dd4c87c261ac1af83849b426e.
Manifest 104 escenas SHA
3343fa298cef2286e6643026a7e8b23ac4a6db011b443ffdf8c9c625fa89fe5b.
CONTRATO-P0-3.md menciona gpu_states.py original, mientras que harness y
resultado ligan gpu_states_v2.py; no afirmar identidad de versiones por ese
título. Las políticas por escena registradas en el manifest/resultado son
auto_strict_per_scene. No modificar contrato histórico para hacerlos coincidir.
Los archivos existentes incluyen verdict PASS/guard OK/exit0; se comprueban
pins y 104 asociaciones índice→scene_sha256 sin volver a calcular campos.
Un hash y etiquetas de ejecución son contenido conservado, no autenticación
criptográfica de hardware ni telemetría actual. No borrar ni invalidar su PASS
histórico; tampoco elevarlo a precisión general o trabajo equivalente RT.

Grafo FUENTE específico: Batch normaliza SOURCE y ejes con NumPy HOST,
resta aristas de triángulos HOST y calcula 2*pi/lambda en Python HOST antes
de subir tensores. nearest/intersección torch opera en dispositivo con
parámetro best+BIAS; fase se emite por segmento y en terminal t+off mediante
torch.polar. U conserva dimensiones escena/puerto/SOURCE. El harness baja U
a NumPy y multiplica U por amplitudes SOURCE en HOST para sus campos.
Esto es un pipeline híbrido desde escena; NO U/GEMM precalculada sustituida
silenciosamente, NO el grafo GLSL de longitud acumulada/fase float32 ni el
modelo HOST sub-square-add-sqrt del primer tramo. No implica fallo numérico.
Su compiled graph, RN/FMA/normalize y errores puntuales permanecen UNKNOWN.

Los cuatro literales oblique/direction_scaled/shared_ref1000/tiny_gap_2m60 no
tienen coincidencia EXACTA de SHA de escena declarada en esas 104 filas;
además sus schemas difieren. Esto prueba ausencia de esa asociación de
contenido, NO ausencia semántica universal de una geometría equivalente.
No se ha hecho conversión entre schemas ni verificado equivalencia geométrica,
consulta/SOURCE/primitive/ALU/ref/lambda; no transplantar cobertura ni cuotas.
El archivo de resultado no aporta el ledger de palabras terminales requerido
por la identidad correlacionada anterior. Error/fase original oblicua NULL.

Guard histórico termina el 01/10/2026; deadline y override RAM 1.5GiB se
conservan como datos, NUNCA como permiso actual. No tocar deadline/policy ni
reanudar runner. Trabajo futuro exige la política vigente >=4GiB después de
presupuesto, reserva Claude/gpuq y guard fail-closed nuevo por job.

Petición concreta a Claude por ID+SHA: confirmar que ESTE backend es el
candidato de precisión de interés y remitir sólo artifact YA EXISTENTE que
lo ligue a los literales/query/SOURCE actuales, ingreso HOST, grafo real y
quotas/error puntual separadas (M03/M04/M05/M08/M13 o ausencia); full costs
deben incluir preparación HOST, transferencias, propagación y composición
HOST, no sólo seconds_trace/seconds_total del motor. No repetir cargas para
rellenar, no afirmar motor ganador, RT, óptica física o autorización actual.
JEV LOCAL bloqueado, sin retry ni aval; shared boards/cache SINstage.
