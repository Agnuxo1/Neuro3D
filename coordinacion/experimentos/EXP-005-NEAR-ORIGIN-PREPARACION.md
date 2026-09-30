# Intervalo excluido: contrato prospectivo de rechazo conservador

NO CONGELADO, CPU exclusivamente. No cambia t_min, nearestV2, V3 ni sus gates.
No ofrece un backend nativo, permiso GPU ni una reparación de red completa.

## Criterio

Para cada intersección candidata, disponer de un intervalo [lo,hi] verificable
del parámetro firmado t. Si hi>0 y lo<=t_min, puede existir un impacto en el
intervalo excluido (0,t_min]: ABORTAR la muestra, nunca omitir la superficie
para seguir con un impacto lejano. La frontera superior es inclusiva.

La referencia CPU `exp005_near_origin_audit` calcula t racional sobre coordenadas
binary64 representadas y usa [t-e,t+e] con e explícito. e=0 significa solamente
modelo matemático de inputs representados; NO error GPU/Bpy igual a cero.
Este es un oráculo acotado de parámetros, no un propagador ni un límite demostrado
de error geométrico nativo. Barycentrics exactas estrictas NO equivalen a las
tolerancias GPU. Rayos coplanares sin intersección única abortan la referencia.

El criterio no excluye objetos ni primitivas por identidad. Con e=0, t=0 o
t<0 no se clasifican como impactos cercanos positivos; aun así quedan obligados
los controles de identidad/superficies coincidentes y de partida legítima.
Con e>0, incluso un t=0 puede forzar aborto: falsos rechazos conservadores son
posibles. No inventar e=0 para que los controles pasen.

## Condiciones antes de congelar o integrar

1. GPU obtiene candidatos desde triángulos crudos ANTES del descarte de t_min;
   sin listas CPU de impactos ni lectura intermedia de frontier.
2. Enclosure demostrado para t, signo y pertenencia triangular, o dominio
   justificado con rechazo ante incertidumbre. No solo un error fijo arbitrario.
3. Estado por rama/snapshot y salida inválida explícita; campos parciales NO
   válidos, sin renormalización, sin perder flags en splitting.
4. Adversarios subumbral y frontera, controles encima, retornos legítimos,
   coplanaridad, caras adyacentes, bounds y propagación de incertidumbre.
5. Gates previos de fase/modo/campos/ledger/counters/energía conservados. No afirmar
   validez de escena completa por pasar este componente.
6. Crítica independiente, contrato/hashes ANTES de variante compilada. Nueva
   autorización GPU + gpuq/guard/deadline; no ampliar conf1/bounds por este texto.

Evidencia CPU disponible: dos casos F5 abortan en este componente prospectivo,
dos controles superiores y tres pasos A→B→A pasan bajo e=0 del modelo numérico;
una muestra con e=1.1e-9 aborta. Ocho tests enfocados. Nada nativo ejecutado.
