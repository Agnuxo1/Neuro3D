# Gate de actualización en vivo del divisor

Seguimiento local del V2 numérico63/63 (eb07c4b), no cambio de umbrales/shader.
V2rechazó cinco propiedades por mismatchevaluado: evidencia de fail-closed, NO
de cada validador de tipo/rango ejecutado tras reevaluación. Conservarartefactos.

Reabrir T05.blend0151 SOLOLECTURA. Tras editar `power_transmittance`, llamar
update_tag() del objeto antes de view_layer.update/export para renovar depsgraph.
Controles positivos en vivoT=.2/.8/.5, 9probes cadauno (27). ReadbackTactual
exacto, propiedad evaluadaigualoriginal, GPUcampos vsoráculo<=1e-4,
potencia/balance<=2e-4. Frente a escena guardada T05, T=.2 tiene efecto>=1e-3
en basis0. Simetría.2/.8potencia<=2e-4/campodistinto>=1e-3. Shaderprevioigual.

Después negativos realesbpy conupdate_tag antes de readback. Missing debe dar
KeyError; bool/negative/above_one deben dar error de valor/tipo, NO mismatch
de evaluación. NaN puede ser rechazado por desigualdad de NaN en gate evaluado
(NaN!=NaN): conservar mensaje y no certificar por él el decoder runtime.
Todos antes de dispatch y sin guardar fixture. Hashentradaintacto/al cierre limpio.
GPUq/guard120s/host1,5device1/piso4/cap18/temp80/cierre06UTC. NoRT/físicacompleta.
JEVbloqueado/fallbacklocal; Claude revisa propiedad/depsgraph sin duplicar.
