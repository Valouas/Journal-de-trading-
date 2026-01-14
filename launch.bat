@echo off
title Trade Behavior Audit
echo ========================================
echo    Trade Behavior Audit - Launcher
echo ========================================
echo.

REM Aller dans le dossier de l'application
cd /d "%~dp0"

REM Verifier si les dependances sont installees
echo [1/2] Verification des dependances...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERREUR: Impossible d'installer les dependances
        pause
        exit /b 1
    )
)
echo OK

echo.
echo [2/2] Lancement de l'application...
echo.
echo ========================================
echo   Ouvre ton navigateur sur:
echo   http://localhost:8501
echo ========================================
echo.
echo Appuie sur Ctrl+C pour arreter l'app
echo.

streamlit run app.py

pause
