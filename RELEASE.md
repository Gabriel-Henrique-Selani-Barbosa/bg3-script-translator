# BG3 Script Translator — Release Notes

## Nome da Release
**v1.0.0 — Initial Release**

## Tag
`v1.0.0`

---

## Description (copiar e colar no GitHub)

```markdown
# BG3 Script Translator v1.0.0

Automatically translate **Baldur's Gate 3** mod localization files to any language via Google Translate.

## ✨ Features

- **Graphical Interface (GUI)** — Modern dark theme built with CustomTkinter
- **Terminal Mode (CLI)** — Full command-line support for automation and scripting
- **.pak Support** — Extract and repack `.pak` files (Windows native, Linux via Bottles/Wine)
- **Batch Mode** — Translate multiple mods in one run
- **Auto Language Detection** — Detects source language from folder name (`English/`, `Japanese/`, etc.)
- **Built-in LOCA Converter** — Convert `.loca` / `.locas` ↔ XML without external tools
- **Persistent Settings** — Saves your config to JSON (always in the script folder)
- **Multilingual UI** — Interface available in Portuguese, English, and Spanish
- **Cross-platform** — Windows (native) & Linux (via Bottles Flatpak auto-detection)

## 📦 What's Included

| File | Purpose |
|------|---------|
| `tradutor_bg3_gui.py` | GUI mode (double-click to run) |
| `tradutor_bg3.py` | CLI mode (terminal) |
| `setup.bat` / `setup.sh` | One-click dependency installer |
| `build_exe.bat` | Generate standalone `.exe` for Windows |
| `README.md` | Full documentation |

## 🚀 Quick Start

1. Install Python 3.8+
2. Run `setup.bat` (Windows) or `./setup.sh` (Linux)
3. Launch the GUI: `python tradutor_bg3_gui.py`

## 📝 Notes

- A `_backups/` folder is auto-created next to your `.pak` files to preserve originals
- On Windows, CMD windows are hidden during `.pak` operations
- Requires internet connection for Google Translate

## 🔗 Links

- [LSLib / Divine.exe](https://github.com/Norbyte/lslib) — Required for `.pak` support
- [Report Issues](https://github.com/Gabriel-Henrique-Selani-Barbosa/bg3-script-translator/issues)
```

---

*Criado em: 2026-05-31*
