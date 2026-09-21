param(
    [Parameter(Mandatory = $true)]
    [string]$SnapshotId,
    [switch]$Resume
)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw "No existe el Python del proyecto: $python"
}

Set-Location -LiteralPath $root
$arguments = @('-m', 'app.tg_cell_runner', '--snapshot-id', $SnapshotId)
if ($Resume) { $arguments += '--resume' }

& $python @arguments
$exitCode = if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE }
if ($exitCode -ne 0) {
    throw "La matriz por activo/temporalidad/direccion quedo incompleta (codigo $exitCode). Ejecute el mismo comando con -Resume."
}

Write-Host 'OPTIMIZACION CELULAR TERMINADA' -ForegroundColor Green
