# Script de lancement PowerShell pour La Station Prospection

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  La Station Prospection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Demarrage de l'application..." -ForegroundColor Green
Write-Host ""

# Activer l'environnement virtuel
& ".\venv\Scripts\Activate.ps1"

# Lancer l'application
python run.py

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 