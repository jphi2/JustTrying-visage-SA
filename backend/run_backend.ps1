$ErrorActionPreference = "Stop"

$Root = Split-Path $PSScriptRoot -Parent
$Python = Join-Path $Root "python\venv\Scripts\python.exe"

Set-Location $Root

& $Python -m uvicorn app.main:app `
    --app-dir backend `
    --host 127.0.0.1 `
    --port 8765

if ($LASTEXITCODE -ne 0) {
    throw "Le backend AI_Visage s'est arrete avec une erreur."
}
