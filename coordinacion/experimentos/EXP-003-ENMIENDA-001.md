# EXP-003 · Enmienda 001 de contraste de fase

Fecha: 2026-09-29. Complementa sin reemplazar
`EXP-003-PREINSCRIPCION-CONDICIONAL.md`. Se decidió **antes de cualquier
ray-cast de EXP-003 en Blender**; no se ha ejecutado esta corrida aquí.

## Motivo y comprobación previa

Los tres desplazamientos originales solo cubren `P_A≤0,0955`. Un error de
factor dos o de convenio de puertos podría pasar inadvertido. Claude
propuso dos puntos de mayor contraste. Codex los comprobó con un trazador
CPU independiente que elige el primer impacto entre todos los discos:
las rutas permanecen R1→R2→F1→BS2 y M2→BS2, sin oclusión cruzada;
`ΔL−2d` tiene error máximo `3,54e-16 BU` en los cinco puntos. Esto no
es un resultado de Blender.

## Cambio congelado antes de medir

Mantener `d={0; 0,0025; 0,005} BU` y añadir:

| d (BU) | ΔL objetivo (BU) | Δφ objetivo (rad) | P_A ideal | P_B ideal |
|---:|---:|---:|---:|---:|
| 0,0125 | 0,025 | π/2 | 0,5 | 0,5 |
| 0,025 | 0,05 | π | 1,0 | 0,0 |

Se mantienen sin cambios los umbrales originales de longitud (`1e-4 BU`),
fase (`1e-2 rad`), potencia (`1e-3`), balance y readback, así como sham,
ablación y prohibición de respaldo analítico en la inferencia.

Separar en el informe dos pruebas: (A) causalidad geométrica `ΔL=2d`
derivada de impactos; (B) combinación de campos/puertos condicionada a
esa longitud. Cumplir (B) sin (A) no es éxito. Tampoco (A)+(B) convierte
el híbrido en cómputo óptico íntegro de la escena.

Claude versionó los cinco d en `claude/opt-015-fixture` @ `f8d7fc5`;
el commit previo `17b2740` conserva los tres d originales. Codex comparó
ambos commits: solo cambian las listas y las dos salidas esperadas del
fixture; no cambian geometría ni umbrales. Los blobs locales coinciden
con `f8d7fc5` (`fixture.py=e270ba1`, `fixture.json=4e0ea03`). El runner
debe fijarse a esa revisión exacta antes de cualquier corrida.
Un fixture estático y una comprobación CPU no sustituyen revisión del
runner Blender ni autorización vigente de recursos.

## Gate de anclaje absoluto antes de medir

La revisión independiente de Claude detectó una degeneración: trasladar
R1 y R2 `+0,3 BU` en x mantiene la ruta y `ΔL=2d`, pero cambia la
longitud base de brazo 1 a `5,6 BU`. El puerto A base puede seguir oscuro
por periodicidad, de modo que la fase relativa no detecta el cambio.
Codex añadió `exp003_fixture_guard.py`: fijar SHA-256 del fixture JSON
`89cdd5f50bf23716a6143e074cbcfd9b5c1123b78ae2f17782f43c176faa886b`,
comprobar al construir y reabrir posición y normal mundiales, radio, escala
unitaria, una cara, al menos 32 vértices y cero modificadores en cada disco
(tolerancia `1e-6`). Antes de intervenciones, exigir en el ray-cast de
Blender `L1=5,0±1e-4 BU` y `L2=3,0±1e-4 BU`. Este gate comprueba la
escena observada; las longitudes absolutas no se inyectan en inferencia.
