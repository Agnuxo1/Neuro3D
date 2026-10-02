# EXP005 — dos cotas HOST no nulas ligadas al dominio axial ORIGINAL

ID AXIAL-NONZERO-UNIT-DOMAIN-HOST-001. Base 6d3ffb7085a48dcff8715fcf480a6f8e0eb973e6.
Acuse AXIAL-HOST-READOUT-CONTRACT-001, SHA
51abb0abe0b462ed943a9115c93db70604c43a5246511cbe9b774b690dc9b8e6.

## Alcance nuevo y condición aritmética

Modelo opt-in axial-nonzero-domain-Horner26-ORIGINAL-bound-HOST-v1.
No añade otra prueba de identidad de readout: cierra desigualdades de error
complejo/fase para dos dominios NO nulos, thin_resolved y nonexact_geometry_phase_PASS.
Reutiliza exclusivamente cajas de planos-X compartidos/YZ fijo, selector axial,
referencia ORIGINAL, cuarto de vuelta y envolvente de argumento ya certificados.
Fuentes ordenadas, escena, snapshot, ABI, grupos y gauges se contrastan con INPUT.
No da por válido el interior sólo a partir de muestras de esquina.

Hipótesis explícita: binary64 nearest-even, subnormales graduales, coeficientes
retenidos, Horner26 separado, sin FMA. Es una cota CONDICIONAL del grafo HOST,
NO evidencia de que un runner o kernel lo haya ejecutado, ni admisión nativa.
API pública sólo lista acotada de casos retenidos y modelo; no cupos/perfiles
o certificados caller. Ningún contrato congelado ni recibo anterior se modifica.

## Composición y cargos

B es la cota L1 uniforme del polinomio HOST al seno/coseno IDEAL del argumento
representado, con coeficientes, redondeo del cuadrado, nodos RN y resto Taylor
separados. Reconstrucción racional nueva de las recurrencias y cotejo exacto
de hashes/cargos del certificado retenido: NO RN/cast/productor puntual nuevo.
No se vuelve a ejecutar uniform_unit_interval ni otro productor anterior.

delta = cota uniforme de transporte parámetro→fase ORIGINAL + argumento RN/2pi.
Mismo cuarto de vuelta estable y gauge ORIGINAL para TODO el dominio.
Para vector unitario ideal u(theta), cada componente tiene derivada de módulo
<=1, así que ||u(theta)-u(theta0)||1 <= 2*|theta-theta0|.
La permutación exacta de cuarto de vuelta conserva L1.

Cota compleja ORIGINAL: B + 2*delta.
Cota angular ORIGINAL: B/(1-B) + delta, con 0<B<1/2.
La segunda se compara con el MISMO cupo INPUT 1e-12 rad, sin epsilon ni aumento.
No confundir L1 de unidad (adimensional) con cota de fase (rad).
Los coeficientes encoded no se tratan como Taylor exactos; su error sigue cargado.

También se prueban 52 intervalos analíticos de salida de nodo (26 por dominio)
finitos, estrictamente normales y sin cruce por cero. Es una propiedad
restringida del grafo hipotético, NO una aceptación del runner antiguo:
inherited_runner_accepts_entire_interval permanece false.

## Bloqueos y preservación

Nuevo restricted_nonzero_unit_error_to_ORIGINAL_bound_proved sólo dos fuentes.
14 unit STOP anteriores intactos; tres dominios cero fuera de esta unidad,
con su prueba exacta anterior intacta y SIN reejecución.
two_sources conserva other no probado; no suma parcial.
Las nuevas filas permanecen STOP por allocations de fuente/etapa INPUT y
backend ejecutado ausentes. No cierra fuente compleja, reflexión, reducción,
potencia, detector, fullpipeline, física, native, RT o autenticación.
El contrato de readout anterior y sus 17 STOP/11 costes no medidos siguen intactos.
Ninguna mejora de velocidad/eficiencia/ganador ni sustitución de escena por U/GEMM.

## Verificación y continuidad

Cuatro tests nuevos, 37 rechazos; primera suite PASS 7.365816299978178s.
Captura exacta 127455bytes SHA
483d10f9f812bfc402c72670c92808b1cc2791445dbcffd0b0aaf6a50cf0ee09.
Oráculo stdlib independiente sin imports de producción reconstruye intervalos,
cargos y composición; 302 pins (298 heredados y cuatro propios).
Capturas y tiempos en reporte; cotas racionales grandes conservadas en strings
decimales exactos y stdout original comprimido, no números JS aproximados.

Export inicial excedió el límite de comando Windows (OS206): se preservó la
captura de la suite y se escribió por 27 bloques apply_patch, sin rerun numérico.
Primer recibo del oráculo quedó sin recoger por parse prematuro de sesión activa:
su exit/veredicto son desconocidos, NO se afirma PASS de ese intento. Tras
comprobar que no quedaba su proceso, verificación nueva PASS 6.714021799998591s,
stdout538bytes SHA4661d0c281924fdd8aa2af844fd5b56ce99ce46de5fa90d940550f8809a01970,
stderr vacío. Ambos incidentes de transporte se documentan en el reporte.

Siguiente propia útil: error uniforme de fuente ORIGINAL para estos dos dominios
NO constantes, amplitud fuente y coeficiente/material separados; no asumir
fuente con error cero ni promover allocations faltantes. Backend/mapping/
guard/fullcosts existentes aún solicitados a Claude por ID+SHA, sin duplicar RT.
CPU1hilo/afinidad1/hijo60s; sin GPU/Blender/raycast/SDKDrJit/Kaggle/pushmerge.
JEV bloqueado: LOCAL sin aval/reintento. 0337 cerrada y deadline intacto.
Cinco propios revisados/versionados; cuatro boards/checkpoint locales SINstage.
Frozen/fixtures conf1/v0/v4/0119/0315/nearestV2/cupos/radios/FAIL intactos.
Futuro GPU sólo reserva Claude exclusiva, telemetría, guard fail-closed,
nuevo deadline verificable por job y todos los límites originales.
