#!/bin/bash
echo "=========================================="
echo " Instalador - Tradutor BG3"
echo "=========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERRO: python3 nao encontrado!"
    echo "Instale Python 3: sudo apt install python3 python3-venv"
    exit 1
fi

echo "Criando ambiente virtual (venv)..."
python3 -m venv venv

echo "Instalando dependencias..."
venv/bin/pip install -r requirements.txt

echo ""
echo "=========================================="
echo " Instalacao concluida!"
echo "=========================================="
echo ""
echo "Para executar o tradutor:"
echo "  venv/bin/python tradutor_bg3.py"
echo ""
