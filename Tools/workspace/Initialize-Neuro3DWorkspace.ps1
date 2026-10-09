<#
.SYNOPSIS
Prepara el diseno de carpetas que esperan los registros congelados de Neuro3D.

.DESCRIPTION
Algunos registros congelados contienen rutas absolutas D:/PROJECTS/... y sus
SHA-256 aparecen en recibos publicados, por eso no se reescriben. Este script crea
uniones (junctions) con el mismo diseno de carpetas, sin modificar el contenido de
ningun archivo y sin sobrescribir nada que ya exista.

Los artefactos externos (neuro3d, neuro3d-sequential-20261008, gpu_queue) no estan
en git. Deben proceder de la copia de seguridad del proyecto.

.PARAMETER WorkspaceRoot
Carpeta donde viven el repositorio y .cognition. Por defecto D:\PROJECTS.

.PARAMETER ExternalRoot
Carpeta que contiene neuro3d, neuro3d-sequential-20261008 y gpu_queue.

.EXAMPLE
.\Initialize-Neuro3DWorkspace.ps1 -ExternalRoot 'E:\neuro3d-artifacts' -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$WorkspaceRoot = 'D:\PROJECTS',
    [Parameter(Mandatory = $true)][string]$ExternalRoot
)

$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pairs = @(
    @{ Path = (Join-Path $WorkspaceRoot '9_NEBULA_NEW'); Target = $repo },
    @{ Path = (Join-Path $WorkspaceRoot '.cognition');   Target = $ExternalRoot }
)

foreach ($pair in $pairs) {
    if (Test-Path -LiteralPath $pair.Path) {
        Write-Host "Existente, no se toca: $($pair.Path)"
        continue
    }
    if ($PSCmdlet.ShouldProcess($pair.Path, "crear union hacia $($pair.Target)")) {
        New-Item -ItemType Junction -Path $pair.Path -Target $pair.Target | Out-Null
        Write-Host "Creada union: $($pair.Path) -> $($pair.Target)"
    }
}

foreach ($name in @('neuro3d', 'neuro3d-sequential-20261008', 'gpu_queue')) {
    $expected = Join-Path $ExternalRoot $name
    if (-not (Test-Path -LiteralPath $expected)) {
        Write-Warning "Falta el artefacto externo requerido: $expected"
    }
}
