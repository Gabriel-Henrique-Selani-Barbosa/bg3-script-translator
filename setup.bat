@echo off
echo ==========================================
echo  BG3 Script Translator - Installer
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Download and install from: https://python.org/downloads
    echo IMPORTANT: Check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Creating virtual environment (venv)...
python -m venv venv

echo Installing dependencies...
venv\Scripts\pip install -r requirements.txt

echo.
echo ==========================================
echo  Installation complete!
echo ==========================================
echo.
echo To run the translator:
echo   GUI: venv\Scripts\python tradutor_bg3_gui.py
echo   CLI: venv\Scripts\python tradutor_bg3.py
echo.
pause
