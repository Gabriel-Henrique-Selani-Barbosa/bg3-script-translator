@echo off
setlocal

REM Tenta usar o venv primeiro
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe "%~dp0tradutor_bg3.py"
    exit /b %errorlevel%
)

REM Fallback: python do sistema
python "%~dp0tradutor_bg3.py"
exit /b %errorlevel%
