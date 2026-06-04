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
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Make sure you have permission to write to this folder.
    pause
    exit /b 1
)

echo Installing dependencies...
venv\Scripts\pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  Installation complete!
echo ==========================================
echo.
echo To run the translator, double-click:
echo   run_gui.bat  - Graphical mode
echo   run_cli.bat  - Terminal mode
echo.
pause
