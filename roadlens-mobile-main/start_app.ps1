$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectDir "backend"
$venvDir = Join-Path $backendDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        & py -3 -m venv $venvDir
    } else {
        Get-Command python -ErrorAction Stop | Out-Null
        & python -m venv $venvDir
    }
}

& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $backendDir "requirements.txt")

Write-Host ""
Write-Host "RoadLens is starting at http://127.0.0.1:4173/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the local inference server." -ForegroundColor DarkGray
Write-Host ""

& $venvPython -m uvicorn backend.server:app --app-dir $projectDir --host 127.0.0.1 --port 4173
