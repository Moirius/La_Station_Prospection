@echo off
echo ========================================
echo   Installation du service Windows
echo   La Station Prospection
echo ========================================
echo.

REM Vérifier si NSSM est installé
where nssm >nul 2>nul
if %errorlevel% neq 0 (
    echo ERREUR: NSSM n'est pas installe.
    echo Veuillez installer NSSM depuis: https://nssm.cc/
    pause
    exit /b 1
)

REM Chemin vers Python dans l'environnement virtuel
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
set SCRIPT_PATH=%~dp0run.py
set SERVICE_NAME=LaStationProspection

echo Installation du service...
nssm install %SERVICE_NAME% "%PYTHON_PATH%" "%SCRIPT_PATH%"
nssm set %SERVICE_NAME% AppDirectory "%~dp0"
nssm set %SERVICE_NAME% Description "Service La Station Prospection - Application de prospection commerciale"

echo.
echo Service installe avec succes!
echo Pour demarrer le service: net start %SERVICE_NAME%
echo Pour arreter le service: net stop %SERVICE_NAME%
echo Pour supprimer le service: nssm remove %SERVICE_NAME% confirm
echo.

pause 