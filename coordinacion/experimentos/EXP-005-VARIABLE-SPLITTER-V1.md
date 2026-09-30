# Divisor lossless configurable por propiedades de escena

**RECHAZADO EN PREFLIGHT CPU01:44UTC, sinGPU.** T=.2/.8 para basis0 produce
intensidades iguales por simetría (diferencia7,11e-15), aunque los campos cambian.
El control de potencia indicado abajo NO es causal para ese par/entrada. Conservar
este diseño fallido; una enmienda nueva debe especificar contraste no simétrico y
comprobar el campo del contraste simétrico. No bajar umbrales tras medir.

Contrato local,30/09/2026. No cambia el esquema v1 ni sus fixtures/shader.
Nuevo readback-v2 exige `power_transmittance` T en TODOS los divisores.
T real finito entre0y1; coeficientes de campo t=sqrt(T), r=i*sqrt(1-T).
Convención ideal escalar recíproca sin pérdidas; no Fresnel ni polarización.
Los dos brazos se siguen geométricamente incluso si su coeficiente resulta0.

Nueva ABI v2: códigos4=t/5=r y cuarto escalar del impacto=T crudo. CPU copia T,
no calcula coeficientes. GPU nativo calcula sqrt, propagación, interferencia y
abs². Shader separado; el shader v1 rechaza códigos no soportados antes del
dispatch desde su puente, nunca los trata como coeficiente1 silencioso.
GPU externa v1 queda explícitamente limitada a códigos0–3.

Escenas nuevas de dosceldas/3modos/dosdet+escape (no modificar escape0119):
T de b.bs2={0,.2,.5,.8,1}; restoT=.5. Además sham visual conT=.5 y fase+.4rad
conT=.2. Siete escenas guardadas/reabiertas, nueve inputs bases/pares1/i por caso.
Campos todospuertos<=1e-4 vsoráculo de triángulos independiente; potencia/balance
<=2e-4; historial y longitud<=1e-5BU; sham<=1e-12. Efecto T>=1e-3 en basis0
entreT=.2y.8; fase causal>=1e-3. Libro detectores+escape sin renormalizar.
T ausente, bool, NaN,fuera[0,1] deben rechazarse. T=.5paridad conv1CPU<=1e-11.

Gate geométrico modal previo se mantieneFalse como prueba física y rechaza los
casos incompatibles. Readback comprueba T del objeto evaluado vs original.
No matriz/campo precomputado de CPU como inputshader. Un esquema v1 con T
inyectado se rechaza: no ignorar una propiedad de peso por usar otra versión.

GPUq/guard120s/host1.5device1/pisoRAM4/VRAM18/temp80/corte06UTC. Artefactos nuevos
y hashes; no modificar conf1/v0/v4/escape0119/archivosClaude. No RT/capacidad/
ventaja ni óptica física. JEVbloqueado, fallbacklocal. Claude revisa independiente.
