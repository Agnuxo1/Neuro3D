# Recorrido GPU compartido: verificación local

30/09/2026, 03:39 UTC. Contrato, shader, backend y runner **b7d8bbb**
congelados antes de medir. Versiones anteriores y doce escenas de0315 intactas.

## Qué cambia

Una única invocación lógica enumera los caminos de todas las fuentes y
acumula campos complejos por puerto. Antes, cada puerto volvía a recorrer
la escena completa. Sigue siendo óptica escalar digital en GPU ALU dentro
de Blender, **no RT/BVH ni computación óptica física**.

El shader recibe solo geometría/fuentes/propiedades crudas de escena reabierta.
No hay matriz ni trazado CPU de entrada, suma de interferencia CPU, ni
readback intermedio de frontier. Exportación, preflight, transferencias,
readback final y verificación independiente siguen siendo trabajo del host.

Una cuarta imagen final contiene total de consultas, caminos terminales,
invocaciones y estado. El decoder contrasta esos contadores con las copias
por puerto y el oráculo independiente. **No sumar las copias por puerto**
como si fueran recorridos ejecutados: ahora son metadata compartida.

## Evidencia

246 probes, 9.348 contribuciones de camino y diez abortos específicos pasan
en las doce escenas K3/K4 reabiertas solo en lectura. Sham exacto, cuatro
intervenciones causales y 107 controles fuera del cono causal pasan.
La auditoría offline recalcula todos los oráculos después de finalizar Blender.

| Medida | Máximo error absoluto |
|---|---:|
| Campo complejo contra triángulos independientes | 4,491e-7 |
| Campo contra composición analítica | 3,514e-7 |
| Campo frente al backend anterior | 1,333e-7 |
| Intensidad | 7,408e-7 |
| Balance incluyendo escape | 9,509e-7 |
| Campo por camino | 1,414e-7 |
| Longitud efectiva por camino | 1,066e-14 BU |

Los contadores GPU, verificados contra el oráculo, registran **30.138
consultas geométricas**, frente a 142.962 en el recorrido repetido del
backend anterior sobre esas mismas entradas. Esto demuestra eliminación
de trabajo duplicado, **no un factor de aceleración temporal**.

137 pruebas CPU pasan. Como contraste adicional, ejecuté el `pytracer.py`
retenido de Claude sin modificarlo sobre cuatro superposiciones 1+i
(base, fase, T y λ): máximo error 3,16925e-7. Su script tiene defaults
ópticos y omite rayos perdidos/profundidad excesiva: el contraste es
numérico parcial, no certifica su fail-closed, historias ni modos físicos.
La revisión03:25 de Claude cubre bases; falta auditoría completa del kernel.

## Operación y artefactos

gpuq03:38:37–03:39:09 UTC; guard32,145s/rc0/sinviolaciones. RAM disponible
mínima9,267GiB, VRAM global máxima0,736GiB, temperatura máxima34°C.
PID31396 terminado, sinBlender residual y reserva liberada. Sin push ni merge.
No se editaron los archivos de Claude ni se guardó sobre escenas previas.

En `D:/PROJECTS/.cognition/neuro3d/`:

- `exp005_shared_native_20260930_0337.json` y carpeta de readbacks.
  SHA: `ca23f606478b3c5897c141ab80f877af5ba47aacd572bc527825ac7047c7d5b3`.
- `exp005_shared_guard_20260930_0337.json`.
- `exp005_shared_audit_20260930_0340.json`.
- `exp005_shared_peer_pairs_20260930_0342.json`;
  SHA del trazador Claude: `8b451edcb61c3af18aaafec535edb07ea06ba30324df8c8b9693c8a3de124de4`.

No se midió ventaja temporal, energética ni de capacidad frente a redes
convencionales. El siguiente paso es un protocolo pareado de costes con
ambos backends en el mismo proceso; no comparar estos jobs de lifecycle
distinto. Stack/ledgeroverflow/rol siguen defensivos sin negativo runtime.
RT/OptiX corresponde a Claude. JEV sigue bloqueado por seguridad; fallback local.
