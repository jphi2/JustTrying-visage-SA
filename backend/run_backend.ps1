$ErrorActionPreference = "Stop"

$Root = Split-Path $PSScriptRoot -Parent
$Python = Join-Path $Root "python\python.exe"

if (-not (Test-Path $Python)) {
    throw "Python du projet introuvable : $Python"
}

Set-Location $Root

& $Python -c "import sys; sys.path.insert(0, 'backend'); from app.core.config import settings; import uvicorn; uvicorn.run('app.main:app', host=settings.host, port=settings.port)"

if ($LASTEXITCODE -ne 0) {
    throw "Le backend AI_Visage s'est arrêté avec une erreur."
}
