# EXP-005: longitudes y referencia por historia completa, CPU ideal

30/09/2026, 12:45 UTC. Unidad Codex independiente; GPU de otro proyecto
ocupada y piloto RT-CAP-006 de Claude en cola. JEV bloqueado por seguridad:
fallback local sin aval remoto. No GPU/Blender, import ni escritor ajeno.

## Resultado y contrato acotado

Nueva referencia opt-in `history_lengths_cpu_v1.py`, sin cambiar helpers,
contratos, shaders ni fixtures congelados. Primero valida el árbol geométrico
completo; después reconstruye distancias por ancestros de cada fuente desde
los extremos representados exactos. No acepta longitudes suministradas por
un ledger ni interpreta el parámetro t como distancia con dirección no unitaria.

Para cada segmento: q = dx²+dy²+dz² se mantiene racional exacto en BU².
La raíz se encierra entre números representables comprobando exactamente
lower² <= q <= upper². Las sumas de intervalos son racionales; también se
exportan extremos float redondeados hacia fuera. La fase no se calcula.

En terminales se exige dirección de modo exactamente colineal y hacia
delante. Es un perfil ideal CPU explícito, NO sustitución del gate angular
nativo ni prueba de modos físicos/ortogonalidad. La corrección de referencia
es d·(reference-point)/sqrt(d·d), encerrada antes de sumar a la longitud.
No se fuerza que la longitud efectiva sea positiva: puede incluir referencia
con signo. Todas las fuentes conservan historias separadas; no fusión de ondas.

## Evidencia nueva retenida

- Cuatro árboles: espejo, divisor, dirección cruda escalada por 3 con
  referencia desplazada 0,25 BU, y dos fuentes declaradas independientes.
  Longitudes efectivas analíticas: [3], [2,3], [2,25;3], [2,3,2,3] BU.
- Seis comprobaciones de raíces racionales, incluyendo sqrt(2), sqrt(5),
  sqrt(2^60+1) y una separación de longitud 2^-30 BU.
- Modo no colineal con componente 1e-12 rechaza bajo ESTE perfil exacto;
  antiparalelo rechaza y eje escalado por 7 acepta. Truncación de historia
  rechaza antes de calcular longitudes. Inputs preservados.
- Cuatro tests propios PASS, 0,049 s, CPU un hilo, cada hijo timeout60s.
  No suites completas ni repetición de gates anteriores sin cambio.
- Report: `D:/PROJECTS/.cognition/neuro3d/exp005_history_lengths_cpu_20260930_1247.json`
  (1247 es etiqueta del fichero, ejecución completó 12:45 UTC).
  SHA256 `4c21037ec6f01711d892a304c9db345b548002f84211ddb3ef6002d94b2399f9`.
  Once codeSHA en el report incluyen los dos shaders congelados.

Comandos desde `D:/PROJECTS/9_NEBULA_NEW/Blender/tests`, con variables de
hilos a 1 y timeout60 por hijo en el wrapper propio:

```
python -B -m unittest -v test_exp005_history_lengths
python -B exp005_history_lengths_audit.py --output NUEVA_RUTA_REPORT.json
```

El auditor abre output con modo exclusivo: no sobreescribir evidencia.

## No demostrado y siguiente paso

Este intervalo certifica SOLO raíz/suma/referencia del árbol ideal de
coordenadas representadas. No encierra errores de intersección/redondeo GPU,
normalización nativa, transporte hi-lo, pérdida anterior de Bpyfloat32,
fase trigonométrica, amplitudes ni estado óptico físico. No promover conf1,
subir bounds o aplicar exención nativa por esta evidencia.

RT-CAP-006 permanece la petición prioritaria; ninguna carga nueva ni otra
reparación operacional solicitada. Después del piloto, Claude tiene
PRECISION-COMPLETE-001 ya registrada: una crítica retenida, sin paralelismo;
puede usar estas longitudes para comprobar que una omisión no se oculta en
el ledger. No abrir otro barrido ni cambiar umbrales para obtener PASS.
