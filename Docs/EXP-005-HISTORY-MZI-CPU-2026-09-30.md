# EXP-005: dos brazos geométricos y recombinación, fixture CPU ideal

30/09/2026, 13:08 UTC. Unidad propia independiente. GPU ocupada por otro
proyecto y piloto006 de Claude en cola; ningún lanzamiento/reserva GPU.
JEV bloqueado por seguridad, fallback local sin aval remoto.

## Qué se ha probado

Nuevo fixture sintético representado exacto, sin tocar conf1/v0/v4/0119/
0315, shaders, runners ni los helpers ya congelados. Una fuente, dos
divisores 50/50, dos espejos y dos detectores: seis objetos, doce triángulos,
trece registros de historia y cuatro caminos terminales, dos por detector.
Cada brazo usa un espejo y un punto geométrico distinto. El validador exacto
CPU reconstruye impactos/reflexiones/ancestros y exige las cuatro salidas.
Los registros son candidatos verificados, no trayectorias nativas leídas.

Fuente (-1,0) → B1 (0,0). Brazo A: MA (1,0) → B2 (1,1);
brazo B: MB (0,1) → B2 (1,1). Dx (2,1), Dy (1,2).
Todos los segmentos miden 1 BU, longitud total4 BU por camino, lambda0,125 BU.
Espejos/divisores diagonales giran x↔y. Fase phi es una propiedad óptica
de MA calculada por Python: NO desplazamiento de espejo medido en Blender.

Oráculo analítico separado del recorrido/ledger:

```
E_Dx = -i*(1+exp(i*phi))/2
E_Dy = (1-exp(i*phi))/2
```

Un desplazamiento de referencia delta del modo Dx multiplica su campo por
exp(i*2*pi*delta/lambda), sin cambiar la intensidad. El modelo sigue siendo
una onda plana ideal por puerto; no certifica solape/ortogonalidad físicos.

## Evidencia retenida

- Seis controles: phi=0, pi/2, pi, 3pi/2, 2pi y referencia Dx+0,03125 BU.
  Campo complejo y potencia total1 del MZI ideal de una sola fuente.
- Máximo error de campo contra fórmula: 2,220446049250313e-16;
  máximo error de potencia total: 4,440892098500626e-16.
  Umbrales predefinidos en auditor: ambos <=1e-13, sin modificación trasrun.
- Cuatro tests PASS0,199s, CPU un hilo, timeout60s por hijo. Cuatro omisiones
  diferentes de terminal rechazan; cambios de fase invalidan binding
  hasta actualizar historia; ancestros distintos/inputs intactos verificados.
- Report: `D:/PROJECTS/.cognition/neuro3d/exp005_history_mzi_cpu_20260930_1308.json`
  (1308 es etiqueta; ejecución completó13:06 UTC).
  SHA256 `f261130eff38946c1b626c30c3e483bb3f93e9f3e67a4f294b5d15efaa4c12cf`.
  Diez codeSHA verificados, incluyendo los dos shaders congelados.

Desde `D:/PROJECTS/9_NEBULA_NEW/Blender/tests`:

```
python -B -m unittest -v test_exp005_history_mzi
python -B exp005_history_mzi_audit.py --output NUEVO_REPORT.json
```

Output exclusivo; no sobrescribir evidencia ni ejecutar scripts ajenos.

## Límites y siguiente paso

Solo fixture exacto sintético CPU y campos digitales Python, NO raycast
Blender, export/readback Bpyfloat32, redGPU/RT o computación óptica física.
NO prueba nueva de precisión nativa/libm/hi-lo/campos generales ni ventaja
de velocidad. La fase se varía en propiedad ideal, no en geometría.
No promover conf1 ni aumentar bounds por este resultado.

Se formaliza la petición YAexistente PRECISION-COMPLETE-001 porID/SHA:
una omisión aceptada, después de006 y sin otroencargo paralelo.006 sigue
prioridad; no nuevas capturas por este aviso. Próximo Codex auditar006 si
llega, o preparar contrato opt-in de exportación/paridad de este fixture
antes de una carga nativa con nuevos gates, guard/reserva/preflight.
