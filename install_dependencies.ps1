# ============================================================
# AI_VISAGE - Installation des dépendances dans python\
# ============================================================

$ErrorActionPreference = "Stop"
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Project "python\python.exe"
$RootRequirements = Join-Path $Project "requirements.txt"
$BackendRequirements = Join-Path $Project "backend\requirements.txt"

if (!(Test-Path $Python)) {
    throw "Python du projet introuvable : $Python. Lance d'abord install_python.ps1."
}
if (!(Test-Path $RootRequirements)) { throw "Fichier introuvable : $RootRequirements" }

Write-Host "Installation des dépendances principales..." -ForegroundColor Cyan
& $Python -m pip install -r $RootRequirements
if ($LASTEXITCODE -ne 0) { throw "Échec de l'installation des dépendances principales." }

if (Test-Path $BackendRequirements) {
    Write-Host "Installation des dépendances du backend..." -ForegroundColor Cyan
    & $Python -m pip install -r $BackendRequirements
    if ($LASTEXITCODE -ne 0) { throw "Échec de l'installation des dépendances du backend." }
}

Write-Host "`nDépendances installées dans : $Python" -ForegroundColor Green
