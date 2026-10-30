# ============================================================
# AI_VISAGE - Installation Python autonome (sans venv)
# Python 3.13.17 - Windows 64 bits
# ============================================================

$ErrorActionPreference = "Stop"

$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonDir = Join-Path $Project "python"
$Version = "3.13.17"
$Installer = Join-Path $env:TEMP "python-$Version-amd64.exe"
$Url = "https://www.python.org/ftp/python/$Version/python-$Version-amd64.exe"
$PythonExe = Join-Path $PythonDir "python.exe"

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " AI_VISAGE - INSTALLATION PYTHON AUTONOME" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null

if (!(Test-Path $PythonExe)) {
    Write-Host "`nTéléchargement de Python $Version..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $Url -OutFile $Installer

    Write-Host "Installation de Python dans $PythonDir..." -ForegroundColor Yellow
    $Arguments = @(
        "/quiet", "InstallAllUsers=0", "TargetDir=`"$PythonDir`"",
        "Include_pip=1", "Include_launcher=0", "Include_test=0",
        "PrependPath=0", "AppendPath=0", "Shortcuts=0",
        "InstallLauncherAllUsers=0"
    )
    $Process = Start-Process -FilePath $Installer -ArgumentList $Arguments -Wait -PassThru
    Remove-Item $Installer -Force -ErrorAction SilentlyContinue
    if ($Process.ExitCode -ne 0) {
        throw "Échec de l'installation Python. Code : $($Process.ExitCode)"
    }
} else {
    Write-Host "Python existe déjà. Installation ignorée." -ForegroundColor Yellow
}

if (!(Test-Path $PythonExe)) {
    throw "python.exe introuvable : $PythonExe"
}

$InstalledVersion = (& $PythonExe --version).Trim()
Write-Host "`nPython installé : $InstalledVersion" -ForegroundColor Green
if ($InstalledVersion -ne "Python $Version") {
    throw "Version inattendue : $InstalledVersion (attendu : Python $Version)"
}

Write-Host "`nMise à jour de pip dans le Python du projet..." -ForegroundColor Yellow
& $PythonExe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Échec de la mise à jour de pip." }

Write-Host "`nInstallation terminée. Interpréteur : $PythonExe" -ForegroundColor Green
Write-Host "Aucun environnement virtuel n'a été créé." -ForegroundColor Green
