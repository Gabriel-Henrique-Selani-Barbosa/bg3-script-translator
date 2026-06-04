#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Tenta usar o venv primeiro
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    "$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/tradutor_bg3.py"
    exit 0
fi

# Fallback: python3 do sistema
python3 "$SCRIPT_DIR/tradutor_bg3.py"
