@echo off
chcp 65001 >nul
echo ==========================================
echo  Gerador de .exe - Tradutor BG3
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Baixe em: https://python.org/downloads
    echo Marque "Add Python to PATH"
    pause
    exit /b 1
)

echo [1/5] Criando ambiente virtual...
python -m venv build_venv

echo [2/5] Instalando dependencias...
build_venv\Scripts\pip install -r requirements.txt pyinstaller

echo [3/5] Gerando Tradutor_BG3.exe (modo terminal)...
build_venv\Scripts\pyinstaller ^
    --onefile ^
    --name "Tradutor_BG3" ^
    --console ^
    --clean ^
    --distpath . ^
    --workpath build_temp ^
    --specpath build_temp ^
    tradutor_bg3.py

echo [4/5] Gerando Tradutor_BG3_GUI.exe (modo grafico)...
build_venv\Scripts\pyinstaller ^
    --onefile ^
    --name "Tradutor_BG3_GUI" ^
    --noconsole ^
    --hidden-import tkinter ^
    --hidden-import customtkinter ^
    --clean ^
    --distpath . ^
    --workpath build_temp_gui ^
    --specpath build_temp_gui ^
    tradutor_bg3_gui.py

echo [5/5] Limpando arquivos temporarios...
rmdir /s /q build_temp 2>nul
rmdir /s /q build_temp_gui 2>nul
rmdir /s /q build_venv 2>nul

echo.
echo ==========================================
echo  CONCLUIDO!
echo ==========================================
echo.
if exist "Tradutor_BG3.exe" (
    echo [CLI]  Tradutor_BG3.exe       - Modo terminal
echo.
) else (
    echo [CLI]  ERRO: Tradutor_BG3.exe nao foi gerado.
)

if exist "Tradutor_BG3_GUI.exe" (
    echo [GUI]  Tradutor_BG3_GUI.exe   - Modo grafico
echo.
) else (
    echo [GUI]  ERRO: Tradutor_BG3_GUI.exe nao foi gerado.
)

echo.
echo Para usar:
echo   CLI: De duplo clique em Tradutor_BG3.exe (abre terminal)
echo   GUI: De duplo clique em Tradutor_BG3_GUI.exe (abre janela)
echo.
pause
