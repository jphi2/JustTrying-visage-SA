# ============================================================
# AI_VISAGE - Installation des dependances
# ============================================================

$ErrorActionPreference = "Stop"

$Project = "E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage"

$Python = Join-Path $Project "python\venv\Scripts\python.exe"
$Requirements = Join-Path $Project "requirements.txt"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " AI_VISAGE - DEPENDANCES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (!(Test-Path $Python)) {
    throw "Environnement Python introuvable."
}

if (!(Test-Path $Requirements)) {
    throw "requirements.txt introuvable."
}

Write-Host "`nInstallation des dependances..." -ForegroundColor Yellow

& $Python -m pip install -r $Requirements

if ($LASTEXITCODE -ne 0) {
    throw "Erreur pendant l'installation des dependances."
}

Write-Host "`nInstallation terminee !" -ForegroundColor Green
