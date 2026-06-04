@echo off
echo ==========================================
echo  Instalador - Tradutor BG3
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Baixe e instale em: https://python.org/downloads
    echo IMPORTANTE: Marque "Add Python to PATH" na instalacao
    pause
    exit /b 1
)

echo Criando ambiente virtual (venv)...
python -m venv venv

echo Instalando dependencias...
venv\Scripts\pip install -r requirements.txt

echo.
echo ==========================================
echo  Instalacao concluida!
echo ==========================================
echo.
echo Para executar o tradutor:
echo   CLI: venv\Scripts\python tradutor_bg3.py
echo   GUI: venv\Scripts\python tradutor_bg3_gui.py
echo.
pause
