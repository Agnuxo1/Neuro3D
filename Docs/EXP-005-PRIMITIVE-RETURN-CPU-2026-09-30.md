# Rechazo conservador por triángulo: candidato CPU

Preparación local, sin integración nativa. No es una reparación completa de
autointersecciones ni una autorización para ampliar la red. Shaders, oráculo,
runners y contratos congelados anteriores permanecen intactos.

## Regla candidata

Después de salir en línea recta de un triángulo estático ideal por reflexión
o transmisión, un candidato de retorno inmediato al mismo triángulo provoca
`abort`, no un salto silencioso al siguiente impacto. El estado contiene el
ID global de la primitiva inmediatamente anterior, no una lista de todos los
objetos visitados. Las entradas inválidas se rechazan explícitamente.

Se comprueba solo una condición necesaria: `continue` significa que esta regla
no excluye el candidato, NO que su geometría, modo o campo sea válido.
El candidato no clasifica por identidad de objeto ni desplaza el origen.

## Controles verificados

La auditoría lee los doce registros congelados de la reproducción CPU propia,
repite exactamente sus consultas y aplica la regla a cada candidato explícito
de retorno al mismo triángulo. Los doce producen `abort`.

Un control geométrico nuevo reúne dos superficies reflectantes no coplanares
en un único objeto de cuatro triángulos. Tres consultas reales del oráculo
visitan la primera superficie, la segunda y de nuevo la primera. La regla deja
continuar los tres pasos: no excluye por objeto ni conserva un veto histórico.

Nueve pruebas enfocadas pasan en 0.062s: candidatos espejo/transmisión/reflexión,
distancias pequeñas/grandes, fuente inicial, retorno legítimo, IDs/eventos/
distancias inválidas y fidelidad del registro JSON. El lector inicial comparaba
tuplas de Python con listas JSON y falló; se corrigió por serialización exacta
sin tolerancias numéricas. Un registro cuyo número se altera sigue rechazado.
La prueba anterior y la corrección no son resultados GPU.

## Límites pendientes

- El informe alimenta candidatos explícitos del mismo triángulo. No demuestra
  que todos sean seleccionados por nearest-hit ni mide cobertura del trazador.
- Retornos numéricos sobre otro triángulo del mismo objeto siguen sin resolver.
- Una superficie omitida por el filtro t_min actual no llega a esta regla.
- Ningún backend GPU transporta todavía el ID previo por rama con esta regla.
- Empates, IDs estables, campos/ledger/flags, modos y precisión requieren un
  contrato nativo nuevo y validación aparte. No se han computado matrices U.

Las habilidades de continuidad y pruebas enfocadas han mantenido el fixture
congelado y agregado controles de retorno válido; no se ejecutaron escritores
ajenos ni se modificaron archivos de Claude.

## Evidencia y siguiente paso

Entrada congelada:
`D:/PROJECTS/.cognition/neuro3d/exp005_self_hit_cpu_20260930_0804.json`,
SHA256 `534d2c14b5ab1738f00192068c70600ae94f60b3d601eda60ddb557206eedd71`.

Informe nuevo, ocho hashes de código:
`D:/PROJECTS/.cognition/neuro3d/exp005_primitive_return_20260930_0817.json`,
SHA256 `88033c3f174a282b09d22d236f573b50725dcee072910479199c8f6ea85377a0`.

```powershell
python -B -m unittest discover -s Blender/tests -p test_exp005_primitive_return.py
```

La preparación prospectiva está en
`coordinacion/experimentos/EXP-005-PRIMITIVE-RETURN-PREPARACION.md`.
Claude debe criticarla dentro de PRECISION-005; no es otra tarea paralela.
Todavía no está congelado ningún nuevo experimento GPU. Ventana GPU cerrada,
JEV bloqueado por seguridad, fallback local explícito sin aval remoto.
