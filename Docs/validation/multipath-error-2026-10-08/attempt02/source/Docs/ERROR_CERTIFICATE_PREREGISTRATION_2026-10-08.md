# Punto 4: protocolo prospectivo del certificado integral

Antes de ejecutar el certificado nuevo, se fija la pregunta: ¿se pueden encerrar longitud, fase, campo e intensidad del recorrido escalar completo en intervalos demostrables, incluyendo entradas acotadas y rechazo de topología no certificada?

## Alcance y aceptación

1. El modelo representado del punto 3 usa geometría y dirección racionales exactas. Se certificará cada uno de los 41 estímulos K3/K4; cada puerto conservará intervalos racionales de campo e intensidad y cotas del error de las salidas flotantes efectivamente producidas. Cota absoluta L1 de campo e intensidad <=1e-11.
2. Raíces se encerrarán mediante `isqrt` y comprobación entera; pi mediante la identidad de Machin y resto alternante de arctan; seno/coseno mediante reducción de argumento certificada, Taylor y resto de Lagrange. Toda operación se redondeará hacia fuera a una malla diádica de 128 bits. No se supondrá que `math.sin/cos` son correctamente redondeados.
3. Entradas no exactas requerirán radios explícitos de todos los componentes del presupuesto, en unidades de la escena o radianes. Se ensayará una caja no nula estable: traslaciones rígidas de superficies y posiciones/dirección de fuente compatibles con el modo terminal. Se comprobarán muestras deterministas contra sus intervalos; el muestreo no sustituye la demostración por inclusión.
4. Cambios posibles de orden de impactos, denominador que cruce cero, cobertura no probada, soporte de ramas/fuentes que pueda aparecer, referencia o dirección modal incompatibles producirán UNKNOWN, sin intervalo presentado como campo completo certificado.
5. Se incluirán hueco diminuto perturbado, dirección angular incierta, recorrido incompleto y entrada física con cota ausente. Estos casos no podrán recibir un certificado de éxito.
6. Una referencia decimal independiente de alta precisión podrá comprobar diagnósticamente pi/trig/raíces y algunos campos; ni esa referencia ni una tolerancia empírica constituyen la prueba.

La incertidumbre física no suministrada será `UNKNOWN_NOT_ZERO`. Este cierre se refiere al motor CPU completo de óptica escalar ideal; los kernels completos GPU/RT y una plataforma física requieren sus propias verificaciones. Las cotas antiguas basadas en errores upstream asumidos conservan su alcance y no se promueven automáticamente.

Fuentes matemáticas consultadas: [NIST DLMF, series de arctan](https://dlmf.nist.gov/4.24.E3) y [series de seno/coseno](https://dlmf.nist.gov/4.19). La identidad y las cotas utilizadas se demostrarán en la documentación del certificado. JEV connected/provenance=jev aconseja derivar inclusiones y rechazar lo no probado; su consejo no es evidencia numérica.
