@echo off
echo ========================================
echo   La Station Prospection
echo ========================================
echo.
echo Demarrage de l'application...
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Lancer l'application
python run.py

pause 