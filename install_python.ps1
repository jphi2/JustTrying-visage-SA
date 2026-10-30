
# ============================================================
# AI_VISAGE - Installation Python autonome
# Python 3.13.17 - Windows 64 bits
# ============================================================

$ErrorActionPreference = "Stop"

$Project = "E:\SYNC-01M.I7\80_Developpements_Informatique\Python\Projects\AI_Visage"
$PythonDir = Join-Path $Project "python"
$VenvDir = Join-Path $PythonDir "venv"

$Version = "3.13.17"
$Installer = Join-Path $env:TEMP "python-$Version-amd64.exe"
$Url = "https://www.python.org/ftp/python/$Version/python-$Version-amd64.exe"

$PythonExe = Join-Path $PythonDir "python.exe"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " AI_VISAGE - INSTALLATION PYTHON" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Vérification du dossier projet
if (!(Test-Path $Project)) {
    throw "Le dossier du projet est introuvable : $Project"
}

New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null

# Téléchargement et installation de Python
if (!(Test-Path $PythonExe)) {

    Write-Host "`nTéléchargement de Python $Version..." -ForegroundColor Yellow

    Invoke-WebRequest -Uri $Url -OutFile $Installer

    Write-Host "Installation de Python..." -ForegroundColor Yellow

    $Arguments = @(
        "/quiet"
        "InstallAllUsers=0"
        "TargetDir=`"$PythonDir`""
        "Include_pip=1"
        "Include_launcher=0"
        "Include_test=0"
        "PrependPath=0"
        "AppendPath=0"
        "Shortcuts=0"
        "InstallLauncherAllUsers=0"
    )

    $Process = Start-Process -FilePath $Installer `
        -ArgumentList $Arguments `
        -Wait -PassThru

    if ($Process.ExitCode -ne 0) {
        throw "Échec de l'installation Python. Code : $($Process.ExitCode)"
    }

    Remove-Item $Installer -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "`nPython existe déjà. Installation ignorée." -ForegroundColor Yellow
}

# Vérification de Python
if (!(Test-Path $PythonExe)) {
    throw "python.exe introuvable après installation."
}

$InstalledVersion = & $PythonExe --version

Write-Host "`nPython installé : $InstalledVersion" -ForegroundColor Green

if ($InstalledVersion -ne "Python $Version") {
    throw "Version inattendue : $InstalledVersion"
}

# Création de l'environnement virtuel
if (!(Test-Path $VenvPython)) {

    Write-Host "`nCréation de l'environnement virtuel..." -ForegroundColor Yellow

    & $PythonExe -m venv $VenvDir

    if ($LASTEXITCODE -ne 0) {
        throw "Impossible de créer l'environnement virtuel."
    }
}
else {
    Write-Host "`nEnvironnement virtuel déjà présent." -ForegroundColor Yellow
}

# Mise à jour de pip dans le venv
Write-Host "`nMise à jour de pip..." -ForegroundColor Yellow

& $VenvPython -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    throw "Échec de la mise à jour de pip."
}

# Vérifications finales
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " INSTALLATION TERMINEE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

Write-Host "`nPython principal :"
& $PythonExe --version

Write-Host "`nPython virtuel :"
& $VenvPython --version

Write-Host "`nPip :"
& $VenvPython -m pip --version

Write-Host "`nEnvironnement : $VenvDir" -ForegroundColor Green
Write-Host "`nAI_Visage est prêt pour la suite !" -ForegroundColor Green
