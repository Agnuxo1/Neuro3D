# PRECISION-POSITION-PHASE-REFERENCE-UNIT-NATIVE-CPU-001

Backend parcial CPU opt-in capacity_audit/EXP005, basef37810a. Consume solo evidencia sellada UNIT-HOST001 SHA f83bd046776cafcf3fd7db70aa11978ce6e1e7119fe80fc79c513fbf912d6002/388070bytes, 777 entradas/15HOST/762STOP. No importa/repite productor ni suite padres. Mismo selector SOURCE/ORIGINAL/overlay/referencia1-target3; ninguna ampliación de bounds/conf1/fixtures congelados.

## Contrato numérico explícito

Los16bytes deben coincidir ANTES de decode yALU. Se decodifican dos palabras radianes, después ejecuta RN64 hi+lo UNA vez. No es transporte hi-lo sin pérdida: x=exactHOST(hi)+exactHOST(lo), y=RN64(hi+lo), Ecollapse=|y-x| se retiene y carga dos veces para errorL1. Scalar INTERNO explícito, no fase scalar exportada. Puede perder low2^-60, control que demuestra y cobra esa pérdida, no la oculta. No wrap/recenter/quarter/tolerancia axial2e-12.

Dominio antes suma |x|+Bangle<=1rad; después |y|+Bangle+Ecollapse<=1rad. Capfase original1e-4rad; capunidadL1=2*capfase=2e-4 fijo. Para cos12/sin13 Taylor centrados0, Bpre=2*Bangle+2*Ecollapse+|y|^14/14!+|y|^15/15! se comprueba ANTES del Horner. 14 coeficientes exactos racionales se convierten RN64 con palabras y error medido. Grafo26nodos Horner SINFMA, más suma argumento1=27. Python float IEEE radix2/mant53/maxexp1024; oráculo verifica RNEties por enteros, no biblioteca trig.

Error separado por componente: E_RN y E_coef. Si z_exact=y², z_native=RN64(y²), Ez=|z_native-z_exact|, en producto h*z: E_RN'=|h_native|*Ez+|z_exact|*E_RN+|delta_mul|, E_coef'=|z_exact|*E_coef. En suma coef: sumar |delta_add| aRN y|delta_coef| acoef. Inicial E_RN=0/E_coef=errorcoef6. Sinfinal multiplica ambas cotas por|y| y añade |delta_mul| aRN. Todos cargos positivos; no compensación entre fuentes. Bfinal=Bpre+sum(E_RN)+sum(E_coef)<=capunidad. Enclosures de cada componente nativa v±(Bangle+Ecollapse+R+E_RN+E_coef). Comparar oráculo polinomial exacto a y: |v-P(y)|<=E_RN+E_coef; diferencia con x cargada por derivadas de trig acotadas1.

Solo IEEE normal/±0; no FTZ implícito. Inputs/nodos normales y resultado EXACTO nozero debajo2^-1022 provocan STOP tras preservar nodo yaejecutado. Subnormales entrantes paran antesALU. Fallos prebudget/postbudget separados; conservar conversiones/nodos/diagnósticos parciales/costos sin convertir STOP aPASS.

## Alcance y verificación

Salida dos componentes nativas cos/sin polinomiales, NO dos limbs de fase ni |u|=1 normalizado, NO campo/amplitud/potencia físicos. Escena aún CPU sintética con incertidumbre declarada, no referencia calibrada ni auth/completitud/backendGPU/RT. U/GEMM no sustituyen inferencia desde escena. Costes completos UNMEASURED_NOT_ZERO; contador27nodos y14coef no mide tiempo/coste total ni establece ganador.

Tests focalizados sobre777 padres retenidos,128bits,5wire,selector/modelo estricto, API ymissingreceipt. Diez helpers UNBOUND (noescena): zero/±zero/hi+lo±half, prebudgetSTOP, domain-radiusSTOP, subnormalinputSTOP, underflowsquareSTOP con2nodos/14conversions preservados, capoverSTOP, postbudgetSTOP con27nodos/14conversions. Oráculo independiente sobre todos nodos/palabras RNE por enteros, coeficientes/propagación/error/cotas/fases-contextos/pins, negativos alterados de evidencia.

CPU1hilo/afinidad1/hijo<=60s; GPU/Blender0, deadline histórico intacto. Nuevosbackendcontrato/tests/commit antes cualquierGPU; congelados intactos. Skills cogniciónextendida ydesarrollo focalizado reutilizan capturas yevitan barridos idénticos. JEVbloqueado: fallbackLOCAL sinretry/avalremoto. Versionar únicamente own4 revisados, sharedboards/checkpoint SINstage. SolicitarClaude SOLO ACK ID+SHA yartifacts YA existentes mismoORIGINAL-contexto/reference-auth-completitud/backendguardfailclosed/igualtrabajo-salidas-costes completos ID/path/SHA/bytes.

Medición retenida:924main=15CPU+909STOP (762 heredados+147 nuevos negativos),405nodosRN64/210conversiones main. APIduplicada27nodos/14coef aparte; diez helpers138nodos/84conversiones aparte. SuitePASS1.1603625000007014s/raw2056443<2097152/SHA8d8c860956222923760daa94fae08e22501751347b2caeaf78a68cb9a0163371. Oráculo independiente PASS0.85199620000094s/232pins, ocho alteraciones rechazadas. Dos capturas de suite propias: primera numericexit0 pero transporte truncado, segunda mismoSHA/raw íntegro con mayor límite de transporte; nada de código/umbral/dominio se modificó para rescatarPASS. Coste de ambas suites1140nodos/616conversiones, no coste completo. Fallos administrativos ruta cwd/aplicador/parse JS preservados enrecibo.
