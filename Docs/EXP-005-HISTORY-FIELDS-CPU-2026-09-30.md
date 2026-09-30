# EXP-005: campos ideales ligados a escena e historia completa, CPU

30/09/2026, 12:56 UTC. Unidad propia Codex mientras RT-CAP-006 espera GPU.
Fallback local: JEV bloqueado por seguridad, sin aval remoto. No GPU,
Blender, import o escritor Claude. No modificación de shaders/fixtures/gates
congelados ni sustitución silenciosa por U/GEMM.

## Implementación y alcance

`history_fields_cpu_v1.py` reconstruye primero el árbol completo validado
y sus longitudes desde fuentes/triángulos/roles/referencias de escena. Las
historias suministradas se verifican, no se confía en distancias declaradas.
CPU aplica los coeficientes ideales de EXP-005: divisor t=sqrt(T),
r=i*sqrt(1-T), espejo=-exp(i*phase_rad). Propagación al terminal:
exp(i*2*pi*L_effective/lambda). Escena v2 manda T y fase; lambda es única
para ese snapshot. Escena v1 mantiene la definición explícita 50/50 del ABI.

Grupos de coherencia OBLIGATORIOS para todas las fuentes: primero suma
campos por puerto/grupo, después intensidades entre grupos independientes.
Un solo modo de onda plana ideal por terminal, con eje colineal verificado
por la referencia de longitud. No prueba solape transversal, polarización,
ortogonalidad física, Fresnel ni autenticidad de trayectorias nativas.
Snapshot y grupos/modelo terminal tienen SHA separado de configuración.

No podar historias por campo cero. Todas las ramas siguen requeridas.
Cada camino retiene fuente/grupo/amplitud/longitud efectiva y campo complejo;
no se confunde intensidad con campo o identidad del grupo de coherencia.

Reducción de fase: longitud efectiva ideal encerrada, punto medio racional,
división por lambda representada y módulo racional ANTES de convertir a
float. Evita perder ciclos enteros en esa etapa CPU. Si hay raíces
irracionales, el punto medio sigue aproximación. El ancho ideal se retiene
en vueltas, pero NO certifica el error de libm, transporte/intersección GPU,
normalización o pérdida previa Bpyfloat32. `phase_error_certified=False`.

## Pruebas nuevas

- Siete casos analíticos retenidos: cuatro T=0/0,25/0,5/1 y tres controles
  de dos fuentes (coherente, independiente y cancelación destructiva).
  Divisor exige campo complejo, incluyendo signo +i en reflexión, no solo
  potencia. Referencias esperadas están en el report, umbral 1e-14 fijo.
- Cinco tests propios PASS0,074s, CPU un hilo, timeout60s por hijo.
  Incluyen amplitud .3+.4i/espejo pi/2, referencia de cuarto de vuelta,
  3*2^50 ciclos enteros, grupos ausentes/extra/vacíos rechazados,
  configuración ligada a grupos, truncación rechazada e inputs intactos.
- Fuente cero conserva ambos terminales con campos cero.
- Dos fuentes idénticas coherentes dan intensidad total4, independientes2
  y oposición coherente0 en estos fixtures. NO presentar sum(|A_source|²)
  como presupuesto de energía de fuentes coherentes coincidentes: su
  interferencia ya cambia el campo incidente. No balance físico general.

Report final: `D:/PROJECTS/.cognition/neuro3d/exp005_history_fields_cpu_20260930_1258.json`
(1258 es etiqueta; ejecución final 12:55 UTC).
SHA256 `0cb11640abe0f9dca09d0330cb4222f6c2bae5664c46414c8b7bf6f1e4608862`.
Trece codeSHA incluyen shaders y helpers congelados. Report1256 previo
de intensidades conservado, SHA b8156c4dfb982bc3f7ef341a141174c52b8b1a4f988f86bc8552d4220c608f8d;
no fallo ocultado: se amplió el gate analítico a campos complejos antescommit.

Desde `D:/PROJECTS/9_NEBULA_NEW/Blender/tests`:

```
python -B -m unittest -v test_exp005_history_fields
python -B exp005_history_fields_audit.py --output NUEVO_REPORT.json
```

Auditor crea output exclusivamente, sin sobrescribir evidencia existente.

## Coordinación y siguiente paso

RT-CAP-006 sigue prioridad operativa; no repetir capturas/guards ni crear
otro encargo paralelo. Después del piloto, una crítica retenida ya pedida
en PRECISION-COMPLETE-001; este artefacto puede apoyar la comprobación de
una omisión. Próximo Codex auditar el piloto si llega, o preparar un fixture
de interferencia entre dos rutas distintas antes de una nueva comparación.
NO red nativa nueva, RT coherente, promociónconf1 ni ventaja de velocidad.
