# Espacio de trabajo y rutas

Este documento explica cómo reproducir Neuro3D en otra máquina y qué rutas absolutas se han conservado a propósito.

## 1. Por qué hay rutas absolutas

Los registros de evidencia (recibos JSON, protocolos y copias de scripts dentro de `Docs/validation/`) contienen rutas `D:/PROJECTS/...`. Algunos de esos scripts tienen su SHA-256 registrado en recibos publicados. Reescribir esos archivos cambiaría sus bytes y rompería la cadena de hashes. Por eso el código congelado **no se edita**.

El código de los módulos no congelados sí se corrige para usar rutas relativas o la variable de entorno `NEURO3D_COGNITION_DIR`. El inventario y la lista exacta de archivos están en `Docs/PATH_MAP.md`, sección 2.

## 2. Diseño de carpetas esperado

| Ruta esperada | Contenido | En git | Cómo obtenerla |
|---|---|---|---|
| `D:\PROJECTS\9_NEBULA_NEW` | Repositorio | Sí | `git clone https://github.com/Agnuxo1/Neuro3D` |
| `D:\PROJECTS\.cognition\neuro3d` | Artefactos experimentales (JSON, recibos CPU) | No | Copia de seguridad del proyecto |
| `D:\PROJECTS\.cognition\neuro3d-sequential-20261008` | Secuencias y recibos del piloto congelado | No | Copia de seguridad del proyecto |
| `D:\PROJECTS\.cognition\gpu_queue` | Cola GPU compartida (herramienta de la estación de trabajo) | No | No necesaria para las pruebas CPU |

Los artefactos externos no están en git por su tamaño y porque algunos proceden de equipos de trabajo. Cada uno debe restaurarse desde la copia de seguridad.

## 3. Procedimiento

1. Clonar el repositorio.
2. Crear el diseño de uniones con el script (sin tocar ningún archivo):

   ```powershell
   .\Tools\workspace\Initialize-Neuro3DWorkspace.ps1 -ExternalRoot 'RUTA_A_LA_COPIA\.cognition' -WhatIf
   .\Tools\workspace\Initialize-Neuro3DWorkspace.ps1 -ExternalRoot 'RUTA_A_LA_COPIA\.cognition'
   ```

   El script no sobrescribe nada que ya exista y avisa de los artefactos que falten.
3. Ejecutar las pruebas CPU de núcleo, con la variable apuntando a la carpeta `.cognition`:

   ```bash
   NEURO3D_COGNITION_DIR=/d/PROJECTS/.cognition python -m unittest discover -s Blender/tests -p "test_*.py"
   ```

   Las pruebas que dependen de artefactos externos fallan o se omiten con un mensaje claro si no están presentes.

## 4. Qué no se reescribe y por qué

- 17 módulos Python con SHA-256 registrado en recibos congelados. Se mantienen byte a byte y dependen del diseño de carpetas de la sección 2.
- 213 JSON y 113 Markdown con rutas en texto. Son evidencia o registro de coordinación; su texto no se modifica.
- Cualquier reescritura de artefactos congelados exige un protocolo nuevo, con su propio recibo y aprobación explícita.

El código nuevo debe usar rutas relativas al repositorio o `NEURO3D_COGNITION_DIR`. No debe introducir rutas `D:/PROJECTS` nuevas.

## 5. Fin de línea (CRLF frente a LF)

El repositorio fija LF en `.gitattributes` para `*.py`, `*.json`, `*.md`, `*.csv` y otros tipos de texto. Los hashes fijados en las pruebas se calculan sobre esos bytes LF.

Con `core.autocrlf=true` (valor habitual en Windows), una copia de trabajo antigua puede tener archivos en CRLF que Git considera sin cambios, pero cuyos bytes no coinciden con los hashes fijados. Eso rompe las pruebas que comparan hashes (por ejemplo, `iris.csv`). Para comprobarlo:

```bash
git ls-files --eol | grep -E '^i/lf +w/crlf' | grep 'eol=lf'
```

Si aparecen filas, restaurar esos archivos desde el índice (sin perder nada, porque Git los considera limpios):

```bash
git ls-files --eol | grep -E '^i/lf +w/crlf' | grep 'eol=lf' | awk -F'	' '{print $2}' | while IFS= read -r f; do rm -f -- "$f" && git checkout -- "$f"; done
```

En la integración de 2026-10-09 se restauraron 19 archivos de este tipo (lista en `Docs/validation/p0-1-rutas-2026-10-09/`).

