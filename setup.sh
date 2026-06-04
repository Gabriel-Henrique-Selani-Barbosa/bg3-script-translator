#!/bin/bash
set -e

echo "=========================================="
echo " BG3 Script Translator - Installer"
echo "=========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found!"
    echo "Install Python 3: sudo apt install python3 python3-venv"
    exit 1
fi

echo "Creating virtual environment (venv)..."
python3 -m venv venv

echo "Installing dependencies..."
venv/bin/pip install -r requirements.txt

echo ""
echo "=========================================="
echo " Installation complete!"
echo "=========================================="
echo ""
echo "To run the translator:"
echo "  ./run_gui.sh  - Graphical mode"
echo "  ./run_cli.sh  - Terminal mode"
echo ""
