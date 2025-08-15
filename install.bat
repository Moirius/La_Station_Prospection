@echo off
echo ========================================
echo   Installation La Station Prospection
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe.
    echo Veuillez installer Python 3.10+ depuis: https://python.org/
    pause
    exit /b 1
)

echo Python detecte: 
python --version

echo.
echo Creation de l'environnement virtuel...
python -m venv venv

echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo Installation des dependances...
pip install -r requirements.txt

echo.
echo Installation terminee!
echo.
echo Pour lancer l'application:
echo   - Double-cliquez sur launch.bat
echo   - Ou ouvrez un terminal et tapez: python run.py
echo.
echo L'application sera accessible sur: http://localhost:5000
echo.

pause 