# Enmienda previa a GPU: simetría del control T y campo complejo

V1CPUrechazado preservado6626178, sinGPU. Mantener7escenas/9probes, precisiones,
geometría/coeficientes/ABI y TODOS los umbrales. El efecto de potenciaT se mide
entreT=.2 y .5 en basis0 (contraste no complementario), >=1e-3.
T=.2/.8 en basis0 se conserva como control ADICIONAL de la limitación de leer
solo intensidades: diferencia de potencia<=2e-4, diferencia de campo>=1e-3.
EfectofaseT=.2 vsphaseT=.2>=1e-3. No modificar oráculos ni datos para forzar
un resultado. Las fuentes base y superposiciones se comprueban en campos completos.
Esta enmienda se congela antes de primeraGPU; no añade corrida del diseño fallido.
